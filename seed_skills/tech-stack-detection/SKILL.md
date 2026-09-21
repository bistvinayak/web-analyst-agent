---
name: tech-stack-detection
description: Identify the likely technology behind a website: CMS, framework, hosting/CDN, analytics, e-commerce and marketing tools, from headers, markup and script hosts. Use for "what is this site built with", "tech stack".
category: Technical and compliance
version: 1
updated: 2026-09-20T00:00:00+00:00
---
# Tech stack detection

## Steps
1. `fetch_page` the target. Read `other_headers` (`server`, `x-powered-by`, `via`), `cookies`, `scripts.external_hosts`.
2. `query_page` selectors:
   - `meta[name="generator"]` (attribute `content`)
   - `script[src]` (attribute `src`) and `link[href]` (attribute `href`) for path clues
   - `[id="__next"], [id="__nuxt"], [id="root"], [ng-version], [data-reactroot]`
3. `fetch_raw` `/robots.txt` and, if useful, one static asset for extra headers.

## Clues (evidence, not proof)
- WordPress: `/wp-content/`, `/wp-json/`, generator meta. Shopify: `cdn.shopify.com`, `Shopify.theme`. Wix/Squarespace/Webflow: their asset hosts.
- Next.js: `/_next/`, `__next`. Nuxt: `/_nuxt/`. Gatsby: `___gatsby`. Angular: `ng-version`. React SPA: bare `#root` with almost no text.
- CDN and hosting: `server`/`via`/`x-*` headers naming cloudflare, fastly, akamai, vercel, netlify, cloudfront, AWS.
- Analytics and marketing: googletagmanager, google-analytics, segment, hubspot, intercom, hotjar, clarity, meta pixel.
- Payments and e-commerce: stripe.js, paypal, shopify checkout.

## Report
Table: layer (CMS/framework, hosting/CDN, analytics, marketing, payments, other), technology, evidence (the header or URL seen), confidence (High if two independent clues, Medium for one, Low for an inference).

## Pitfalls
- Headers can be hidden or spoofed. Use "likely".
- Do not name versions unless a header or file states one, and flag old versions as a risk only when stated.
