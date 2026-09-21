import json

import pytest
from fastapi.testclient import TestClient

from app import server
from app.runs import RunManager
from app.skills import SkillStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    skills = SkillStore(tmp_path / "skills")
    monkeypatch.setattr(server, "skills", skills)
    monkeypatch.setattr(server, "manager", RunManager(skills, tmp_path / "runs"))
    return TestClient(server.app)


def test_validation(client):
    assert client.post("/api/runs", json={"url": "ftp://x.com", "objective": "look"}).status_code == 422
    assert client.post("/api/runs", json={"url": "x.com", "objective": ""}).status_code == 422


def test_host_header_is_restricted(client):
    assert client.get("/api/skills", headers={"host": "evil.example"}).status_code == 400


def test_run_lifecycle_and_sse(client, monkeypatch):
    seen = {}
    def fake_run(url, objective, emit, skills, selected_skills=None, allow_skill_writes=True):
        emit("text", text="hello")
        seen.update(selected=selected_skills, writes=allow_skill_writes)
        return "# Report", {"turns": 1}
    monkeypatch.setattr("app.runs.run_agent", fake_run)

    server.skills.save("my-skill", "d", "body")
    body = {"url": "example.com", "objective": "look around", "skills": ["my-skill", "my-skill"], "allow_skill_writes": False}
    run_id = client.post("/api/runs", json=body).json()["id"]
    with client.stream("GET", f"/api/runs/{run_id}/events") as r:
        events = [json.loads(line[6:]) for line in r.iter_lines() if line.startswith("data: ")]
    assert [e["type"] for e in events] == ["status", "text", "report", "done"]
    assert client.get(f"/api/runs/{run_id}").json()["report"] == "# Report"
    assert seen == {"selected": ["my-skill"], "writes": False}                 # duplicates removed
    assert client.get(f"/api/runs/{run_id}").json()["skills"] == ["my-skill"]
    assert client.get("/api/runs").json()[0]["id"] == run_id
    assert client.get("/api/runs/missing").status_code == 404


def test_skills_api(client):
    server.skills.save("my-skill", "d", "body")
    assert client.get("/api/skills").json()[0]["name"] == "my-skill"
    assert "body" in client.get("/api/skills/my-skill").json()["content"]
    assert client.delete("/api/skills/my-skill").status_code == 204
    assert client.get("/api/skills/my-skill").status_code == 404
    assert client.get("/api/skills/..%2Fetc").status_code in (400, 404)


def test_index_served(client):
    assert "Web Analyst" in client.get("/").text


def test_unknown_or_too_many_skills_rejected(client):
    r = client.post("/api/runs", json={"url": "example.com", "objective": "look", "skills": ["nope"]})
    assert r.status_code == 422 and "Unknown skill" in r.json()["detail"]
    too_many = {"url": "example.com", "objective": "look", "skills": [f"s{i}" for i in range(6)]}
    assert client.post("/api/runs", json=too_many).status_code == 422


def test_skills_list_has_categories(client):
    server.skills.install_seeds()
    server.skills.save("my-own", "d", "body")
    cats = {s["name"]: s["category"] for s in client.get("/api/skills").json()}
    assert cats["seo-onpage-audit"] == "Search and visibility" and cats["my-own"] == "Custom"


def test_architecture_page_served(client):
    r = client.get("/architecture")
    assert r.status_code == 200 and "Web Analyst Agent" in r.text
