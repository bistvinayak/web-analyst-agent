---
name: security-headers-review
description: Review HTTP security headers, cookie flags, HTTPS behavior and obvious exposure on a site. Use for "security headers check", "basic security audit", "is this site hardened".
category: Technical and compliance
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Security headers review

Passive review only. Never probe for vulnerabilities, guess paths that are not public, or try credentials.

## Steps
1. `fetch_page` the https URL. Read `security_headers`, `missing_security_headers`, `other_headers` and `cookies`.
2. `fetch_page` the `http://` version. It should redirect to https in one hop.
3. `fetch_raw` `/.well-known/security.txt` (a good sign if present).
4. Fetch one inner page and one login or form page if linked, and compare headers.

## Checks
- `strict-transport-security`: present with `max-age` of at least 15552000 (about 6 months). Missing on an https site = High.
- `content-security-policy`: present. Absent = Medium. Note `unsafe-inline` / `unsafe-eval` / wildcard sources as weaknesses.
- `x-frame-options` or CSP `frame-ancestors`: clickjacking protection. Missing = Medium.
- `x-content-type-options: nosniff`: missing = Low.
- `referrer-policy`, `permissions-policy`: missing = Low.
- Cookies: session-like cookies should have `Secure` and `HttpOnly` and a `SameSite` value. Missing flags = Medium.
- Information leaks: precise `server` or `x-powered-by` versions = Low.
- Mixed content: `http://` script or stylesheet URLs on an https page = High (check with `query_page` selectors `script[src^="http:"]`).
- Third-party script hosts: list them, since each is trusted code.

## Report
Table of header, observed value, status, and a suggested value. Then top 3 fixes.

## Pitfalls
- Some headers appear only on certain routes or for browsers. State which URLs you tested.
- This is a header review, not a penetration test. Do not claim the site is "secure".
