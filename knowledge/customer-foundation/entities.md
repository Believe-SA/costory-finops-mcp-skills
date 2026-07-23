# Customer Foundation — Entities

The canonical business-entity model the Costory skills operate on. Today this model is *implicit* — it exists only as `cos_*` CEL field conventions, virtual dimensions, budgets, and events scattered across skills. This file names it once.

**How to read the table.** *Canonical handle* is the CEL field (for `groupBy` / `filterCel`) or object identifier a skill uses to reference the entity. Always confirm a field exists for the org via `search` with `type: ["dimensions"]` before relying on it — this table records the *convention*, not a guarantee every org has populated it.

## Core cost dimensions (`cos_*`)

| Entity | Canonical handle | Notes / cardinality | Foundation status |
|--------|------------------|---------------------|-------------------|
| CloudProvider | `cos_provider` | Low cardinality (AWS / GCP / Azure). Common top-of-tree root. | ✅ canonical |
| Service | `cos_service_name` | e.g. `AmazonEC2`, `Compute Engine`. The default fallback split. | ✅ canonical |
| Region | `cos_region` | Geographic axis. | ✅ canonical |
| BillingAccount / Project | `cos_sub_account_id` | Account / project / subscription. Mid-level DIGEST tier. | ✅ canonical |
| Environment | `cos_environment` **or** VDIM `virtual_environment` | Providers rarely ship a clean prod/staging/dev axis — usually a **virtual dimension**. | ✅ canonical (often a VDIM) |
| Team | `cos_team` **or** team scope (`list_teams` → `scopeId`) | Two mechanisms: a cost label and a saved scope. | ✅ canonical |
| Namespace | `cos_namespace_reallocated` (prefer) / raw namespace label | Prefer the reallocated field when the org uses K8s reallocation. | ✅ canonical |
| Cluster | `cos_cluster_name` | K8s cluster scope; `!= null` selects all clusters. | ✅ canonical |
| Invoice / Issuer | `cos_invoice_issuer`; period via `LAST_INVOICE_MONTH` | Issuer = marketplace vendor / seller. | ✅ canonical |
| ChargeCategory | `cos_charge_category` | Usage / credit / discount / tax lines. Credit lines are **negative**. | ✅ canonical |
| MarketplacePurchase | `cos_marketplace_purchase` (boolean) | `== true` for marketplace/private-offer spend; `== false` excludes it. | ✅ canonical |

## Costory objects (first-class, not `cos_*` dimensions)

| Entity | Canonical handle | Notes | Foundation status |
|--------|------------------|-------|-------------------|
| Budget | parent budget `id` → resolve `budgetVersionId` via `get` | Queries take the **version** id, never the parent id. | ✅ canonical |
| VirtualDimension | immutable `bqName` (not display `name`) | User-defined axis (Environment, Team, Prod/R&D, Product line, CostCenter…). Poll `computeStatus: COMPLETED` after publish. | ✅ canonical |
| Report / Dashboard / Alert / Tag | object `id` | Delivery + monitoring objects; own skills. | ✅ canonical |
| Team scope | `scopeId` (from `list_teams`) | Query scope, distinct from report **ownership** (`teamId`/`visibility`). | ✅ canonical |
| Destination | `destinationType` + `channelId` (`list_available_destinations`) | Slack / Teams / email. | ✅ canonical |

## Derived, and not-yet-modeled entities

| Entity | Current representation | Gap |
|--------|------------------------|-----|
| Commitment / SavingsPlan / CUD | *implicit* — surfaces as `contracted_cost` − `effective_cost` ("effective savings") | Model as a **derived metric** (see `metrics.md`), not a raw entity. |
| Recommendation | *implicit* — `suggest_actions` tool output only | ❌ **Not modeled.** Blocks a first-class `recommendations` skill. |
| Forecast | none — no forecast tool in the MCP surface | ❌ **Not modeled.** Confirm backend support before designing a `forecast` skill. |
| Event (Deployment / Incident) | generic `Event` (`create_event` / `list_events`) — untyped | ⚠️ Present but **untyped**. Costory's "correlate cost with engineering events" pillar wants typed Deployment/Incident events. |
| CostCenter / BusinessUnit / Owner | would be **virtual dimensions** | ⚠️ Pattern exists (VDIM), not first-class Foundation entities. |

