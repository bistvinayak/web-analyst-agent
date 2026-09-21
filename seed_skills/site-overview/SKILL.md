---
name: site-overview
description: First-pass understanding of any website: what it is, who it is for, how it is organized, and what to investigate next. Use for open-ended objectives like "analyze this site" or before a deeper audit.
category: Orientation
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Site overview

## When to use
The objective is broad ("analyze this site", "what is this company"), or you need context before a specialised audit.

## Steps
1. `fetch_page` on the given URL. Note the final URL after redirects, status, and the redirect chain.
2. Read title, meta description, H1/H2 headings and the text excerpt. State in one sentence what the site is and who it is for.
3. From `links.internal_sample`, identify the main sections (product, pricing, docs, blog, about, contact, login).
4. `fetch_raw` on `/robots.txt` and `/sitemap.xml` to see how big and how structured the site is (count URLs, note sections).
5. Fetch at most 2 more pages that best explain the offer (for example pricing or about).

## What to report
- What the site is, audience, and main call to action.
- Site structure: sections found, rough size from the sitemap.
- Technology and hosting hints (`server`, `x-powered-by`, script hosts).
- 3 to 5 areas worth a deeper audit, each naming the skill that fits (for example seo-onpage-audit, security-headers-review).

## Pitfalls
- A near-empty text excerpt usually means the page renders client-side. Say so instead of guessing what the site contains.
- Do not infer company size, traffic or revenue from the site alone.
