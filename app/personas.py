"""Personas: a role's lens and its recommended skills.

A persona is a JSON file in personas/. It changes how the agent frames its findings (the lens),
narrows the skill catalog the agent sees, and supplies example objectives for the UI. To add
one, drop a file in personas/ with the same fields as the existing ones.
"""
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import config

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PersonaError(ValueError):
    pass


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    tagline: str
    lens: str
    skills: tuple
    examples: tuple
    order: int = 99

    def public(self) -> dict:
        d = asdict(self)
        d.pop("lens")  # the lens is guidance for the model, not for the page
        d["skills"], d["examples"] = list(self.skills), list(self.examples)
        return d


def _parse(path: Path) -> Persona:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        pid = d["id"]
        if not ID_RE.match(pid) or pid != path.stem:
            raise PersonaError(f"id must be a slug that matches the file name ({path.name})")
        for key in ("name", "tagline", "lens"):
            if not isinstance(d[key], str) or not d[key].strip():
                raise PersonaError(f"'{key}' must be a non-empty string ({path.name})")
        skills = tuple(d["skills"])
        if not skills or not all(isinstance(s, str) for s in skills):
            raise PersonaError(f"'skills' must be a non-empty list of names ({path.name})")
        examples = tuple({k: e[k] for k in ("label", "url", "objective", "skills")} for e in d.get("examples", []))
        return Persona(pid, d["name"].strip(), d["tagline"].strip(), d["lens"].strip(), skills, examples, int(d.get("order", 99)))
    except (KeyError, TypeError, ValueError) as e:
        if isinstance(e, PersonaError):
            raise
        raise PersonaError(f"Invalid persona file {path.name}: {e!r}") from e


def load_personas(directory: Path | None = None) -> dict:
    """All personas, keyed by id, in display order."""
    directory = Path(directory or config.PERSONAS_DIR)
    found = [_parse(p) for p in sorted(directory.glob("*.json"))] if directory.exists() else []
    return {p.id: p for p in sorted(found, key=lambda p: (p.order, p.name))}


def get_persona(pid: str, directory: Path | None = None) -> Persona:
    personas = load_personas(directory)
    if pid not in personas:
        raise PersonaError(f"Unknown perspective '{pid}'.")
    return personas[pid]
