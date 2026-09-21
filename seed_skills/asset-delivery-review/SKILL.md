---
name: asset-delivery-review
description: Review how images, fonts, CSS and JavaScript are delivered: formats, sizing, lazy loading, preloading, font loading, compression and cache headers. Use for "why is the page heavy", "image optimization", "asset delivery review".
category: Front end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Asset delivery review

## Steps
1. `fetch_page` the target. Read `size_bytes`, `images`, `scripts`, `stylesheets` and `other_headers`.
2. `query_page` with these selectors and note counts:
   - Images: `img` (attributes `src`, then `loading`, `width`, `height`, `srcset`), `picture source` (attribute `type`)
   - Loading hints: `link[rel="preload"], link[rel="preconnect"], link[rel="dns-prefetch"], [fetchpriority]`
   - Blocking resources: `head script[src]:not([async]):not([defer]):not([type="module"])`, `link[rel="stylesheet"]`
   - Fonts: `link[rel="preload"][as="font"]`
3. `fetch_raw` the main stylesheet (`max_chars` 15000) and look for `@font-face`, `font-display`, `url(` font formats and large inlined `data:` URIs.
4. `fetch_page` on 3 assets (a stylesheet, a script, an image) and read their `other_headers` for `cache-control`, `content-encoding` and `content-type`.

## Checks
- **Image formats:** modern formats (AVIF, WebP) where possible. Large PNG or JPEG photos [Medium].
- **Image sizing:** `width` and `height` set (avoids layout shift), `srcset` for responsive sizes, `loading="lazy"` below the fold, the main hero not lazy loaded, `fetchpriority="high"` on the largest visible image.
- **Blocking:** render-blocking scripts in the head [Medium]. `defer` or `async` or `type=module` preferred.
- **CSS:** count and size, unused-code risk when very large, critical CSS inlined or a small first stylesheet.
- **Fonts:** WOFF2, `font-display: swap` or `optional`, few families and weights, preloaded when critical [Medium].
- **Compression:** `gzip` or `br` on text assets. Missing [High].
- **Caching:** long `cache-control` with immutable fingerprinted files, short for HTML. No cache headers on static assets [Medium].
- **Third parties:** hosts other than the site itself that load scripts or fonts (see privacy-and-tracking-review).

## Report
1. Table of asset type, what was found, verdict.
2. The 5 fixes with the largest likely gain, each with a code snippet (for example the exact `img` markup or header value).
3. A suggested performance budget (HTML, CSS, JS, images) for this page type.
4. Measure next: run Lighthouse or WebPageTest for real timings.

## Pitfalls
- Sizes are for the fetched response only. You did not run the page, so total transferred weight is a lower bound.
- CDNs may vary headers by client. Say you saw one request.
