---
name: positioning-teardown
description: Assess a product's positioning from its site: competitive alternatives, unique attributes, value, target customer and market category, then judge clarity and write a sharper positioning statement. Use for "is our positioning clear", "how is X positioned".
category: Product management
version: 1
updated: 2026-09-21T00:00:00+00:00
---
# Positioning teardown

Uses the widely taught positioning components: competitive alternatives, unique attributes, value, target customer, and market category.

## Steps
1. `fetch_page` the homepage. Capture the H1, subheadline, first paragraph and the primary call to action exactly.
2. `fetch_page` one product or "why us" page and one customer story or pricing page (max 3 pages total).
3. Look for named competitors or "vs" language with `query_page` (selectors like `a[href*="vs"], a[href*="alternative"], a[href*="compare"]`).

## Extract each component (quote the page, then judge)
- **Competitive alternatives:** what the customer would do without this, including "do nothing" and spreadsheets. Named or implied?
- **Unique attributes:** capabilities the alternatives lack. Are they specific and checkable, or generic ("powerful", "seamless")?
- **Value:** the outcome those attributes create, and whether proof backs it (numbers, named customers).
- **Target customer:** who cares most. Is it explicit (role, size, situation) or "everyone"?
- **Market category:** the frame that tells buyers how to think about it (for example "project management tool" versus a new category). Does the category help or hurt?

## Clarity tests
- **5-second test:** from the H1 and subheadline alone, could a stranger say what it is, for whom, and why it is different?
- **Consistency:** do homepage, pricing and product pages tell the same story?
- **Differentiation:** could a competitor put their logo on the page and keep the copy? If yes, it is weak.

## Report
1. A table: component, what the site says (short quote), judgment (clear, vague, missing), evidence URL.
2. The top 3 positioning problems, ordered by how much they would confuse a buyer.
3. A rewritten positioning statement for the same product, using only claims the site already supports: "For [target], [product] is the [category] that [key value], unlike [alternative], because [unique attribute]."
4. Two experiments to test it (for example a homepage headline test, a sales-call script).

## Pitfalls
- Marketing copy is a claim, not proof of how buyers see the product. Say that positioning is validated by customer interviews and win-loss data, which you do not have.
- Do not invent competitors. Use only ones the site names or that the objective provides.
