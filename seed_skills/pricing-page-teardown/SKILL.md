---
name: pricing-page-teardown
description: Break down a pricing page: plans, price points, metrics, packaging, anchoring, free tier, friction, and how it compares to alternatives. Use for "analyze this pricing", "pricing strategy", "what does X charge".
category: Conversion and content
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Pricing page teardown

## Steps
1. Find the pricing page: use the given URL, or look in `links.internal_sample` for "pricing", "plans", or fetch `/pricing`.
2. `fetch_page` it. Use `query_page` on likely containers: `[class*="plan"], [class*="tier"], [class*="price"], table, li` to extract plan names, prices, and feature lists.
3. If prices are missing from the HTML, say they are likely loaded by JavaScript or hidden behind "Contact sales", and stop guessing.
4. Fetch one supporting page (FAQ, terms or upgrade page) if it explains limits or billing.

## What to extract
- Plans, price per period, currency, billing options (monthly versus annual discount).
- The pricing metric (per seat, usage, flat, per feature).
- Free tier or trial: limits and whether a card is required.
- What differentiates each tier; which tier is highlighted ("Most popular").
- Enterprise or custom tier and how it is reached.

## Analysis
- Packaging logic: is the jump between tiers explained by value?
- Anchoring and decoy effects; annual discount size.
- Friction: hidden prices, unclear limits, hard-to-find pricing.
- Fit for the stated buyer.
- If competitors are named in the objective, compare using competitor-comparison.

## Report
Plan table (plan, price, key limits), followed by strengths, weaknesses and 3 concrete recommendations.

## Pitfalls
- Quote only prices you saw in the fetched HTML, with the URL. Never fill gaps from memory of what a company "usually" charges.
- Prices can vary by region or login. State the region-agnostic caveat.
