---
name: unit-economics
description: "Use for cost-per-unit / unit economics — cost per request, per GB, per delivery, per customer, per token. Build a cost leg (a) + a usage / saved-metric / external-metric leg (b) + formula c = \"a / b\", grounded in query Workflow E. Covers saved metric vs live external (Tsuga / BigQuery) driver, and the decision between a KPI-only ratio and reallocating shared spend (→ recipes reallocate-by-external-metric / virtual-dimensions telemetry). Both legs must share scope + period; the unit must be a real business driver; never fabricate a figure. Call get_skill with skillId \"unit-economics\" before non-trivial cost-per-unit work."
---

# Unit economics

**Cost per unit of business value** — cost per request, per GB, per delivery, per customer, per token. The method is a two-leg ratio: a **cost** leg `a`, a **unit** leg `b` (a saved metric, an infra usage metric, or a live external metric), and a **formula** leg `c = "a / b"`. This is the dedicated home of `query` **Workflow E**; it stays self-contained so the ratio is built the same way every time.

Every figure comes from `query` — both the cost and the unit count. **Never fabricate** a numerator or a denominator.

**Load this skill first** for "what's our cost per X?", efficiency-at-scale tracking, or a cost-per-driver KPI.

## When to Trigger

- "What's our cost per request / per GB / per delivery / per customer / per token?"
- "Is unit cost improving as we scale?" (cost flat or down while volume rises)
- Cost per business driver for a team / product / feature
- Pricing / margin input: cost side of a per-unit economics model

**Hand off instead of this skill:**

- *"Fairly split the shared platform bill across teams by usage"* → this is **reallocation**, not a KPI → `recipes` → `reallocate-by-external-metric` (backed by a `virtual-dimensions` telemetry allocation).
- *"Why did the bill jump?"* → `recipes` → `explain-period-change`.

## The method (query Workflow E)

Three legs, one query. `a` is cost, `b` is the unit, `c` divides them.

| Leg | `type` | Discover the id with |
|-----|--------|----------------------|
| `a` cost | `cost` | — (`metricId: "cost"`, default) |
| `b` unit — saved business metric | `metric` | `list_metrics` `{}` → `id` |
| `b` unit — infra usage (CPU hours, GB, …) | `usage` | `suggest_usage_metrics` with a specific `filterCel` |
| `b` unit — live external (Tsuga / BigQuery) | `externalMetric` | `list_metrics` `{ includeExternal: true, search: "…" }` |
| `c` cost per unit | `formula` | `formula: "a / b"` |

### Tool order

1. `get_skill` with `skillId: "unit-economics"` — this guide
2. `get_context` — currency, integrations
3. Resolve the unit id (`list_metrics`, `suggest_usage_metrics`, or `list_metrics includeExternal`)
4. `query` — cost `a` + unit `b` + formula `c`
5. Persist / deliver via `dashboards` / `reports`

**Saved metric (preferred when one exists):**

```json
{
  "queries": [
    { "type": "cost", "name": "a", "metricId": "cost", "currency": "USD" },
    { "type": "metric", "name": "b", "metricId": "<metric-id>" },
    { "type": "formula", "name": "c", "alias": "Cost per unit", "formula": "a / b" }
  ],
  "datePreset": "TRAILING_30_DAYS",
  "aggBy": "Week"
}
```

Swap leg `b` for `{ "type": "usage", "metricId": "<usage-id>" }` (per-GB, per-CPU-hour) after `suggest_usage_metrics`.

## Saved metric vs live external metric

| Source | Leg `b` | When |
|--------|---------|------|
| **Saved Costory metric** | `type: "metric"` | A synced business metric already exists — **prefer this** |
| **Infra usage** | `type: "usage"` | Per-GB / per-CPU-hour / per-byte, scoped by `filterCel` |
| **Live external (Tsuga / BigQuery)** | `type: "externalMetric"` | Exploring a driver not yet saved as a Costory metric |

**Live external — Tsuga** (after `list_metrics` with `includeExternal: true`, `search: "request"`):

```json
{
  "queries": [
    { "type": "cost", "name": "a", "metricId": "cost", "currency": "USD" },
    { "type": "externalMetric", "name": "b", "provider": "tsuga",
      "integrationId": "<integration-id>", "metricName": "<metric-name>", "aggregator": "SUM" },
    { "type": "formula", "name": "c", "alias": "Cost per request", "formula": "a / b" }
  ],
  "datePreset": "TRAILING_30_DAYS",
  "aggBy": "Week"
}
```

**BigQuery** — same shape with `provider: "bigquery"`, `metricName` = `project.dataset.table`, plus `dateColumn`, `metricColumn`, `gapFillingMethod`. See `query` Workflow E for the full external payloads.

A live external metric is fine to **validate** a driver in Explorer, but it **cannot back a telemetry reallocation** — save it as a Costory metric first (see the reallocation hand-off below).

## KPI ratio vs reallocating shared cost

The most common wrong turn. Decide up front:

| Goal | Do this |
|------|---------|
| Track a **ratio** (cost per unit) as a KPI, trend, dashboard, or report | **Stay here** — formula `c = a / b`, then persist |
| **Fairly split** a shared bill across teams / products / customers **by** the driver | **Hand off** → `recipes` → `reallocate-by-external-metric` → `virtual-dimensions` **telemetry** allocation |

A ratio answers "how efficient are we?"; a reallocation reassigns real dollars proportionally so each owner sees their fair share. If the ask is showback / chargeback of shared spend, the ratio alone is not the deliverable — the telemetry VDIM is.

## Persist / deliver

- `dashboards` — pin the cost-per-unit widget (cost, unit, and the `a / b` formula series) for a standing efficiency view
- `reports` — scheduled delivery of the ratio (weekly / monthly), or an Explain (DIGEST) narrative around it

## Safety Rules / Anti-patterns

- **Both legs, same scope and period.** Use the same `filterCel` and the same period + `aggBy` on `a` and `b` — a ratio built from mismatched scopes or windows is meaningless
- **Never fabricate** a cost or a unit count — both legs come from `query`; if the denominator isn't measured, say so rather than estimate it
- **The unit must be a real business driver** — a saved metric, a real usage metric, or a real external metric. Do not invent a denominator or hard-code a volume
- Prefer saved `type: "metric"` over `externalMetric` when a saved metric already exists
- A live external metric can validate the driver but **cannot** back a telemetry reallocation — save it as a Costory metric first
- Watch near-zero denominators early in a period (data lag ~2 days): a cost-per-unit spike is often missing volume, not runaway cost — read the raw legs before concluding
- Use only the valid `DatePreset` tokens (see `query`) — if none matches, use explicit `from` / `to`; do not invent a preset

## Related Skills / Next Steps

- `query` — Workflow E (unit economics) is this method; Workflow D pairs usage alongside cost
- `recipes` → `reallocate-by-external-metric` — when the ratio should drive a proportional shared-cost split
- `virtual-dimensions` — the `telemetry` allocation that backs that split
- `dashboards` — persist the cost-per-unit widget
- `reports` — scheduled cost-per-unit delivery
