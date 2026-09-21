# Web Analyst: product brief

A product case study for the Web Analyst Agent. It covers the problem, the decisions behind the design, and how the interface was tested for accessibility. Numbers in the "Measured" sections come from runs of the scripts in this repo. Numbers under "Proposed metrics" are targets, not results.

## The problem

Analysts and marketers repeat the same website checks all the time: SEO, security headers, pricing, accessibility, competitor positioning. Existing tools split into two groups. Audit products run a fixed checklist and cannot answer a specific question. General AI chat can answer a question, but it often invents details about a page it never opened.

**Who it is for:** a product manager, marketer or founder who has a link and a question, and wants an answer they can check.

**Job to be done:** "Look at this site and tell me what matters for my goal, and show me where you saw it."

## Product principles

1. **Evidence over fluency.** Every finding has to cite what was observed. The agent refuses to write a report before it has fetched the page.
2. **The user stays in control.** Choose skills or let the agent choose, stop a run, turn off skill writing, see every step.
3. **Say what you cannot see.** The tool reads server-delivered HTML and headers, not JavaScript. Reports state that limit.
4. **Free to run.** The default setup uses free models with automatic backups.

## Key decisions

| Decision | Why | Trade-off accepted |
|---|---|---|
| Skills are Markdown playbooks, not code | Reusable and reviewable by a non-engineer, and nothing the model writes is executed, so no sandbox is needed | Skills cannot run custom logic |
| Objective first, skills second | Users think in goals ("why is this not ranking"), not tools | The agent must choose well, so users can override with a skill picker |
| Chosen skills are sent to the model in full | Saves model requests, which matters on free tiers | Longer first message |
| Fetcher blocks private networks and honors robots.txt | A tool that fetches URLs for users must not become a way into internal systems | Some sites cannot be analyzed |
| Static HTML only, no browser rendering in v1 | Keeps it fast, cheap and predictable | Client-rendered pages come back thin, and the report says so |
| Perspectives: one site, five lenses (PM, SEO, front end, back end, AI) | The person who asks decides what a good answer is. A PM wants hypotheses and metrics, an engineer wants a fix and a snippet | More content to maintain. A shared skill can be framed differently by each lens |
| Stop button and step-by-step log | Runs cost quota and take up to a minute or more | Extra interface to build and test |

## Perspectives

**Problem.** One generic report serves nobody well. A product manager needs the user and the hypothesis. An SEO analyst needs the exact title rewrite. A back end engineer needs the header value. Sending all of them the same audit means each has to translate it.

**Design.** A perspective is a data file with three parts: a lens (how to frame findings and what to leave out), the skills that fit the role, and example objectives. Choosing one changes the report's framing, narrows the skill catalog the model reads (which also keeps the prompt small on free models), reorders the skill picker to show that role's skills first, and swaps the example prompts.

**What ships.** Five perspectives and 50 skills: 13 for product management, and new skills for SEO (4), front end (4), back end (5) and AI engineering (5). Adding a role is adding one JSON file, and a test checks that every listed skill exists.

**Checked.** The same run configuration produced clearly different reports: a front end report with severity, selectors, counts and before and after markup; a back end report that found a Swagger 2.0 spec and flagged that it could only read part of it; an AI engineering report that separated three AI features by job, grounding and controls.

**Found while testing.** A front end run failed because the model followed a 20-selector checklist one selector per call and ran out of turns. The fix was in the product: `query_page` now takes several selectors per call, the agent gets an earlier wrap-up warning, and a cut-off final reply gets a second chance. The rerun finished in 7 requests.

## UX and accessibility

**Method.** I audited the interface with axe-core, the engine behind most accessibility checkers, driven through Chrome. It covers 8 states: home, skill picker open, finished run with report, skill preview dialog, each in light and dark themes where relevant, plus a 375px phone layout. I then added manual checks: contrast ratios computed for every color pair, tap-target sizes, and a reading of the keyboard and screen-reader flow.

**Measured, before and after the redesign**

| Check | Before | After |
|---|---|---|
| axe-core violations across 8 states | 11 | 0 |
| Border contrast of inputs and buttons (needs 3:1) | 2.2:1 | 3.7:1 to 4.2:1 in light, 4.4:1 to 4.9:1 in dark |
| Layout at 375px wide | scrolled sideways | fits |
| Interactive targets my size check flagged as under 24px (WCAG 2.2) | 40 or more | 0 |
| Progress readable without color | no | yes (check marks and hidden state text) |

**What changed and why**

- **Skip link, landmarks, proper heading order.** Keyboard and screen-reader users can jump to the form and move by section.
- **Progress is announced.** A polite live region says when a run starts, which page is being fetched, and when the report is ready. The full activity log is not live, to avoid noise.
- **Errors sit next to the field.** Each field has a message, the field is marked invalid, and focus moves to the first problem. Server errors map back to fields.
- **Stage tracker uses shape and text,** not only color. Each stage exposes its state ("done", "in progress") to assistive technology.
- **Type is sized in rem with a 12px floor,** so browser font-size settings work.
- **Choices remembered.** Draft text and skill picks survive a reload. The theme can be set to System, Light or Dark.
- **Control over long tasks.** A Stop button ends a run after its current step, since a slow run should not be a trap.
- **Other:** reduced-motion support, print styles that show only the report, forced-colors support, a focused dialog with a labelled close button.

**Not done yet.** No test with a real screen reader (VoiceOver, NVDA), no test with real users, and automated tools find only part of the problems. These are the next steps before claiming the interface is accessible.

## Model selection

Free models vary a lot. I wrote a benchmark (`scripts/rank_models.py`) that gives each model the same two probes taken from this product's real workload: call the fetch tool correctly given a chosen skill, and write a report grounded in real fetched data.

**Measured.** 18 candidates. 8 passed both probes fully, 4 could call tools but never stopped calling them to write a report, 2 refused outside their own harness, 1 had no provider that supports the tool setting, 3 were rate limited on every attempt and could not be judged. The final list mixes vendors inside each chain of three, so one outage cannot take a chain down, and puts a router model last as a safety net. Results are a snapshot from one sample each, so the script exists to re-run when quality drops.

## Proposed metrics (not yet measured)

- Share of runs that end with a report (target above 90 percent).
- Share of report findings that cite an observed value (target 100 percent, checkable automatically).
- Median time to a report (target under 60 seconds on the fastest models).
- Share of users who choose skills versus letting the agent choose.

## Risks

- **Prompt injection from analyzed pages.** Page content is marked as untrusted and the agent is told to report attempts, not follow them. Not yet tested against a wide set of hostile pages.
- **Free tier changes.** Model lists and limits shift often, so the model list is discovered live and the fallback API is configurable.
- **Skill quality.** A poor skill shapes every later run. Skills are visible, previewable and deletable, and skill writing can be turned off.

## Next

1. Screen reader pass and five user sessions with people who use assistive technology.
2. Automatic evidence check on every report (does each finding quote a fetched value).
3. Browser rendering for client-side sites, behind an option.
4. Compare two runs of the same site over time.
