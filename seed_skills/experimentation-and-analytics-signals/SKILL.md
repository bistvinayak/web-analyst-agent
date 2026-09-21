---
name: experimentation-and-analytics-signals
description: Detect which analytics, experimentation and feedback tools a site loads to judge its measurement maturity and how it learns. Use for "how data-driven are they", "what analytics do they use", "do they run A/B tests".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Experimentation and analytics signals

A read of how a team measures and learns, from what its pages load.

## Steps
1. `fetch_page` the homepage. Read `scripts.external_hosts` and `cookies`.
2. `query_page` with `script[src]` (attribute `src`) for full script URLs, and `link[rel="preconnect"], link[rel="dns-prefetch"]` (attribute `href`).
3. `fetch_raw` the homepage with `max_chars` 15000 to read inline configuration for `dataLayer`, `gtag`, `analytics.load`, `posthog`, `amplitude`, `optimizely`, `statsig`.
4. `fetch_page` a signup or pricing page and compare which tools load there (funnel pages usually carry more).

## Tool families to look for (evidence is a host or a code name)
- **Web analytics:** Google Analytics or Tag Manager, Plausible, Fathom, Matomo.
- **Product analytics:** Segment, Mixpanel, Amplitude, Heap, PostHog.
- **Experimentation and flags:** Optimizely, VWO, AB Tasty, LaunchDarkly, Statsig, GrowthBook, Split.
- **Behavior and feedback:** Hotjar, FullStory, Microsoft Clarity, Intercom, Drift, survey widgets.
- **Attribution and ads:** ad pixels, affiliate scripts, call tracking.
- **Consent tooling:** presence of a consent manager (see privacy-and-tracking-review).

## Judge maturity (a rough ladder, with your evidence for each rung)
1. No analytics seen.
2. Page analytics only.
3. Product analytics or event pipeline (Segment, Mixpanel, Amplitude).
4. Experimentation or feature flags present.
5. Experimentation plus behavior tools plus consent management.

## Report
1. The tools found in a table: category, tool, evidence, where it loads.
2. The maturity rung with reasoning, and what the stack lets this team do (funnel analysis, experiments, session review).
3. Gaps that matter for the objective, and a suggested minimal measurement plan (5 events, 2 experiments, 1 dashboard) for the reader's own product.

## Pitfalls
- Tools loaded through a tag manager after consent may not appear. The list is a lower bound.
- A tool being present does not mean it is used well.
- Never infer traffic or conversion numbers.
