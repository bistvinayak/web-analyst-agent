---
name: structured-data-audit
description: Find and review schema.org structured data (JSON-LD, microdata) for rich results and machine readability. Use for "schema markup audit", "rich results", "is my structured data correct".
category: Search and visibility
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Structured data audit

## Steps
1. `fetch_page` the target. If `json_ld_present` is false, also `query_page` with selector `[itemscope]` to look for microdata.
2. Read the JSON-LD: `query_page` with selector `script[type="application/ld+json"]` (no attribute). Parse each block by reading it.
3. For each block note `@type`, required and recommended properties, and whether values match visible page content.
4. Fetch 1 or 2 other page types (article, product, contact) and repeat.

## Checks
- Site-level: `Organization` or `WebSite` with name, url, logo, `sameAs` links.
- Page-level type fits the page: `Article`/`BlogPosting` (headline, author, datePublished), `Product` (name, offers with price and currency, availability), `FAQPage`, `BreadcrumbList`, `LocalBusiness`.
- JSON is valid (balanced braces, quoted keys). Invalid JSON = High.
- Markup describes content that is actually visible. Marking up hidden or false content = High.
- Missing recommended properties = Low to Medium.

## Report
List each block found with type and key fields, gaps, and a corrected JSON-LD snippet for the most valuable missing type.

## Pitfalls
- You cannot run Google's Rich Results Test. Say "checked by reading the markup, not validated by a search engine".
- Markup added by JavaScript will not appear.
