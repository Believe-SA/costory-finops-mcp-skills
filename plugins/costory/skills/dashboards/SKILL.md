---
name: dashboards
description: "Use when creating or extending Costory dashboards, adding or replacing widgets, copying widgets between dashboards, or applying context-first inheritance for period, groupBy, metric, currency, and CEL filters. Call get_skill with skillId \"dashboards\" before create_dashboard or update_dashboard."
---

# Dashboards

A **DashboardV2** has a shared **`context`** (global theme) and **widgets** that inherit it by default. Each widget is either an Advanced Explorer chart or a **text block** (`type: "text"`, `textContent`).

**Context-first rule:** define the full dashboard `context` **before** listing widgets. Widgets should contain **only overrides** — never duplicate what already lives in `context`. If two or more widgets share the same period, `groupBy`, metric, currency, or filter scope, extract that shared value to `context` first.

## When to Trigger

- Creating a new Costory dashboard
- Adding, replacing, or removing widgets on an existing dashboard
- Copying a widget to another dashboard
- User asks for a cost overview "by service / by region" style dashboard

## Dashboard `context` fields

| Field | Role | Widget inheritance |
|-------|------|-------------------|
| `metricId` | Default cost column (e.g. `"cost"`) | Cost widgets omit `metricId` to inherit |
| `currency` | USD, EUR, GBP | Cost widgets omit `currency` to inherit |
| `groupBy` | Default split dimension — use when most widgets share the same axis | Cost widgets omit `groupBy` to inherit (or set `null` explicitly for totals) |
| `datePreset` **or** `startDate`/`endDate` | Dashboard period — **required on create**. Prefer `datePreset` whenever an available preset matches the requested range | Widgets omit `from`/`to`/`datePreset` to inherit |
| `conditionsCel` | Dashboard-wide CEL filter (scope) | AND-merged into every cost widget by default |
| `scopeId` | Optional saved scope | Inherited like other context fields |

Each query still needs `"type": "cost"` (query kind — not inherited). What you omit on cost widgets is `metricId`, `currency`, `groupBy`, and period when they match `context`.

## Inheritance semantics

- **Period, metricId, currency, groupBy:** omit on widgets when they match the dashboard `context`.
- **Similarity rule:** when widgets or dashboards are very similar, identify the common `datePreset`/dates, `groupBy`, `metricId`, `currency`, and `conditionsCel` before writing widgets. Put common values in `context`; widget fields are for exceptions only.
- **`groupBy`:** omit the field to inherit `context.groupBy`; set `groupBy: null` to explicitly disable grouping for that widget.
- **Period presets:** if the user's range maps to an available `DatePreset` (for example `TRAILING_30_DAYS`, `TRAILING_90_DAYS`, `LAST_MONTH`, `YTD`), use `context.datePreset`. Use `startDate`/`endDate` only for truly custom ranges.
- **`conditionsCel`:** inherited by default. Every cost widget AND-merges dashboard `conditionsCel` with its own `filterCel`.
- **`extendDashboardConditions`:** defaults to `true` (inherit dashboard filter). Set `false` **only** when the widget must ignore the dashboard filter entirely.
- **Widget `filterCel`:** widget-specific scope only — do **not** put the dashboard-wide filter here; put it in `context.conditionsCel`.

## Text widgets

Use for notes, headings, or commentary — no queries, period, or dashboard inheritance.

```json
{
  "type": "text",
  "title": "Notes",
  "textContent": "## AWS overview\nKey findings..."
}
```

Default grid size is 6×2 columns/rows. Override with `w`/`h`; pin position on add via `x`/`y` (same as chart widgets).

## Supporting tools

| When | Tool |
|------|------|
| Org context, recent dashboards, popular groupBys | `get_context` |
| Discover CEL field names and values | `search` with `type: ["dimensions"]` |
| Validate filters / explore spend before building | `query` |
| Pick a meaningful default groupBy | `suggest_groupby` |
| Read existing dashboard + widget layout | `get` |
| Create a new dashboard | `create_dashboard` |
| Add / replace / remove widgets | `update_dashboard` |
| Run saved widget data | `get_dashboard_widget_data` |

## Workflow A — Create a new dashboard

1. `get_skill` with `skillId: "dashboards"` (this guide) — you are here
2. `get_context` + optional `search` / `query` to pick dimensions and validate CEL
3. **Draft the dashboard `context` first:**
   - `metricId`, `currency`, default `groupBy` when two or more widgets share the same split
   - **Period:** prefer `datePreset` (e.g. `TRAILING_90_DAYS`) when possible; otherwise use `startDate` + `endDate`
   - Global scope: `conditionsCel` when all widgets share a filter
