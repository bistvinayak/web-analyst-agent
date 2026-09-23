"""Optional observability via Langfuse: one trace per run, a generation per model turn, a
span per tool call.

Disabled by default. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env to turn it on;
with them unset, get_tracer() returns NoopTracer and the agent behaves exactly as before, with
no import of the langfuse package and no network calls. Nothing else in the codebase should
import the langfuse package directly, so this stays the one place that knows its API.
"""
from contextlib import contextmanager
from typing import Any, Iterator, Protocol

from . import config


class Span(Protocol):
    def update(self, **fields: Any) -> None: ...


class Tracer(Protocol):
    """Duck-typed interface both NoopTracer and LangfuseTracer implement."""

    def run(self, *, run_id: str, url: str, objective: str, persona: str, skills: list[str]) -> "Iterator[Span]": ...
    def generation(self, *, turn: int) -> "Iterator[Span]": ...
    def tool(self, *, name: str, turn: int) -> "Iterator[Span]": ...
    def trace_url(self, run_id: str) -> str: ...
    def flush(self) -> None: ...


class _NoopSpan:
    def update(self, **fields: Any) -> None:
        pass


@contextmanager
def _noop_span() -> Iterator[_NoopSpan]:
    yield _NoopSpan()


class NoopTracer:
    """Used whenever Langfuse isn't configured. Every method is free and does nothing;
    the `with` blocks still run their body and still propagate exceptions normally."""

    enabled = False

    def run(self, **kwargs: Any):
        return _noop_span()

    def generation(self, **kwargs: Any):
        return _noop_span()

    def tool(self, **kwargs: Any):
        return _noop_span()

    def trace_url(self, run_id: str) -> str:
        return ""

    def flush(self) -> None:
        pass


class LangfuseTracer:
    """Wraps a Langfuse client (langfuse>=3, OpenTelemetry-based). `client` is injectable so
    tests can pass a fake and never touch the network or import the real package."""

    enabled = True

    def __init__(self, client: Any):
        self._client = client

    @contextmanager
    def run(self, *, run_id: str, url: str, objective: str, persona: str, skills: list[str]):
        from langfuse import propagate_attributes
        from langfuse.types import TraceContext

        tags = [f"persona:{persona}"] if persona else ["no-persona"]
        with propagate_attributes(
            trace_name="web-analyst-run",
            session_id=run_id,
            tags=tags,
            metadata={"url": url, "skills": ",".join(skills) or "auto"},
        ):
            with self._client.start_as_current_observation(
                trace_context=TraceContext(trace_id=self._trace_id(run_id)),
                name="agent_run",
                as_type="span",
                input={"url": url, "objective": objective},
            ) as span:
                yield span

    @contextmanager
    def generation(self, *, turn: int):
        with self._client.start_as_current_observation(
            name=f"turn-{turn}", as_type="generation", metadata={"turn": turn}
        ) as gen:
            yield gen

    @contextmanager
    def tool(self, *, name: str, turn: int):
        with self._client.start_as_current_observation(
            name=name, as_type="tool", metadata={"turn": turn}
        ) as span:
            yield span

    def _trace_id(self, run_id: str) -> str:
        # Our run ids (secrets.token_urlsafe) aren't valid OTel trace ids; derive a stable
        # one from the same seed so the same run always maps to the same Langfuse trace.
        return self._client.create_trace_id(seed=run_id or None)

    def trace_url(self, run_id: str) -> str:
        try:
            return self._client.get_trace_url(trace_id=self._trace_id(run_id)) or ""
        except Exception:
            return ""

    def flush(self) -> None:
        self._client.flush()


_cached: Tracer | None = None


def get_tracer() -> Tracer:
    """A tracer for the caller to use for one or more runs. Cached, since constructing a
    Langfuse client opens background threads that should be shared, not one per run."""
    global _cached
    if _cached is not None:
        return _cached
    if not (config.LANGFUSE_PUBLIC_KEY and config.LANGFUSE_SECRET_KEY):
        _cached = NoopTracer()
        return _cached
    try:
        from langfuse import Langfuse

        client = Langfuse(
            public_key=config.LANGFUSE_PUBLIC_KEY,
            secret_key=config.LANGFUSE_SECRET_KEY,
            base_url=config.LANGFUSE_HOST,
        )
        _cached = LangfuseTracer(client)
    except ImportError:
        _cached = NoopTracer()
    return _cached
