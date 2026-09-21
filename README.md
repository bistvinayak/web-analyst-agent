# Web Analyst Agent

Give it a website or link and an objective. It checks its skill library for a matching playbook, writes a new skill if none fits, gathers evidence from the site, and returns a report with cited findings. Skills persist in `skills/`, so later runs start from what earlier runs learned.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # then put your keys in .env (it is gitignored)
.venv/bin/uvicorn app.server:app --port 8000
# open http://localhost:8000  (port busy? use --port 8010)
```

Tests (no API key needed, the model is faked): `.venv/bin/python -m pytest`

## Using the web page

- Paste a link and an objective, then click Analyze. The example chips fill both in for you.
- **Skills:** leave it on "Let the agent choose", or switch to "Choose skills" and pick up to 5 from the categorized list (filter, preview, delete). Chosen skills go to the agent in full, which also saves model requests. Untick the box below to stop the agent from writing or changing skills during the run.
- The run view shows the stage, each tool call with a readable result, elapsed time, models used, and token counts. Reports can be copied or downloaded as Markdown.
- `/architecture` shows how the whole thing works, with diagrams. `?run=<id>` in the URL reopens a saved run.

## Starter skills

19 skills ship in `seed_skills/` and are copied into `skills/` on startup if missing (never overwritten, so the agent's improvements to a skill are kept):

- **Orientation:** `site-overview`, `company-research-brief`, `competitor-comparison`
- **Search:** `seo-onpage-audit`, `technical-seo-crawlability`, `structured-data-audit`, `social-sharing-metadata`, `ai-search-readiness`, `link-health-check`
- **Conversion and content:** `conversion-cro-audit`, `content-and-messaging-review`, `pricing-page-teardown`, `navigation-and-ux-review`, `trust-and-credibility-review`
- **Technical and compliance:** `security-headers-review`, `privacy-and-tracking-review`, `accessibility-quick-audit`, `performance-signals-audit`, `tech-stack-detection`

Each one names the tools to call, the checks with severity, the report shape, and what it cannot see. When an objective fits none of them, the agent writes a new skill and saves it. Tests validate every seed (format, size, cross-references).

## Model providers

Set these in `.env`:

- **Primary, OpenRouter:** `OPENROUTER_API_KEY`. Leave `OPENROUTER_MODELS` empty and the app asks OpenRouter which models are free and support tool calling, trying the ones Vidur found reliable first. Or list your own, best first. OpenRouter accepts at most 3 fallback models per request, so only the first 3 are sent.
- **Fallback, any OpenAI-compatible API:** `FALLBACK_BASE_URL`, `FALLBACK_API_KEY`, `FALLBACK_MODEL`, and an optional `FALLBACK_NAME`. Groq, Gemini's OpenAI-compatible endpoint, Together, a second OpenRouter account, or a local server all work.

Failover order: OpenRouter's own model chain, then retries with backoff on 429, 5xx and timeouts, then the fallback API. A daily-quota 429 skips the retries and fails over at once. The chat history is plain OpenAI format, so a run can switch providers mid-way. The UI shows which model served each stretch.

Free-tier caveat: OpenRouter limits free models per minute and per day (the daily cap is low unless your account has purchased credits). A run makes up to `MAX_TURNS` requests (15 by default), so a handful of runs can use up a day's quota. That is what the fallback is for.

## How it works

- `app/llm.py`: provider-neutral chat client with retries, failover, live free-model discovery, and cleanup of leaked `<think>` text.
- `app/agent.py`: the loop. Five tools, a turn cap, a forced wrap-up on the last turn, and guards for weaker models: it refuses to write a report before fetching anything, blocks repeated identical calls, sends malformed tool arguments back as errors, and trims old tool results when the context grows.
- `app/tools.py`: `load_skill`, `save_skill`, `fetch_page`, `fetch_raw`, `query_page`.
- `app/skills.py`: one folder per skill with a `SKILL.md` (frontmatter plus a Markdown playbook). Overwrites bump a version and archive the old one in `.history/`.
- `app/webfetch.py`: safe fetching and HTML summarizing.
- `app/runs.py`, `app/server.py`: background runs, a replayable event log, and a FastAPI server that streams progress over SSE. `app/static/index.html` is the UI.

Skills are Markdown playbooks, not code. The agent does not execute anything it writes, so there is no sandbox to run.

## Safety choices

- The fetcher only allows http(s), refuses private, loopback and link-local addresses, re-checks every redirect, caps response size, redirects and fetches per run, and honors robots.txt.
- Page content is treated as untrusted. Tool results carry a note saying so, and the system prompt tells the agent to report injection attempts instead of following them.
- Skills can only be written under `skills/`, with slug-validated names and size limits. Review skills in the UI now and then, and delete any you don't trust, because a saved skill shapes every later run.
- The server accepts only localhost Host headers. It has no login. If you deploy it anywhere shared, add authentication and rate limiting first, since every run spends API credits and makes outbound requests.

## Known limits

- Free models vary a lot in how well they follow tool-calling instructions, and OpenRouter's metadata about which models support tools is not always right. If reports come back thin or a run stops with "would not use its tools", set `OPENROUTER_MODELS` to a model that works for you.
- It reads server-delivered HTML and headers. It does not run JavaScript, so client-rendered content, real performance timing, and logged-in areas are out of reach. A headless browser tool (Playwright) is the natural next step.
- DNS is checked once for validation and again on connect, so DNS rebinding is not fully closed. Run it somewhere with no route to internal systems if that matters.
- Runs are held in memory while active and written to `runs/` when they finish.

## Settings

Environment variables: `MAX_TURNS` (15), `MAX_TOKENS` (4096), `CONTEXT_CHAR_BUDGET` (100000), `LLM_TIMEOUT`, `LLM_MAX_RETRIES`, `MAX_FETCHES_PER_RUN` (25), `MAX_CONCURRENT_RUNS` (2), `RESPECT_ROBOTS` (1), `SKILLS_DIR`, `RUNS_DIR`. See `app/config.py`.
