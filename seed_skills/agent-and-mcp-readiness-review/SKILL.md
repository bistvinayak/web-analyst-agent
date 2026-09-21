---
name: agent-and-mcp-readiness-review
description: Check whether AI agents can use a product or site: machine-readable interfaces (OpenAPI, llms.txt, MCP), auth for automation, structured data, stable actions, rate limits and crawler policies. Use for "agent readiness", "MCP support", "can an AI agent use this".
category: AI engineering
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Agent and MCP readiness review

## Steps
1. `fetch_page` the homepage and docs entry point. Look for "API", "developers", "integrations", "MCP", "agents", "automation" in navigation and links.
2. `fetch_raw` these public files, one request each: `/llms.txt`, `/llms-full.txt`, `/.well-known/ai-plugin.json`, `/openapi.json`, `/robots.txt`.
3. `query_page` on the docs page with `a[href*="mcp"], a[href*="openapi"], a[href*="sdk"], a[href*="webhook"]` (attribute `href`). `fetch_page` an MCP or agent page if one exists.
4. Read the authentication and rate-limit pages (see api-documentation-review) for automation friendliness.

## Score each dimension (strong, partial, none)
- **Machine-readable description:** an OpenAPI spec or tool schema that an agent can load, with clear operation names and descriptions.
- **Agent protocol support:** a documented MCP server, function-calling schema, or plugin manifest, and which capabilities it exposes.
- **Discoverability:** an `llms.txt` that points to the right docs, a clean sitemap, stable URLs.
- **Authentication for automation:** API keys or OAuth with scopes, service accounts, no interactive-only steps such as CAPTCHAs for API use.
- **Predictable behavior:** idempotent operations, consistent errors, pagination, rate-limit headers, webhooks for events.
- **Safety for agents:** least-privilege scopes, confirmation or dry-run modes for destructive actions, audit logs.
- **Content access:** structured data (schema.org), server-rendered content, clear robots rules for AI crawlers and agents.
- **Machine-readable commercial info:** pricing, limits and terms in a form software can read.

## Report
1. Scorecard with the file or page as evidence.
2. A verdict: what an agent could do today and what would block it.
3. Top 5 improvements ordered by unlocked capability, each with an example (a sample `llms.txt` entry, an MCP tool definition sketch).
4. A test plan: 5 tasks an agent should complete end to end, and the success criteria.

## Pitfalls
- A file that exists may be empty, stale or wrong. Read what it says.
- Do not call any API or attempt to log in. Static review only.
- Vendors change quickly. State the date of your observation.
