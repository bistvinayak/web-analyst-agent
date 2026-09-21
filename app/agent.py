"""The agent loop: an LLM (via OpenRouter, with a fallback provider) plus the tools in tools.py."""
import json
import re
from collections import Counter
from typing import Callable

from . import config
from .llm import LLMClient, LLMError, build_endpoints
from .prompts import SYSTEM_PROMPT, first_message
from .skills import SkillError, SkillStore
from .tools import TOOLS, ToolContext, run_tool
from .webfetch import Fetcher

Emit = Callable[..., None]

WRAP_UP_NOTE = (
    "Turn budget reached. Do not call any more tools. Write the final report now from the evidence "
    "you have, and state what you could not verify."
)
NO_EVIDENCE_NOTE = (
    "You have not fetched the target yet, so you have no evidence. Do not write a report from memory. "
    "Call fetch_page on the target URL now, using the tool-calling interface."
)
SKILL_PREFIX = "---\nname: "


class AgentError(Exception):
    pass


def _preview(text: str, n: int = 300) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n] + "..."


def _result_summary(name: str, content: str, is_error: bool) -> str:
    """One readable line for the UI instead of a slice of raw JSON."""
    if is_error:
        return _preview(content, 200)
    if name == "load_skill":
        return f"loaded, {len(content):,} characters"
    if name in ("fetch_page", "fetch_raw"):
        status = re.search(r'"status": (\d+)', content)
        size = re.search(r'"size_bytes": (\d+)', content)
        ctype = re.search(r'"content_type": "([^";]*)', content)
        title = re.search(r'"title": "((?:[^"\\]|\\.)*)"', content)
        if status:
            parts = [status.group(1)]
            if title:
                try:
                    parts.append(json.loads(f'"{title.group(1)}"'))
                except ValueError:
                    pass
            elif ctype:
                parts.append(ctype.group(1))
            if size:
                parts.append(f"{int(size.group(1)):,} bytes")
            return ", ".join(parts)
    if name == "query_page":
        m = re.search(r'"match_count": (\d+)', content)
        if m:
            return f"{m.group(1)} matches"
    return _preview(content)


def _tool_call_summary(name: str, args: dict) -> dict:
    """What the UI shows for a tool call. Keeps big skill bodies out of the event stream."""
    if name == "save_skill":
        return {"name": args.get("name"), "description": args.get("description"), "chars": len(args.get("content", ""))}
    return args


def trim_history(messages: list[dict], budget: int = 0) -> None:
    """Shrink old tool results in place once the conversation outgrows the context budget.

    Free models often have small context windows. The system prompt, the first user message,
    skill files, and the four most recent tool results are always kept intact.
    """
    budget = budget or config.CONTEXT_CHAR_BUDGET
    size = sum(len(m.get("content") or "") for m in messages)
    if size <= budget:
        return
    tool_idx = [i for i, m in enumerate(messages) if m["role"] == "tool"]
    for i in tool_idx[:-4]:
        content = messages[i]["content"]
        if content.startswith(SKILL_PREFIX) or content.startswith("[trimmed"):
            continue
        messages[i]["content"] = f"[trimmed to save context: {_preview(content, 100)}]"
        size -= len(content) - len(messages[i]["content"])
        if size <= budget:
            return


