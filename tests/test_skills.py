import re
import pytest

from app.skills import SkillError, SkillStore


@pytest.fixture
def store(tmp_path):
    return SkillStore(tmp_path)


def test_save_load_list(store):
    assert store.save("seo-audit", "Audit SEO.", "# Steps\n1. fetch") == {"name": "seo-audit", "version": 1}
    assert "# Steps" in store.load("seo-audit")
    assert store.list()[0]["description"] == "Audit SEO." and store.list()[0]["version"] == 1
    assert "seo-audit: Audit SEO." in store.catalog_text()


def test_overwrite_requires_flag_and_keeps_history(store, tmp_path):
    store.save("a-b", "d", "one")
    with pytest.raises(SkillError, match="already exists"):
        store.save("a-b", "d", "two")
    assert store.save("a-b", "d", "two", overwrite=True)["version"] == 2
    assert (tmp_path / "a-b" / ".history" / "v1.md").exists()


@pytest.mark.parametrize("name", ["../evil", "Bad Name", "a/b", "", "-x", "x-", "a--b", "x" * 49, None])
def test_rejects_bad_names(store, name):
    with pytest.raises(SkillError):
        store.save(name, "d", "c")


def test_rejects_bad_content(store):
    with pytest.raises(SkillError):
        store.save("ok", "", "c")
    with pytest.raises(SkillError):
        store.save("ok", "d", " ")
    with pytest.raises(SkillError):
        store.save("ok", "d", "x" * 30_000)


def test_multiline_description_is_flattened(store):
    store.save("ok", "line one\nline two", "c")
    assert store.list()[0]["description"] == "line one line two"


def test_delete(store):
    store.save("ok", "d", "c")
    assert store.delete("ok") and not store.delete("ok") and store.list() == []


# ---- shipped starter skills ----
from app import config
from app.skills import NAME_RE, _parse

SEEDS = sorted(config.SEED_SKILLS_DIR.glob("*/SKILL.md"))
TOOL_NAMES = ("fetch_page", "fetch_raw", "query_page")


def test_seed_skills_exist():
    assert len(SEEDS) >= 15


@pytest.mark.parametrize("path", SEEDS, ids=lambda p: p.parent.name)
def test_each_seed_is_valid(path):
    meta, body = _parse(path.read_text(encoding="utf-8"))
    assert meta["name"] == path.parent.name and NAME_RE.match(meta["name"]) and len(meta["name"]) <= 48
    assert 20 < len(meta["description"]) <= config.MAX_SKILL_DESCRIPTION_CHARS
    assert int(meta["version"]) == 1
    assert len(body) <= config.MAX_SKILL_CHARS
    assert any(t in body for t in TOOL_NAMES), "a skill must tell the agent which tools to call"
    for heading in ("## Report", "## Pitfalls"):
        assert heading in body or heading == "## Report" and "## What to report" in body, f"missing {heading}"


def test_seed_cross_references_point_at_real_skills():
    names = {p.parent.name for p in SEEDS}
    for p in SEEDS:
        body = p.read_text(encoding="utf-8")
        for ref in re.findall(r"\b([a-z0-9]+(?:-[a-z0-9]+)+)\b", body):
            if ref.endswith(("-audit", "-review", "-teardown", "-detection", "-comparison", "-check", "-readiness", "-crawlability", "-metadata", "-overview", "-brief", "-signals")):
                assert ref in names, f"{p.parent.name} references unknown skill {ref}"


def test_catalog_stays_small(tmp_path):
    store = SkillStore(tmp_path)
    store.install_seeds()
    assert len(store.catalog_text()) < 6000


def test_install_seeds_never_overwrites(tmp_path):
    store = SkillStore(tmp_path)
    first = store.install_seeds()
    assert len(first) == len(SEEDS) and store.list()
    store.save("seo-onpage-audit", "Mine.", "custom body", overwrite=True)
    assert store.install_seeds() == []
    assert "custom body" in store.load("seo-onpage-audit")


def test_category_survives_overwrite_and_defaults_to_custom(tmp_path):
    store = SkillStore(tmp_path)
    store.install_seeds()
    store.save("seo-onpage-audit", "Mine.", "new body", overwrite=True)
    cats = {s["name"]: s["category"] for s in store.list()}
    assert cats["seo-onpage-audit"] == "Search and visibility"
    store.save("brand-new", "d", "c")
    assert {s["name"]: s["category"] for s in store.list()}["brand-new"] == "Custom"


def test_every_seed_has_a_category():
    for p in SEEDS:
        assert _parse(p.read_text(encoding="utf-8"))[0].get("category"), p.parent.name
