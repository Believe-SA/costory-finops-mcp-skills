---
name: reports
description: "Use when creating, previewing, updating, scheduling, or exploring Costory reports — especially DIGEST cost-change trees — including destinations, delivery safety (NOW/SCHEDULED), period presets, hierarchy groupBy, and execution drill-down. Call get_skill with skillId \"reports\" before create_report or substantial DIGEST work."
---

# Reports

A **report** delivers one or more widgets (chart snapshot, PDF, top/flop, text, or **DIGEST** cost-change tree) to one or more destinations (Slack, Teams, email). DIGEST reports compare two periods, rank qualifying changes, and deliver an executive summary.

**Load this skill first** for any DIGEST conversation, report creation, substantial update, or DIGEST preview.

## When to Trigger

- Creating a DIGEST, GRAPH_SNAPSHOT, TOP_FLOP, or other Costory report
- Previewing DIGEST thresholds or hierarchy before create
- Scheduling or sending a report (`NOW` / `SCHEDULED` / `UNSCHEDULED`)
- Updating destinations, widgets, or schedule on an existing report
- Exploring a delivered DIGEST execution tree

## Prerequisite

1. `get_skill` with `skillId: "reports"` (this guide)
2. `get_context` for org context and popular groupBys
3. `list_teams` when team scoping may apply — each scope's `id` is the `scopeId` value

## Query config (DIGEST, GRAPH_SNAPSHOT, TOP_FLOP)

All query-backed widgets reuse the same shape as `query`:

- `queries` — for DIGEST: exactly one `{ type: "cost", name: "a", groupBy, filterCel?, metricId?, currency? }`
- **Period (always prefer a preset for scheduled reports):**
  - All query widgets (DIGEST, GRAPH_SNAPSHOT, TOP_FLOP) use one field: `datePreset` (same `DatePreset` enum, e.g. `LAST_MONTH`, `LAST_WEEK`) — persisted on the widget so each scheduled run re-resolves relative to send time. For DIGEST the server also resolves the comparison period from it and echoes `resolvedPeriod`.
  - Explicit `from` / `to` (and DIGEST `compare`) only for one-off custom ranges — **never** for recurring schedules. Do not combine `datePreset` with explicit dates.
- `aggBy`
- `scopeId?` — optional saved team scope (from `list_teams`); merges a whereClause into the query

Report **ownership** (`teamId`, `visibility` on `create_report`) is separate from `scopeId` (query filter only).

## DIGEST hierarchy (first-class)

DIGEST builds a **tree**. Map natural-language levels to fields:

| User says | `queries[0].groupBy` (root) | `additionalGroupBy` (deeper, in order) |
|-----------|------------------------------|----------------------------------------|
| provider → service | `cos_provider` | `["cos_service_name"]` |
| env → project → service | `environment` | `["cos_sub_account_id", "cos_service_name"]` |
| team → service | `team` | `["cos_service_name"]` |

Rules:

- Root axis is always `queries[0].groupBy` (required).
- `additionalGroupBy` is ordered deeper levels only — never put the root there.
- Confirm the resolved path with the user when they describe a hierarchy in plain language (e.g. "production → Costory → AmazonEC2").
- Discover CEL field names via `search` with `type: ["dimensions"]` or `get_context` popularGroupBys. Prefer dimensions that appear in popularGroupBys.

## Product choices — ask explicitly

1. **Period** — one `datePreset` field for every query widget: `LAST_MONTH` for monthly digests, `LAST_WEEK` for weekly TOP_FLOP / GRAPH_SNAPSHOT. Use explicit dates only for one-off custom ranges — never on SCHEDULED reports.
2. **Scope filter** — optional `scopeId` from `list_teams`, or `filterCel` on the cost query
3. **Grouping hierarchy** — root `groupBy` + optional `additionalGroupBy` (see table above)
4. **Delivery mode** — `NOW` | `UNSCHEDULED` | `SCHEDULED`
5. **Destinations** — after `list_available_destinations`; missing Slack/Teams integrations: https://app.costory.io/integration
6. **Recurring timing** — for `SCHEDULED`: cadence, weekday (**required** for WEEKLY: 0 = Sunday … 6 = Saturday), and first send time → `firstRunAt` (ISO-8601 UTC datetime, e.g. `2026-07-16T10:00:00.000Z`)

## Preview defaults

