"""Provider-neutral chat client for OpenAI-compatible APIs, with failover.

Endpoints are tried in order (OpenRouter first, then your fallback). Within an endpoint,
429/5xx/network errors are retried with backoff. Anything that still fails moves on to the
next endpoint. The conversation history uses the plain OpenAI message format, so it can
switch providers mid-run without translation.

Lessons carried over from the Vidur project:
  * OpenRouter rejects a `models` array with more than 3 entries (HTTP 400).
  * Some free models ignore tool calling or leak <think>/<tool_call> text.
  * The free model roster changes often, so it is discovered live instead of hardcoded.
"""
import json
import re
import time
from dataclasses import dataclass, field
from typing import Callable

import httpx

from . import config

OPENROUTER_MAX_MODELS = 3
MAX_WAIT_SECONDS = 20  # longer than this and we fail over instead of waiting
# Measured with scripts/rank_models.py (see README). Used first when models are auto-discovered,
# and as the whole list if discovery fails. Vendors are mixed so one outage cannot sink a chain.
SEED_FREE_MODELS = [
    "poolside/laguna-s-2.1:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "inclusionai/ling-3.0-flash-vl:free",
    "poolside/laguna-xs-2.1:free",
    "dots-studio/dots-3-note-preview:free",
    "openrouter/free",  # router: a different free model each request, so it stays last
]
# Domain-specialised variants are poor general agents.
_SKIP_MODEL_HINTS = ("-sante", "-fin")


class LLMError(Exception):
    """Every configured endpoint failed. The message lists why, without secrets."""


@dataclass
class Endpoint:
    name: str
    base_url: str
    api_key: str
    models: list[str]

    @property
    def is_openrouter(self) -> bool:
        return "openrouter.ai" in self.base_url


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict
    parse_error: str = ""


@dataclass
class Completion:
    text: str
    reasoning: str
    tool_calls: list[ToolCall]
    finish_reason: str
    usage: dict
    provider: str
    model: str


class _Retryable(Exception):
    def __init__(self, reason: str, wait: float = 0.0, give_up: bool = False):
        super().__init__(reason)
        self.reason, self.wait, self.give_up = reason, wait, give_up


class _Failed(Exception):
    pass


def sanitize_text(text: str) -> str:
    """Strip chain-of-thought and tool-call markup that some models leak into content."""
    text = re.sub(r"<think>[\s\S]*?</think>", "", text or "", flags=re.I)
    text = re.sub(r"</?think>", "", text, flags=re.I)
    text = re.sub(r"</?tool_call>", "", text, flags=re.I)
    return text.strip()


def _short(body: str, n: int = 200) -> str:
    return " ".join((body or "").split())[:n]


def discover_free_models(http: httpx.Client | None = None, base_url: str | None = None) -> list[str]:
    """Free, tool-capable models from OpenRouter's public list, best guess first."""
    base_url = base_url or config.OPENROUTER_BASE_URL
    own = http is None
    http = http or httpx.Client(timeout=15)
    try:
        data = http.get(f"{base_url}/models").json()["data"]
    except Exception:
        return list(SEED_FREE_MODELS)
    finally:
        if own:
            http.close()

    now = time.time()
    live = {}
    for m in data:
        pricing = m.get("pricing") or {}
        free = str(pricing.get("prompt")) in ("0", "0.0") and str(pricing.get("completion")) in ("0", "0.0")
        expired = False
        if m.get("expiration_date"):
            try:
                expired = time.mktime(time.strptime(m["expiration_date"][:10], "%Y-%m-%d")) < now
            except ValueError:
                pass
        if free and "tools" in (m.get("supported_parameters") or []) and not expired:
            live[m["id"]] = m.get("context_length") or 0

    ordered = [m for m in SEED_FREE_MODELS if m in live]  # known-good first
    rest = sorted(
        (m for m in live if m not in ordered and not any(h in m for h in _SKIP_MODEL_HINTS)),
        key=lambda m: -live[m],
    )
    return (ordered + rest) or list(SEED_FREE_MODELS)


def build_endpoints() -> list[Endpoint]:
    endpoints = []
    if config.OPENROUTER_API_KEY:
        models = config.OPENROUTER_MODELS or discover_free_models()
        # One request can carry only 3 models, so models 4-6 become a second chain on the same key.
        for n, start in enumerate(range(0, min(len(models), 2 * OPENROUTER_MAX_MODELS), OPENROUTER_MAX_MODELS)):
            name = "openrouter" if n == 0 else f"openrouter-{n + 1}"
            endpoints.append(
                Endpoint(name, config.OPENROUTER_BASE_URL, config.OPENROUTER_API_KEY, models[start : start + OPENROUTER_MAX_MODELS])
            )
    if config.FALLBACK_BASE_URL and config.FALLBACK_API_KEY and config.FALLBACK_MODEL:
        endpoints.append(
            Endpoint(config.FALLBACK_NAME, config.FALLBACK_BASE_URL.rstrip("/"), config.FALLBACK_API_KEY, [config.FALLBACK_MODEL])
        )
    if not endpoints:
        raise LLMError(
            "No model provider is configured. Copy .env.example to .env and set OPENROUTER_API_KEY "
            "(and optionally the FALLBACK_* values), then restart the server."
        )
    return endpoints


