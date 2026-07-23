# Customer Foundation — Glossary

Vocabulary used across the Costory skills, with the concrete handle Costory uses for each. Grouped by area. See [`entities.md`](./entities.md) for CEL fields and [`metrics.md`](./metrics.md) for cost columns/formulas.

## Cost & billing

- **Blended / unblended cost** — averaged vs raw per-account cost. Columns: `unblended_cost`, `net_unblended_cost`.
- **Amortized cost** — upfront commitment fees spread across the term. Columns: `amortized_cost`, `net_amortized_cost`.
- **List / contracted / effective cost** — public price / on-demand-before-commitments / what you actually pay. Columns: `list_cost`, `contracted_cost`, `effective_cost`.
- **Effective savings** — `contracted_cost − effective_cost`; how much commitments (SP/RI/CUD) save you.
- **Charge category** — the kind of line: usage, credit, discount, tax, fee. Field: `cos_charge_category`. Credit lines are **negative**.
- **Marketplace / private offer** — third-party SaaS billed through the cloud invoice. Field: `cos_marketplace_purchase` (bool); vendor = `cos_invoice_issuer`.
- **Data lag** — billing/cost data lands ~2 days late; affects when a "last week" report is complete.

## Commitments & discounts

- **Commitment** — a spend/usage pledge for a discount: **Savings Plan (SP)**, **Reserved Instance (RI)**, **Committed Use Discount (CUD)**. Surfaces via effective savings, not a raw entity.
- **Credit runway** — how long remaining promotional credits/discounts last before the "real" bill appears. Tracked via `cos_charge_category` trend (`provider-credits`).
- **Coverage (commitment)** — share of eligible spend covered by a commitment. (Distinct from *tag coverage*.)

## Allocation

- **Showback** — attributing cost to a team/owner for visibility (no cross-charge).
- **Chargeback** — actually billing a team/owner for their cost.
- **Reallocation** — redistributing shared cost (e.g. a cluster) onto consumers, proportional to a driver. K8s: `cos_namespace_reallocated`.
- **Virtual dimension (VDIM)** — a custom cost axis from ordered CEL rules; immutable `bqName` vs display `name`.
- **Leftover** — spend not matched by any named VDIM rule (the auto catch-all). High leftover ⇒ add rules.
- **Shadowing** — an earlier VDIM rule capturing spend a later rule also matches (later shows 0). Detected via `virtual_dimension_overlap_matrix`.
- **Tag coverage** — `tagged / in-scope cost`; the movable share of the bill that carries a required label.
- **Untaggable spend** — cost that structurally cannot carry the tag; excluding/including it changes the coverage ceiling.

## Analysis & explanation

- **SCOPE vs SPLIT** — SCOPE = which rows (`filterCel`); SPLIT = how to break them out (`groupBy`). Never mix the two.
- **Period-over-period (PoP)** — comparing one range to another; `query` `compare`.
- **DIGEST** — Costory's cost-**change tree** vs the previous period, with top movers; the primary "what changed / explain last month" deliverable (preview-first, not `query`+`compare`).
- **Movers** — the largest increases/decreases between two periods (`topIncreases` / `topDecreases`; `TOP_FLOP` widget).
- **Drivers** — the underlying dimensions/resources responsible for a delta.
- **Unit economics** — cost per unit of business value: `cost / <metric>` (per request, per GB, per delivery…).
- **Waste ratio** — `k8s_waste / k8s_cost`; requested-but-unused K8s capacity.
- **Budget utilization** — `cost / budget` over the same window.

## Delivery & monitoring

- **Report** — scheduled or one-shot delivery of widgets to Slack/Teams/email.
- **Widget types** — `DIGEST`, `GRAPH_SNAPSHOT`, `TOP_FLOP`, `DASHBOARD_PDF`, `TEXT`.
- **TOP_FLOP** — ranked increases + decreases; `10/0` = biggest items only, `10/10` = movers both directions (see [`business-rules.md`](./business-rules.md)).
- **Context-first inheritance** — a dashboard/report defines a shared `context` (period, metric, currency, groupBy, scope); widgets carry only overrides.
- **Destination** — the concrete channel (`destinationType` + `channelId`); resolved late, only after the channel *type* is known.
- **Alert** — a standing rule that notifies when a cost condition trips (`create_alert`).
- **Event** — a time-anchored engineering marker (deploy, incident) correlated against cost (`list_events`).

## Time

- **DatePreset** — one of 16 server-accepted relative-period tokens (authoritative list in `query`). Never invent a token; never freeze dates on a scheduled report.
- **MTD / QTD / YTD** — month/quarter/year to date. **Trailing** — rolling window ending today. **Last \<period\>** — the previous complete calendar period.
- **`LAST_INVOICE_MONTH`** — the last closed invoice month (finance close).
