---
name: error-handling-and-status-code-review
description: Review how a site handles missing pages, redirects, errors and unusual paths: correct status codes, soft 404s, redirect types and chains, custom error pages. Use for "status codes", "404 handling", "redirect audit", "how does it fail".
category: Back end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Error handling and status code review

Use only benign, public URLs. Never send unusual input, high volumes or anything that tests for vulnerabilities. Stay under 8 requests.

## Steps
1. `fetch_page` the canonical https homepage. Note status, `redirect_chain` and headers.
2. `fetch_page` the `http://` version and the `www` or non-`www` counterpart. Compare final URLs and the number of hops.
3. `fetch_page` one clearly non-existent path such as `/this-page-should-not-exist-12345`. Read the status, title and text.
4. `fetch_page` an inner URL with and without a trailing slash, and one with different capitalization.
5. `fetch_raw` `/robots.txt` and read the status and `content_type`.

## Checks
- **Missing pages:** a real 404 (or 410) with an error page. A 200 status with "not found" text is a soft 404 [Medium to High]. A redirect to the homepage is also a soft 404 pattern.
- **Error page quality:** clear message, navigation, search, no stack traces, framework names or internal paths leaking [High if leaks].
- **Redirects:** http to https in one 301, one canonical host, at most one hop [Medium for chains]. Temporary (302, 307) used where permanent is meant [Medium].
- **Trailing slash and case:** one form redirects to the other, or both serve the same content with a canonical tag. Two live versions with no canonical = duplicate risk.
- **Content types:** correct `content-type` on `robots.txt`, feeds, JSON.
- **Headers on errors:** do error responses keep security headers? Do they cache correctly (`cache-control` on 404s)?
- **Status semantics:** 200 for success, 301 for moves, 404 for missing, 410 for gone, 5xx for server faults. Note anything unusual.

## Report
Table of each request: URL, status, hops, final URL, verdict. Then the fixes with example configuration in words or a short server snippet.

## Pitfalls
- One request per case is a sample. Behavior can differ by path prefix or bot detection.
- If you receive a challenge or block page, say so and stop. Do not try to get around it.
