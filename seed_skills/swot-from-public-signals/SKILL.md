---
name: swot-from-public-signals
description: Produce an evidence-based SWOT for a product or company from its public pages, with each point tied to a source and labeled as evidence or inference, ending in strategic implications. Use for "SWOT analysis", "strengths and weaknesses of X".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# SWOT from public signals

## Steps
1. Gather evidence first with `fetch_page`: homepage, pricing, one product or features page, customers or case studies, and changelog or blog (about 5 pages). Reuse findings from product-teardown thinking where relevant.
2. If competitors are named in the objective, add one `fetch_page` each for comparison.
3. Only then write the SWOT.

## Rules for each quadrant
- **Strengths and weaknesses are internal.** They describe the product and company as shown by their own pages: clarity, proof, breadth, pricing, speed of shipping, trust signals.
- **Opportunities and threats are external.** They come from the market context, so they are mostly inference. Anchor them to a visible signal (for example a new category term, a rival's launch).
- Each item has: the statement, the evidence (page and short quote), and a tag **Evidence** (seen on a page) or **Inference** (your reasoning).
- A weakness or threat with no quote or observed value does not belong in the table. Move it to "data that would sharpen it".
- Keep 3 to 5 items per quadrant. Drop generic items that fit any company.

## Turn it into strategy
Cross the quadrants: which strengths capture which opportunities, which weaknesses expose which threats. Produce up to 4 implications, each with a suggested move, a hypothesis and a rough impact and effort judgment.

## Report
1. The four quadrants as a table, each row tagged Evidence or Inference.
2. The implications list.
3. What data would sharpen it: win-loss notes, retention, support tickets, pricing tests.

## Pitfalls
- A SWOT without evidence is opinion. If a quadrant has no sourced items, say it is thin instead of padding.
- Do not state market trends as facts unless a fetched page states them.
- Keep the reader's product and a competitor separate. Do not mix their strengths.
