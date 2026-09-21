---
name: http-caching-and-headers-review
description: Review HTTP caching, validation, compression and CDN headers for a page and its assets, and recommend policies. Use for "caching review", "cache-control audit", "why isn't this cached", "CDN configuration".
category: Back end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# HTTP caching and headers review

Read-only. You see one response per URL from one location.

## Steps
1. `fetch_page` the HTML page. Read `other_headers` (`cache-control`, `content-encoding`, `via`, `server`) and the full header set through `security_headers` and `cookies`.
2. `query_page` with `link[rel="stylesheet"], script[src], img` (attributes `href` or `src`) to choose 4 assets: a stylesheet, a script, an image and a font if present.
3. `fetch_page` each chosen asset and read the same headers.
4. `fetch_raw` the HTML with `max_chars` 1000 only if you need the raw status and `content_type`.

## Compare against good practice
- **HTML:** short or revalidating `cache-control` (for example `no-cache` with an `ETag`, or a few minutes at the CDN), not long-lived if it references fingerprinted assets.
- **Fingerprinted static assets** (hash in the file name): `public, max-age=31536000, immutable`. Missing or short = Medium.
- **Non-fingerprinted assets:** moderate lifetimes with validators.
- **Validators:** `ETag` or `Last-Modified` present on cacheable responses.
- **`Vary`:** only the headers that matter (`Accept-Encoding`). `Vary: *` or `Vary: Cookie` on public pages defeat shared caches [Medium].
- **Cookies:** `Set-Cookie` on cacheable static responses prevents caching [High].
- **Compression:** `br` or `gzip` on text (HTML, CSS, JS, JSON, SVG). Missing = High.
- **CDN signals:** `cf-cache-status`, `x-cache`, `age`, `x-served-by`, `via`. A `MISS` on a static asset or no `age` suggests weak edge caching.
- **Conflicts:** `no-store` next to long `max-age`, or `Pragma` and `Expires` contradicting `cache-control`.

## Report
1. Table per URL: cache-control, validators, compression, CDN signal, verdict.
2. Recommended policy by resource type with exact header values.
3. Expected effect in plain terms (fewer origin hits, faster repeat visits), and how to verify (curl -I, CDN analytics).

## Pitfalls
- You cannot test conditional requests or repeat visits. Say the verdict is from one response.
- Do not assume a CDN from one header. Combine signals.
