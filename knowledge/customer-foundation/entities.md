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
