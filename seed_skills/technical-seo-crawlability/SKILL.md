---
name: technical-seo-crawlability
description: Check whether search engines can crawl and index a site: robots.txt, sitemap, status codes, redirects, canonicals, noindex. Use for "why isn't my site indexed", "technical SEO audit", "check robots and sitemap".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Technical SEO: crawlability and indexing

## Steps
1. `fetch_raw` `/robots.txt`. Note `User-agent` groups, `Disallow` rules, and `Sitemap:` lines. A `Disallow: /` for all agents is High.
2. `fetch_raw` the sitemap (from robots.txt, else `/sitemap.xml`). Count `<loc>` entries; if it is a sitemap index, fetch one child. Check that listed URLs use the preferred host and https.
3. `fetch_page` the homepage, then test host variants: `http://` version, `www` and non-`www`. Each should end at one canonical URL with one redirect. Long redirect chains (3 or more hops) = Medium.
4. `fetch_page` 3 to 5 sitemap URLs. Each should return 200, be self-canonical, and not have `noindex` in `meta_robots` or `x-robots-tag`.
5. `fetch_page` a made-up path like `/this-page-should-not-exist-12345`. It must return 404. A 200 (soft 404) = Medium.

## Checks and severity
- Blocking rules that hide important sections: High.
- No sitemap or sitemap not referenced in robots.txt: Low to Medium.
- Sitemap URLs that redirect, 404, or are noindex: Medium.
- Mixed http/https or www/non-www serving the same content without redirect: High.
- Canonical missing or inconsistent with the sitemap: Medium.

## Report
Findings with URL and observed status/header for each. End with a prioritized fix list.

## Pitfalls
- robots.txt controls crawling, not indexing. Say which one a finding affects.
- Respect robots.txt for your own fetches. If a URL is disallowed, report that as a limitation.
- You cannot see Search Console data, so you cannot confirm what is actually indexed.