def run_agent(
    url: str,
    objective: str,
    emit: Emit,
    skills: SkillStore | None = None,
    llm: LLMClient | None = None,
    selected_skills: list[str] | None = None,
    allow_skill_writes: bool = True,
) -> tuple[str, dict]:
    """Run one analysis. Returns (report_markdown, usage). Raises AgentError on failure.

    selected_skills: skills the user picked. Their text is placed in the first message, which
    saves model requests. allow_skill_writes=False stops the agent from saving skills.
    """
    skills = skills or SkillStore()
    selected: list[tuple[str, str]] = []
    for name in selected_skills or []:
        try:
            selected.append((name, skills.load(name)))
        except SkillError as e:
            raise AgentError(str(e)) from e
    try:
        llm = llm or LLMClient(build_endpoints())
    except LLMError as e:
        raise AgentError(str(e)) from e
    fetcher = Fetcher()
    ctx = ToolContext(
        skills=skills, fetcher=fetcher, allow_skill_writes=allow_skill_writes,
        on_skill_saved=lambda info: emit("skill_saved", **info),
    )
    usage = {"input": 0, "output": 0, "turns": 0, "fetches": 0, "models": []}
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": first_message(url, objective, skills.catalog_text(), selected, allow_skill_writes)},
    ]
    if selected:
        emit("skills", names=[n for n, _ in selected], writes=allow_skill_writes)
    seen_calls: Counter = Counter()
    continuations = nudges = 0
    last_served = None

    try:
        for turn in range(config.MAX_TURNS):
            last_turn = turn == config.MAX_TURNS - 1
            if last_turn:
                messages.append({"role": "user", "content": WRAP_UP_NOTE})
            trim_history(messages)

            try:
                comp = llm.chat(
                    messages, TOOLS, config.MAX_TOKENS,
                    tool_choice="none" if last_turn else "auto",
                    on_notice=lambda msg: emit("llm", message=msg),
                )
            except LLMError as e:
                raise AgentError(str(e)) from e

            usage["turns"] += 1
            usage["input"] += comp.usage["input"]
            usage["output"] += comp.usage["output"]
            served = (comp.provider, comp.model)
            if served != last_served:
                emit("llm", message=f"Using {comp.model} via {comp.provider}")
                last_served = served
                if comp.model not in usage["models"]:
                    usage["models"].append(comp.model)

            if comp.reasoning:
                emit("thinking", text=comp.reasoning)
            if comp.text and comp.tool_calls:  # a reply with no tool call is the report, sent as its own event
                emit("text", text=comp.text)

            assistant: dict = {"role": "assistant", "content": comp.text or None}
            if comp.tool_calls and not last_turn:
                assistant["tool_calls"] = [
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}}
                    for tc in comp.tool_calls
                ]

            if comp.finish_reason == "length" and not comp.tool_calls:
                if continuations >= 2:
                    raise AgentError("The model kept hitting its output limit. Try a narrower objective or raise MAX_TOKENS.")
                continuations += 1
                messages += [assistant if comp.text else {"role": "assistant", "content": "..."},
                             {"role": "user", "content": "Continue exactly where you left off."}]
                continue

            if not comp.tool_calls or last_turn:
                if not comp.text:
                    raise AgentError("The model returned an empty response. Try again, or configure a different model.")
                if fetcher.fetch_count == 0 and not last_turn:
                    if nudges >= 1:
                        raise AgentError(
                            "The model would not use its tools, so there is no evidence to report. "
                            "Set OPENROUTER_MODELS to a model that supports tool calling, or check the fallback model."
                        )
                    nudges += 1
                    messages += [assistant, {"role": "user", "content": NO_EVIDENCE_NOTE}]
                    continue
                report = comp.text
                if len(report) > config.MAX_REPORT_CHARS:
                    report = report[: config.MAX_REPORT_CHARS] + "\n\n[Report truncated: the model's output ran unusually long.]"
                usage["fetches"] = fetcher.fetch_count
                return report, usage

            messages.append(assistant)
            for tc in comp.tool_calls:
                emit("tool_call", id=tc.id, name=tc.name, input=_tool_call_summary(tc.name, tc.arguments))
                if tc.parse_error:
                    content, is_error = f"Your arguments for {tc.name} were rejected: {tc.parse_error}. Call it again with a valid JSON object.", True
                else:
                    key = (tc.name, json.dumps(tc.arguments, sort_keys=True))
                    seen_calls[key] += 1
                    if seen_calls[key] > 2:
                        content, is_error = "You already made this exact call and have its result above. Use that instead of repeating it.", True
                    else:
                        content, is_error = run_tool(ctx, tc.name, tc.arguments)
                emit("tool_result", id=tc.id, name=tc.name, ok=not is_error, preview=_result_summary(tc.name, content, is_error))
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": ("Error: " + content) if is_error else content})

        raise AgentError("The agent hit its turn limit without producing a report.")
    finally:
        usage["fetches"] = fetcher.fetch_count
        fetcher.close()
