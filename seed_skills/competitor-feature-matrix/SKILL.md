---
name: competitor-feature-matrix
description: Build an evidence-backed feature matrix across two or more products, classify table stakes, differentiators and gaps, and suggest what to build or message next. Use for "feature comparison", "how do we stack up", "gap analysis".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Competitor feature matrix

## Steps
1. List the products from the target URL and the objective. If a competitor URL is missing, say which one you could not identify. Do not guess a site.
2. Budget about 4 `fetch_page` calls per product: homepage, features or product page, pricing, and docs or integrations if present. Use `query_page` on a fetched page (for example `table`, `li`, `h3`) to pull feature lists without spending another fetch.
3. Build the feature list from what the pages themselves emphasize, then merge duplicates ("SSO" and "single sign-on"). Keep it to 10 to 15 rows that matter for the objective.
4. For every cell record: present, partial, absent or not found. "Not found" means you did not see it on the fetched pages, which is not the same as absent.

## Classify each row
- **Table stakes:** every product has it. Missing it is a risk, having it earns no credit.
- **Differentiator:** only some have it. Note who and how prominently it is marketed.
- **Gap:** competitors have it and the target does not (or the reverse, an advantage).
- **Plan gating:** available only on a paid tier. Record the tier.
Note that a true Kano classification needs customer surveys. This is a market-parity view.

## Report
1. The matrix as a table: rows are features, columns are products, cells hold the status plus a short evidence tag (page name).
2. Summary: 3 table stakes, 3 differentiators, 3 gaps.
3. **Recommendations:** for the target product, up to 5 moves (build, improve, message, price), each with a hypothesis and a rough impact and effort judgment (low, medium, high).
4. Coverage note: how many pages you read per product, so the reader can judge fairness.

## Pitfalls
- Compare like with like: a marketing claim on one site versus documentation on another is not fair. State the source type for each cell.
- Keep fetches balanced across products.
- Do not infer roadmap or quality from feature presence. A checkmark says nothing about depth.
