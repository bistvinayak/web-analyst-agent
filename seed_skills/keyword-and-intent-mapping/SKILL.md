---
name: keyword-and-intent-mapping
description: Infer the topic and search intent each page targets from its title, headings, copy and URL, then find gaps and pages competing for the same query. Use for "what is this page targeting", "keyword cannibalization", "map intent".
category: Search and visibility
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Keyword and intent mapping

Works from page evidence only. There is no search volume, ranking or click data here.

## Steps
1. `fetch_raw` `/sitemap.xml` to list URLs. Pick the 8 to 12 most important ones (home, main product or service pages, top blog posts).
2. `fetch_page` each chosen URL (stay inside the fetch budget). Record title, meta description, H1, H2s and the first 200 words.
3. Use `query_page` with `h2, h3` if the summary heading list is short.

## For each page
- **Primary topic:** the phrase the title, H1 and URL slug agree on. If they disagree, note it.
- **Secondary topics:** recurring terms in H2s and body copy.
- **Search intent:** informational (learn), navigational (find a site), commercial (compare options) or transactional (act or buy). Justify from the page: calls to action, comparison tables, how-to structure.
- **Fit:** does the page format match the intent (a buying page for a how-to query is a mismatch)?

## Across pages
- **Cannibalization risk:** two or more pages with the same primary topic and intent. List them.
- **Coverage gaps:** intents a visitor at each funnel stage would have that no page addresses (for example comparison, pricing, alternatives, how-to, troubleshooting).
- **Mismatches:** titles promising one thing while the H1 and content deliver another.

## Report
1. Table: URL, primary topic, intent, fit (good, weak, mismatch), evidence.
2. Cannibalization groups with a recommended action each (merge, redirect, differentiate, canonicalize).
3. The 5 highest-impact gaps or fixes, ordered by likely organic impact and effort, with an exact new title or H1 where useful.
4. What you cannot know: volume, difficulty, actual rankings. Suggest confirming with Search Console and a keyword tool.

## Pitfalls
- A phrase appearing often does not make it the target. Weight title, H1 and URL above body copy.
- Do not invent keyword volumes or rank positions.
