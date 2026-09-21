---
name: privacy-and-tracking-review
description: Review a site's privacy posture from public signals: third-party trackers, cookies, consent banner, privacy policy, contact for data requests. Use for "privacy audit", "GDPR/cookie check", "what trackers does this site use".
category: Technical and compliance
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Privacy and tracking review

This is an observation report, not legal advice.

## Steps
1. `fetch_page` the target. Read `scripts.external_hosts`, `cookies` and the links.
2. Classify script hosts: analytics (google-analytics, googletagmanager, segment, mixpanel, hotjar, clarity), advertising (doubleclick, facebook, tiktok, linkedin, adroll), support widgets, fonts/CDNs. Use `query_page` with selector `script[src]` and attribute `src` for full URLs.
3. Look for a consent mechanism: `query_page` selectors like `[id*="cookie"]`, `[class*="consent"]`, `[id*="onetrust"]`.
4. Find the privacy policy and cookie policy links in the footer (`query_page` with `footer a[href]`). `fetch_page` the privacy policy.
5. Note cookies set on first response (before any consent).

## Checks
- Trackers loaded server-side in the HTML with no visible consent mechanism = High for EU/UK audiences.
- Non-essential cookies set on first load = Medium to High.
- Privacy policy present, dated, names controller/contact, lists purposes, retention and user rights. Missing = High.
- Cookie policy or preferences link reachable = Medium if absent.
- Forms collecting personal data (`forms` count, inputs of type email/tel) state purpose near the form = Low to Medium.
- Third-party host count: many unrelated hosts increases exposure.

## Report
Inventory table (host, category, evidence), cookie table, policy findings, prioritized fixes.

## Pitfalls
- Trackers injected by a tag manager after consent do not appear in static HTML. Say the inventory is a lower bound.
- Do not state legal conclusions. Say "may not meet" not "violates".
