---
name: conversion-cro-audit
description: Audit a landing page or homepage for conversion: value proposition, calls to action, forms, friction, social proof, urgency. Use for "improve conversion", "landing page review", "why don't visitors sign up".
category: Conversion and content
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Conversion (CRO) audit

## Steps
1. `fetch_page` the target. Read title, H1, subheadings and the text excerpt as a first-time visitor would.
2. `query_page` for: `a[class*="btn"], a[class*="button"], button` (calls to action), `form` and `input` (fields), `[class*="testimonial"], [class*="review"], [class*="logo"]` (proof).
3. Fetch the page the primary CTA leads to (signup, demo, checkout) and count form fields.

## Checks
- Value proposition: within the H1 and first paragraph, can you say who it is for, what it does, and why it is better? Vague = High.
- One clear primary CTA above the fold, with specific wording ("Start free trial" beats "Submit"). Competing equal CTAs = Medium.
- Form friction: count fields; each unnecessary field costs conversions. More than 5 for a top-of-funnel form = Medium.
- Social proof near the CTA: customer logos, testimonials with names, numbers, reviews. None = Medium.
- Risk reducers: free trial, no card, guarantee, cancel anytime, security or privacy note near forms.
- Pricing or next step visible without hunting. Contact info reachable.
- Consistency: ad or search promise matches the page headline.

## Report
Scorecard per check with evidence quoted from the page, then a ranked list of tests to run, each with a concrete rewrite (headline, CTA text) and the hypothesis behind it.

## Pitfalls
- You have no analytics. Frame everything as hypotheses to A/B test, never as proven causes of low conversion.
- Layout and visual hierarchy are invisible to you. Do not comment on colours or placement beyond what the HTML order shows.
