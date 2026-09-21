---
name: social-sharing-metadata
description: Check Open Graph, Twitter card, favicon and title tags that control how links look when shared. Use for "link preview looks wrong", "social sharing audit".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Social sharing metadata

## Steps
1. `fetch_page` the target (and 1 or 2 key pages such as an article or product).
2. Read `open_graph` and `twitter_card` from the result. Use `query_page` with selector `meta[property^="og:"]` and attribute `content` if you need more, and `link[rel*="icon"]` with attribute `href` for icons.

## Checks
- `og:title`, `og:description`, `og:image`, `og:url`, `og:type` all present. Missing `og:image` = High for shareability.
- `og:image` is an absolute https URL. `fetch_raw` it (counts as a fetch) to confirm it returns 200 and an image content type; relative or broken = High.
- `twitter:card` set (`summary_large_image` for image-led pages).
- `og:url` matches the canonical URL.
- Title and description are written for humans, not stuffed with keywords.
- Favicon and touch icon declared.

## Report
Table of tags with the observed value, then a ready-to-paste corrected `<meta>` block.

## Pitfalls
- Platforms cache previews. Mention that fixes may need a re-scrape in the platform's debugger tool.
- You cannot render the actual preview.
