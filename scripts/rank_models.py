"""Rank OpenRouter free models on this agent's real workload.

Each model gets the same two probes, one request each, with no fallback between models:

  1. Tool call: given a chosen skill and a target, does it call fetch_page with a valid URL?
  2. Report: given a real fetched page summary, does it write a report that is grounded in
     that data (title, missing meta description, missing canonical, a number from the page)?

Usage (from the project root):
    .venv/bin/python scripts/rank_models.py                 # test and print a ranking
    .venv/bin/python scripts/rank_models.py --write-env     # also set OPENROUTER_MODELS in .env
    .venv/bin/python scripts/rank_models.py --models a:free,b:free

Results are a snapshot: free models change often and one sample is noisy, so re-run it
when quality drops. The top 6 become two chains of 3 (see app/llm.py build_endpoints).
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from app import config  # noqa: E402
from app.llm import Endpoint, LLMClient, LLMError, discover_free_models  # noqa: E402
from app.prompts import SYSTEM_PROMPT, first_message  # noqa: E402
from app.skills import SkillStore  # noqa: E402
from app.tools import TOOLS, ToolContext, run_tool  # noqa: E402
from app.webfetch import Fetcher  # noqa: E402

TARGET = "https://example.com"
OBJECTIVE = "Give me a quick on-page SEO audit and the fixes with the biggest impact."
SKILL = "seo-onpage-audit"
PROBE_TIMEOUT = 90


def make_client(model: str) -> LLMClient:
    """One model, no OpenRouter fallback chain, one retry, so a result is about that model."""
    config.LLM_MAX_RETRIES = 1
    ep = Endpoint("probe", config.OPENROUTER_BASE_URL, config.OPENROUTER_API_KEY, [model])
    return LLMClient([ep], http=httpx.Client(timeout=httpx.Timeout(PROBE_TIMEOUT)))


def build_fixtures():
    skills = SkillStore(config.SEED_SKILLS_DIR.parent / "skills")
    skills.install_seeds()
    fetcher = Fetcher()
    ctx = ToolContext(skills=skills, fetcher=fetcher)
    page_json, is_error = run_tool(ctx, "fetch_page", {"url": TARGET})
    fetcher.close()
    if is_error:
        raise SystemExit(f"Could not fetch {TARGET} for the fixture: {page_json}")
    page = json.loads(page_json)["page"]
    body = skills.load(SKILL)
    first = first_message(TARGET, OBJECTIVE, skills.catalog_text(), [(SKILL, body)])
    base = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": first}]
    with_result = base + [
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "fetch_page", "arguments": json.dumps({"url": TARGET})}}]},
        {"role": "tool", "tool_call_id": "call_1", "content": page_json},
    ]
    return base, with_result, page


def probe_tool_call(client, messages):
    started = time.monotonic()
    c = client.chat(messages, TOOLS, config.MAX_TOKENS)
    secs = time.monotonic() - started
    calls = c.tool_calls
    ok = bool(calls) and all(not t.parse_error and t.name in {x["name"] for x in TOOLS} for t in calls)
    fetch = next((t for t in calls if t.name == "fetch_page"), None)
    correct = ok and fetch is not None and "example.com" in str(fetch.arguments.get("url", ""))
    return {"pass": correct, "secs": round(secs, 1), "called": [t.name for t in calls], "served": c.model,
            "note": "" if correct else ("no tool call" if not calls else "wrong or malformed call")}


def probe_report(client, messages, page):
    started = time.monotonic()
    c = client.chat(messages, TOOLS, config.MAX_TOKENS)
    secs = time.monotonic() - started
    text = c.text or ""
    low = text.lower()
    facts = {
        "wrote a report, no more tools": bool(text) and not c.tool_calls and len(text) >= 600 and c.finish_reason == "stop",
        "cites the title": (page.get("title") or "").lower() in low,
        "meta description missing": "meta description" in low and bool(re.search(r"missing|absent|not present|no meta|none|null|lacks|without", low)),
        "canonical missing": "canonical" in low and bool(re.search(r"missing|absent|not present|no canonical|none|null|lacks|without", low)),
        "uses a number from the page": any(str(n) in text for n in (page.get("word_count"), page.get("size_bytes")) if n),
    }
    return {"score": sum(facts.values()), "of": len(facts), "secs": round(secs, 1), "facts": facts,
            "chars": len(text), "finish": c.finish_reason, "out_tokens": c.usage["output"],
            "note": "" if facts["wrote a report, no more tools"] else ("kept calling tools" if c.tool_calls else "short or truncated report")}


TRANSIENT = re.compile(r"rate limited|429|503|overloaded|timed out|temporarily", re.I)


def evaluate(model, base, with_result, page, patience=2, wait=25):
    """Run both probes. Transient errors (rate limit, overload) are retried after a pause,
    so a busy upstream is not mistaken for a bad model."""
    client = make_client(model)
    result = {"model": model, "a": None, "b": None, "error": ""}
    try:
        for attempt in range(patience + 1):
            try:
                result["a"] = result["a"] or probe_tool_call(client, base)
                result["b"] = probe_report(client, with_result, page)
                result["error"] = ""
                break
            except LLMError as e:
                result["error"] = re.sub(r"\s+", " ", str(e))[:160]
                if attempt < patience and TRANSIENT.search(result["error"]):
                    time.sleep(wait)
                    continue
                break
    except Exception as e:  # keep one bad model from ending the whole run
        result["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    finally:
        client.close()
    a, b = result["a"], result["b"]
    result["points"] = (1 if a and a["pass"] else 0) + (b["score"] if b else 0)
    result["secs"] = round((a["secs"] if a else 0) + (b["secs"] if b else 0), 1)
    return result


ROUTER = "openrouter/free"  # picks a different free model per request, so quality varies: keep it last


def arrange(results, size=6, chain=3):
    """Best models first (by points, then speed), but no two from the same vendor within one chain
    of 3, so a single vendor outage cannot take a whole chain down. The router goes last."""
    vendor = lambda m: m.split("/")[0]
    pool = [r["model"] for r in results if r["points"] >= 5 and r["model"] != ROUTER]
    picked = []
    while pool and len(picked) < size - (1 if any(r["model"] == ROUTER and r["points"] >= 5 for r in results) else 0):
        current = picked[len(picked) // chain * chain:]
        nxt = next((m for m in pool if vendor(m) not in {vendor(x) for x in current}), pool[0])
        picked.append(nxt); pool.remove(nxt)
    if any(r["model"] == ROUTER and r["points"] >= 5 for r in results):
        picked.append(ROUTER)
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", help="comma-separated model ids (default: every free tool-capable model)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--write-env", action="store_true", help="write the top 6 to OPENROUTER_MODELS in .env")
    ap.add_argument("--use-saved", action="store_true", help="skip testing and reuse scripts/ranking.json")
    args = ap.parse_args()
    if not config.OPENROUTER_API_KEY:
        raise SystemExit("OPENROUTER_API_KEY is not set in .env")

    out = Path(__file__).parent / "ranking.json"
    if args.use_saved:
        results = json.loads(out.read_text())["results"]
        finish(results, args)
        return
    models = [m for m in args.models.split(",")] if args.models else [
        m for m in discover_free_models(base_url=config.OPENROUTER_BASE_URL)
    ]
    if not args.models:  # discovery skips the seed-filtered ones already; add the router as a last-resort candidate
        models = list(dict.fromkeys(models + ["openrouter/free"]))
    print(f"Testing {len(models)} models with {args.workers} workers (2 requests each)...", flush=True)
    base, with_result, page = build_fixtures()
    print(f"Fixture: {TARGET} -> title={page.get('title')!r}, words={page.get('word_count')}, skill={SKILL}\n", flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(lambda m: evaluate(m, base, with_result, page), models):
            results.append(r)
            tag = f"{r['points']}/6" if not r["error"] else "error"
            print(f"  {tag:>6}  {r['secs']:>5}s  {r['model']}  {r['error'] or ''}", flush=True)

    if args.models and out.exists():  # a partial re-test: keep everyone else's earlier result
        old = {r["model"]: r for r in json.loads(out.read_text())["results"]}
        old.update({r["model"]: r for r in results})
        results = list(old.values())
    results.sort(key=lambda r: (-r["points"], r["secs"]))
    out.write_text(json.dumps({"tested_at": time.strftime("%Y-%m-%d %H:%M:%S"), "results": results}, indent=1))

    finish(results, args)


def finish(results, args):
    print("\nRanking (points out of 6, total seconds for both requests):")
    for i, r in enumerate(results, 1):
        a, b = r["a"], r["b"]
        detail = "error: " + r["error"] if r["error"] else (
            f"tool call {'ok' if a['pass'] else 'FAIL (' + a['note'] + ')'}; report {b['score']}/{b['of']}" + (f" ({b['note']})" if b["note"] else ""))
        print(f"{i:>2}. {r['points']}/6  {r['secs']:>5}s  {r['model']:<52} {detail}")

    good = arrange(results)
    print("\nRecommended OPENROUTER_MODELS (chain 1 = first 3, chain 2 = next 3, router last as a safety net):")
    print("  " + (",".join(good) or "(none reached 5 points)"))
    if args.write_env and good:
        env = config.ROOT / ".env"
        text = env.read_text(encoding="utf-8")
        line = "OPENROUTER_MODELS=" + ",".join(good)
        text = re.sub(r"^OPENROUTER_MODELS=.*$", lambda _: line, text, flags=re.M) if re.search(r"^OPENROUTER_MODELS=", text, re.M) else text + "\n" + line + "\n"
        env.write_text(text, encoding="utf-8")
        print("  wrote OPENROUTER_MODELS to .env (restart the server to use it)")


if __name__ == "__main__":
    main()
