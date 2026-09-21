---
name: ai-search-readiness
description: Check how ready a site is to be found and cited by AI assistants and AI search: AI crawler rules, llms.txt, structured data, answer-ready content, freshness. Use for "GEO", "AI visibility", "will ChatGPT/Perplexity cite us".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# AI search readiness

## Steps
1. `fetch_raw` `/robots.txt`. Look for rules naming AI crawlers: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, CCBot, Bytespider. Note allowed or blocked, and whether the block is on purpose for training versus search.
2. `fetch_raw` `/llms.txt` (and `/llms-full.txt`). Presence is a plus, not a requirement; note quality if present.
3. `fetch_page` the target and 2 key content pages. Check structured data (see structured-data-audit), headings, and whether the text is server-rendered (`word_count`).
4. `fetch_raw` `/sitemap.xml` and check that `lastmod` dates exist and look current.

## Checks
- Important content is in the initial HTML, not only rendered by JavaScript (AI crawlers rarely run scripts). Very low `word_count` on content pages = High.
- Not blocking search-oriented AI crawlers by accident (blanket `Disallow: /` or a WAF challenge). Report a block as a business decision to confirm, not always a defect.
- Clear entity information: who the organization is, what it offers, `Organization` schema with `sameAs`.
- Answer-ready content: direct definitions, question headings, FAQs, tables, and specific facts with dates and sources.
- Freshness: visible dates, recent `lastmod`.
- Consistent naming of the brand and products across pages.
- Authorship and citations on articles.

## Report
Checklist with evidence, then a prioritized plan. Add a note that citation behavior of AI systems cannot be measured with these tools.

## Pitfalls
- No one can guarantee AI citations. Avoid promises and invented ranking factors.
- Say clearly which crawler names you searched for.
