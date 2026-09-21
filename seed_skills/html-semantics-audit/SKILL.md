---
name: html-semantics-audit
description: Review semantic HTML: landmarks, heading outline, lists, buttons versus clickable divs, form labels, tables, images, ARIA misuse and document metadata. Use for "audit our markup", "is the HTML semantic", "front end code review".
category: Front end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# HTML semantics audit

## Steps
1. `fetch_page` the target. Read `lang`, `headings`, `forms`, `images` and the title.
2. Run these `query_page` selectors and note the counts and examples:
   - Landmarks: `header, nav, main, footer, aside`
   - Fake controls: `div[onclick], span[onclick], a:not([href]), a[href="#"], a[href^="javascript:"]`
   - Buttons and forms: `button:not([type])`, `input:not([type=hidden]):not([type=submit])`, `label`, `select`, `textarea`
   - ARIA: `[role]`, `[aria-hidden="true"]`, `[aria-label]`, `[tabindex]`
   - Content: `table`, `th`, `ul, ol`, `br`, `img:not([alt])`, `iframe:not([title])`
3. `fetch_page` one more template (article, form or product) and repeat the key checks.

## Checks (severity in brackets)
- One `main`, one `h1`, no skipped heading levels [Medium].
- Interactive things are real `button` or `a[href]` elements. Clickable `div` or `span` [High], links used as buttons and buttons used as links [Medium].
- Every form control has a label. Missing labels [High]. Buttons have a `type`.
- Lists use `ul`/`ol`, not repeated `br` or divs [Low]. Data tables use `th` with `scope` [Medium].
- ARIA used only where native HTML cannot do the job. `role="button"` on a div, redundant roles on native elements, `aria-hidden` on focusable content [Medium].
- `iframe` has a `title`. Images have meaningful `alt`.
- Document: `lang` set, a unique `title`, `meta viewport`, a single `charset`.
- Positive `tabindex` values [Low].

## Report
1. Findings table: issue, severity, element or selector, count, evidence.
2. For the top 5, a before and after markup snippet (a few lines each).
3. A short lint suggestion: which rules (eslint-plugin-jsx-a11y, axe in CI) would catch these automatically.

## Pitfalls
- Static HTML only. Elements created by JavaScript after load are not seen.
- Counts come from the fetched page, not the whole site. Say which templates you checked.
- Semantics are necessary, not sufficient, for accessibility. See accessibility-quick-audit for the wider check.
