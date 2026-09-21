"""Runs: background execution of the agent, with a replayable event log per run."""
import json
import secrets
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .agent import AgentCancelled, AgentError, run_agent
from .skills import SkillStore


class TooManyRuns(Exception):
    pass


@dataclass
class Run:
    id: str
    url: str
    objective: str
    status: str = "running"  # running | done | error | cancelled
    report: str = ""
    error: str = ""
    usage: dict = field(default_factory=dict)
    skills: list[str] = field(default_factory=list)  # skills the user chose; empty means the agent decides
    allow_writes: bool = True
    created: float = field(default_factory=time.time)
    events: list[dict] = field(default_factory=list)
    stop_event: threading.Event = field(default_factory=threading.Event, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def finished(self) -> bool:
        return self.status != "running"

    def emit(self, type_: str, **data) -> None:
        with self._lock:
            event = {"seq": len(self.events), "ts": round(time.time(), 2), "type": type_, **data}
            self.events.append(event)

    def events_since(self, seq: int) -> list[dict]:
        with self._lock:
            return self.events[seq:]

    def meta(self) -> dict:
        return {
            "id": self.id, "url": self.url, "objective": self.objective, "status": self.status,
            "error": self.error, "usage": self.usage, "created": self.created,
            "skills": self.skills, "allow_writes": self.allow_writes,
        }


class RunManager:
    def __init__(self, skills: SkillStore, runs_dir: Path | None = None):
        self.skills = skills
        self.dir = Path(runs_dir or config.RUNS_DIR)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._runs: dict[str, Run] = {}
        self._lock = threading.Lock()

    def start(self, url: str, objective: str, skills: list[str] | None = None, allow_writes: bool = True) -> Run:
        with self._lock:
            active = sum(1 for r in self._runs.values() if not r.finished)
            if active >= config.MAX_CONCURRENT_RUNS:
                raise TooManyRuns(f"{active} runs are already in progress. Wait for one to finish.")
            run = Run(id=secrets.token_urlsafe(8), url=url, objective=objective, skills=list(skills or []), allow_writes=allow_writes)
            self._runs[run.id] = run
        threading.Thread(target=self._execute, args=(run,), daemon=True).start()
        return run

    def _execute(self, run: Run) -> None:
        run.emit("status", message="Started")
        try:
            run.report, run.usage = run_agent(
                run.url, run.objective, run.emit, self.skills,
                selected_skills=run.skills, allow_skill_writes=run.allow_writes,
                should_stop=run.stop_event.is_set,
            )
            run.status = "done"
            run.emit("report", markdown=run.report)
        except AgentCancelled:
            run.status = "cancelled"
            run.emit("cancelled", message="Stopped at your request.")
        except AgentError as e:
            run.status, run.error = "error", str(e)
            run.emit("error", message=str(e))
        except Exception as e:  # unexpected: log the type, keep details out of the UI
            run.status, run.error = "error", f"Unexpected error ({type(e).__name__})."
            run.emit("error", message=run.error)
        finally:
            run.emit("done", status=run.status, usage=run.usage)
            self._persist(run)

    def stop(self, run_id: str) -> "bool | None":
        """Ask a run to stop after its current step. None: unknown run. False: already finished."""
        with self._lock:
            run = self._runs.get(run_id)
        if run is None:
            return None
        if run.finished:
            return False
        run.stop_event.set()
        run.emit("status", message="Stopping after the current step")
        return True

    def _persist(self, run: Run) -> None:
        d = self.dir / run.id
        d.mkdir(parents=True, exist_ok=True)
        (d / "meta.json").write_text(json.dumps(run.meta()), encoding="utf-8")
        (d / "events.jsonl").write_text("\n".join(json.dumps(e) for e in run.events), encoding="utf-8")
        if run.report:
            (d / "report.md").write_text(run.report, encoding="utf-8")

    def get(self, run_id: str) -> Run | None:
        with self._lock:
            run = self._runs.get(run_id)
        if run:
            return run
        d = self.dir / run_id  # finished in an earlier server session?
        if run_id.replace("-", "").replace("_", "").isalnum() and (d / "meta.json").exists():
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            run = Run(id=meta["id"], url=meta["url"], objective=meta["objective"], status=meta["status"],
                      error=meta.get("error", ""), usage=meta.get("usage", {}), created=meta["created"],
                      skills=meta.get("skills", []), allow_writes=meta.get("allow_writes", True))
            if (d / "report.md").exists():
                run.report = (d / "report.md").read_text(encoding="utf-8")
            run.events = [json.loads(line) for line in (d / "events.jsonl").read_text(encoding="utf-8").splitlines() if line]
            return run
        return None

    def recent(self, limit: int = 20) -> list[dict]:
        metas = []
        for p in self.dir.glob("*/meta.json"):
            try:
                metas.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        for r in self._runs.values():
            if not r.finished:
                metas.append(r.meta())
        metas.sort(key=lambda m: m["created"], reverse=True)
        return metas[:limit]
