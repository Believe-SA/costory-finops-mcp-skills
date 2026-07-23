---
name: forecast
description: "Use when the user asks whether they are on pace to overspend, what month-end / period-end spend will be, or to project a cost trend. IMPORTANT: the Costory MCP exposes NO statistical/ML forecast tool — this skill does honest run-rate / budget-pace projection from query actuals (MTD rolling vs budget) and flags cost regressions via alerts. For true statistical forecasting, point the user to Costory's in-product forecast feature. Never fabricate a projected number beyond arithmetic you can show. Call get_skill with skillId \"forecast\" before projecting spend."
---

# Forecast

Project where spend is heading. **Read this first:** the Costory **MCP surface has no statistical/ML forecast tool** — so this skill does **run-rate / pace projection** from actuals (arithmetic you can show), plus regression detection via `alerts`. Costory's *product* has a forecasting feature; for a real statistical forecast, point the user there. **Never fabricate a projected figure** beyond simple run-rate math whose inputs you pulled from `query`.

This is the honest boundary of Forecasting on the MCP today (a known product-vs-MCP gap; see [`../../knowledge/customer-foundation/entities.md`](../../knowledge/customer-foundation/entities.md) → Forecast).

**Load this skill first** for "are we on pace?", "what will we spend this month?", or "project this trend".

## When to Trigger

- "Are we on pace to blow the budget this month?"
- "What will month-end / quarter-end spend be at this rate?"
- "Project the cost trend for \<scope\>"
- "Warn me if spend is trending up" → regression detection

## What this skill can and cannot do

| Ask | MCP answer | How |
|-----|-----------|-----|
| On pace vs budget this month? | ✅ run-rate | `query` MTD cost (rolling) vs budget → linear projection to period end |
| Period-end spend at current rate? | ✅ run-rate | MTD/actuals ÷ elapsed × total days — **state it is linear run-rate** |
| Statistical / seasonal forecast with a band | ❌ not on MCP | point to Costory's in-product **Forecasting with TimesFM** (on budgets); do not invent a curve |
| Is spend regressing (trending up)? | ✅ | `alerts` WoW/DoD spike condition (DetectCostRegression) |

## Tool order

1. `get_skill` with `skillId: "forecast"` — this guide
2. `get_context` — currency, budgets
3. `query` — the actuals the projection is built from (never skip; the numbers must be real)
4. `search` `type: ["budgets"]` → `get` → `budgetVersionId` when projecting against a budget
5. Hand off to `alerts` for standing regression detection

## Workflow A — Month-end budget-pace projection

Answers "are we on pace?". Uses `query` Workflow F shapes — a linear run-rate, stated as such.

1. Resolve the budget (`search` → `get` → `budgetVersionId`)
2. `query` MTD cost with a monthly rolling window + the budget leg (same window)
3. Project: `run_rate_month_end = MTD_cost ÷ days_elapsed × days_in_month`. Compare to budget. **Say it is a linear run-rate that ignores seasonality and known one-offs.**

```json
{
  "queries": [
    { "type": "cost", "name": "a", "alias": "MTD cost", "metricId": "cost", "currency": "USD",
      "rollingAggregation": { "aggregator": "SUM", "window": { "preset": "MONTH" } } },
    { "type": "budget", "name": "b", "alias": "MTD budget", "budgetId": "<budgetVersionId>",
      "rollingAggregation": { "aggregator": "SUM", "window": { "preset": "MONTH" } } }
  ],
  "datePreset": "MTD",
  "aggBy": "Day"
}
```

Read the latest `a` (MTD actual) and days elapsed to compute the run-rate; compare with the budget `b`. Present the projection with its assumption stated.

## Workflow B — Trend read (no fabricated numbers)

For "where is this heading?": `query` a Week/Month time series over a trailing window and **describe the direction and slope in words** grounded in the returned points. Do **not** invent a regression equation or a specific future value beyond a run-rate you can show. If they need a real forecast curve, point to the product's forecast feature.

```json
{
  "queries": [{ "type": "cost", "name": "a", "metricId": "cost", "currency": "USD", "chartType": "LINE" }],
  "datePreset": "TRAILING_14_WEEKS",
  "aggBy": "Week"
}
```

## Workflow C — Regression detection (hand off to alerts)

For "warn me if spend trends up", this is a standing monitor, not a one-shot projection → `alerts` with a WoW/DoD spike condition (e.g. `rollingSum(a, 7, DAY) > timeShift(rollingSum(a, 7, DAY), 7, DAY) * 1.1`).

## Safety Rules / Anti-patterns

- Do not present a statistical/ML forecast — the MCP has none; only run-rate arithmetic you can show
- Do not state a projected number without its **inputs** (from `query`) and its **assumption** ("linear run-rate, ignores seasonality/one-offs")
- Do not extrapolate off a partial early-month window without noting data lag (~2 days) skews run-rate early in the period
- Do not invent a forecast curve or confidence band — point to Costory's in-product **Forecasting with TimesFM** (docs: `features/budgets`) instead
- Do not project against a budget without resolving `budgetVersionId` via `get`

## Related Skills / Next Steps

- `query` — Workflow F (budget burn) is the data source for pace projection
- `recipes` → `budget-vs-actual-dashboard` — persist the pace view
- `alerts` — standing regression detection
- `recommendations` — if the projection shows overspend, derive actions to bend the curve
