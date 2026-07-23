---
name: optimization
description: "Use for the ANALYTICAL METHOD behind a specific cost-reduction lever: rightsizing / idle detection (cost vs usage), rate & commitment optimization (RI/SP/CUD coverage %, effective vs list rate, break-even utilization, laddering, amortized cost), and waste elimination (K8s requests vs usage). This is the how-to-compute-the-opportunity companion to recommendations (which ranks and presents the plan). Every opportunity is sized from observed query figures — never invented. Call get_skill with skillId \"optimization\" when digging into how to find and size a saving on one lever."
---

# Optimization

The **analytical methods** for finding and sizing cost-reduction opportunities, lever by lever. This is the *how do I actually compute this saving?* companion to `recommendations` (which ranks, presents, and operationalizes the plan). Split of duties:

- **`optimization`** (here) — the method + sizing per lever, from `query` data.
- **`recommendations`** — the action-plan entry point; it also sizes opportunities at summary level, then prioritizes, explains, and operationalizes. `optimization` (here) is the deep-dive sizing *method* for one lever.
- **`governance`** — set the coverage/commitment targets. **`forecast`** — project pace.

Every opportunity is **sized from observed `query` figures**, stated as an estimate with its basis period. Never invent a saving.

**Load this skill first** when digging into *how* to find and quantify a saving on one lever.

## Levers

| Lever | Signal | `query` method | Size the opportunity |
|-------|--------|----------------|----------------------|
| **Rightsizing / idle** | cost with little/no matching usage, sustained | cost + usage on the same scope (`suggest_usage_metrics`), trailing window | cost of the over-provisioned/idle portion vs a right-sized target |
| **Rate & commitment** | low effective discount and/or large steady on-demand not under SP/RI/CUD | `query` H (`contracted_cost` vs `effective_cost`) + `list_cost` vs `effective_cost` rate; `amortized_cost` for term fees | uncovered steady-state baseline × expected SP/RI/CUD discount |
| **Waste (K8s)** | requested ≫ used | `query` G: `k8s_waste` / `k8s_cost` by namespace/cluster | waste spend recoverable by right-requesting |
| **Discount / credit runway** | shrinking credit line | `recipes` → `provider-credits` (`cos_charge_category`) | not a saving — a runway risk to plan for |

## Tool order

1. `get_skill` with `skillId: "optimization"` — this guide
2. `get_context` — currency
3. `query` — the lever's method below (this is where every number comes from)
4. `suggest_usage_metrics` / `suggest_groupby` — to scope usage or find the axis; `search` `type: ["dimensions"]` to resolve the commitment / charge split field (org-specific)
5. Hand the sized opportunities to `recommendations` to rank and present

## Method — Rightsizing / idle

1. Scope to the resource class (`filterCel`, e.g. a service or instance family)
2. `suggest_usage_metrics` for that scope → pull cost + the usage metric together (`query` Workflow D)
3. Look for **sustained** low utilization over a trailing window (not one quiet day) — spiky scopes are not rightsizing candidates
4. Size: the cost of capacity above a right-sized target. State the assumption (target utilization) and that validation is required before acting

## Method — Rate & Commitment Optimization

Two questions on one lever: **rate** — are we paying the best price for what we run? — and **commitment** — is enough steady-state usage under RI/SP/CUD? Both are read from the `query` cost columns; none is invented.

### RI/SP/CUD coverage %

1. Coverage % = covered eligible spend ÷ total eligible spend over a trailing window.
2. Costory has **no dedicated coverage column** — split eligible spend by the commitment / pricing dimension: discover the real field with `search` `type: ["dimensions"]` (keywords `commitment`, `savings plan`, `on demand`, `charge`); the label is **org-specific — resolve it, never hardcode**. Then `groupBy` that field and read covered vs on-demand.
3. Compare to the target `governance` owns (it sets the coverage SLO). If no such split is exposed, fall back to the rate metrics below as the coverage proxy and say true coverage % needs the provider console.

### Effective vs list rate

- `list_cost` = public on-demand list price for the same usage; `effective_cost` = what you actually pay after commitments + negotiated discounts.
- **Blended discount = `1 − effective_cost / list_cost`** (formula `b / a` on the two legs) — the realized rate, all discounts folded in.
- `contracted_cost − effective_cost` (`query` Workflow H) is the savings **already captured by commitments specifically** — a narrower figure than the blended discount.

