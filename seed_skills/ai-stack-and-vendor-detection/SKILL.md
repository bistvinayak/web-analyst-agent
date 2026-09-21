---
name: ai-stack-and-vendor-detection
description: Detect which model providers, AI infrastructure and tooling a product uses from script hosts, docs, pricing and integration pages, with a confidence level for each. Use for "which LLM do they use", "AI vendor stack", "model provider detection".
category: AI engineering
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# AI stack and vendor detection

Evidence is a stated name, a host, or a code marker. Anything else is a guess.

## Steps
1. `fetch_page` the homepage, then docs, pricing, security and integrations pages if linked (max 4). Read `scripts.external_hosts`.
2. `query_page` with `script[src]` (attribute `src`) and `a[href]` for names of providers, and `img[alt]` for partner logos.
3. `fetch_raw` a docs or homepage URL with `max_chars` 15000 and search the text for provider and model names, API paths such as `/v1/chat/completions` or `/v1/messages`, and SDK names.
4. Check subprocessor or trust pages for AI vendors (a "subprocessors" list is strong evidence).

## What to look for
- **Model providers:** OpenAI, Anthropic, Google (Gemini, Vertex), Azure OpenAI, AWS Bedrock, Mistral, Cohere, Meta Llama hosts, open-source model hubs.
- **Inference and gateways:** OpenRouter, Together, Groq, Fireworks, Replicate, Hugging Face endpoints.
- **Orchestration and tooling:** LangChain, LlamaIndex, Vercel AI SDK, Langfuse, Helicone, Weights and Biases.
- **Retrieval and storage:** Pinecone, Weaviate, Qdrant, pgvector, Elasticsearch mentions.
- **Speech, vision, embeddings:** named providers or models.
- **Model names in copy:** a model or version a page states outright.

## Rate confidence
- **High:** the vendor or model is named on the product's own page, docs or subprocessor list.
- **Medium:** a script host, SDK or API path points to it, or a partner logo appears.
- **Low:** indirect hints only. Report as a guess and say what would confirm it.

## Report
1. Table: layer (model, gateway, orchestration, retrieval, other), vendor or model, evidence, confidence.
2. What the stack suggests for cost, latency, data flow and lock-in, labeled as inference.
3. Questions to ask (which models per feature, fallbacks, data retention, evaluation).

## Pitfalls
- Vendors run behind gateways. The front-end host may not be the model provider.
- Old blog posts and docs may describe a past stack.
- Never present a guess as a fact, and do not infer proprietary architecture.
