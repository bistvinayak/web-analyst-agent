---
name: product-teardown
description: Full product teardown from public pages: who it is for, the job it does, value proposition, activation path, business model, moat signals, and ranked recommendations. Use for "tear down this product", "PM analysis of X", "what would you change".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Product teardown

The classic PM exercise, done from public evidence only. Keep evidence and inference visibly separate.

## When to use
The objective is to understand a product as a product manager would: what it is, why it wins or struggles, and what to do next. For one narrow question use the matching skill instead (positioning-teardown, pricing-page-teardown, onboarding-and-signup-flow-review).

## Steps
1. `fetch_page` the homepage. Read the H1, subheadline, primary call to action and the text excerpt.
2. From `links.internal_sample` find pricing, signup or demo, docs, changelog and customers. `fetch_page` up to 5 of them, choosing the ones that best answer the objective.
3. `fetch_raw` `/sitemap.xml` only if you need to see how large the product surface is.

## The frame (fill each from evidence, mark gaps as "not found")
- **Who and what job:** the target user and the job they hire it for, as one sentence in the form "When [situation], [user] wants to [job] so they can [outcome]".
- **Value proposition:** the claimed benefit, the proof offered (numbers, logos, quotes), and the alternative it replaces.
- **Activation path:** steps from landing to first value, required commitment (card, email, call), what they promise the first result will be.
- **Business model:** pricing metric, free tier or trial, self-serve versus sales-led, expansion levers visible on the site.
- **Retention and expansion hooks visible publicly:** integrations, templates, teams and collaboration, data or workflow lock-in, community.
- **Moat signals:** proprietary data, network effects, integrations depth, brand, switching costs. Say which are visible and which are only guesses.
- **Friction and risks:** unclear promise, hidden pricing, heavy signup, missing proof, dependence on one channel.

## Report
1. **Product on a page:** the frame above in a compact table with an evidence column (URL and what you saw).
2. **What works, what does not:** up to 3 strengths and 3 weaknesses. Each needs a quote or a value you fetched. A suspected weakness you cannot see goes under item 4 instead.
3. **Recommendations:** 3 to 5, each with a hypothesis ("we believe X will improve Y"), and a rough RICE-style judgment (reach, impact, confidence, effort as low, medium or high). Label these as judgments, not measurements.
4. **What to validate:** the questions only user research or analytics can answer.

## Pitfalls
- You see marketing, not usage. Never state retention, revenue, market share or user counts unless the site states them, and then quote it.
- Static HTML only: pages built by JavaScript may look empty. Say so.
- Do not confuse a confident tone with evidence of product-market fit.
