---
name: rag-content-readiness-review
description: Assess how well a documentation or content site could be chunked, retrieved and cited by a RAG system: structure, headings, self-contained sections, metadata, freshness, duplication and machine-readable access. Use for "RAG readiness", "is our docs retrieval friendly".
category: AI engineering
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# RAG content readiness review

## Steps
1. `fetch_raw` `/sitemap.xml` to gauge size, section structure and `lastmod` freshness.
2. `fetch_page` 4 representative pages (a landing page, a how-to, a reference page, a long article). Read `headings`, `word_count`, canonical and the text excerpt.
3. `query_page` with `h2, h3` for the outline, `table`, `pre, code`, `details`, `[id]` (anchors), `time` (attribute `datetime`), and `link[rel="canonical"]`.
4. `fetch_raw` `/llms.txt` and `/robots.txt` for machine-access signals.

## Assess retrieval friendliness
- **Chunkability:** clear heading hierarchy and sections of roughly 100 to 400 words that make sense alone. Long unbroken pages [Medium]. Sections that say "as above" or rely on images for meaning [Medium].
- **Self-contained answers:** definitions and steps that include their own context (product name, version, prerequisites).
- **Structure that helps:** tables and lists with headers, code blocks with language and caption, FAQ format, stable anchors per section.
- **Metadata:** titles, descriptions, dates, version labels, breadcrumbs, canonical URLs, structured data. These become filters and citations.
- **Freshness and versioning:** dated pages, version markers, and old versions clearly labeled. Mixed versions without labels cause wrong answers [High].
- **Duplication:** near-duplicate pages and repeated boilerplate that would pollute the index.
- **Extraction quality:** is the main text in the HTML, not in images, PDFs only or JavaScript rendered content?
- **Access:** an `llms.txt`, a clean sitemap, crawler rules in robots.txt (see ai-search-readiness).

## Report
1. Scorecard table with evidence for each aspect.
2. A recommended ingestion plan: sources, chunking rule (for example split by H2 with heading path as context), metadata fields to store, and refresh strategy from `lastmod`.
3. The 5 content changes that would most improve answer quality.
4. **How to evaluate:** propose 20 real questions, expected source pages, and metrics (hit rate at k, answer faithfulness, citation accuracy).

## Pitfalls
- You judged readiness from a sample. Retrieval quality is decided by testing, not reading.
- Respect robots.txt and terms before ingesting any site.
