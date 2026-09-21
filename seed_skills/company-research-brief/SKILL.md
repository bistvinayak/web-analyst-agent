---
name: company-research-brief
description: Build a fact-based research brief on a company from its own website: what it sells, to whom, how it positions, size signals, team, customers, tech and buying triggers. Use for sales prospecting, investor or partner research, "tell me about this company".
category: Orientation
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Company research brief

## Steps
1. `fetch_page` the homepage. Capture the one-line offer and audience.
2. Find and fetch, within budget: about, product or solutions, pricing, customers or case studies, careers, blog or news, contact (max 6 pages).
3. `fetch_raw` `/sitemap.xml` for size and focus (count product, blog and job URLs).
4. Read the footer and structured data for legal name, address, social profiles (`sameAs`).

## What to capture (only if stated on the site)
- What they sell, categories, and how it works in plain words.
- Target customers and industries; named customers and results.
- Positioning versus alternatives; claimed differentiators.
- Business model and pricing signals.
- Size signals: number of open roles, offices, team page, breadth of sitemap. Label them "signals", not facts.
- Recent activity: latest blog or news dates, product updates.
- Technology signals (see tech-stack-detection) and integrations listed.
- Likely pains or triggers a seller or partner could address, clearly labelled as inference.

## Report
A one-page brief: Snapshot, Offer, Customers, Positioning, Signals, Open questions, Suggested angles for outreach. Each factual line cites the page it came from.

## Pitfalls
- Funding, revenue, headcount and traffic are not on most sites. Do not supply them from memory. List them under "Open questions".
- Keep inference visibly separate from evidence.
- Do not collect personal data about individuals beyond what the company itself publishes as a team page, and do not include private contact details.
