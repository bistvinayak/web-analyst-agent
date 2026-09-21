---
name: responsible-ai-disclosure-review
description: Review a product's public AI disclosures: AI use labeling, data use for training, retention, opt-outs, limitations, human oversight, safety and security statements, and terms about AI outputs. Use for "responsible AI review", "AI policy audit", "does it disclose AI use".
category: AI engineering
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Responsible AI disclosure review

An observation report against a checklist. It is not legal advice or a compliance opinion.

## Steps
1. `fetch_page` the homepage, then find AI policy, trust, security, privacy, terms and help pages (`query_page` with `footer a[href], a[href*="ai"], a[href*="trust"], a[href*="privacy"], a[href*="terms"]`, attribute `href`).
2. `fetch_page` up to 4 of those pages. Read the text for sections on AI, machine learning, models, training, generated content and automated decisions.
3. Use `query_page` with `h2, h3` on long policy pages to find the relevant sections quickly.

## Checklist (present, partial, missing, with a short quote and the page)
- **AI use disclosure:** where AI is used and that users are told when they interact with it or receive generated content.
- **Data use:** whether customer inputs or outputs are used to train models, by default or by opt-in. This is the most important line.
- **Retention:** how long prompts, outputs and logs are kept, and deletion options.
- **Subprocessors and model vendors:** named third parties that process data.
- **Controls:** opt-out, admin settings, data residency, enterprise terms.
- **Limitations:** accuracy caveats, known failure modes, guidance to verify outputs.
- **Human oversight:** review steps for consequential outputs, ways to contest or report issues.
- **Safety and abuse:** content policies, reporting channel, red-teaming or evaluation statements, incident process.
- **Security:** how AI features are covered by security practices (access control, prompt injection, data isolation) if stated.
- **Ownership and IP:** who owns outputs, indemnity language, training data provenance claims.
- **Provenance:** labeling or watermarking of generated media (for example content credentials), if relevant.

## Report
1. Checklist table with ratings, quotes and pages.
2. The 3 most important gaps for a customer or regulator, in order of risk.
3. Questions to send the vendor for each gap.

## Pitfalls
- Absence on the site is not absence in the contract. Say "not found on the public pages".
- Do not interpret regulations or declare compliance. Point out what to ask a specialist.
- Quote sparingly and attribute every quote to its page.
