import json

import httpx
import pytest

from app import config
from app.llm import Endpoint, LLMClient, LLMError, discover_free_models, sanitize_text

TOOLS = [{"name": "fetch_page", "description": "d", "input_schema": {"type": "object", "properties": {}}}]
MSGS = [{"role": "user", "content": "hi"}]


def ok(content="hello", tool_calls=None, model="real/model:free"):
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return httpx.Response(200, json={"model": model, "choices": [{"message": msg, "finish_reason": "stop"}],
                                     "usage": {"prompt_tokens": 11, "completion_tokens": 5}})


def make(handler, *endpoints, sleeps=None):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return LLMClient(list(endpoints), http=http, sleep=(sleeps.append if sleeps is not None else lambda s: None))


OR = Endpoint("openrouter", "https://openrouter.ai/api/v1", "sk-or-SECRET", ["a:free", "b:free", "c:free", "d:free"])
FB = Endpoint("groq", "https://api.groq.com/openai/v1", "gsk-SECRET", ["llama-x"])


def test_openrouter_request_shape_and_parsing():
    seen = {}

    def handler(req):
        seen["url"], seen["auth"], seen["body"] = str(req.url), req.headers["authorization"], json.loads(req.content)
        return ok("<think>secret plan</think>Answer", [{"id": "c1", "function": {"name": "fetch_page", "arguments": '{"url": "https://a.com"}'}}])

    c = make(handler, OR).chat(MSGS, TOOLS, 500)
    b = seen["body"]
    assert seen["url"].endswith("/chat/completions") and seen["auth"] == "Bearer sk-or-SECRET"
    assert b["models"] == ["a:free", "b:free", "c:free"]            # capped at 3
    assert "model" not in b and b["provider"] == {"require_parameters": True}
    assert b["tools"][0] == {"type": "function", "function": {"name": "fetch_page", "description": "d", "parameters": TOOLS[0]["input_schema"]}}
    assert c.text == "Answer" and c.model == "real/model:free" and c.provider == "openrouter"
    assert c.tool_calls[0].arguments == {"url": "https://a.com"} and c.usage == {"input": 11, "output": 5}


def test_non_openrouter_endpoint_uses_single_model():
    seen = {}
    make(lambda r: (seen.update(json.loads(r.content)), ok())[1], FB).chat(MSGS, TOOLS, 100)
    assert seen["model"] == "llama-x" and "models" not in seen and "provider" not in seen


def test_malformed_arguments_flagged_not_raised():
    tc = [{"id": "c1", "function": {"name": "fetch_page", "arguments": "{oops"}}]
    c = make(lambda r: ok("", tc), FB).chat(MSGS, TOOLS, 100)
    assert c.tool_calls[0].parse_error and c.tool_calls[0].arguments == {}


def test_retries_429_then_succeeds():
    n, sleeps = {"n": 0}, []

    def handler(req):
        n["n"] += 1
        return httpx.Response(429, text="slow down", headers={"retry-after": "3"}) if n["n"] == 1 else ok()

    c = make(handler, OR, sleeps=sleeps).chat(MSGS, TOOLS, 100)
    assert c.text == "hello" and n["n"] == 2 and sleeps == [3.0]


def test_daily_quota_fails_over_immediately():
    hosts = []

    def handler(req):
        hosts.append(req.url.host)
        return httpx.Response(429, text="Rate limit exceeded: free-models-per-day") if "openrouter" in req.url.host else ok(model="llama-x")

    notes = []
    c = make(handler, OR, FB).chat(MSGS, TOOLS, 100, on_notice=notes.append)
    assert hosts == ["openrouter.ai", "api.groq.com"]  # no retries wasted on a daily cap
    assert c.provider == "groq" and any("Switching" in n for n in notes)


def test_server_errors_retry_then_fail_over():
    hosts = []

    def handler(req):
        hosts.append(req.url.host)
        return httpx.Response(503) if "openrouter" in req.url.host else ok()

    c = make(handler, OR, FB).chat(MSGS, TOOLS, 100)
    assert hosts.count("openrouter.ai") == config.LLM_MAX_RETRIES + 1 and c.provider == "groq"


