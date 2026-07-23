---
name: alerts
description: "Use when creating a standing cost alert / anomaly monitor that notifies when a spend condition fires (threshold, week-over-week spike, budget pace), or when reviewing existing alerts. Preview-first: backtest the condition with preview_alert (firing count) before create_alert. MCP is create-only — edits happen in the UI via the returned URL. Covers the condition grammar (rollingSum / timeShift / weekToDateSum / monthToDateSum), dedup, destinations-last, and delivery safety. Call get_skill with skillId \"alerts\" before preview_alert or create_alert."
---

# Alerts

An **alert** is a standing rule that monitors one or more cost queries and notifies a channel when a `condition` fires. It is the **Automation / anomaly** capability: catch a spike or threshold breach without a human polling dashboards.

**MCP is create-only** — there is no `update_alert`. Edits happen in the Costory UI via the URL returned by `create_alert` (always include that URL in your reply).

**Preview before you create.** `preview_alert` backtests the condition over recent data and reports how often it would have fired — always run it and tune before `create_alert`.

**Load this skill first** for any alert creation, tuning, or review.

## When to Trigger

- "Warn me if \<scope\> spend exceeds $X" / "…jumps more than N% week-over-week"
- "Alert if we're on pace to blow the monthly budget"
- "Notify on-call when EC2 (or any service/team/env) spikes"
- "What alerts do we have?" (review → `list_alerts`)

## Core concepts

### Condition grammar

A single boolean expression over the query `name`s. Supports `+ - * /`, comparisons (`> >= < <= == !=`), `and`/`or`/`not`, parentheses, and window functions:

| Function | Meaning |
|----------|---------|
| `rollingSum(a, N, UNIT)` | trailing sum over the last N units (`DAY`/`WEEK`/`MONTH`), inclusive of today |
| `timeShift(a, N, UNIT)` | the value shifted back N units (may wrap a window function) |
| `weekToDateSum(a)` | Monday-to-date sum |
| `monthToDateSum(a)` | 1st-of-month-to-date sum |

Window math is evaluated **daily in BigQuery** — you do **not** pick an evaluation cadence. The period (`datePreset` / `from`/`to`) is only the look-back window for the underlying queries. Control *re-notification* frequency with `dedup`.

### Dedup

| Shape | Meaning |
|-------|---------|
| `{ "kind": "CALENDAR", "calendarUnit": "WEEK" \| "MONTH" }` | at most once per ISO week / calendar month |
| `{ "kind": "ROLLING", "windowDays": N }` | at most once every N days |

### Common condition patterns

| Intent | `condition` |
|--------|-------------|
| Absolute threshold over any 7 days | `rollingSum(a, 7, DAY) > 50000` |
| WoW spike >10% (7-day sum vs prior 7-day sum) | `rollingSum(a, 7, DAY) > timeShift(rollingSum(a, 7, DAY), 7, DAY) * 1.1` |
| Day-over-day jump >20% | `(a - timeShift(a, 1, DAY)) / timeShift(a, 1, DAY) > 0.2` |
| Today above the trailing 7-day average +10% | `a > (rollingSum(a, 7, DAY) / 7) * 1.1` |

## Tool order

1. `get_skill` with `skillId: "alerts"` — this guide
2. `get_context` — currency
3. `search` `type: ["dimensions"]` — resolve the scope CEL if not obvious
4. Confirm scope, threshold, dedup
5. `list_available_destinations` — **only after** the channel type (Slack/Teams/email) is known
6. `preview_alert` → show firing count → tune → `create_alert` (after explicit confirm)

## Workflow A — Create a spike / threshold alert

1. `get_context`; resolve scope CEL (`search` if needed)
2. Confirm: scope, threshold (and what it means — see the guard below), dedup, channel type
3. `preview_alert` (queries + condition + dedup + `lookbackDays`) → present `firingDays` / `notificationsCount`; if noisy, tune the threshold/dedup and re-preview
4. Resolve the concrete destination: `list_available_destinations` for that channel type → match by name
5. **Explicit confirm** → `create_alert` with the same queries + condition → include the returned URL

**Example — preview a WoW spike alert (backtest 45 days):**

```json
{
  "queries": [{ "type": "cost", "name": "a", "metricId": "cost", "currency": "USD", "filterCel": "cos_service_name in [\"AmazonEC2\"]" }],
  "condition": "rollingSum(a, 7, DAY) > timeShift(rollingSum(a, 7, DAY), 7, DAY) * 1.1",
  "dedup": { "kind": "CALENDAR", "calendarUnit": "WEEK" },
  "lookbackDays": 45
}
```

**Then create (adds channel + name; same queries/condition/dedup):**

```json
{
  "name": "AmazonEC2 +10% vs prior 7 days",
  "queries": [{ "type": "cost", "name": "a", "alias": "AmazonEC2 cost", "metricId": "cost", "currency": "USD", "filterCel": "cos_service_name in [\"AmazonEC2\"]" }],
  "datePreset": "TRAILING_90_DAYS",
  "aggBy": "Day",
  "condition": "rollingSum(a, 7, DAY) > timeShift(rollingSum(a, 7, DAY), 7, DAY) * 1.1",
  "dedup": { "kind": "CALENDAR", "calendarUnit": "WEEK" },
  "notificationChannel": "SLACK",
  "slackChannelId": "C…"
}
```

For the concrete EC2 card (frozen defaults + confirm gates), load `recipes` → `ec2-cost-spike-alert`.

## Workflow B — Review existing alerts

`list_alerts` (`type: "cost" | "budget" | "all"`) — **only** when the user explicitly asks what monitors exist. Returns each alert's `condition` + `dedup` (legacy alerts return structured `thresholds`).

## Safety Rules / Anti-patterns

- Do not `create_alert` without a `preview_alert` first — always show the backtest fire count
- Do not treat `datePreset` as an evaluation cadence — it is the query look-back; use `dedup` for notification frequency
- Do not resolve destinations before the channel **type** is known; then list only that type and match by name
- **Guard the condition's meaning:** "7-day sum vs prior 7-day sum" ≠ "today vs 7-day average". Confirm which the user means and pick the matching pattern
- Do not invent a `datePreset` token or CEL field — use the enum / `search`
- Do not promise in-place edits — MCP alerts are create-only; edits happen in the UI via the returned URL
- Do not call `list_alerts` unprompted — only when the user asks about current monitors

## Related Skills / Next Steps

- `query` — sanity-check the baseline before setting a threshold
- `recipes` → `ec2-cost-spike-alert` — the concrete spike-alert card
- `events` — annotate the cause once an alert fires and is understood
- `recommendations` — a fired alert becomes an anomaly-follow-up recommendation
- `reports` — for scheduled *digests* (vs event-driven alerts): different tool, different intent
