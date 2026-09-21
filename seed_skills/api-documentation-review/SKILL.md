---
name: api-documentation-review
description: Review API documentation for developer experience: quickstart, authentication, errors, rate limits, pagination, webhooks, versioning, SDKs and examples. Use for "review our API docs", "developer experience audit", "time to first call".
category: Back end
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# API documentation review

## Steps
1. `fetch_page` the docs home or API reference from the given URL, or find it in `links.internal_sample` (developers, docs, api, reference).
2. `query_page` with `nav a[href], aside a[href]` (attribute `href`) to read the docs structure, then `fetch_page` up to 4 key pages: quickstart, authentication, errors, an endpoint reference.
3. Use `query_page` with `pre, code` to count code samples and see which languages are shown.

## Score each area (strong, adequate, weak, missing) with evidence
- **Quickstart:** steps to a first successful call, and whether it is copy-pasteable. Long or missing quickstarts are the top drop-off point.
- **Authentication:** how to get credentials, a working example, scopes, key rotation.
- **Reference:** every endpoint with parameters, types, required flags, example request and response.
- **Errors:** a full list of codes with causes and fixes, retry guidance.
- **Limits:** rate limits, payload sizes, timeouts, quotas, with the headers used.
- **Pagination and filtering:** documented once, applied consistently.
- **Versioning and changes:** changelog, deprecation timeline, migration guides.
- **Webhooks and events:** payloads, signatures, retries, ordering.
- **SDKs and tools:** official libraries, a Postman or OpenAPI download, a sandbox or test mode.
- **Findability:** search, stable URLs, sidebar structure, a clear path from marketing site to docs.
- **Trust:** status page link, security and compliance pages, support channel.

## Report
1. Scorecard table with the evidence page for each area.
2. Time-to-first-call estimate as a judgment: number of steps and prerequisites from the quickstart.
3. Top 5 fixes ordered by impact on adoption, each with an example of what to add.
4. What you cannot judge: accuracy against the real API, and how it feels in practice.

## Pitfalls
- Documentation quality is about the reader's task. Judge from the point of view of a developer with no context.
- Do not execute example code or call any endpoint.