4. **List widgets as minimal overrides** — each widget: `title`, `queries` (`type`, `name`, `chartType`, optional `groupBy` / `filterCel`), `aggBy`. Omit `metricId`, `currency`, period, `groupBy`, and `conditionsCel` when they match `context`.
5. `create_dashboard` — include the returned URL in your reply

**Example — AWS overview, by service and by region:**

> **`context.metricId` ≠ query `"type"`.** Both can be `"cost"` but mean different things:
> - `context.metricId` → which cost **column** to query (inherited — widgets omit `metricId`)
> - `queries[].type` → query **kind** (`"cost"`, `"metric"`, `"formula"`…) — required on every query, not inherited
>
> Widgets below do **not** repeat `metricId`, `currency`, period, `groupBy`, or `conditionsCel` from `context`. Only `"type": "cost"` stays on each query.

```json
{
  "name": "AWS Overview",
  "context": {
    "conditionsCel": "cos_provider in [\"AWS\"]",
    "groupBy": "cos_service_name",
    "metricId": "cost",
    "currency": "USD",
    "datePreset": "TRAILING_90_DAYS"
  },
  "widgets": [
    {
      "title": "By Service",
      "queries": [{ "type": "cost", "name": "a", "chartType": "BAR" }],
      "aggBy": "Month"
    },
    {
      "title": "By Region",
      "queries": [{ "type": "cost", "name": "a", "chartType": "BAR", "groupBy": "cos_region" }],
      "aggBy": "Month"
    }
  ]
}
```

## Workflow B — Extend an existing dashboard

1. `search` → dashboard id
2. `get` → read `context` and each widget's `queryConfig`
3. `update_dashboard` with `op: "add"` (or `replace` / `remove`) — new widgets omit fields that match the dashboard `context`, especially the period and common `groupBy`
4. Response includes `inheritedContext` — use it to know what widgets can omit
5. Include the returned URL in your reply

**Example — add a region breakdown:**

```json
{
  "dashboardId": "clx9abc",
  "operations": [{
    "op": "add",
    "widget": {
      "title": "By Region",
      "queries": [{ "type": "cost", "name": "a", "chartType": "BAR", "groupBy": "cos_region" }],
      "aggBy": "Month"
    }
  }]
}
```

## Workflow C — Copy a widget to another dashboard

1. `get` on the source dashboard → note `x`, `y`, `w`, `h` and the widget's effective query (resolved `queryConfig`)
2. `get` on the target dashboard → read its `context`
3. `update_dashboard` on the target with `op: "add"`:
   - Pass `x`, `y`, `w`, `h` to preserve layout
   - Rebuild queries using **overrides only** relative to the **target** dashboard `context` — do not copy inherited metricId/currency/period/filter fields that the target already provides

## Per-widget overrides

- **Period:** when one widget needs a different range, set `from` + `to` (or `datePreset`) on **that widget only**. The dashboard `context` must still define the default period for all other widgets.
- **groupBy:** when one widget needs a different split, set `groupBy` on **that query only**. When multiple widgets use the same split, move it to `context.groupBy` and omit `groupBy` on those widget queries.

## QUERY NAMING

`name` is a single letter (`a`, `b`, `c`) for formulas; put human labels in `alias`, never in `name`.

## Safety Rules / Anti-patterns

- Do not repeat `metricId`, `currency`, `groupBy`, `from`/`to`, or `datePreset` on every widget when already in `context`
- Do not use widget `from`/`to` for a common dashboard period when a `context.datePreset` is possible
- Do not repeat the same `groupBy` across similar widgets instead of setting `context.groupBy`
- Do not put the global scope (e.g. `cos_provider in ["AWS"]`) in each widget's `filterCel` instead of `context.conditionsCel`
- Do not set `extendDashboardConditions: true` on every widget — omit it (default is inherit)
- Do not call `create_dashboard` without a period in `context` — validation rejects it (chart widgets need a dashboard period; text widgets do not)

## Related Skills / Next Steps

- `reports` — when the user wants a scheduled DIGEST or delivered report instead of (or in addition to) a live dashboard
- `virtual-dimensions` — when the desired `groupBy` axis does not exist yet and must be built as a custom cost axis
