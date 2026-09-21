---
name: market-landscape-scan
description: Map a product category from a seed site using its comparison pages, alternatives pages, integrations and category language: who the players are, how they segment, and where whitespace may exist. Use for "who are the competitors", "map this market".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Market landscape scan

## Steps
1. `fetch_page` the seed site's homepage. Note how it names its own category.
2. Look for pages that name others: `query_page` with `a[href*="vs"], a[href*="alternative"], a[href*="compare"], a[href*="competitor"]` (attribute `href`). `fetch_page` up to 3 of them.
3. `fetch_page` the integrations or partners page to see adjacent players.
4. For up to 3 named competitors, `fetch_page` the homepage only, to capture how each names its category and audience.

## Build the map
- **Players:** name, one-line description in its own words, target segment, and where you learned of it.
- **Segments:** group players by who they serve (company size, industry, role) or by approach (all-in-one versus point solution, self-serve versus enterprise).
- **Axes:** pick two dimensions that separate players clearly (for example breadth of features versus ease of adoption) and place each player, marking placement as a judgment.
- **Adjacent categories:** tools that solve part of the job (for example spreadsheets, agencies).
- **Whitespace hypotheses:** segments or jobs no player addresses well, backed by what the pages leave out.

## Report
1. Landscape table and the 2-axis placement described in text or a small table.
2. Segment summary and the seed product's neighbors.
3. 2 or 3 whitespace hypotheses with the evidence and the research needed to confirm.
4. Source note: which claims come from vendor-written comparison pages.

## Pitfalls
- Comparison pages are written by one vendor about its rivals. Treat them as positioning, not neutral fact.
- Do not estimate market size, share or funding.
- Stay inside the named market. Do not add players you did not see in the fetched pages.
