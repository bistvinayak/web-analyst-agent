---
name: changelog-and-roadmap-signals
description: Read a product's changelog, release notes, blog and careers page to infer shipping velocity, focus areas and strategic direction. Use for "what are they building", "how fast do they ship", "roadmap signals".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Changelog and roadmap signals

## Steps
1. `fetch_page` the homepage and find links named changelog, release notes, what's new, updates, roadmap, blog or product news.
2. If none are linked, try `fetch_raw` on `/changelog`, `/releases`, `/whats-new`, `/updates`, and the feeds `/changelog.rss`, `/feed`, `/rss.xml`. Stop after 4 attempts.
3. Read the entries you find. `query_page` with selectors like `article h2, .entry h3, time` and attribute `datetime` can pull titles and dates.
4. `fetch_page` the careers page. Count open roles by function (engineering, design, sales, support, AI or data).
5. `fetch_page` a public roadmap or status page if linked.

## What to compute
- **Cadence:** entries per month over the last 6 to 12 months, and the date of the latest one (staleness above 90 days is a signal).
- **Themes:** group entries into areas (new capability, integrations, performance, security, AI features, pricing changes). Count each.
- **Type of work:** big launches versus steady polish. Breaking changes and deprecations.
- **Direction signals:** repeated new areas, new integration categories, enterprise features (SSO, audit logs) suggesting a move up-market, AI features appearing.
- **Investment signal from hiring:** roles by team, and any that name a new product area.

## Report
1. A short timeline of notable entries with dates and links.
2. A table of themes with counts, and what they suggest.
3. 3 hypotheses about direction, each with the evidence and a confidence level.
4. Implications for the reader's product: what to watch, what to respond to, what to ignore.

## Pitfalls
- Changelogs show what a company chooses to announce, not everything it ships.
- Hiring pages lag reality and may list evergreen roles.
- Label all direction claims as inference. Never present a guess about a private roadmap as fact.
