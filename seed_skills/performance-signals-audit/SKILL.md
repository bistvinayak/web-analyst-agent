---
name: performance-signals-audit
description: Assess page speed risk from static signals: HTML size, compression, caching headers, script and stylesheet counts, third-party hosts, image loading. Use for "why is my site slow", "performance audit". Cannot measure real load time.
category: Technical and compliance
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Performance signals audit

## Steps
1. `fetch_page` the target. Record `size_bytes`, `elapsed_ms` (server response time for the HTML only), `redirect_chain`, `other_headers` (`content-encoding`, `cache-control`), `scripts`, `stylesheets`, `images`.
2. `query_page` for: `script[src]:not([async]):not([defer]):not([type=module])` (render-blocking scripts), `link[rel=stylesheet]`, `img:not([width])`, `img[loading=lazy]`, `link[rel=preload], link[rel=preconnect]`.
3. Fetch one or two heavy resources with `fetch_raw` (a main CSS or JS file, max_chars 500) to read `size_bytes`, `content-type`, and confirm they are served compressed and cacheable.

## Checks
- Server response `elapsed_ms` over about 800 = Medium (single measurement from one location; say so).
- HTML `size_bytes` over 500 KB = Medium.
- No `content-encoding` (gzip, br) on HTML/CSS/JS = High.
- Static assets with no `cache-control` or short max-age = Medium.
- Many blocking scripts in `<head>` = Medium. More than about 15 external scripts or many third-party hosts = Medium.
- Images without `width`/`height` (layout shift) and no lazy loading below the fold = Low to Medium.
- Redirect hops before the final page = Low each.
- Missing `viewport` meta = Medium for mobile.

## Report
Metrics table (value, threshold, verdict), then fixes ordered by likely impact.

## Pitfalls
- You did not run a browser. You cannot report LCP, CLS, INP or Lighthouse scores. Recommend running PageSpeed Insights for those.
- One request from one location is a weak sample. Use words like "suggests".
