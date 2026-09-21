---
name: content-and-messaging-review
description: Review website copy for clarity, audience fit, tone, structure and gaps. Use for "review our copy", "is the messaging clear", "content audit", "tone of voice".
category: Conversion and content
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Content and messaging review

## Steps
1. `fetch_page` the target, then 2 to 4 pages that carry the message (about, product, blog post, pricing).
2. For each page note the H1, key headings and the opening paragraph. Use `query_page` with `p` or `h2` if the excerpt is too short.
3. Compare pages against each other for consistency.

## Checks
- Audience: is it explicit who the page is for? Is jargon explained?
- Clarity: can the main point be stated in one sentence after reading the top section? Long, abstract or buzzword-heavy openings = Medium.
- Benefits over features: do headlines say what the reader gains?
- Specificity: numbers, names, examples, proof versus vague claims ("best-in-class", "innovative").
- Structure: scannable headings, short paragraphs, lists where useful.
- Consistency: same product name, terminology and promise across pages; same voice.
- Gaps: missing answers to obvious questions (price, how it works, who uses it, how to start).
- Freshness: dates, copyright year, references that look outdated.

## Report
Per-page verdict with short quotes as evidence (under 25 words each), then a list of rewrite suggestions with before and after lines, then content gaps.

## Pitfalls
- Judge only the text you fetched. Say which pages you read.
- Tone is subjective. Tie feedback to the stated audience and objective, not personal taste.
