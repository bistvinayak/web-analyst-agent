---
name: prd-and-spec-review
description: Review a public product requirements doc, spec, RFC or product write-up for completeness: problem, users, goals and non-goals, metrics, requirements, risks and open questions. Use for "critique this PRD", "review this spec".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# PRD and spec review

## Steps
1. `fetch_page` the document URL. If the text excerpt is nearly empty, the document is likely behind a login or built by JavaScript. Say so and stop, since you cannot review what you cannot read.
2. Use `query_page` with `h1, h2, h3` to list the section outline. Use `fetch_raw` with a larger `max_chars` to read the body when the excerpt is too short.
3. Read the whole document before judging any single section.

## Checklist (rate each as strong, adequate, weak or missing, with a quote)
- **Problem and evidence:** is the problem stated with data, user quotes or a clear cause, not just a solution?
- **Users and context:** who, in what situation, and how many are affected?
- **Goals and non-goals:** explicit goals, and explicit exclusions that prevent scope creep.
- **Success metrics:** a primary metric with a baseline, a target and a time frame, plus a guard metric. Leading versus lagging indicators.
- **Requirements:** testable statements, prioritized (must, should, could), free of solution bias where possible.
- **Scope and phasing:** an MVP boundary and what comes later.
- **Dependencies and risks:** technical, legal, data, people. Mitigations named.
- **Assumptions and open questions:** listed with owners or how they will be resolved.
- **Rollout and learning:** launch plan, experiment or staged rollout, and how results will be reviewed.
- **Clarity:** a stranger can explain the goal after one read; terms defined.

## Report
1. A scorecard table: item, rating, evidence quote.
2. The 3 most important gaps in order of risk, each with a concrete fix or an example sentence.
3. Questions the author must answer before build starts.
4. A rewritten one-paragraph summary of the document using only what it states.

## Pitfalls
- Judge the document as written. Do not assume missing sections exist elsewhere without saying you could not see them.
- Do not comment on the quality of the idea, only how well the document supports a decision.
- Private documents cannot be read. Never ask for credentials.
