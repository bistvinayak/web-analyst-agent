---
name: responsive-design-review
description: Review responsive design from markup and CSS: viewport meta, breakpoints, fluid units, responsive images, fixed widths and mobile-hostile patterns. Use for "is it mobile friendly", "responsive review", "why does it break on phones".
category: Front end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Responsive design review

Layout cannot be rendered here, so judge the code that makes layout adapt.

## Steps
1. `fetch_page` the target. Read `viewport`, `stylesheets` and `images`.
2. `query_page` with `link[rel="stylesheet"]` (attribute `href`) to list stylesheets, then `fetch_raw` the main one with `max_chars` 15000.
3. In the CSS text look for: `@media` queries and their widths, `@container`, `clamp(`, `min(`, `max(`, `vw`, `rem`, `display:grid`, `display:flex`, `minmax(`, fixed `px` widths on containers, and `overflow-x`.
4. `query_page` for `img[srcset], picture source, img[sizes]` and for `[style*="width"]`, `table`, `iframe`, `video`.

## Checks
- **Viewport:** `width=device-width, initial-scale=1` present. Missing [High]. `user-scalable=no` or `maximum-scale=1` blocks zoom [High].
- **Breakpoints:** a small set of media queries, mobile-first (`min-width`) preferred. Only desktop widths [High]. Dozens of one-off breakpoints [Low].
- **Fluid layout:** flex or grid with flexible tracks, relative units, `clamp()` for type. Fixed pixel widths on wide containers [Medium].
- **Responsive media:** images with `srcset` and `sizes`, `max-width:100%`, iframes and videos with a ratio wrapper. Large fixed-size images [Medium].
- **Tables and code:** wide tables or pre blocks in a scroll container, not stretching the page.
- **Text:** base size at least 16px equivalent, line length controlled, no text in images for key content.
- **Touch:** navigation that depends on hover only [Medium]. Tap targets cannot be measured here.
- **Modern features:** container queries, `dvh` units, `prefers-reduced-motion`, `prefers-color-scheme`.

## Report
1. Findings table with severity, evidence (a CSS rule or tag) and fix.
2. A short list of breakpoints found and whether they cover common widths (about 360, 768, 1024, 1280).
3. Recommended test matrix: 3 devices or widths and what to check on each, since real rendering needs a browser.

## Pitfalls
- Stylesheets may be split or built by JavaScript. Say which files you read.
- Minified CSS is hard to scan. Search for the patterns above, not for style.
- Never state that a page "looks broken" on any device. You saw code, not pixels.