| Field | Default |
|-------|---------|
| `minAbsoluteDiff` | **100** |
| `minRelativeDiff` | **5** (percent) |
| `topLargestAbsoluteChange` | **20** (allowed: 5, 10, 15, or 20) |

Always show `resolvedPeriod` (when present), `comparisonPeriodSummary`, `totals`, `counts`, `topIncreases` / `topDecreases`, `rootNodes`, and `summaryMarkdown`.

Tune from `recommendations`: thresholds, `topLargestAbsoluteChange` (only 5, 10, 15, or 20), grouping. Repeat `preview_report_widget` until satisfied.

## Schedule modes and delivery safety

| Mode | Confirm first? |
|------|----------------|
| `NOW` | **Yes** — sends now |
| `UNSCHEDULED` | No |
| `SCHEDULED` | **Yes** — authorizes future delivery |

## Workflow A — DIGEST creation

1. `get_context` → `list_teams` if needed
2. Ask period (prefer preset), scope, hierarchy, delivery mode
3. `preview_report_widget` with defaults **100 / 5% / 20** — pass the DIGEST widget as `{ widget: { type: "DIGEST", ... } }`
4. Tune loop → re-preview
5. `list_available_destinations`
6. Confirm → `create_report` with the **same widget object** (as an element of `widgets`)

The object below is the DIGEST **widget**: pass it as `preview_report_widget`'s `widget`, then as an element of `create_report`'s `widgets` array — no field changes between the two.

**Example — DIGEST widget (preferred datePreset):**

```json
{
  "type": "DIGEST",
  "queries": [{
    "type": "cost",
    "name": "a",
    "alias": "Cost by environment",
    "metricId": "cost",
    "currency": "USD",
    "groupBy": "environment",
    "filterCel": ""
  }],
  "datePreset": "LAST_MONTH",
  "aggBy": "Month",
  "additionalGroupBy": ["cos_sub_account_id", "cos_service_name"],
  "minAbsoluteDiff": 100,
  "minRelativeDiff": 5,
  "topLargestAbsoluteChange": 20
}
```

**Example — explicit custom dates (only when preset does not fit):**

```json
{
  "type": "DIGEST",
  "queries": [{
    "type": "cost",
    "name": "a",
    "alias": "Cost by provider",
    "metricId": "cost",
    "currency": "USD",
    "groupBy": "cos_provider",
    "filterCel": ""
  }],
  "from": "2026-05-01",
  "to": "2026-05-31",
  "aggBy": "Month",
  "compare": { "from": "2026-04-01", "to": "2026-04-30" },
  "additionalGroupBy": ["cos_service_name"],
  "minAbsoluteDiff": 100,
  "minRelativeDiff": 5,
  "topLargestAbsoluteChange": 20
}
```

For `create_report`, pass each widget (with `type` **inside** it) as an element of the `widgets` array, alongside `visibility`, `schedule`, and `destinations`. A single-widget report is just a one-element array; `get_report` echoes them back as a `widgets` array:

```json
{
  "visibility": "PRIVATE",
  "schedule": { "mode": "UNSCHEDULED" },
  "widgets": [{ "type": "DIGEST", "...": "same widget fields as the preview above" }],
  "destinations": [{ "destinationType": "SLACK", "channelId": "C…" }]
}
```

## Workflow B — Update

`get_report` → preview if DIGEST content changes → `update_report`.

## Workflow C — Run, retry, transfer, archive

Retry **failed executions only** — never `run_report_now` to fix one destination.

## Workflow D — Explore delivered DIGEST

`get_report_execution` → `get_report_execution_widget` with `view: "tree"` for the full formatted tree.

## Safety Rules / Anti-patterns

- Do not hand-compute last-month/last-week dates when `datePreset` applies — especially on SCHEDULED reports (frozen dates never roll forward)
- Do not put the root hierarchy axis in `additionalGroupBy` instead of `queries[0].groupBy`
- Do not skip preview before create
- Do not use a different shape for preview vs create
- Do not substitute destinations silently
- Do not poll executions in an unbounded loop
- Always confirm before `NOW` or `SCHEDULED` delivery

## Related Skills / Next Steps

- `dashboards` — when the user wants an interactive dashboard instead of a delivered report
- `virtual-dimensions` — when DIGEST hierarchy needs a custom axis that does not exist yet
