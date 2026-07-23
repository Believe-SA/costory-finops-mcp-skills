# Customer Foundation — Business Rules

The decision rules the skills enforce, stated once as IF / THEN / OTHERWISE. Today they are scattered across each skill's *Safety / Anti-patterns* section. This is the canonical statement; skill bodies should stay consistent with it (and, where a rule is runtime-critical, render from a shared fragment — see [`../fragments/`](../fragments/)).

## Routing — explain vs explore vs schedule

- **IF** the user asks *"why did spend move / what changed / explain last month"* (a drivers question)
  **THEN** answer with a preview-first **DIGEST** change tree (`preview_report_widget`).
  **OTHERWISE (explorer PoP totals only)** use `query` with `compare`. Never substitute `query`+`compare` for the DIGEST on the first "explain" answer.
- **IF** the delivery is recurring to a channel **THEN** it is a *Schedule* report; **IF** one-shot in chat **THEN** *Explain*. If ambiguous, ask which.

## TOP_FLOP — rank-only vs movers

- **IF** the report answers *"what are the biggest items?"* (e.g. env costs, marketplace vendors)
  **THEN** `topN: 10, flopN: 0` (rank-only — biggest items are not symmetric movers).
- **OTHERWISE IF** it answers *"what moved?"* (namespace, credits, coverage, weekly pulse)
  **THEN** `topN: 10, flopN: 10` (movers both directions).

## Delivery safety (scheduled reports)

- **IF** a report is `SCHEDULED` **THEN** use a `datePreset` that rolls forward — **never** frozen `from`/`to`.
- **IF** the cadence is a weekly calendar-week pulse (`LAST_WEEK`) **THEN** send **Tuesday** (`weekday: 2`) because cost data is ~2 days late. **OTHERWISE IF** it must land Monday (or earlier) **THEN** switch the period to `TRAILING_7_DAYS` so the window is not a half-empty calendar week.
- **IF** delivery mode is `NOW` or `SCHEDULED` **THEN** require explicit user confirmation before `create_report`. `UNSCHEDULED` does not.
- **THEN** resolve destinations **last** — only after the channel *type* (Slack/Teams/email) is known; list only that type and match by name, never paste the whole channel list.

## AI features (DIGEST only)

- **DEFAULT** tree-only (`display: "tree"`, `enableAiInvestigation: false`).
- **IF** the audience wants a written executive overview **THEN** `display: "summary"`.
- **IF** they want per-node deep analysis **THEN** `enableAiInvestigation: true` (warn: slower) — prefer with `display: "summary"`.
- Say the speed trade-off out loud before enabling either. Only DIGEST produces `summaryMarkdown`.

## Virtual dimensions

- **IF** VDIM leftover > ~10–20% **THEN** add rules for the largest unclaimed buckets before publishing.
- **IF** a rule you meant to keep shows 0 in the costs preview **THEN** check `virtual_dimension_overlap_matrix` for shadowing; put narrower/specific rules **before** broader ones.
- **Strategy approval ≠ rule approval:** after the user picks a *mapping strategy*, still present the concrete rule set and wait for explicit **rule** approval before `create_virtual_dimension_draft`.
- **IF** the target bucket values are unclear **THEN** ask the user what values they expect — do **not** invent bucket names from spend patterns.
- **THEN** use immutable `bqName` (never display `name`) in `groupBy`/`filterCel`; after publish, poll `computeStatus` until `COMPLETED` before querying.
- Do not put a catch-all/leftover rule in `rules` (it is auto-added); always carry each existing rule's `id` forward on update.

## Coverage (tagging)

- **THEN** measure a **ratio** (`tagged / in-scope`), not an absolute dollar amount.
- **IF** some in-scope spend is structurally un-taggable **THEN** either exclude it from the denominator or call it out — silently including it permanently caps the ratio below 100%.

## CEL & query hygiene

- **THEN** null labels are CEL `null` — use `== null` / `!= null`, never `is_null` or the string `"null"`. *(Shared fragment: `cel-null`.)*
- **THEN** SCOPE goes in `filterCel`, SPLIT goes in `groupBy` — never mix them.
- **THEN** query `name` is a single letter (`a`,`b`,`c`) for formulas; human labels go in `alias`.
- **IF** resolving a budget **THEN** pass the `budgetVersionId` (from `get`), never the parent budget id from `search`.

## The "never invent" guard set

Do **not** fabricate any of the following — discover or ask instead:

- **DatePreset tokens** — only the 16 in `query`; unknown tokens fail with `-32602`. *(Enforced by the DatePreset drift lint.)*
- **CEL field names / dimension values** — discover via `search` `type: ["dimensions"]` or `get_context`.
- **Findings numbers** — only cite figures actually observed via `query` / preview.
- **VDIM bucket names** — ask the user for expected values.

## Payload shape traps

- DIGEST preview takes a singular `widget`; `create_report`/`update_report` take a `widgets[]` array. Mixing them fails validation.
- Report `TEXT` widget field is `contentMarkdown`; dashboard text widget field is `textContent`. Not interchangeable.
- In a dashboard/report, do not repeat `metricId`/`currency`/`groupBy`/period/scope on a widget when it already matches `context`.

## Related

- [`finops-taxonomy.md`](./finops-taxonomy.md) · [`glossary.md`](./glossary.md) · [`entities.md`](./entities.md) · [`metrics.md`](./metrics.md)
