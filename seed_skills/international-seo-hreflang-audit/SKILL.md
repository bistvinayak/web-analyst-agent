---
name: international-seo-hreflang-audit
description: Check international and multilingual SEO setup: hreflang annotations and their reciprocity, x-default, language and region codes, canonicals and URL structure. Use for "hreflang audit", "multi-country SEO", "language versions".
category: Search and visibility
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# International SEO and hreflang audit

## Steps
1. `fetch_page` the homepage. Read `lang` and `canonical`.
2. `query_page` with `link[rel="alternate"][hreflang]` (attribute `hreflang`, then attribute `href`) to list declared language versions.
3. If none appear in the HTML, `fetch_raw` the sitemap and look for `xhtml:link` alternates, and check the `link` response header via `fetch_page` (`other_headers`).
4. `fetch_page` 2 or 3 of the alternate URLs and repeat the hreflang query on each.

## Checks
- **Presence:** hreflang declared for every real language version. None on a multilingual site = High.
- **Reciprocity:** if A points to B, B must point back to A. Missing return links = High, since engines may ignore the set.
- **Self-reference:** each page lists itself in its own hreflang set.
- **x-default:** a fallback for unmatched users. Missing = Low.
- **Codes:** valid ISO 639-1 language, optional ISO 3166-1 region (`en-GB`, not `en-UK`). Invalid codes = Medium.
- **Canonical consistency:** each version canonicalizes to itself, not to the main language. Cross-language canonicals = High.
- **`html lang`:** matches the page language.
- **URL strategy:** subfolders, subdomains or country domains, used consistently.
- **Auto-redirects by IP or language:** a page that redirects visitors away from other versions can hide them from crawlers. Look for it in redirects.

## Report
Table of language versions with hreflang status, reciprocity and canonical. Then the fixes in priority order, each with an example tag.

## Pitfalls
- If the site has one language, say hreflang is not needed and stop.
- Only three annotation methods exist (HTML, header, sitemap). Say which you checked.
- You cannot see which version a search engine actually serves.
