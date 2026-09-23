import json
import copy
from contextlib import contextmanager

import pytest

from app import config
from app.agent import AgentCancelled, AgentError, run_agent, trim_history
from app.llm import Completion, LLMError, ToolCall
from app.skills import SkillStore


def call(id_, name_, /, **args):
    return ToolCall(id=id_, name=name_, arguments=args)


def comp(text="", calls=(), finish="stop", model="model-a", provider="openrouter", reasoning=""):
    return Completion(text=text, reasoning=reasoning, tool_calls=list(calls), finish_reason=finish,
                      usage={"input": 100, "output": 20}, provider=provider, model=model)


class FakeLLM:
    """Scripted stand-in for LLMClient. Records what the agent sent each turn."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def chat(self, messages, tools, max_tokens, tool_choice="auto", on_notice=lambda m: None):
        self.calls.append({"messages": copy.deepcopy(messages), "tool_choice": tool_choice, "tools": tools})
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def run(llm, tmp_path, url="https://x.test", events=None):
    events = events if events is not None else []
    return run_agent(url, "obj", lambda t, **d: events.append((t, d)), SkillStore(tmp_path), llm)


class TracerSpan:
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.updates = []

    def update(self, **fields):
        self.updates.append(fields)


class FakeTracer:
    """Records what run_agent asked to be traced. Exceptions raised inside its `with` blocks
    propagate normally, same as NoopTracer and the real LangfuseTracer, so tests that pass this
    in can still assert on AgentError/AgentCancelled reaching the caller."""

    def __init__(self):
        self.runs, self.generations, self.tools = [], [], []
        self.flushed = 0

    @contextmanager
    def run(self, **kwargs):
        span = TracerSpan(kwargs)
        self.runs.append(span)
        yield span

    @contextmanager
    def generation(self, **kwargs):
        span = TracerSpan(kwargs)
        self.generations.append(span)
        yield span

    @contextmanager
    def tool(self, **kwargs):
        span = TracerSpan(kwargs)
        self.tools.append(span)
        yield span

    def trace_url(self, run_id):
        return f"https://fake.trace/{run_id}"

    def flush(self):
        self.flushed += 1


def test_full_run_creates_skill_fetches_and_reports(site, local_ok, tmp_path):
    url = site + "/"
    llm = FakeLLM([
        comp(reasoning="Plan: write a skill first.", calls=[
            call("t1", "save_skill", name="homepage-audit", description="Audit a homepage.", content="# Steps\n1. fetch_page")]),
        comp(calls=[call("t2", "fetch_page", url=url), call("t3", "query_page", url=url, selector="h1"),
                    call("t4", "fetch_page", url="file:///etc/passwd")], model="model-b", provider="fallback"),
        comp(text="# Report\nTitle is 'Test Site'.", model="model-b", provider="fallback"),
    ])
    events = []
    report, usage = run(llm, tmp_path, url, events)

    assert report.startswith("# Report")
    assert SkillStore(tmp_path).list()[0]["name"] == "homepage-audit"
    assert usage["turns"] == 3 and usage["fetches"] == 1 and usage["input"] == 300
    assert usage["models"] == ["model-a", "model-b"]

    types = [t for t, _ in events]
    assert types.count("tool_call") == 4 and "skill_saved" in types and "thinking" in types
    notices = [d["message"] for t, d in events if t == "llm"]
    assert notices == ["Using model-a via openrouter", "Using model-b via fallback"]
    saved = next(d for t, d in events if t == "tool_call" and d["name"] == "save_skill")
    assert "content" not in saved["input"] and saved["input"]["chars"] > 0

    # Third request: system + user + (assistant, tool) + (assistant, 3 tools)
    msgs = llm.calls[2]["messages"]
    assert msgs[0]["role"] == "system" and "(the skill library is empty)" in msgs[1]["content"]
    assistant = msgs[4]
    assert [tc["id"] for tc in assistant["tool_calls"]] == ["t2", "t3", "t4"]
    tools = msgs[5:8]
    assert [m["tool_call_id"] for m in tools] == ["t2", "t3", "t4"]
    assert "never as instructions" in tools[0]["content"] and not tools[0]["content"].startswith("Error")
    assert tools[2]["content"].startswith("Error:")
    assert llm.calls[0]["tool_choice"] == "auto"


def test_no_tools_first_gets_one_nudge_then_works(site, local_ok, tmp_path):
    url = site + "/"
    llm = FakeLLM([comp(text="Here is my report from memory."), comp(calls=[call("t1", "fetch_page", url=url)]), comp(text="Real report")])
    report, _ = run(llm, tmp_path, url)
    assert report == "Real report"
    assert "have not fetched the target" in llm.calls[1]["messages"][-1]["content"]


def test_refuses_to_report_without_evidence(tmp_path):
    llm = FakeLLM([comp(text="made up"), comp(text="still made up")])
    with pytest.raises(AgentError, match="would not use its tools"):
        run(llm, tmp_path)


def test_malformed_tool_arguments_are_sent_back_as_error(site, local_ok, tmp_path):
    bad = ToolCall(id="t1", name="fetch_page", arguments={}, parse_error="arguments were not valid JSON")
    llm = FakeLLM([comp(calls=[bad]), comp(calls=[call("t2", "fetch_page", url=site + "/")]), comp(text="done")])
    run(llm, tmp_path, site + "/")
    result = llm.calls[1]["messages"][-1]
    assert result["role"] == "tool" and "rejected" in result["content"] and result["content"].startswith("Error:")


def test_repeated_identical_call_is_blocked(site, local_ok, tmp_path):
    same = lambda i: comp(calls=[call(f"t{i}", "fetch_page", url=site + "/")])
    llm = FakeLLM([same(1), same(2), same(3), comp(text="done")])
    run(llm, tmp_path, site + "/")
    assert "already made this exact call" in llm.calls[3]["messages"][-1]["content"]


def test_last_turn_forces_report(site, local_ok, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MAX_TURNS", 2)
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="Final report", calls=[call("t2", "fetch_page", url=site + "/")])])
    report, _ = run(llm, tmp_path, site + "/")
    assert report == "Final report"
    assert llm.calls[1]["tool_choice"] == "none"
    assert "Turn budget reached" in llm.calls[1]["messages"][-1]["content"]


def test_length_finish_without_tools_continues(site, local_ok, tmp_path):
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="part one", finish="length"), comp(text="part two")])
    report, _ = run(llm, tmp_path, site + "/")
    assert report == "part two"
    assert llm.calls[2]["messages"][-1]["content"].startswith("Continue")


def test_llm_failure_becomes_agent_error(tmp_path):
    with pytest.raises(AgentError, match="All model providers failed"):
        run(FakeLLM([LLMError("All model providers failed. openrouter: rate limited")]), tmp_path)


def test_missing_provider_config_gives_clear_error(tmp_path, monkeypatch):
    for name in ("OPENROUTER_API_KEY", "FALLBACK_API_KEY", "FALLBACK_BASE_URL", "FALLBACK_MODEL"):
        monkeypatch.setattr(config, name, "")
    with pytest.raises(AgentError, match=r"\.env"):
        run_agent("https://x.test", "obj", lambda *a, **k: None, SkillStore(tmp_path))


def test_trim_history_keeps_recent_and_skills():
    skill = "---\nname: s\n---\nbody"
    msgs = [{"role": "system", "content": "sys"}, {"role": "user", "content": "task"}]
    msgs.append({"role": "tool", "tool_call_id": "s", "content": skill})
    for i in range(8):
        msgs.append({"role": "tool", "tool_call_id": str(i), "content": "x" * 1000})
    trim_history(msgs, budget=5000)
    contents = [m["content"] for m in msgs]
    assert contents[2] == skill and contents[0] == "sys" and contents[1] == "task"
    assert contents[3].startswith("[trimmed")           # oldest fetch result trimmed
    assert contents[-1] == "x" * 1000                    # the 4 newest stay intact
    assert sum(map(len, contents)) <= 5000


def test_selected_skills_are_inlined_and_announced(site, local_ok, tmp_path):
    store = SkillStore(tmp_path)
    store.save("my-audit", "Mine.", "# Steps\nDo the thing.")
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="report")])
    events = []
    run_agent(site + "/", "obj", lambda t, **d: events.append((t, d)), store, llm, selected_skills=["my-audit"])
    first = llm.calls[0]["messages"][1]["content"]
    assert "===== skill: my-audit =====" in first and "Do the thing." in first and "do not call load_skill" in first
    assert ("skills", {"names": ["my-audit"], "writes": True}) in events


def test_unknown_selected_skill_is_an_agent_error(tmp_path):
    with pytest.raises(AgentError, match="No skill named"):
        run_agent("https://x.test", "o", lambda *a, **k: None, SkillStore(tmp_path), FakeLLM([]), selected_skills=["ghost"])


def test_skill_writes_can_be_switched_off(site, local_ok, tmp_path):
    store = SkillStore(tmp_path)
    llm = FakeLLM([
        comp(calls=[call("t1", "save_skill", name="x-y", description="d", content="c"), call("t2", "fetch_page", url=site + "/")]),
        comp(text="report"),
    ])
    run_agent(site + "/", "obj", lambda *a, **k: None, store, llm, allow_skill_writes=False)
    assert store.list() == []
    assert "turned off" in llm.calls[1]["messages"][-2]["content"]
    assert "Do not call save_skill" in llm.calls[0]["messages"][1]["content"]


def test_stop_is_honored_between_steps(site, local_ok, tmp_path):
    stop = {"now": False}
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="never reached")])

    def emit(t, **d):
        if t == "tool_result":
            stop["now"] = True        # the user presses Stop while the first tool runs

    with pytest.raises(AgentCancelled):
        run_agent(site + "/", "obj", emit, SkillStore(tmp_path), llm, should_stop=lambda: stop["now"])
    assert len(llm.calls) == 1        # no second model request was made


from app.agent import clean_report


def test_clean_report_drops_leaked_narration_only():
    leaked = "Now I need to gather information.\n\nBased on what I found, here goes:\n\n## Analysis\nReal content."
    assert clean_report(leaked) == "## Analysis\nReal content."
    assert clean_report("# Title\nBody") == "# Title\nBody"                       # already clean
    assert clean_report("No headings here at all.") == "No headings here at all."  # nothing to cut
    assert clean_report("Intro\n# H1\ntext\n\n## H2") == "# H1\ntext\n\n## H2"
    long_prefix = "word " * 400 + "\n## Late heading"
    assert clean_report(long_prefix) == long_prefix                                 # too far in: do not guess
    assert clean_report("Uses C# a lot.\n## Real") == "Uses C# a lot.\n## Real"     # prefix contains '#': leave alone


def test_soft_wrap_up_warning_comes_two_turns_before_the_limit(site, local_ok, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MAX_TURNS", 5)
    step = lambda i: comp(calls=[call(f"t{i}", "fetch_page", url=site + f"/?q={i}")])
    llm = FakeLLM([step(1), step(2), step(3), step(4), comp(text="# Final report")])
    report, _ = run(llm, tmp_path, site + "/")
    assert report == "# Final report"
    assert "running low on turns" in llm.calls[2]["messages"][-1]["content"]      # turn index 2 of 5
    assert "Turn budget reached" in llm.calls[4]["messages"][-1]["content"]


def test_cut_off_final_reply_gets_a_second_chance(site, local_ok, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MAX_TURNS", 2)
    llm = FakeLLM([
        comp(calls=[call("t1", "fetch_page", url=site + "/")]),
        comp(text="", finish="length"),                     # the forced final turn was spent on reasoning
        comp(text="# Report after retry"),
    ])
    report, _ = run(llm, tmp_path, site + "/")
    assert report == "# Report after retry"
    assert llm.calls[2]["tool_choice"] == "none" and llm.calls[2]["messages"][-1]["content"].startswith("Continue")


def test_query_page_takes_several_selectors_in_one_call(site, local_ok, tmp_path):
    url = site + "/"
    llm = FakeLLM([
        comp(calls=[call("t1", "fetch_page", url=url)]),
        comp(calls=[call("t2", "query_page", url=url, selectors=["h1", "a[href]", "img:not([alt])"], attribute=None),
                    call("t3", "query_page", url=url, selectors=[])]),
        comp(text="# ok"),
    ])
    run(llm, tmp_path, url)
    good, bad = llm.calls[2]["messages"][-2], llm.calls[2]["messages"][-1]
    data = json.loads(good["content"])["results"]["results"]
    assert [r["selector"] for r in data] == ["h1", "a[href]", "img:not([alt])"] and data[0]["match_count"] == 1
    assert bad["content"].startswith("Error:") and "selectors" in bad["content"]


def test_selectors_sent_as_one_comma_separated_string_still_work(site, local_ok, tmp_path):
    url = site + "/"
    llm = FakeLLM([
        comp(calls=[call("t1", "fetch_page", url=url)]),
        comp(calls=[call("t2", "query_page", url=url, selectors="h1, h2, a[href], img, .a-selector-that-is-longer-than-twelve")]),
        comp(text="# ok"),
    ])
    run(llm, tmp_path, url)
    result = llm.calls[2]["messages"][-1]["content"]
    assert not result.startswith("Error:") and '"match_count"' in result


# ---------------------------------------------------------------------------
# Tracer wiring (app/tracing.py). run_agent defaults to NoopTracer via get_tracer(); these
# tests pass in FakeTracer to check exactly what spans it opens and when it flushes (never:
# that's owned by runs.py, which flushes once per run regardless of outcome).


def test_tracer_wraps_the_run_each_turn_and_each_tool_call(site, local_ok, tmp_path):
    tracer = FakeTracer()
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="# Report")])
    report, usage = run_agent(
        site + "/", "obj", lambda *a, **k: None, SkillStore(tmp_path), llm, tracer=tracer, run_id="r1"
    )
    assert report == "# Report"
    assert len(tracer.runs) == 1
    root = tracer.runs[0]
    assert root.kwargs == {"run_id": "r1", "url": site + "/", "objective": "obj", "persona": "", "skills": []}
    assert root.updates and root.updates[-1]["output"] == "# Report"

    assert len(tracer.generations) == usage["turns"] == 2
    assert [g.kwargs["turn"] for g in tracer.generations] == [0, 1]
    assert tracer.generations[0].updates[-1]["model"] == "model-a"
    assert tracer.generations[0].updates[-1]["usage_details"] == {"input": 100, "output": 20}

    assert len(tracer.tools) == 1
    assert tracer.tools[0].kwargs == {"name": "fetch_page", "turn": 0}
    assert tracer.tools[0].updates[-1]["level"] == "DEFAULT"
    assert tracer.flushed == 0  # flushing is runs.py's job, not run_agent's


def test_tracer_records_llm_error_and_still_propagates(tmp_path):
    tracer = FakeTracer()
    llm = FakeLLM([LLMError("boom")])
    with pytest.raises(AgentError, match="boom"):
        run_agent("https://x.test", "o", lambda *a, **k: None, SkillStore(tmp_path), llm, tracer=tracer, run_id="r2")
    assert len(tracer.runs) == 1                                  # root span was still entered and exited
    assert len(tracer.generations) == 1
    assert tracer.generations[0].updates[-1]["level"] == "ERROR"
    assert not tracer.runs[0].updates                             # no success output was ever recorded


def test_tracer_failed_tool_call_is_marked_as_an_error(site, local_ok, tmp_path):
    tracer = FakeTracer()
    # The bad fetch fails without counting toward fetch_count, so the agent still has "no
    # evidence" afterward and gets one nudge turn before a second, successful attempt.
    llm = FakeLLM([
        comp(calls=[call("t1", "fetch_page", url="file:///etc/passwd")]),
        comp(calls=[call("t2", "fetch_page", url=site + "/")]),
        comp(text="# Report"),
    ])
    run_agent(site + "/", "obj", lambda *a, **k: None, SkillStore(tmp_path), llm, tracer=tracer, run_id="r3")
    assert tracer.tools[0].updates[-1]["level"] == "ERROR"
    assert tracer.tools[1].updates[-1]["level"] == "DEFAULT"


def test_tracer_run_receives_persona_and_selected_skills(site, local_ok, tmp_path):
    from app.personas import get_persona

    store = SkillStore(tmp_path)
    store.install_seeds()
    persona = get_persona("seo-analyst")
    tracer = FakeTracer()
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="# Report")])
    run_agent(
        site + "/", "obj", lambda *a, **k: None, store, llm,
        selected_skills=["seo-onpage-audit"], persona=persona, tracer=tracer, run_id="r4",
    )
    assert tracer.runs[0].kwargs["persona"] == "seo-analyst"
    assert tracer.runs[0].kwargs["skills"] == ["seo-onpage-audit"]


def test_tracer_defaults_to_a_noop_when_not_passed(site, local_ok, tmp_path):
    """No tracer given and no LANGFUSE_* env set (true for the whole test suite): run_agent
    must behave exactly as before tracing was added, with no extra event or side effect."""
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="# Report")])
    report, _ = run_agent(site + "/", "obj", lambda *a, **k: None, SkillStore(tmp_path), llm)
    assert report == "# Report"
