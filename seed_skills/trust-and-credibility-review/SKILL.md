---
name: trust-and-credibility-review
description: Judge how trustworthy a website looks to a first-time visitor or buyer: identity, contact details, policies, proof, security basics, red flags. Use for "is this site legit", "vendor due diligence", "why don't people trust us".
category: Conversion and content
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Trust and credibility review

## Steps
1. `fetch_page` the target. Read title, text excerpt, and footer links via `query_page` `footer a[href]`.
2. `fetch_page` about, contact, terms, privacy and refund or returns pages if linked (max 4).
3. `fetch_page` the `http://` version and note security headers (see security-headers-review).

## Signals of trust
- Identity: company name, registered address, team or founder names, an About page with substance.
- Contact: email, phone, physical address, support hours; a working contact form.
- Policies: privacy, terms, refund/returns, shipping; last updated dates.
- Proof: named customers, case studies with results, reviews on the page, press mentions. Anonymous or generic testimonials weigh less.
- Technical hygiene: https everywhere, HSTS, no mixed content.
- Consistency: copyright year current, no placeholder text, no dead links in the footer.

## Red flags
- No identifiable owner or address on a site that takes payment.
- Pressure tactics, countdown timers that reset, unrealistic guarantees.
- Copy that is generic, contradictory or evidently templated.
- Very thin site (few pages, tiny sitemap) claiming to be a large business.
- Payment on a non-https page or asks for unusual payment methods.

## Report
A trust scorecard (signal, present or not, evidence), a short overall assessment in plain language, and the highest-impact improvements.

## Pitfalls
- Domain age, reviews on other sites and business registries are outside your tools. Say they were not checked.
- Do not accuse a site of fraud. Report observable signals and their absence.
