---
name: recommendations
description: "Use when the user wants savings recommendations, an action plan, estimated savings, or a prioritized \"what should we do\" list — rightsizing, commitment/Savings-Plan coverage, waste reduction, tagging fixes, anomaly follow-ups. Costory's MCP has no dedicated recommendation engine, so recommendations are DERIVED analytically from query (effective savings, K8s waste, coverage) and grounded in observed figures — never invented. suggest_actions provides UI next-steps only. Call get_skill with skillId \"recommendations\" before producing a recommendation or savings estimate."
---

# Recommendations

Turn Costory cost data into a **prioritized, quantified action plan**: what to change, how much it saves, and why. Costory's MCP has **no dedicated recommendation/rightsizing engine** — so recommendations are **derived analytically** from the query surface and grounded in observed numbers. Never fabricate a saving; every estimate must trace to a figure you pulled from `query`.

`suggest_actions` is a **UI next-step** helper (save a view, set an alert, share, drill, compare) — it is *not* a FinOps savings feed. Use it to offer follow-ups, not as the source of a recommendation.

**Load this skill first** for savings recommendations, action plans, estimated savings, or prioritization.

## When to Trigger

- "What should we do to cut cost?" / "give me an action plan"
- "How much could we save on commitments / rightsizing / waste?"
- "Prioritize these opportunities" / "explain this recommendation"
- After an investigation, to convert findings into ranked actions

## Recommendation classes (and the analysis each is derived from)

| Class | Derived from | Estimated saving |
|-------|--------------|------------------|
| **Commitment coverage** (Savings Plans / RIs / CUDs) | `query` Workflow H — `contracted_cost` vs `effective_cost` | uncovered on-demand spend × expected commitment discount |
| **Rightsizing / idle** | `query` usage vs cost (`suggest_usage_metrics`), low-utilization scopes | cost of over-provisioned / idle capacity |
| **K8s waste** | `query` Workflow G — `k8s_waste` / `k8s_cost` (waste ratio) | waste spend recoverable by right-requesting |
| **Tagging / allocation** | `recipes` → `untagged-coverage` — coverage ratio | not $ savings — unlocks accountability; rank by unallocated $ |
| **Anomaly follow-up** | `alerts` fire / DIGEST mover | the recurring excess vs baseline |

## Tool order

1. `get_skill` with `skillId: "recommendations"` — this guide
2. `get_context` — currency, popular groupBys
3. `query` — the analysis backing each candidate (H for savings, G for waste, usage for idle); never skip — this is where the numbers come from
4. `list_events` — check whether a movement has a known cause before recommending action
5. `suggest_actions` — offer UI next-steps once recommendations are presented

## Workflow — derive, quantify, prioritize, explain

1. **Scope** the question (whole org, a team/scope, a service) as `filterCel`
2. **Derive candidates** — run the backing `query` for each relevant class above; keep only opportunities with a real, observed gap
3. **Quantify** each: estimated saving from the observed figures (see `query` Workflow H — `contracted_cost` − `effective_cost`, and Workflow G — `k8s_waste` / `k8s_cost`). State the basis period and that it is an **estimate**
4. **Prioritize** — rank by `estimatedSaving × confidence ÷ effort`. Lead with the biggest, most confident, lowest-effort wins
5. **Explain** each recommendation: the evidence (the number and where it came from), the action, the estimated impact, and the risk/effort
6. Offer to operationalize: a standing `alerts` monitor, an `events` annotation when acted on, a tracking dashboard/report

**Example — effective-savings opportunity (commitment coverage):**

```json
{
  "queries": [
    { "type": "cost", "name": "a", "alias": "Contracted (on-demand)", "metricId": "contracted_cost", "currency": "USD" },
    { "type": "cost", "name": "b", "alias": "Effective (paid)", "metricId": "effective_cost", "currency": "USD" },
    { "type": "formula", "name": "c", "alias": "Already saved via commitments", "formula": "a - b" }
  ],
  "datePreset": "LAST_MONTH",
  "aggBy": "Month"
}
```

Read `a` (what uncommitted on-demand would cost), `b` (what you pay), and `c` (savings already captured). Remaining on-demand in `a` that is steady-state is the **candidate** for more commitment coverage — estimate the incremental saving at the provider's SP/CUD discount rate and say it is an estimate.

## Presenting a recommendation

Each item, most-impactful first:

- **Action** — one concrete sentence.
- **Estimated saving** — money + currency + period, with the basis (e.g. "≈ $4.2k/mo, from last month's idle EC2").
- **Evidence** — the observed figure and its source query. No figure ⇒ no recommendation.
- **Effort / risk** — rightsizing needs validation; commitments are a lock-in; waste fixes touch requests.
- **Confidence** — high when the gap is large and stable; low when spiky.

## Safety Rules / Anti-patterns

- Do not invent a savings number — every estimate traces to an observed `query` figure; say "estimate" and give the basis period
- Do not treat `suggest_actions` output as savings recommendations — it is UI next-steps
- Do not recommend a commitment purchase off one spiky period — check stability over a trailing window first
- Do not present tagging coverage as dollar savings — it unlocks accountability; rank by unallocated $ instead
- Do not claim a Costory rightsizing/Savings-Plan *engine* exists — recommendations here are analyst-derived from the data
- Do not recommend action on a movement with a known benign cause without checking `list_events` first

## Related Skills / Next Steps

- `query` — Workflow H (effective savings), Workflow G (K8s waste), usage-vs-cost (idle) — the evidence for every recommendation
- `recipes` → `untagged-coverage` — the allocation-coverage input
- `alerts` — make an accepted recommendation self-monitoring
- `events` — annotate when a recommendation is acted on, to track its effect
- `playbooks` → `spend-spike-triage` — recommendations are the "estimate savings" step of the flagship loop
