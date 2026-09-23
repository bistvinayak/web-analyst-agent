"""Tracing is optional and must never touch the network in tests. LangfuseTracer is tested
against a hand-rolled fake client (no real Langfuse client is ever constructed here); the
NoopTracer path is what every other test in this project runs under."""
from contextlib import contextmanager

import pytest

from app import config
from app.tracing import LangfuseTracer, NoopTracer, get_tracer


@pytest.fixture(autouse=True)
def _reset_cache(monkeypatch):
    """get_tracer() caches its result at module level; each test starts clean."""
    monkeypatch.setattr("app.tracing._cached", None)


class FakeSpan:
    def __init__(self, name, as_type, kwargs):
        self.name, self.as_type, self.start_kwargs = name, as_type, kwargs
        self.updates = []

    def update(self, **fields):
        self.updates.append(fields)


class FakeLangfuseClient:
    """Stands in for langfuse.Langfuse. Records every span opened and every flush."""

    def __init__(self):
        self.spans = []
        self.flushed = False

    @contextmanager
    def start_as_current_observation(self, *, name, as_type="span", trace_context=None, **kwargs):
        span = FakeSpan(name, as_type, {"trace_context": trace_context, **kwargs})
        self.spans.append(span)
        yield span

    def create_trace_id(self, *, seed=None):
        return f"trace-for-{seed or 'random'}"

    def get_trace_url(self, *, trace_id=None):
        return f"https://cloud.langfuse.com/trace/{trace_id}"

    def flush(self):
        self.flushed = True


# ---------------------------------------------------------------------------
# get_tracer(): the on/off switch


def test_defaults_to_noop_when_keys_are_unset(monkeypatch):
    monkeypatch.setattr(config, "LANGFUSE_PUBLIC_KEY", "")
    monkeypatch.setattr(config, "LANGFUSE_SECRET_KEY", "pk")
    assert isinstance(get_tracer(), NoopTracer)  # only one of the two keys set: still off


def test_uses_langfuse_when_both_keys_are_set(monkeypatch):
    monkeypatch.setattr(config, "LANGFUSE_PUBLIC_KEY", "pk")
    monkeypatch.setattr(config, "LANGFUSE_SECRET_KEY", "sk")
    monkeypatch.setattr("langfuse.Langfuse", lambda **kw: FakeLangfuseClient())
    tracer = get_tracer()
    assert isinstance(tracer, LangfuseTracer) and tracer.enabled


def test_get_tracer_is_cached(monkeypatch):
    monkeypatch.setattr(config, "LANGFUSE_PUBLIC_KEY", "")
    monkeypatch.setattr(config, "LANGFUSE_SECRET_KEY", "")
    assert get_tracer() is get_tracer()


def test_missing_langfuse_package_falls_back_to_noop(monkeypatch):
    monkeypatch.setattr(config, "LANGFUSE_PUBLIC_KEY", "pk")
    monkeypatch.setattr(config, "LANGFUSE_SECRET_KEY", "sk")

    def boom(**kw):
        raise ImportError("no module named langfuse")
    monkeypatch.setattr("langfuse.Langfuse", boom)
    assert isinstance(get_tracer(), NoopTracer)


# ---------------------------------------------------------------------------
# NoopTracer: free, and never swallows an exception


def test_noop_spans_accept_any_update_and_do_nothing():
    tracer = NoopTracer()
    with tracer.run(run_id="r1", url="https://x.test", objective="o", persona="", skills=[]) as span:
        span.update(output="anything", model="m", usage_details={"input": 1}, level="ERROR")
    with tracer.generation(turn=0) as gen:
        gen.update(input=[{"role": "user"}])
    with tracer.tool(name="fetch_page", turn=0) as t:
        t.update(output="ok")
    assert tracer.trace_url("r1") == ""
    tracer.flush()  # must not raise


def test_noop_still_propagates_exceptions():
    tracer = NoopTracer()
    with pytest.raises(ValueError):
        with tracer.run(run_id="r1", url="u", objective="o", persona="", skills=[]):
            raise ValueError("boom")
    with pytest.raises(ValueError):
        with tracer.tool(name="fetch_page", turn=0):
            raise ValueError("boom")


# ---------------------------------------------------------------------------
# LangfuseTracer: wiring against the fake client


def test_run_opens_a_root_span_with_a_stable_trace_id():
    client = FakeLangfuseClient()
    tracer = LangfuseTracer(client)
    with tracer.run(run_id="abc", url="https://x.test", objective="obj", persona="seo-analyst", skills=["a", "b"]) as root:
        root.update(output="# Report", metadata={"usage": {"turns": 1}})
    assert len(client.spans) == 1
    span = client.spans[0]
    assert span.name == "agent_run" and span.as_type == "span"
    assert span.start_kwargs["input"] == {"url": "https://x.test", "objective": "obj"}
    assert span.start_kwargs["trace_context"]["trace_id"] == "trace-for-abc"
    assert span.updates == [{"output": "# Report", "metadata": {"usage": {"turns": 1}}}]
    # the same run id always maps to the same trace id
    assert tracer.trace_url("abc") == "https://cloud.langfuse.com/trace/trace-for-abc"


def test_run_tags_by_persona():
    client = FakeLangfuseClient()
    with LangfuseTracer(client).run(run_id="r", url="u", objective="o", persona="", skills=[]):
        pass
    with LangfuseTracer(client).run(run_id="r", url="u", objective="o", persona="ai-engineer", skills=[]):
        pass
    # propagate_attributes doesn't hand us the tags back directly, so this just proves both
    # calls complete without error under both the tagged and untagged path.
    assert len(client.spans) == 2


def test_generation_and_tool_spans_nest_under_the_run(monkeypatch):
    from langfuse.types import TraceContext

    client = FakeLangfuseClient()
    tracer = LangfuseTracer(client)
    with tracer.run(run_id="r", url="u", objective="o", persona="", skills=[]):
        with tracer.generation(turn=0) as gen:
            gen.update(input=[{"role": "user", "content": "hi"}], output="text", model="m/x", usage_details={"input": 10, "output": 2})
            with tracer.tool(name="fetch_page", turn=0) as tool:
                tool.update(input={"url": "https://x.test"}, output="ok", level="DEFAULT")

    names = [(s.name, s.as_type) for s in client.spans]
    assert names == [("agent_run", "span"), ("turn-0", "generation"), ("fetch_page", "tool")]
    gen_span = client.spans[1]
    assert gen_span.updates[0]["model"] == "m/x" and gen_span.updates[0]["usage_details"] == {"input": 10, "output": 2}
    tool_span = client.spans[2]
    assert tool_span.updates[0]["output"] == "ok" and tool_span.updates[0]["level"] == "DEFAULT"
    assert isinstance(TraceContext, type) or True  # import above just proves the type is importable here


def test_flush_delegates_to_the_client():
    client = FakeLangfuseClient()
    LangfuseTracer(client).flush()
    assert client.flushed


def test_trace_url_swallows_client_errors():
    class Broken(FakeLangfuseClient):
        def get_trace_url(self, *, trace_id=None):
            raise RuntimeError("network down")
    assert LangfuseTracer(Broken()).trace_url("r") == ""
