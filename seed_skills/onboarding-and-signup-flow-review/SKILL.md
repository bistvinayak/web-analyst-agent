---
name: onboarding-and-signup-flow-review
description: Review the path from landing to first value using public pages: signup steps, required fields, friction, time-to-value promises and activation cues. Use for "why don't signups convert", "review onboarding", "activation analysis".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Onboarding and signup flow review

Reviews only what a logged-out visitor can see. The product inside the login is out of reach.

## Steps
1. `fetch_page` the homepage and find the primary call to action and where it leads.
2. `fetch_page` the signup or trial page, and the pricing page if the plans gate the start.
3. `query_page` on the signup page for the form: `form input:not([type=hidden])`, `form label`, `form button`, and social login links (`a[href*="google"], a[href*="github"], a[href*="sso"]`).
4. Look for what follows signup: `fetch_page` a "getting started" doc, onboarding guide or templates page if linked.

## What to capture
- **Steps and commitment:** clicks from landing to account creation, fields required, card required or not, email verification implied, sales call required.
- **Time to value promise:** any statement like "up and running in 5 minutes". Is it credible given the steps?
- **Aha moment proxy:** what the first successful outcome is, and whether the docs or templates lead straight to it.
- **Friction points:** fields that are not needed to start, forced choices before value, unclear plan selection, jargon.
- **Trust at the moment of commitment:** privacy note, security badges, "no card required", cancel-anytime language near the form.
- **Alternatives to signup:** live demo, sandbox, sample data, video, which lower the cost of trying.
- **Activation levers:** checklists, templates, integrations that make the first session useful.

## Report
1. A step table: step, what the user must do, effort (low, medium, high), evidence URL.
2. The 3 biggest friction points with a hypothesis each ("removing the company-size field will raise signup completion").
3. Suggested experiments, each with a primary metric (signup completion, activation rate) and a guard metric (for example lead quality).
4. What you could not see: everything after login.

## Pitfalls
- Never claim conversion or activation rates. You have no analytics.
- A form built by JavaScript may look empty in static HTML. Say so and treat the step count as a lower bound.
- Do not create accounts or submit forms. This is read-only.
