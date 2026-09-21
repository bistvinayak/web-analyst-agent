---
name: navigation-and-ux-review
description: Review information architecture and navigation from the HTML: menu structure, page hierarchy, findability, footer, breadcrumbs, search, mobile hooks. Use for "site structure review", "is the navigation clear", "UX audit".
category: Conversion and content
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Navigation and UX review

## Steps
1. `fetch_page` the target. From `links.internal_sample` and `query_page` (`nav a[href]`, `header a[href]`, `footer a[href]`, attribute `href` or text) list the primary navigation, footer and any secondary menus.
2. `fetch_raw` `/sitemap.xml` to see the true structure and depth versus what navigation exposes.
3. Fetch 2 or 3 inner pages to check header consistency, breadcrumbs (`[aria-label="breadcrumb"], .breadcrumb`) and the path back to key pages.

## Checks
- Primary nav has a small number of clearly named items (about 5 to 8). Overloaded or jargon labels = Medium.
- Labels describe destinations, not internal team names.
- The main goal (buy, sign up, contact) is reachable in one or two clicks from the homepage.
- Important pages in the sitemap but not linked from navigation = Medium (orphan risk).
- Breadcrumbs on deep pages; consistent header and footer across templates.
- Search present where content is large.
- URL structure: short, readable, hierarchical, lowercase. Long parameter URLs = Low.
- Mobile hooks: `viewport`, a menu control (`button[aria-expanded]`, `[class*="burger"]`).

## Report
Sitemap-style outline of the discovered structure, issues with evidence, and a proposed simplified navigation.

## Pitfalls
- You see the markup order, not how it looks. Avoid claims about visual layout, size or colour.
- Menus rendered by JavaScript may be missing. Say so.
