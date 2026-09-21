---
name: competitor-comparison
description: Compare two or more websites side by side on positioning, offer, pricing, SEO signals, trust and technology. Use when the objective names several URLs or asks "how do we compare to X", "competitor analysis".
category: Orientation
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Competitor comparison

## Steps
1. List every site to compare from the target URL and the objective. If the objective names competitors without URLs, ask nothing: use the obvious homepage URL only if it is unambiguous, otherwise say which ones you could not identify.
2. Budget the fetches: about 4 per site. For each site: `fetch_page` homepage, one pricing or product page, `fetch_raw` `/robots.txt` or `/sitemap.xml` only if SEO is in scope.
3. Extract the same fields for every site so the comparison is fair.

## Dimensions (pick those the objective needs)
- Positioning: H1, tagline, target audience, primary CTA.
- Offer: products or plans, differentiators claimed, proof used.
- Pricing: model, entry price, free tier (see pricing-page-teardown).
- SEO basics: title and description quality, structured data, sitemap size.
- Trust: customer logos, reviews, certifications, contact details.
- Technology: platform and notable third-party tools (see tech-stack-detection).
- Content: blog or docs depth from the sitemap and navigation.

## Report
1. A comparison table with one column per site and one row per dimension. Use "not found" for anything you could not verify.
2. Where each site is stronger, in one or two lines each.
3. Gaps and opportunities for the target site, ranked.

## Pitfalls
- Never compare a fetched page with a remembered impression of another site. Every cell must come from a fetch in this run.
- Traffic, revenue and ranking data are out of reach. Do not estimate them.
- Keep fetches balanced across sites; one site with 10 fetches and another with 1 makes an unfair comparison.