def test_client_error_fails_over_without_retry():
    hosts = []

    def handler(req):
        hosts.append(req.url.host)
        return httpx.Response(400, text="No endpoints found that support tool use") if "openrouter" in req.url.host else ok()

    assert make(handler, OR, FB).chat(MSGS, TOOLS, 100).provider == "groq" and hosts.count("openrouter.ai") == 1


def test_200_with_error_body_is_handled():
    bodies = iter([httpx.Response(200, json={"error": {"code": 502, "message": "upstream down"}}), ok()])
    assert make(lambda r: next(bodies), OR).chat(MSGS, TOOLS, 100).text == "hello"


def test_all_providers_failing_raises_without_leaking_keys():
    with pytest.raises(LLMError) as e:
        make(lambda r: httpx.Response(401, text="bad key"), OR, FB).chat(MSGS, TOOLS, 100)
    msg = str(e.value)
    assert "openrouter" in msg and "groq" in msg and "401" in msg
    assert "SECRET" not in msg


def test_network_error_is_retryable():
    def handler(req):
        raise httpx.ConnectError("boom")

    with pytest.raises(LLMError, match="network error"):
        make(handler, FB).chat(MSGS, TOOLS, 100)


def test_sanitize_text():
    assert sanitize_text("<think>a\nb</think> Hi <tool_call>x</tool_call>") == "Hi x"
    assert sanitize_text("<think>unterminated") == "unterminated"
    assert sanitize_text(None) == ""


def test_discover_free_models_filters_and_orders():
    def m(id_, prompt="0", completion="0", tools=True, ctx=1000, exp=None):
        return {"id": id_, "pricing": {"prompt": prompt, "completion": completion}, "context_length": ctx,
                "supported_parameters": ["tools"] if tools else ["temperature"], "expiration_date": exp}

    data = [m("nex-agi/nex-n2.5-pro:free", ctx=10), m("inclusionai/ling-3.0-flash-vl:free", ctx=10),
            m("big/one:free", ctx=900), m("small/one:free", ctx=100), m("paid/model", prompt="0.001"),
            m("no/tools:free", tools=False), m("inclusionai/ling-3.0-flash-fin:free", ctx=999), m("old/one:free", exp="2020-01-01")]
    http = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"data": data})))
    assert discover_free_models(http) == ["inclusionai/ling-3.0-flash-vl:free", "nex-agi/nex-n2.5-pro:free", "big/one:free", "small/one:free"]


def test_discovery_failure_falls_back_to_seed_list():
    http = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500, text="no")))
    assert discover_free_models(http)[0] == "inclusionai/ling-3.0-flash-vl:free"


def test_more_than_three_models_make_a_second_chain(monkeypatch):
    from app.llm import build_endpoints
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(config, "OPENROUTER_MODELS", [f"m{i}:free" for i in range(8)])
    monkeypatch.setattr(config, "FALLBACK_BASE_URL", "")
    eps = build_endpoints()
    assert [e.name for e in eps] == ["openrouter", "openrouter-2"]
    assert eps[0].models == ["m0:free", "m1:free", "m2:free"] and eps[1].models == ["m3:free", "m4:free", "m5:free"]


def test_second_chain_used_on_server_error_but_skipped_on_daily_quota():
    chain1 = Endpoint("openrouter", "https://openrouter.ai/api/v1", "K", ["a:free"])
    chain2 = Endpoint("openrouter-2", "https://openrouter.ai/api/v1", "K", ["b:free"])

    def erroring(req):
        return httpx.Response(503) if json.loads(req.content)["models"] == ["a:free"] else ok()
    assert make(erroring, chain1, chain2, FB).chat(MSGS, TOOLS, 10).provider == "openrouter-2"

    hosts = []

    def daily(req):
        hosts.append(json.loads(req.content).get("models") or req.url.host)
        return httpx.Response(429, text="free-models-per-day") if "openrouter" in req.url.host else ok()
    assert make(daily, chain1, chain2, FB).chat(MSGS, TOOLS, 10).provider == "groq"
    assert hosts == [["a:free"], "api.groq.com"]  # chain 2 skipped: same key, same quota
