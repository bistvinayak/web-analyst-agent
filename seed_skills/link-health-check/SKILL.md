---
name: link-health-check
description: Sample a page's links and report broken, redirecting or suspicious ones, including external links. Use for "find broken links", "link audit", "check the footer/nav links".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Link health check

The fetch budget is small, so this is a sample, never a full crawl.

## Steps
1. `fetch_page` the target and read `links.internal_sample` and `links.external_sample`.
2. Choose up to 8 links: the main nav, footer legal links (privacy, terms), the primary CTA target, 2 external links, plus any anchor text that looks stale.
3. `fetch_page` each. Record status, final URL and redirect chain.

## Checks
- 4xx or 5xx status = High for nav, CTA and legal links; Medium elsewhere.
- Redirect chains over 2 hops or redirects to the homepage (a soft 404) = Medium.
- Links to `http://` from an https page = Low.
- External links that fail or land on parked or unrelated domains = Medium.
- Empty `href`, `#` only, or `javascript:` links used as navigation = Low.
- Anchors with generic text ("click here") = Low.

## Report
Table: link, anchor text, status, final URL, issue, fix. State how many links the page has in total versus how many you tested.

## Pitfalls
- A block or timeout on the fetch does not prove a link is broken for people. Label such results "unverified".
- Respect robots.txt; report disallowed links as untested.
