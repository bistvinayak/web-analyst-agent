---
name: customer-voice-synthesis
description: Synthesize themes from testimonials, case studies or a public review page into pains, praised features, switching triggers and objections, with quotes and counts. Use for "what do customers say", "summarize these reviews".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Customer voice synthesis

## Steps
1. `fetch_page` each page named in the objective: testimonials, case studies, or a public review page whose text is in the HTML.
2. Use `query_page` to pull quotes: selectors like `blockquote, [class*="testimonial"], [class*="review"], cite`. Fetch more pages only if the sample is under about 10 quotes.
3. If a page returns almost no text, it is probably built by JavaScript or blocked. Say so and use another source.

## Method
- Copy each usable quote with its page and any role or company shown.
- Tag every quote with one or more themes: **pain before** (why they looked), **switching trigger**, **alternatives mentioned**, **praised capability**, **outcome achieved**, **objection or complaint**, **effort to adopt**.
- Count how many quotes support each theme. Keep the raw counts.
- Note the mix of sources: named customers, anonymous, logos only, third-party review versus vendor-curated.

## Report
1. Sample summary: number of quotes, sources, and how they were selected.
2. Theme table: theme, count, 1 or 2 short quotes as evidence.
3. What customers seem to value, what they struggle with, and language worth borrowing (their words for the problem).
4. Implications for the product and messaging, each with the theme it comes from.
5. **Bias note:** what this sample cannot tell you.

## Pitfalls
- Vendor-curated testimonials are marketing, not research. They overstate praise and hide churned users.
- Small samples do not support percentages. Report counts and say "in this sample".
- Quote sparingly and attribute each quote to its page. Do not add details about individuals beyond what the page shows.
