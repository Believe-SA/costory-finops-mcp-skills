# Customer Foundation — Metrics

Cost columns and the derived formulas the skills compute. The cost columns are enumerated authoritatively in `query`; the derived formulas are currently re-derived in 4+ places (dashboards reference, and the `reallocate`, `budget-vs-actual`, `untagged-coverage` recipes). This file holds them once.

## Cost columns (`metricId` on a `type: "cost"` query)

| `metricId` | Meaning |
|------------|---------|
| `cost` | Default billed cost. |
| `effective_cost` | Cost after commitments/discounts are applied — what you actually pay. |
| `list_cost` | Public list price before any discount. |
| `contracted_cost` | On-demand / contracted cost before commitment savings are applied. |
| `unblended_cost` | Raw per-account cost, discounts unspread. |
| `net_unblended_cost` | `unblended_cost` net of credits/refunds. |
| `amortized_cost` | Upfront commitment fees spread across the term. |
| `net_amortized_cost` | `amortized_cost` net of credits/refunds. |

**Currency** defaults to `USD`; use the org currency from `get_context`. **Null labels** are CEL `null` — filter with `== null` / `!= null`, never `is_null` or the string `"null"`.

## Derived metrics (formulas over cost + usage/metric legs)

Each is a `formula` query referencing single-letter leg names (`a`, `b`, …). Keep the same `filterCel` / `groupBy` on every leg so scope and split stay aligned.

| Derived metric | Formula | Legs | Where used |
|----------------|---------|------|-----------|
| **Effective savings** | `a - b` | `a` = `contracted_cost`, `b` = `effective_cost` | `query` Workflow H |
| **Unit cost** (cost per X) | `a / b` | `a` = `cost`, `b` = a usage / saved / external metric | `query` Workflow E; dashboards unit-economics widget; `reallocate` validation |
| **Budget utilization** | `a / b` | `a` = `cost`, `b` = `budget` (same rolling window on both) | `query` Workflow F; `budget-vs-actual-dashboard` |
| **K8s waste ratio** | `b / a` | `a` = `k8s_cost`, `b` = `k8s_waste` (usage metrics) | `query` Workflow G |
| **Tag / allocation coverage** | `a / b` | `a` = cost where the tag is present, `b` = in-scope cost | `untagged-coverage` |

### Notes that travel with these formulas

- **Coverage is a ratio, not a dollar amount.** Do not include structurally un-taggable spend in the denominator without calling it out — it permanently caps the ratio below 100%.
- **Effective savings** ≈ what commitments (Savings Plans / RIs / CUDs) save you: `contracted_cost − effective_cost`. This is how the *Commitment* entity surfaces (see `entities.md`) — a derived metric, not a raw dimension.
- **Utilization / cumulated-vs-budget** views use `rollingAggregation` with the **same** window preset on both the cost and budget legs so each day shows a running total within the period.
- **Credit lines are negative.** A "credits received" total is signed; only take the absolute value when the user wants positive magnitude, and say so.

## Related

- Entity definitions and canonical CEL fields → [`entities.md`](./entities.md).
- Full `query` workflows with worked JSON → `plugins/costory/skills/query/SKILL.md`.
