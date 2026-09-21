---
name: go-to-market-analysis
description: Read a company's go-to-market motion from public signals: product-led or sales-led, ideal customer profile, channels, pricing transparency, sales assets and distribution. Use for "how do they sell", "GTM analysis", "PLG or sales-led".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Go-to-market analysis

## Steps
1. `fetch_page` the homepage. Note whether the primary call to action is "Start free" (self-serve) or "Book a demo" (sales-assisted).
2. `fetch_page` pricing. Note transparency, tiers, and any "Contact sales" gates.
3. `fetch_raw` `/sitemap.xml` and count URL groups: blog, docs, integrations, customers, comparison pages, partners. It shows where the company invests.
4. `fetch_page` up to 2 of: integrations or marketplace, partners or resellers, customers, careers.

## Motion signals
- **Product-led (PLG):** self-serve signup, free tier or trial, public pricing, in-product upgrade language, strong docs and templates.
- **Sales-led:** demo request, no pricing, ROI calculators, security and procurement pages, industry landing pages, "talk to an expert".
- **Hybrid:** self-serve entry with a "Contact sales" enterprise tier. Note where the handoff happens.

## Fill the GTM canvas (evidence or "not found")
- **Ideal customer profile:** size, industry, role, from the pages.
- **Positioning and message:** the one line they lead with (see positioning-teardown for depth).
- **Acquisition channels visible:** content and SEO (blog volume), integrations marketplace, partner program, community, events, paid landing pages, affiliates.
- **Sales assets:** case studies, ROI tools, comparison pages, security documentation, trials.
- **Pricing motion:** metric, land-and-expand hints (seats, usage), annual discount, enterprise tier.
- **Proof:** logos, quotes, numbers, awards, and whether they match the ICP.

## Report
1. A one-paragraph verdict on the motion, with the 3 strongest signals.
2. The GTM canvas as a table with evidence links.
3. Strengths, gaps, and 3 recommendations with a hypothesis, target metric and rough effort.
4. Caveats: what you cannot see (pipeline, CAC, win rates, channel mix).

## Pitfalls
- Sitemap counts show content investment, not results.
- Do not label a motion with certainty from one signal. Two independent signals or lower the confidence.
- No revenue, headcount or funding figures unless the site states them.
