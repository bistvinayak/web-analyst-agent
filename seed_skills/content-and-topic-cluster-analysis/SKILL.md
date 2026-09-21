---
name: content-and-topic-cluster-analysis
description: Analyze a site's content structure from its sitemap and blog: topic clusters, pillar pages, coverage gaps, freshness and thin sections. Use for "content audit", "topic clusters", "what content is missing", "content strategy".
category: Search and visibility
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Content and topic cluster analysis

## Steps
1. `fetch_raw` `/sitemap.xml`. If it is an index, fetch one or two child sitemaps (blog, pages).
2. Group URLs by first path segment and count each group (for example /blog, /guides, /docs, /features, /customers).
3. For blog or resource URLs, group by slug themes and any category or tag paths.
4. `fetch_page` the blog or resource index and 2 or 3 posts. Use `query_page` with `time` (attribute `datetime`) and `h1` to read dates and titles.

## Analyze
- **Volume and balance:** how the content splits across sections. A large blog with a thin product section may be misaligned with the business.
- **Clusters:** topics with a pillar page plus supporting posts that interlink. Name each cluster and list its pages.
- **Orphans and singletons:** posts with no related content.
- **Freshness:** share of pages with a recent `lastmod` or date, and the age of the newest post. Stale core pages = Medium.
- **Depth:** `word_count` of sampled pages. Very short pages on competitive topics = Medium.
- **Gaps:** questions a buyer would ask at each stage (learn, compare, decide, adopt) that no page answers.
- **Duplication:** near-identical titles or repeated templates suggesting thin or duplicate content.

## Report
1. A content inventory table by section with counts and freshness.
2. The clusters found, each with its pillar and gaps.
3. 5 content opportunities, each with a working title, the intent it serves (see keyword-and-intent-mapping) and why it matters.
4. Housekeeping: pages to merge, update or remove.

## Pitfalls
- A sitemap shows what the site lists, not what performs. Do not claim traffic.
- Dates on pages can be publication dates or update dates. Say which you saw.
- Small samples of `word_count` are indicators, not verdicts.
