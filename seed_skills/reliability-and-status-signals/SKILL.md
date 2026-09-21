---
name: reliability-and-status-signals
description: Read public reliability signals: status page and incident history, uptime claims and SLA, response time samples, rate-limit headers, deprecation policy and security contact. Use for "is this vendor reliable", "vendor due diligence", "reliability review".
category: Back end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Reliability and status signals

## Steps
1. `fetch_page` the homepage and find links named status, uptime, trust, security or SLA (`query_page` with `a[href*="status"], a[href*="uptime"], a[href*="trust"], a[href*="security"], a[href*="sla"]`, attribute `href`).
2. `fetch_page` the status page and the trust or security page if linked. Read current state, history and any listed components.
3. Sample response time: the `elapsed_ms` from 3 separate `fetch_page` calls on different pages. Say these are single-location samples.
4. `fetch_page` an API or docs URL and read headers for `x-ratelimit-limit`, `x-ratelimit-remaining`, `retry-after`.
5. `fetch_raw` `/.well-known/security.txt`. Read a changelog or deprecation policy if linked.

## What to capture
- **Transparency:** a public status page, per-component status, incident history with dates and post-incident reviews.
- **Availability claims:** stated uptime or SLA and its terms (credits, exclusions, measurement).
- **Observed responsiveness:** the samples above, in ms.
- **Limits and backoff:** documented rate limits and the headers that report them, guidance on retries.
- **Change management:** changelog cadence, deprecation notice period, versioning.
- **Security operations:** security contact, disclosure policy, certifications listed (name them only if stated).
- **Support:** channels and stated response times.

## Report
1. Signal table: signal, what you saw, source page, strength (strong, partial, none).
2. Overall assessment in words, with the 3 most important observations and a confidence level.
3. Questions to ask the vendor that the public pages do not answer (data residency, RPO and RTO, failover design, past outages).

## Pitfalls
- Public claims are not measurements. Do not state that a service is reliable, only what it shows and claims.
- Three response-time samples say almost nothing. Present them as a rough hint.
- Never test rate limits or try to trigger errors.
