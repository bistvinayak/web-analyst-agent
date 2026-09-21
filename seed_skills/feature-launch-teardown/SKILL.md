---
name: feature-launch-teardown
description: Review how a specific feature or product launch was communicated on a launch page or changelog entry: problem framing, audience, proof, availability, call to action and follow-through. Use for "review this launch page", "critique our announcement".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Feature launch teardown

## Steps
1. `fetch_page` the launch page, blog post or changelog entry given in the objective.
2. Follow up to 3 links from it: the feature's docs page, the pricing or plans page, and the main product page. `fetch_page` each.
3. `query_page` for the calls to action (`a[class*="btn"], a[class*="button"], button`) and any dated or versioned text (`time`, attribute `datetime`).

## Score each dimension (clear, partial, missing) with a quote or observation
- **Problem framing:** does it start with the user's problem before the feature name?
- **Audience:** who is it for, and is that stated? Are existing users told what changes for them?
- **Benefit over feature:** are outcomes described, not only capabilities?
- **Proof:** demo, screenshot description, numbers, customer quote, beta results.
- **Why now:** the trigger or timing, and what it enables next.
- **Availability:** who gets it and when. Plan gating, rollout stage, regions, prerequisites.
- **Call to action:** one clear next step, and whether it leads somewhere that works (docs, activation).
- **Follow-through:** docs exist, pricing page and product pages reflect it, changelog and announcement match.
- **Risk handling:** migration notes, deprecations, limits, support path.

## Report
1. Scorecard table: dimension, rating, evidence.
2. The 3 highest-impact fixes, each with a rewrite (for example a new headline, a clearer CTA) and the hypothesis behind it.
3. A short launch checklist the team could reuse.
4. Suggested success metrics for this launch: one adoption metric, one activation metric, one guard metric.

## Pitfalls
- You cannot see adoption or sentiment. Do not judge whether the launch worked, only how well it was communicated.
- Compare the announcement with the live product pages. Inconsistencies are findings, not assumptions.
