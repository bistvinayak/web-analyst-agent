---
name: seo-onpage-audit
description: Audit on-page SEO of one or a few pages: title, meta description, headings, canonical, links, images, content depth. Use for "SEO audit", "why is this page not ranking", "improve this page's SEO".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# On-page SEO audit

## When to use
The objective concerns search visibility of specific pages. For site-wide crawl and indexing problems use technical-seo-crawlability as well.

## Steps
1. `fetch_page` on the target. Fetch up to 3 more important pages (from `links.internal_sample`) for comparison.
2. Check each item below using the fields returned. Use `query_page` for details the summary lacks, for example selector `h2` or `a[rel]`.

## Checks
- Title: present, unique, roughly 30 to 60 characters, leads with the main topic. Missing or duplicated = High.
- Meta description: present, roughly 70 to 160 characters, states a benefit. Missing = Medium.
- Exactly one H1 that matches the page topic; H2/H3 outline is logical. Zero or multiple H1 = Medium.
- Canonical: present and points to the intended URL. Missing or pointing elsewhere = High if unintended.
- `meta_robots`: no accidental `noindex`. Accidental noindex = High.
- `lang` set; `viewport` set (mobile-first indexing).
- Images: `missing_alt` count; large share missing = Medium.
- Internal links: descriptive anchor text, no dead-end page. Generic anchors ("click here") = Low.
- Content depth: `word_count`. Under about 300 words on a page meant to rank = Medium. Say this is a heuristic.
- Open Graph and Twitter tags present (see social-sharing-metadata).

## Report
Table of checks with status and evidence (value observed), then the top fixes ordered by impact, each with the exact suggested change (for example a rewritten title).

## Pitfalls
- You cannot see rankings, backlinks, keyword volume or Core Web Vitals. Do not claim them.
- Content injected by JavaScript is invisible to these tools. Flag thin text as "possibly client-rendered".
