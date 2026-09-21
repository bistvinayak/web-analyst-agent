---
name: ai-feature-discovery
description: Find and describe the AI features a product offers from its public pages: what they do, where they appear, how they are described, controls given to users, and limits. Use for "what AI does this product have", "AI feature audit".
category: AI engineering
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# AI feature discovery

## Steps
1. `fetch_page` the homepage and note AI terms in the headline, navigation and calls to action (AI, assistant, copilot, agent, chat, generate, summarize, ask, smart).
2. `fetch_raw` `/sitemap.xml` and look for paths such as `/ai`, `/assistant`, `/agents`, `/copilot`, `/features/ai`, `/docs/ai`. `fetch_page` up to 3 of them plus the pricing page.
3. `query_page` for chat and assistant widgets (`[class*="chat"], [id*="chat"], [class*="assistant"], iframe`) and for AI mentions in headings (`h1, h2, h3`).

## For each feature found, capture (or write "not stated")
- **Name and where it appears** (in the product, on the site, in the API).
- **Job it does** for the user, in one sentence, and the type: generation, summarization, search and Q&A, classification, recommendation, automation or agent.
- **Inputs and grounding:** what data it uses (user content, public web, connected apps). Does the site say answers cite sources?
- **User controls:** opt in or out, editing outputs, feedback buttons, human review steps, data usage settings.
- **Claims:** accuracy or time-saving claims and any evidence given.
- **Availability and cost:** plan gating, credits or usage limits.
- **Disclosure:** whether AI use is labeled, and whether limitations are stated (see responsible-ai-disclosure-review).

## Report
1. Feature table: feature, job, type, grounding, controls, availability, evidence page.
2. Assessment: is the AI central to the product or a bolt-on? Is the value proposition specific or generic ("powered by AI")?
3. Questions an AI engineer would ask next (evaluation, latency, failure handling, data flow).

## Pitfalls
- Marketing pages overstate. Report what is claimed and what is shown as evidence separately.
- Do not name a model or vendor unless a page does (see ai-stack-and-vendor-detection).
- Features behind login are not visible.
