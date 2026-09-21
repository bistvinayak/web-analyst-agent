---
name: api-surface-discovery
description: Find and review a service's public API description (OpenAPI or Swagger): base URLs, auth, endpoints, versioning, pagination and error conventions. Use for "review this API", "what does the API look like", "API design review".
category: Back end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# API surface discovery

Public, documented resources only. Do not guess private endpoints, call API methods, or test authentication.

## Steps
1. `fetch_page` the site. Look in `links.internal_sample` for "developers", "docs", "api", "reference".
2. Try well-known specification paths with `fetch_raw`, stopping after 5 attempts: `/openapi.json`, `/openapi.yaml`, `/swagger.json`, `/api-docs`, `/spec.json`. Also look for a spec link on the docs page (`query_page` with `a[href*="openapi"], a[href*="swagger"], a[href".json"], a[href".yaml"]`, attribute `href`).
3. Read the specification text that comes back: title, version, `servers`, `securitySchemes`, the list of paths, tags, and a sample of 3 operations with their parameters and responses.

## Review
- **Versioning:** version in the path, header or none. Is there a stated deprecation policy?
- **Naming and structure:** nouns for resources, consistent plural style, consistent casing, sensible nesting depth.
- **HTTP semantics:** methods used correctly (GET safe, PUT and DELETE idempotent, POST creates). Status codes documented per operation.
- **Authentication:** schemes declared (API key, OAuth 2, bearer), scopes described.
- **Pagination, filtering, sorting:** one consistent pattern (cursor or page), documented limits.
- **Errors:** a single error schema with a machine-readable code and message, not free text.
- **Idempotency and rate limits:** idempotency keys for unsafe operations, rate limit headers documented.
- **Consistency across operations:** same field names for the same concept, same date and ID formats.
- **Size:** number of paths and operations, and whether the spec is complete or partial.

## Report
1. Summary of the API (purpose, base URL, auth, size).
2. Design scorecard with evidence (the path or schema name) and severity.
3. The 5 changes that would most improve developer experience, each with an example (a corrected path, a response shape).
4. If no spec was found, say which paths you tried, and review the documentation pages instead (see api-documentation-review).

## Pitfalls
- Do not call the API. A specification is a claim about the API, not proof of how it behaves.
- Large specs are truncated by the tool. Say what part you read.
- Never treat a missing spec as a missing API.
