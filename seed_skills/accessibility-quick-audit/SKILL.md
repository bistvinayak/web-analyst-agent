---
name: accessibility-quick-audit
description: Quick static accessibility check against common WCAG issues: language, headings, alt text, form labels, landmarks, link text, zoom. Use for "accessibility audit", "WCAG check", "is this site accessible".
category: Technical and compliance
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Accessibility quick audit

## Steps
1. `fetch_page` the target and 1 or 2 other templates (article, form, checkout).
2. Use `query_page` for details:
   - `img:not([alt])` and `img[alt=""]` (empty alt is fine only for decorative images)
   - `input:not([type=hidden]):not([type=submit])` versus `label` elements and `[aria-label]`
   - `main, nav, header, footer` landmarks
   - `a` elements whose text is generic ("click here", "read more")
   - `[tabindex]` values above 0
   - `button:empty, a:empty`
3. Read the heading outline from `headings`.

## Checks (WCAG level A/AA in mind)
- `lang` on `<html>` present. Missing = Medium.
- One H1, no skipped heading levels. Skips = Low.
- Informative images have meaningful alt text. Missing alt on content images = High.
- Every form control has a programmatic label. Unlabelled inputs = High.
- A `main` landmark exists, and a skip-to-content link is available = Medium if absent.
- `viewport` does not disable zoom (`user-scalable=no`, `maximum-scale=1`) = High.
- Links and buttons have accessible names; generic link text = Low.
- Positive `tabindex` = Low.
- Low colour contrast, focus visibility and keyboard traps cannot be judged from static HTML.

## Report
Issue table with WCAG criterion, evidence (selector and counts), severity, fix. Add a clear line listing what could not be tested.

## Pitfalls
- Static checks catch only a fraction of accessibility problems. Never say a site "is accessible" or "passes WCAG".
