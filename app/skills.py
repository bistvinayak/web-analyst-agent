"""Persistent skill library: one folder per skill, each with a SKILL.md.

A skill is a reusable, site-independent playbook the agent wrote for a kind of
objective (for example "seo-onpage-audit"). The file format is:

    ---
    name: seo-onpage-audit
    description: One line saying when to use this skill.
    version: 2
    updated: 2026-09-20T10:15:00+00:00
    ---
    # Markdown body
"""
import os
import re
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class SkillError(ValueError):
    pass


def _parse(text: str) -> tuple[dict, str]:
    """Split a SKILL.md into (frontmatter dict, body)."""
    meta: dict = {}
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                key, _, value = line.partition(":")
                if key.strip():
                    meta[key.strip()] = value.strip()
            return meta, text[end + 5 :]
    return meta, text


class SkillStore:
    def __init__(self, root: Path | None = None):
        self.root = Path(root or config.SKILLS_DIR)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, name: str) -> Path:
        if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 48:
            raise SkillError(
                "Skill name must be lowercase words joined by single hyphens "
                "(a-z, 0-9), at most 48 characters, e.g. 'seo-onpage-audit'."
            )
        return self.root / name / "SKILL.md"

    def _seed_category(self, name: str) -> str:
        seed = Path(config.SEED_SKILLS_DIR) / name / "SKILL.md"
        return _parse(seed.read_text(encoding="utf-8"))[0].get("category", "") if seed.exists() else ""

    def list(self) -> list[dict]:
        out = []
        for path in sorted(self.root.glob("*/SKILL.md")):
            meta, _ = _parse(path.read_text(encoding="utf-8"))
            out.append(
                {
                    "name": path.parent.name,
                    "description": meta.get("description", ""),
                    "category": meta.get("category") or self._seed_category(path.parent.name) or "Custom",
                    "version": int(meta.get("version", "1") or 1),
                    "updated": meta.get("updated", ""),
                }
            )
        return out

    def load(self, name: str) -> str:
        path = self._path(name)
        if not path.exists():
            raise SkillError(f"No skill named '{name}'.")
        return path.read_text(encoding="utf-8")

    def save(self, name: str, description: str, content: str, overwrite: bool = False) -> dict:
        path = self._path(name)
        description = " ".join((description or "").split())
        content = (content or "").strip()
        if not description:
            raise SkillError("description is required (one line: when to use this skill).")
        if len(description) > config.MAX_SKILL_DESCRIPTION_CHARS:
            raise SkillError(f"description must be at most {config.MAX_SKILL_DESCRIPTION_CHARS} characters.")
        if not content:
            raise SkillError("content is required.")
        if len(content) > config.MAX_SKILL_CHARS:
            raise SkillError(f"content must be at most {config.MAX_SKILL_CHARS} characters.")

        with self._lock:
            version, category = 1, ""
            if path.exists():
                if not overwrite:
                    raise SkillError(
                        f"Skill '{name}' already exists. Load it, improve it, and call save_skill "
                        "again with overwrite=true, or pick a different name."
                    )
                meta, _ = _parse(path.read_text(encoding="utf-8"))
                category = meta.get("category") or self._seed_category(name)
                version = int(meta.get("version", "1") or 1) + 1
                history = path.parent / ".history"
                history.mkdir(exist_ok=True)
                (history / f"v{version - 1}.md").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

            updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
            category_line = f"category: {category}\n" if category else ""
            text = (
                f"---\nname: {name}\ndescription: {description}\n{category_line}"
                f"version: {version}\nupdated: {updated}\n---\n{content}\n"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
        return {"name": name, "version": version}

    def delete(self, name: str) -> bool:
        path = self._path(name)
        if not path.exists():
            return False
        with self._lock:
            for child in sorted(path.parent.rglob("*"), reverse=True):
                child.unlink() if child.is_file() else child.rmdir()
            path.parent.rmdir()
        return True

    def install_seeds(self, seed_dir: Path | None = None) -> "list[str]":
        """Copy shipped starter skills whose folder is missing from the library.

        Never overwrites, so a skill the agent has improved keeps its version. A seed you
        delete comes back on the next start, because its folder is gone."""
        seed_dir = Path(seed_dir or config.SEED_SKILLS_DIR)
        installed = []
        if not seed_dir.exists():
            return installed
        with self._lock:
            for src in sorted(seed_dir.glob("*/SKILL.md")):
                dest = self.root / src.parent.name / "SKILL.md"
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dest)
                    installed.append(src.parent.name)
        return installed

    def catalog_text(self) -> str:
        skills = self.list()
        if not skills:
            return "(the skill library is empty)"
        return "\n".join(f"- {s['name']}: {s['description']}" for s in skills)