**Example — effective rate + already-captured savings, last month:**

```json
{
  "queries": [
    { "type": "cost", "name": "a", "alias": "List (on-demand)", "metricId": "list_cost", "currency": "USD" },
    { "type": "cost", "name": "b", "alias": "Effective (paid)", "metricId": "effective_cost", "currency": "USD" },
    { "type": "cost", "name": "c", "alias": "Contracted", "metricId": "contracted_cost", "currency": "USD" },
    { "type": "formula", "name": "d", "alias": "Effective rate", "formula": "b / a" },
    { "type": "formula", "name": "e", "alias": "Captured by commitments", "formula": "c - b" }
  ],
  "datePreset": "LAST_MONTH",
  "aggBy": "Month"
}
```

### Break-even / utilization threshold

- A commitment bills its committed rate for the **whole term** whether or not you use it; on-demand bills list only while running. So **break-even utilization ≈ the effective rate = `effective_cost / list_cost`** at the committed rate.
- Read it as: if the committed effective rate is 65% of list, the resource must run **≥ 65% of the term** for the commitment to beat on-demand; below that threshold the commitment loses money.
- Size the coverable baseline as the **steady-state minimum** (the trough) over a trailing window — not the peak, not the average. Only baseline that clears break-even utilization is a safe commitment.

### Laddering

- Cover the proven baseline now, then add commitment in **staggered tranches with staggered expiries** as the baseline holds — not one large purchase. Laddering tracks a growing baseline, avoids an expiry cliff, and caps over-commit risk if usage drops.

### amortized_cost — measure the rate correctly

- `unblended_cost` lumps upfront RI/SP fees on the purchase day, distorting any rate / effective-cost read over a window that contains a purchase. Use `amortized_cost` (or `net_amortized_cost` after credits) to spread that fee across the term so the effective rate and per-period cost are true.

### Size it

Incremental saving = steady uncovered on-demand baseline × the provider's expected SP/RI/CUD discount. State it is an **estimate**, name the basis period, note the lock-in trade-off, and flag that utilization below break-even erodes the saving. Hand the sized opportunity to `recommendations`.

## Method — Waste elimination (K8s)

1. `query` G — `k8s_waste` and `k8s_cost` (usage metrics), `groupBy: cos_namespace_reallocated` or `cos_cluster_name`
2. Rank namespaces/clusters by waste ratio and absolute waste $
3. Size: recoverable = waste $ of the worst offenders that right-requesting can reclaim; validate against real usage before changing requests

## Safety Rules / Anti-patterns

- Do not size a saving from a single period — require sustained/steady behavior over a trailing window; commit only the steady-state trough, not the peak or average
- Do not invent a number — every estimate traces to an observed `query` figure; say "estimate" + basis period
- Do not invent a coverage column — Costory has none; split by the `search`-discovered commitment/charge field (org-specific) or report the rate metrics as the proxy
- Do not recommend rightsizing without noting it needs validation, or a commitment without the lock-in / break-even caveat (usage below break-even utilization loses money)
- Do not read the effective rate over a window containing a purchase from `unblended_cost` — use `amortized_cost` so the upfront fee is spread across the term
- Prefer laddered tranches over one large commitment when the baseline is still growing
- Stay in your lane vs `recommendations`: this skill is the deep-dive **sizing method** for one lever; ranking, presentation, and operationalization live there (`recommendations` also sizes at summary level). The coverage **target** is `governance`'s to set
- Do not treat credit runway as a saving — it is a risk to plan for, not money to cut

## Related Skills / Next Steps

- `query` — Workflows D (usage), G (K8s waste), H (effective savings, `contracted_cost` vs `effective_cost`); the rate read (`list_cost` vs `effective_cost`, `amortized_cost`) uses the same cost columns
- `recommendations` — hands the sized opportunities into a ranked, explained plan
- `governance` — commitment-coverage and budget **targets** that make these levers policy (owns the coverage SLO)
- `recipes` → `provider-credits` — the discount/credit-runway view
