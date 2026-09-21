---
name: persona-and-jtbd-inference
description: Infer likely user personas and jobs-to-be-done from a product's public pages, as hypotheses with the interview questions needed to validate them. Use for "who is this for", "what job do users hire it for", "persona hypotheses".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Persona and jobs-to-be-done inference

The output is a set of hypotheses to test with research, never a finding about real users.

## Steps
1. `fetch_page` the homepage and read the audience language ("for teams", "for founders", role names, industries).
2. Fetch up to 4 pages that reveal users: use cases or solutions, customer stories, docs "getting started", pricing plan descriptions.
3. `query_page` for testimonial and role text (selectors such as `[class*="testimonial"], [class*="quote"], cite`).

## Build each persona hypothesis (2 or 3 maximum)
- **Who:** role, company type and size, and how they were described on the site (quote it).
- **Job statement:** "When [situation], I want to [motivation], so I can [expected outcome]." Include functional, emotional and social parts if the evidence supports them.
- **Trigger:** what event starts the search (a growth stage, a failure, a new mandate).
- **Current alternatives:** what they use today, including manual workarounds.
- **Anxieties and objections:** what might stop them, taken from FAQ, security pages and pricing notes.
- **Success signal:** how they would know it worked, from the outcomes the site promises.

## Check the evidence
Count how many pages support each persona. A persona shown on only one page is weak. Note the buyer versus the user versus the approver when they differ (common in business products).

## Report
1. Persona cards with the fields above and an evidence line for each.
2. A confidence rating per persona (high, medium, low) and why.
3. **Validation plan:** for each persona, 5 interview questions that test the hypothesis without leading, and one behavioral data point to look for in analytics.

## Pitfalls
- Customer stories on a site are selected by marketing. They show who the company wants, not who stays.
- Never present inferred personas as research. Use words like "the site suggests".
- Do not add demographic detail the pages do not support.
