---
name: rendering-strategy-detection
description: Detect whether a site is server rendered, statically generated or client rendered, which framework it likely uses, and what that means for speed, SEO and accessibility. Use for "is this an SPA", "SSR or CSR", "will search engines see this".
category: Front end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Rendering strategy detection

## Steps
1. `fetch_page` the target. Compare `word_count` and the text excerpt with what the page should contain.
2. `query_page` with `#root, #app, #__next, #__nuxt, [data-reactroot], [ng-version], [data-server-rendered], astro-island, [data-svelte-h]` to find framework mount points and see whether they contain content.
3. `fetch_raw` the page with `max_chars` 15000 and look for `__NEXT_DATA__`, `__NUXT__`, `window.__INITIAL_STATE__`, `self.__next_f`, `hydrate`, `<noscript>` messages and large inline JSON.
4. `query_page` `script[src]` (attribute `src`) for framework bundle names (`/_next/`, `/_nuxt/`, `/assets/index-`, `main.`, `runtime.`).

## Decide (evidence for each label)
- **Server rendered or static:** meaningful text, headings and links in the initial HTML, plus serialized state for hydration.
- **Client rendered (SPA):** an almost empty mount point, few words, `noscript` warnings, content arriving from bundles.
- **Hybrid or islands:** mostly static HTML with small interactive components (`astro-island`, partial hydration).
- **Unknown:** say so when signals conflict.
Name the likely framework only when a bundle path or marker states it.

## Implications to report
- **SEO:** are title, meta description, headings and links present in the initial HTML? Client-only content depends on the crawler running JavaScript.
- **Performance:** larger JavaScript bundles and hydration cost for client-heavy pages. Time to first content depends on JavaScript for SPAs.
- **Accessibility and resilience:** does the page work without JavaScript? Are links real `a[href]`?
- **Social previews:** Open Graph tags present in the initial HTML.
- **Recommendation:** whether server rendering, static generation or partial hydration would fit the content, and the migration risk.

## Report
1. Verdict with the 3 strongest pieces of evidence.
2. Table of implications with severity.
3. What to verify in a browser: disable JavaScript and reload, view rendered DOM against source, throttle the network.

## Pitfalls
- Some sites serve different HTML to crawlers than to browsers. You see what this fetch received.
- A near-empty page can also be a block, a challenge page or an error. Check the status and title first.
