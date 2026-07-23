---
name: optimization
description: "Use for the ANALYTICAL METHOD behind a specific cost-reduction lever: rightsizing / idle detection (cost vs usage), commitment coverage sizing (contracted vs effective, break-even), and waste elimination (K8s requests vs usage). This is the how-to-compute-the-opportunity companion to recommendations (which ranks and presents the plan). Every opportunity is sized from observed query figures — never invented. Call get_skill with skillId \"optimization\" when digging into how to find and size a saving on one lever."
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
| **Commitment coverage** | large steady on-demand not covered by SP/RI/CUD | `query` H: `contracted_cost` vs `effective_cost` | uncovered steady-state on-demand × expected discount rate |
| **Waste (K8s)** | requested ≫ used | `query` G: `k8s_waste` / `k8s_cost` by namespace/cluster | waste spend recoverable by right-requesting |
| **Discount / credit runway** | shrinking credit line | `recipes` → `provider-credits` (`cos_charge_category`) | not a saving — a runway risk to plan for |

## Tool order

1. `get_skill` with `skillId: "optimization"` — this guide
2. `get_context` — currency
3. `query` — the lever's method below (this is where every number comes from)
4. `suggest_usage_metrics` / `suggest_groupby` — to scope usage or find the axis
5. Hand the sized opportunities to `recommendations` to rank and present

## Method — Rightsizing / idle

1. Scope to the resource class (`filterCel`, e.g. a service or instance family)
2. `suggest_usage_metrics` for that scope → pull cost + the usage metric together (`query` Workflow D)
3. Look for **sustained** low utilization over a trailing window (not one quiet day) — spiky scopes are not rightsizing candidates
4. Size: the cost of capacity above a right-sized target. State the assumption (target utilization) and that validation is required before acting

## Method — Commitment coverage sizing

1. `query` H — `contracted_cost` (a), `effective_cost` (b), `a - b` (already-captured savings)
2. The remaining on-demand in `a` that is **steady over a trailing window** is the coverage candidate — verify stability first (a spike is not a commitment case)
3. Size incremental saving = steady uncovered on-demand × the provider's expected SP/RI/CUD discount. State it is an estimate; note the lock-in trade-off and that utilization below the break-even erodes the saving

## Method — Waste elimination (K8s)

1. `query` G — `k8s_waste` and `k8s_cost` (usage metrics), `groupBy: cos_namespace_reallocated` or `cos_cluster_name`
2. Rank namespaces/clusters by waste ratio and absolute waste $
3. Size: recoverable = waste $ of the worst offenders that right-requesting can reclaim; validate against real usage before changing requests

## Safety Rules / Anti-patterns

- Do not size a saving from a single period — require sustained/steady behavior over a trailing window
- Do not invent a number — every estimate traces to an observed `query` figure; say "estimate" + basis period
- Do not recommend rightsizing without noting it needs validation, or commitments without the lock-in / break-even caveat
- Stay in your lane vs `recommendations`: this skill is the deep-dive **sizing method** for one lever; ranking, presentation, and operationalization live there (`recommendations` also sizes at summary level)
- Do not treat credit runway as a saving — it is a risk to plan for, not money to cut

## Related Skills / Next Steps

- `query` — Workflows D (usage), G (K8s waste), H (effective savings) are the methods above
- `recommendations` — hands the sized opportunities into a ranked, explained plan
- `governance` — commitment-coverage and budget targets that make these levers policy
- `recipes` → `provider-credits` — the discount/credit-runway view
