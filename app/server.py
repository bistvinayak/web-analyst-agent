import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from .personas import PersonaError, get_persona, load_personas
from .runs import RunManager, TooManyRuns
from .skills import SkillError, SkillStore

STATIC = Path(__file__).parent / "static"

app = FastAPI(title="Web Analyst Agent")
# Blocks DNS-rebinding attacks against a locally running server.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])

skills = SkillStore()
skills.install_seeds()
manager = RunManager(skills)


class RunRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2000)
    objective: str = Field(min_length=3, max_length=2000)
    skills: list[str] = Field(default_factory=list, max_length=5)  # empty: the agent chooses
    allow_skill_writes: bool = True
    persona: str = ""  # empty: no particular perspective

    @field_validator("url")
    @classmethod
    def _url(cls, v: str) -> str:
        v = v.strip()
        if "://" not in v:
            v = "https://" + v
        p = urlparse(v)
        if p.scheme not in ("http", "https") or not p.hostname:
            raise ValueError("Enter a valid http or https URL.")
        return v


@app.post("/api/runs", status_code=201)
def create_run(body: RunRequest):
    if body.persona:
        try:
            get_persona(body.persona)
        except PersonaError as e:
            raise HTTPException(422, str(e))
    for name in body.skills:
        try:
            skills.load(name)
        except SkillError:
            raise HTTPException(422, f"Unknown skill '{name}'. Refresh the page and pick again.")
    try:
        run = manager.start(body.url, body.objective.strip(), list(dict.fromkeys(body.skills)), body.allow_skill_writes, body.persona)
    except TooManyRuns as e:
        raise HTTPException(429, str(e))
    return {"id": run.id}


@app.get("/api/runs")
def list_runs():
    return manager.recent()


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = manager.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found.")
    return {**run.meta(), "report": run.report}


@app.post("/api/runs/{run_id}/stop", status_code=202)
def stop_run(run_id: str):
    result = manager.stop(run_id)
    if result is None:
        raise HTTPException(404, "Run not found.")
    if result is False:
        raise HTTPException(409, "That run has already finished.")
    return {"stopping": True}


@app.get("/api/runs/{run_id}/events")
async def run_events(run_id: str, request: Request):
    run = manager.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found.")
    try:
        cursor = int(request.headers.get("last-event-id", "-1")) + 1
    except ValueError:
        cursor = 0

    async def stream():
        nonlocal cursor
        while True:
            for event in run.events_since(cursor):
                cursor = event["seq"] + 1
                yield f"id: {event['seq']}\ndata: {json.dumps(event)}\n\n"
            if run.finished and not run.events_since(cursor):
                return
            if await request.is_disconnected():
                return
            await asyncio.sleep(0.25)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.get("/api/personas")
def list_personas():
    return [p.public() for p in load_personas().values()]


@app.get("/api/skills")
def list_skills():
    return skills.list()


@app.get("/api/skills/{name}")
def get_skill(name: str):
    try:
        return {"name": name, "content": skills.load(name)}
    except SkillError as e:
        raise HTTPException(404, str(e))


@app.delete("/api/skills/{name}", status_code=204)
def delete_skill(name: str):
    try:
        if not skills.delete(name):
            raise HTTPException(404, "Skill not found.")
    except SkillError as e:
        raise HTTPException(400, str(e))


@app.get("/architecture")
def architecture():
    page = STATIC.parent.parent / "docs" / "architecture.html"
    if not page.exists():
        raise HTTPException(404, "Architecture page not found.")
    return FileResponse(page)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
