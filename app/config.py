import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env reader. Real environment variables win over the file."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("'\"")
        if value:
            os.environ.setdefault(key.strip(), value)


_load_dotenv(ROOT / ".env")


def _flag(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").lower() not in ("0", "false", "no", "")


# --- LLM providers -------------------------------------------------------
# Primary: OpenRouter. Leave OPENROUTER_MODELS empty to auto-pick free, tool-capable models.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODELS = [m.strip() for m in os.getenv("OPENROUTER_MODELS", "").split(",") if m.strip()]

# Fallback: any OpenAI-compatible chat completions API (Groq, Gemini, Together, a second
# OpenRouter account, a local server...). Used when the primary fails or is rate limited.
FALLBACK_NAME = os.getenv("FALLBACK_NAME", "fallback")
FALLBACK_BASE_URL = os.getenv("FALLBACK_BASE_URL", "")
FALLBACK_API_KEY = os.getenv("FALLBACK_API_KEY", "")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "")

LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "90"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))  # per endpoint, for 429/5xx/network errors

SKILLS_DIR = Path(os.getenv("SKILLS_DIR", ROOT / "skills"))
SEED_SKILLS_DIR = ROOT / "seed_skills"  # shipped starter skills, copied into SKILLS_DIR if missing
RUNS_DIR = Path(os.getenv("RUNS_DIR", ROOT / "runs"))

# Agent limits. Free tiers cap requests per day, so the defaults are conservative.
MAX_TURNS = int(os.getenv("MAX_TURNS", "15"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
MAX_CONCURRENT_RUNS = int(os.getenv("MAX_CONCURRENT_RUNS", "2"))
# Old tool results are trimmed once the conversation passes this size, for small-context models.
CONTEXT_CHAR_BUDGET = int(os.getenv("CONTEXT_CHAR_BUDGET", "100000"))
MAX_REPORT_CHARS = 30_000

# Web access limits.
MAX_FETCHES_PER_RUN = int(os.getenv("MAX_FETCHES_PER_RUN", "25"))
FETCH_TIMEOUT = float(os.getenv("FETCH_TIMEOUT", "15"))
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", str(2_000_000)))
MAX_REDIRECTS = 5
MAX_TOOL_RESULT_CHARS = 12_000
USER_AGENT = os.getenv("USER_AGENT", "WebAnalystAgent/0.1 (automated site analysis)")
RESPECT_ROBOTS = _flag("RESPECT_ROBOTS", True)

# Only for tests against a local server. Never enable this on a shared deployment.
ALLOW_PRIVATE_HOSTS = _flag("ALLOW_PRIVATE_HOSTS", False)

# Skill limits.
MAX_SKILL_CHARS = 20_000
MAX_SKILL_DESCRIPTION_CHARS = 300