The three ❌/⚠️ rows are exactly the entities whose absence blocks the missing skills (`recommendations`, `forecast`, `events`) — see the roadmap.

## Relationships (informal)

- A **Resource**'s cost carries `cos_provider`, `cos_service_name`, `cos_region`, `cos_sub_account_id`, and (when tagged) `cos_environment` / `cos_team`.
- A **VirtualDimension** re-projects those raw dimensions onto a business axis via ordered CEL rules (first match wins; leftover catches the rest).
- A **Budget** is compared against actual cost over a period; **utilization** = `cost / budget`.
- An **Event** is time-anchored and correlated against a cost delta over the same range (`list_events`).

## Proposed entity models (absent today)

The three gaps above, modeled concretely. Each is the entity a currently-missing skill needs. Modeling them here is the Customer Foundation half of unblocking those skills (the other half is the skill itself — see the roadmap, Phase 4/5).

### Recommendation

A concrete, prioritized action to reduce or reallocate spend, with estimated impact.

| Attribute | Value / source |
|-----------|----------------|
| Backing tool | `suggest_actions` (today only a "next steps" hint; no first-class object) |
| Proposed fields | `id`, `type` (rightsizing \| commitment \| waste \| tagging \| anomaly-followup), `target` (resource/service/scope CEL), `estimatedSavings` (money + currency + period), `confidence`, `effort`, `rationale`, `status` (open \| accepted \| dismissed \| done) |
| Key metric | `estimatedSavings` — grounded in `effective_cost` / `contracted_cost` and usage (see [`metrics.md`](./metrics.md)) |
| Unblocks | `recommendations` skill: RecommendSavingsPlan, RecommendRightsizing, PrioritizeRecommendations, ExplainRecommendation, EstimateSavings |
| Relationships | targets a Resource/Service/Scope; may cite a Commitment; feeds the *Recommendations* and *Cost Optimization* capabilities |

### Forecast

A projection of future spend for a scope over a horizon, with a confidence band.

| Attribute | Value / source |
|-----------|----------------|
| Backing tool | **none in the current MCP surface** — confirm the Costory backend exposes forecasting before designing the skill |
| Proposed fields | `scope` (CEL / VDIM / whole-org), `horizon` (period), `method` (trend \| seasonal \| driver-based), `points[]` (date → projected cost), `low`/`high` band, `basisPeriod`, `assumptions` |
| Key metric | projected `cost` (or `effective_cost`); compared against a Budget for pace |
| Unblocks | `forecast` skill: ForecastSpend, DetectCostRegression |
| Relationships | consumes historical cost + Events (deploys shift the baseline); pairs with Budget for "on pace?"; feeds *Forecasting* and *Budget Management* |
| Status | **product-blocked** — flag as a gap if no backend forecast API exists; do not fabricate forecast behavior |

### Event — typed (Deployment / Incident)

Costory already has a generic, **untyped** `Event` (`create_event` / `update_event` / `list_events`). Costory's stated pillar is *correlating costs with engineering events* — which wants **typed** events so correlation can be automatic and meaningful.

| Attribute | Value / source |
|-----------|----------------|
| Backing tool | `create_event` / `update_event` / `list_events` (present; type is currently free-form) |
| Proposed types | `deployment`, `incident`, `config-change`, `scaling-event`, `feature-launch` |
| Proposed fields | `id`, `type`, `timestamp` (+ optional end), `scope` (service/team/env CEL), `source` (CI/CD, incident tool), `ref` (commit/PR/incident id), `description` |
| Correlation | join to a cost delta over the same range + scope (`query` / DIGEST); a deploy or incident that lines up with a spike is a candidate driver |
| Unblocks | `events` skill: AnalyzeDeploymentImpact, CorrelateDeployments, CorrelateIncidents — and the flagship **spend-spike-triage** playbook |
| Relationships | anchors to a Service/Team/Environment; is the correlation counterpart to a cost mover; feeds *Cost Intelligence* and *Automation* |

**Integration note.** Typed events are the highest-leverage of the three: the tools already exist, and they unblock both the `events` skill and the canonical playbook. Forecasting is the one to verify against the product first.