class LLMClient:
    def __init__(
        self,
        endpoints: list[Endpoint],
        http: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.endpoints = endpoints
        self._http = http or httpx.Client(timeout=httpx.Timeout(config.LLM_TIMEOUT))
        self._sleep = sleep

    def close(self) -> None:
        self._http.close()

    # -- public ------------------------------------------------------------

    def chat(
        self,
        messages: list[dict],
        tools: list[dict],
        max_tokens: int,
        tool_choice: str = "auto",
        on_notice: Callable[[str], None] = lambda msg: None,
    ) -> Completion:
        failures: list[str] = []
        exhausted: set[tuple[str, str]] = set()  # (base_url, key) pairs whose daily quota is spent
        for ep in self.endpoints:
            if (ep.base_url, ep.api_key) in exhausted:
                continue  # same account, same quota: another chain would fail the same way
            try:
                return self._chat_endpoint(ep, messages, tools, max_tokens, tool_choice, on_notice)
            except _Failed as e:
                failures.append(f"{ep.name}: {e}")
                if "daily quota" in str(e):
                    exhausted.add((ep.base_url, ep.api_key))
                if ep is not self.endpoints[-1]:
                    on_notice(f"{ep.name} failed ({e}). Switching to the next provider.")
        raise LLMError("All model providers failed. " + " | ".join(failures))

    # -- internals ---------------------------------------------------------

    def _chat_endpoint(self, ep, messages, tools, max_tokens, tool_choice, on_notice) -> Completion:
        last_reason = "unknown error"
        for attempt in range(config.LLM_MAX_RETRIES + 1):
            try:
                return self._call(ep, messages, tools, max_tokens, tool_choice)
            except _Retryable as e:
                last_reason = e.reason
                if e.give_up or attempt == config.LLM_MAX_RETRIES:
                    break
                wait = min(e.wait or 2 ** (attempt + 1), MAX_WAIT_SECONDS)
                on_notice(f"{ep.name}: {e.reason}. Retrying in {wait:.0f}s.")
                self._sleep(wait)
        raise _Failed(last_reason)

    def _call(self, ep: Endpoint, messages, tools, max_tokens, tool_choice) -> Completion:
        body: dict = {
            "messages": messages,
            "max_tokens": max_tokens,
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}} for t in tools],
            "tool_choice": tool_choice,
        }
        headers = {"Authorization": f"Bearer {ep.api_key}", "Content-Type": "application/json"}
        if ep.is_openrouter:
            # `models` is OpenRouter's server-side fallback chain, hard-capped at 3 entries.
            body["models"] = ep.models[:OPENROUTER_MAX_MODELS]
            # Only route to providers that honor every parameter we send, tools included.
            body["provider"] = {"require_parameters": True}
            headers.update({"HTTP-Referer": "https://github.com/web-analyst-agent", "X-Title": "Web Analyst Agent"})
        else:
            body["model"] = ep.models[0]

        try:
            r = self._http.post(f"{ep.base_url}/chat/completions", json=body, headers=headers)
        except httpx.TimeoutException:
            raise _Retryable("request timed out")
        except httpx.HTTPError as e:
            raise _Retryable(f"network error ({type(e).__name__})")

        if r.status_code == 429:
            text = r.text.lower()
            daily = "per-day" in text or "per day" in text or "daily" in text
            retry_after = r.headers.get("retry-after", "")
            wait = float(retry_after) if retry_after.replace(".", "", 1).isdigit() else 0.0
            raise _Retryable(
                "rate limited (daily quota used up)" if daily else "rate limited (429)",
                wait=wait,
                give_up=daily or wait > MAX_WAIT_SECONDS,
            )
        if r.status_code >= 500 or r.status_code in (408, 409):
            raise _Retryable(f"server error {r.status_code}")
        if r.status_code >= 400:
            raise _Failed(f"HTTP {r.status_code}: {_short(r.text)}")

        try:
            data = r.json()
        except ValueError:
            raise _Retryable("response was not JSON")

        # OpenRouter can return HTTP 200 with an error object and no choices.
        if data.get("error") and not data.get("choices"):
            err = data["error"]
            code = err.get("code") if isinstance(err, dict) else None
            msg = _short(err.get("message", "") if isinstance(err, dict) else str(err))
            if isinstance(code, int) and code < 500 and code != 429:
                raise _Failed(f"{code}: {msg}")
            raise _Retryable(f"provider error {code or ''}: {msg}".strip())
        if not data.get("choices"):
            raise _Retryable("empty response")

        choice = data["choices"][0]
        msg = choice.get("message") or {}
        calls = []
        for i, tc in enumerate(msg.get("tool_calls") or []):
            fn = tc.get("function") or {}
            raw = fn.get("arguments") or "{}"
            args, err = {}, ""
            try:
                args = json.loads(raw) if isinstance(raw, str) else dict(raw)
                if not isinstance(args, dict):
                    args, err = {}, "arguments must be a JSON object"
            except (ValueError, TypeError):
                err = "arguments were not valid JSON"
            calls.append(ToolCall(id=tc.get("id") or f"call_{int(time.time() * 1000)}_{i}", name=fn.get("name", ""), arguments=args, parse_error=err))

        usage = data.get("usage") or {}
        return Completion(
            text=sanitize_text(msg.get("content") or ""),
            reasoning=(msg.get("reasoning") or "").strip(),
            tool_calls=calls,
            finish_reason=choice.get("finish_reason") or "",
            usage={"input": usage.get("prompt_tokens", 0) or 0, "output": usage.get("completion_tokens", 0) or 0},
            provider=ep.name,
            model=data.get("model") or ep.models[0],
        )
