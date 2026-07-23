---
name: events
description: "Use when correlating cost movements with engineering or business events, or when annotating a cost change (deployment, migration, incident, pricing update, business decision). Covers create_event (with a widget annotation chart), list_events to correlate a spike with what happened, and update_event. This is Costory's \"correlate cost with engineering events\" capability. Not for explaining a delta's internal drivers — that is reports DIGEST / explain-period-change. Call get_skill with skillId \"events\" before create_event or update_event."
---

# Events

An **event** annotates a cost change on the timeline so the team can tie a cost movement to a real-world cause — a **deployment**, **migration**, **incident**, **pricing update**, or **business decision**. Events show up as annotations on cost charts and are the bridge for Costory's *correlate cost with engineering events* capability.

An event has: `name` (≥5 chars), `date`, `description`, a `category` (`TECHNICAL` default · `BUSINESS` · `PROVIDER`), optional `tags`, optional `metadata` (e.g. a PR link, owner), and — **strongly recommended** — a `widget` (an annotation chart, same shape as `query` plus a `title`) so the annotation is pinned to the exact cost movement it explains.

**Load this skill first** to log an event, or to correlate a cost spike with what changed.

## When to Trigger

- "Log / annotate the migration (deploy, incident, price change) we did on \<date\>"
- "Did anything happen around that cost spike in mid-March?" (correlate)
- "Why does cost jump every time we deploy?" → correlate deploy events with cost
- Editing or enriching an existing event (add a PR link, fix the date)
- **After** a DIGEST/`query` shows a spike on a date → check for a matching event

**Hand off instead of this skill:** *"explain what drove last month's delta"* (internal drivers tree) → `reports` Explain / `recipes` → `explain-period-change`. Events explain a movement by **external cause**, not by decomposing the number.

## Tool order

1. `get_skill` with `skillId: "events"` — this guide
2. `get_context` — org context, currency
3. `list_tags` — before attaching tags, to reuse existing label values (do not invent)
4. `list_events` (correlate) / `create_event` / `update_event`

## Concepts

| Concept | Meaning |
|---------|---------|
| Category | `TECHNICAL` = deploy/infra change · `BUSINESS` = org/budget/pricing decision · `PROVIDER` = cloud-provider update |
| Widget annotation | Same shape as a `query` (`queries`, `datePreset` or `from`/`to`, `aggBy`, …) + `title`. Pins the event to a specific cost chart. **Strongly recommended**; omit only for a purely org-wide event with no chart |
| Tags | String labels (`"migration"`, `"scaling"`). Discover existing values with `list_tags` first — do not invent parallel labels |
| Metadata | Key-value pairs (`link`, `owner`, external ref). `metadata.source` is reserved/system-managed — never set it |
| Correlation | An event that lines up in time + scope with a cost mover is a **candidate driver** — surface it as such, do not assert causation |

## Workflow A — Log an event (annotate a cost change)

Use when the user wants to document why cost changed.

1. `get_context`; `list_tags` if tagging
2. Draft the event: `name`, `date` (YYYY-MM-DD), `description`, `category`
3. Build a **widget** scoped to the affected spend (same shape as `query` + `title`) so the annotation is visual
4. `create_event` — include the returned event in your reply

**Example — log a Kubernetes migration with an annotation chart:**

```json
{
  "name": "Kubernetes cluster migration",
  "date": "2026-03-18",
  "description": "Migrated the prod cluster; temporary node scaling cost spike from dual-running.",
  "category": "TECHNICAL",
  "tags": ["migration"],
  "metadata": { "link": "https://github.com/acme/infra/pull/42", "owner": "platform-team" },
  "widget": {
    "title": "K8s node cost",
    "queries": [{ "type": "cost", "name": "a", "metricId": "cost", "currency": "USD", "filterCel": "cos_service_name in [\"AmazonEC2\"]" }],
    "from": "2026-03-10",
    "to": "2026-03-25",
    "aggBy": "Day"
  }
}
```

## Workflow B — Correlate a spike with what happened

Use after a `query` / DIGEST shows a cost movement on a date, or when the user asks "did anything happen around then?".

1. Note the movement's **date range** and **scope** (from the query / DIGEST)
2. `list_events` with `from`/`to` spanning that range (optionally `category: "TECHNICAL"` for deploys, or a `tags` filter)
3. Line events up against the movement: an event in the same window + scope is a **candidate driver** — report it as correlation, not proof
4. Optionally `create_event` to annotate the movement for next time; then `suggest_actions`

```json
// list_events around a mid-March spike
{ "from": "2026-03-10", "to": "2026-03-20", "category": "TECHNICAL" }
```

## Workflow C — Update an event

`list_events` → find `eventId` → `update_event` with only the fields to change.

- `tags` **replace** the full label list; `metadata` **merges** (existing `source` preserved)
- `widget` updates the annotation chart (creates one if none); pass `widgetEventId` when the event has multiple charts

```json
{ "eventId": "clx9abc", "metadata": { "link": "https://github.com/acme/app/pull/99" } }
```

## Safety Rules / Anti-patterns

- Do not assert **causation** from correlation — an aligned event is a *candidate* driver; the drivers decomposition is DIGEST's job
- Do not omit the `widget` on a cost-specific event — the annotation is the point (omit only for truly org-wide events)
- Do not invent tag values — `list_tags` first and reuse
- Do not set `metadata.source` — it is reserved
- Do not use a `name` shorter than 5 characters
- Do not use this skill to *explain* a delta's internal composition — hand off to `reports` Explain / `explain-period-change`

## Related Skills / Next Steps

- `query` — find the movement and its date range before correlating (`list_events` uses that range)
- `reports` → `recipes` → `explain-period-change` — decompose *why* the number moved (internal drivers), distinct from external-event correlation
- `alerts` — turn a recurring spike into a standing notification
- `recipes` → (playbook) `spend-spike-triage` — the full loop: explain → correlate events → find drivers → estimate savings → summarize
