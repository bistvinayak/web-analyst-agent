---
name: internal-linking-audit
description: Audit internal links for orphan pages, anchor text quality, link depth, hub pages and dead ends, using the page links and the sitemap. Use for "internal linking", "orphan pages", "improve site architecture for SEO".
category: Search and visibility
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Internal linking audit

## Steps
1. `fetch_page` the homepage and read `links.internal_sample` and `links.internal_count`.
2. `fetch_raw` `/sitemap.xml` and count URLs. Note the main sections.
3. `fetch_page` 3 to 5 pages from different sections (a category page, a deep page, a blog post, a product page).
4. `query_page` with `main a[href], article a[href]` (attribute `href`) to isolate in-content links from navigation and footer links.

## Checks
- **Reach:** are the most important pages linked from the homepage or main navigation (depth 1)? Important pages more than 3 clicks deep = Medium.
- **Orphan risk:** URLs in the sitemap that none of the fetched pages link to. Only call them "possible orphans", since you sampled.
- **Anchor text:** descriptive versus generic ("click here", "read more", bare URLs). Generic anchors on key links = Low to Medium.
- **In-content links:** do articles and product pages link to related pages, or only rely on the menu?
- **Hubs:** are there pages that group and link a topic cluster? Are cluster pages linking back?
- **Dead ends:** pages with almost no outgoing internal links.
- **Broken or redirecting links:** sample 3 links with `fetch_page` and report status (see link-health-check for a fuller check).
- **Nofollow and JavaScript links:** `query_page` for `a[rel~="nofollow"]` and `a:not([href])` on internal navigation.

## Report
1. Sample summary: pages read, links seen.
2. Findings table with severity, evidence and the exact fix (for example "add a link from /pricing to /security using the anchor 'security practices'").
3. A suggested linking plan for the top 3 pages by business value.
4. Limits: you cannot see link equity or crawl data, and you sampled the site.

## Pitfalls
- Navigation links and footer links repeat on every page. Judge contextual links separately.
- Do not claim a page is orphaned from a small sample.
