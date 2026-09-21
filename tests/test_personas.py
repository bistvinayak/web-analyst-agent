import json

import pytest

from app import config
from app.agent import run_agent
from app.personas import PersonaError, get_persona, load_personas
from app.prompts import first_message
from app.skills import SkillStore
from tests.test_agent import FakeLLM, comp, call

SEED_NAMES = {p.parent.name for p in config.SEED_SKILLS_DIR.glob("*/SKILL.md")}


def test_shipped_personas_are_valid_and_reference_real_skills():
    personas = load_personas()
    assert list(personas) == ["product-manager", "seo-analyst", "front-end-engineer", "back-end-engineer", "ai-engineer"]
    for p in personas.values():
        assert set(p.skills) <= SEED_NAMES, (p.id, set(p.skills) - SEED_NAMES)
        assert len(p.lens) > 200 and p.examples
        for e in p.examples:
            assert set(e["skills"]) <= set(p.skills), (p.id, e["label"])       # examples use the persona's own skills
            assert e["url"].startswith("https://") and len(e["objective"]) > 10


def test_every_seed_skill_belongs_to_a_persona_or_is_shared():
    used = {s for p in load_personas().values() for s in p.skills}
    unassigned = SEED_NAMES - used
    assert not unassigned, f"skills that no persona lists: {sorted(unassigned)}"


def test_new_persona_skills_are_specific_to_them():
    p = load_personas()
    assert "keyword-and-intent-mapping" in p["seo-analyst"].skills and "keyword-and-intent-mapping" not in p["back-end-engineer"].skills
    assert "api-surface-discovery" in p["back-end-engineer"].skills and "api-surface-discovery" not in p["seo-analyst"].skills


def test_bad_persona_files_are_rejected(tmp_path):
    good = {"id": "x-y", "name": "X", "tagline": "t", "lens": "l", "skills": ["a"], "examples": []}
    (tmp_path / "x-y.json").write_text(json.dumps(good))
    assert "x-y" in load_personas(tmp_path)
    for name, bad in [("wrong-name", {**good, "id": "other"}), ("no-lens", {**good, "id": "no-lens", "lens": " "}),
                      ("no-skills", {**good, "id": "no-skills", "skills": []}), ("Bad_ID", {**good, "id": "Bad_ID"})]:
        (tmp_path / f"{name}.json").write_text(json.dumps(bad))
        with pytest.raises(PersonaError):
            load_personas(tmp_path)
        (tmp_path / f"{name}.json").unlink()


def test_unknown_persona():
    with pytest.raises(PersonaError, match="Unknown perspective"):
        get_persona("wizard")


def test_first_message_carries_the_lens():
    p = get_persona("front-end-engineer")
    text = first_message("https://x.test", "review", "- a: b", persona=p)
    assert text.startswith("Target URL") and "Perspective: Front End Engineer" in text and p.lens in text
    assert "Skill catalog (for the Front End Engineer perspective)" in text
    assert "Perspective:" not in first_message("https://x.test", "review", "- a: b")


def test_catalog_is_narrowed_to_the_persona_plus_custom_skills(tmp_path):
    store = SkillStore(tmp_path)
    store.install_seeds()
    store.save("my-own-thing", "Written by the agent.", "body")
    names = {line[2:].split(":")[0] for line in store.catalog_text(only=set(get_persona("seo-analyst").skills)).splitlines()}
    assert names == set(get_persona("seo-analyst").skills) | {"my-own-thing"}
    assert "api-surface-discovery" not in names
    full = store.catalog_text()
    assert len(store.catalog_text(only=set(get_persona("back-end-engineer").skills))) < len(full)


def test_agent_sends_the_persona_lens_and_narrow_catalog(site, local_ok, tmp_path):
    store = SkillStore(tmp_path)
    store.install_seeds()
    persona = get_persona("back-end-engineer")
    llm = FakeLLM([comp(calls=[call("t1", "fetch_page", url=site + "/")]), comp(text="# Report\nok")])
    events = []
    run_agent(site + "/", "review headers", lambda t, **d: events.append((t, d)), store, llm, persona=persona)
    first = llm.calls[0]["messages"][1]["content"]
    assert persona.lens in first and "keyword-and-intent-mapping" not in first and "api-surface-discovery" in first
    assert ("persona", {"id": "back-end-engineer", "name": "Back End Engineer"}) in events
