# Costory FinOps Skills — Knowledge-Base Review

*Staff+ FinOps / Knowledge-Engineering review of `costory-finops-mcp-skills` (plugin v0.8.3).*
*Mandate: preserve existing knowledge, extend without breaking compatibility, propose a path to a structured FinOps Knowledge Base. Nothing here deletes knowledge — every recommendation is additive.*

---

## 0. Headline verdict

This repository is **not** the naive skill dump the "transform into a knowledge base" framing assumes. It is a **mature execution layer** with genuinely top-tier prompt engineering: precise triggers, worked JSON examples, explicit anti-patterns, disambiguation tables, confirm-gates on every mutation, and hallucination guards (*never invent preset tokens / dimension names / findings numbers*). The five skills already map cleanly onto FinOps capabilities and hand off to each other through a well-designed router (`recipes`).

The gaps are **not** in what exists — they are in what is *implicit* and what is *absent*:

| Gap | Nature | Severity |
|-----|--------|----------|
| **Customer Foundation is implicit** | The business entity model exists only as scattered `cos_*` CEL conventions, VDIMs, budgets, and events. Never written down as an entity/glossary layer. | **High** |
| **No single source of truth** | Core conventions (DatePreset enum, SCOPE/SPLIT, context-first inheritance, CEL null handling, `bqName` rule, DIGEST thresholds) are duplicated verbatim across skills and recipes, hand-synced. | **High** |
| **Skill coverage < tool coverage** | `create_alert`/`preview_alert`/`list_alerts`, `create_event`/`update_event`/`list_events`, and `suggest_actions` have **no owning skill** — yet these back Costory's own stated pillars (anomaly, event correlation, recommendations). | **High** |
| **Missing capabilities** | Forecasting, Recommendations, Cost Optimization, and Governance are absent or partial as first-class skills. | **Medium-High** |
| **Recipes are single-hop, not playbooks** | Each recipe routes to *one* mechanics skill. The mission's canonical multi-step playbook (bill up → explain → correlate deploys → correlate incidents → find drivers → estimate savings → summary) is **not expressible today**. | **Medium** |

**One constraint governs every "extract to shared files" recommendation** and must not be forgotten: `AGENTS.md` line 127 mandates each `SKILL.md` be **self-contained**, because Costory MCP `get_skill` may not load `references/`. **The duplication is therefore partly load-bearing.** The fix is *single-source-of-truth + build-time sync + a lint gate*, **not** runtime de-duplication. Naively DRY-ing these skills into shared imports would break delivery.

**Aggregate maturity: ~3.4 / 5 — a strong execution layer on top of an immature knowledge layer.** Full scoring in §8.

---

## 1. FinOps capability map

Each skill mapped to exactly one primary capability (secondary in parentheses).

| Skill | Primary capability | Secondary | Notes |
|-------|-------------------|-----------|-------|
| `query` | **Cost Intelligence** | Unit Economics, Budget Management | The analytical engine. SCOPE/SPLIT, PoP compare, cost-per-X, budgets, effective savings, K8s waste. |
| `dashboards` | **Reporting** | Cost Intelligence | Persisted views; context-first inheritance; "interesting overview" generator. |
| `reports` | **Reporting** | Cost Intelligence (DIGEST = explanation) | Scheduled delivery + one-shot DIGEST change-tree; strongest delivery-safety discipline in the repo. |
| `virtual-dimensions` | **Cost Allocation** | Governance (tagging) | Custom cost axes; telemetry/split allocation; leftover & shadowing analysis. |
| `recipes` | *(meta)* **Automation / Playbook router** | all | Outcome→recipe→mechanics-skill router; 14 cards. |

### Coverage heatmap against the capability model

| Capability | Status | Where it lives |
|-----------|--------|----------------|
| Cost Intelligence | ✅ **Strong** | `query`, `dashboards`, `reports` DIGEST |
| Cost Allocation | ✅ **Strong** | `virtual-dimensions`, `namespace-cost`, `reallocate-by-external-metric` |
| Reporting | ✅ **Strong** | `reports`, `dashboards`, report recipes |
| Budget Management | 🟡 **Partial** | `query` Workflow F + `budget-vs-actual-dashboard` recipe — no budget *creation/governance* skill |
| Unit Economics | 🟡 **Partial** | `query` Workflow E + `reallocate-by-external-metric` — no dedicated skill (note: separate `finops-unit-economics*` skills exist in other plugins) |
| **Forecasting** | ❌ **Missing** | Nothing. Costory claims "forecasting costs" as a pillar. |
| **Cost Optimization** | ❌ **Missing** | Only `query` Workflow H (contracted vs effective *analysis*). No optimization *actions*. |
| **Recommendations** | ❌ **Missing** | `suggest_actions` tool is referenced as a "next steps" hook but has no owning skill. |
| **Governance** | 🟡 **Weak** | `untagged-coverage` + tagging in VDIM + confirm-gates. No governance capability/skill. |
| **Automation** (alerts/anomaly/events) | 🟡 **Partial** | `ec2-cost-spike-alert` recipe; `create_alert`/`create_event` tools exist but no owning skill. |

**Key finding:** every ❌ / 🟡 that is *not blocked on the product* is already backed by an existing MCP tool. Those are buildable now (see §6).

---

## 2. Customer Foundation — the missing spine

### Current state: the model exists, but only implicitly

The repository already *operates on* a rich business model — it just never *declares* one. Entities live as:

- **`cos_*` dimension conventions** discovered ad-hoc via `search type:["dimensions"]`
- **Virtual dimensions** (Environment, Team, Prod/R&D, Product line) as user-built axes
- **Budgets** (parent id → `budgetVersionId`), **Events** (`list_events`/`create_event`), **Reports/Dashboards/Alerts/Tags** as first-class objects

No file names these entities, their relationships, or the canonical CEL field for each. Every skill re-teaches "discover the field with `search`." That is the single highest-leverage gap.

### Proposed `entities.md` (ready to lift — populated from actual skill usage)

| Foundation entity | Canonical handle in Costory | Evidence in skills | In Foundation? |
|-------------------|------------------------------|--------------------|----------------|
| CloudProvider | `cos_provider` | query, all recipes | ✅ |
| Service | `cos_service_name` | everywhere | ✅ |
| Region | `cos_region` | query, dashboards | ✅ |
| BillingAccount / Project | `cos_sub_account_id` | reports DIGEST, service-cost-weekly | ✅ |
| Environment | `cos_environment` / VDIM `virtual_environment` | env-costs, prod-vs-rnd | ✅ (often a VDIM) |
| Team | `cos_team` / team scope (`list_teams` → `scopeId`) | reports, query | ✅ |
| Namespace / Cluster | `cos_namespace_reallocated`, `cos_cluster_name` | namespace-cost, query G | ✅ |
| Invoice / Issuer | `cos_invoice_issuer`, `LAST_INVOICE_MONTH` | marketplace-spend | ✅ |
| ChargeCategory | `cos_charge_category` | provider-credits, credits-ytd | ✅ (add explicitly) |
| MarketplacePurchase | `cos_marketplace_purchase` (bool) | marketplace, untagged | ✅ (add explicitly) |
| Budget | budget id → `budgetVersionId` | query F, budget-vs-actual | ✅ |
| VirtualDimension | `bqName` (immutable) vs `name` | virtual-dimensions | ✅ |
| Commitment / SavingsPlan | *implicit* in `contracted_cost` − `effective_cost` | query H | ⚠️ model as derived metric, not entity |
| Recommendation | *implicit* in `suggest_actions` | query/dashboards hooks | ❌ **not modeled** |
| **Forecast** | *(no tool)* | — | ❌ **not modeled** |
| Incident / Deployment | `Event` (`create_event`/`list_events`) — generic, not typed | query post-query | ⚠️ present as untyped Event |
| CostCenter / BusinessUnit / Owner | *(would be VDIMs)* | — | ⚠️ VDIM pattern, not first-class |

**Recommendation:** create `knowledge/customer-foundation/entities.md` as the *canonical* list (entity → CEL field → cardinality note → typical VDIM status). Every skill then links to it instead of re-teaching discovery. The three ⚠️/❌ rows (Commitment, Recommendation, Forecast, typed Events) are the entities that expose the missing capabilities in §6.

### Cost-metric vocabulary (belongs in `metrics.md`)

Already enumerated authoritatively in `query` but nowhere else: `cost`, `effective_cost`, `list_cost`, `contracted_cost`, `unblended_cost`, `net_unblended_cost`, `amortized_cost`, `net_amortized_cost`. Plus derived: **effective savings** = `contracted_cost − effective_cost`; **waste ratio** = `k8s_waste / k8s_cost`; **coverage** = `tagged / all`; **utilization** = `cost / budget`; **unit cost** = `cost / <metric>`. These derived formulas are re-derived in 4+ places (see §5).

---

## 3. Per-skill deliverables

> Template per the mandate: Summary · Capability · Business purpose · Strengths · Weaknesses · Missing knowledge · Missing business rules · Missing examples · Suggested refactoring · Dependencies · Reusable components · Foundation entities · Suggested new Skills · Suggested Playbooks · Migration effort.

### 3.1 `query`

- **Summary.** Unified explorer for cost / usage / saved-metric / external-metric / formula / budget data. 9 named workflows (A–I) with worked JSON.
- **Capability.** Cost Intelligence (+ Unit Economics, Budget Management).
- **Business purpose.** Answer "what are we spending on X, and per unit of what?" — the analytical substrate every other skill validates against.
- **Current strengths.** Best-in-repo teaching of SCOPE vs SPLIT; explicit 16-value `DatePreset` enum with the exact server error it prevents; unit-economics and effective-savings workflows; disciplined "hand off *explain* to DIGEST, don't fake it with `query`+`compare`."
- **Weaknesses.** Longest skill (548 lines) carrying the *authoritative* copies of enum, cost columns, CEL null rule, query naming — other skills reference these from memory, risking drift. No forecasting leg despite budget burn being present.
- **Missing knowledge.** No cross-link to a canonical metric glossary; `rollingAggregation` window presets only shown by example, not enumerated.
- **Missing business rules.** No rule for *when a delta is significant* (that logic lives only in DIGEST thresholds); no guidance on currency conversion caveats.
- **Missing examples.** Multi-currency query; `externalMetric` BigQuery `gapFillingMethod` variants beyond `ZERO`; a forecast/trend-projection example.
- **Suggested refactoring.** Promote the enum, cost-column list, CEL null rule, and query-naming rule to `knowledge/` and mark `query`'s copies as the *rendered projection* of that source (lint keeps them equal).
- **Dependencies.** `get_context`, `search`, `suggest_groupby`, `suggest_usage_metrics`, `list_metrics`, `list_events`, `suggest_actions`.
- **Reusable components.** `DatePreset` enum; SCOPE/SPLIT; cost columns; unit-economics `a/b`; effective-savings `a−b`; K8s waste ratio.
- **Foundation entities.** All `cos_*`, Budget, VirtualDimension (`bqName`), external metrics.
- **Suggested new skills.** `forecast` (trend projection); shares the query substrate.
- **Suggested playbooks.** Feeds every playbook as the "find drivers / quantify" step.
- **Migration effort.** **Low** (mostly link-outs; behavior unchanged).

### 3.2 `dashboards`

- **Summary.** Create/extend DashboardV2 with a shared `context` + override-only widgets; "interesting overview" generator with a widget palette and 12-col layout recipe.
- **Capability.** Reporting (+ Cost Intelligence).
- **Business purpose.** Persist a validated investigation as a durable, self-explaining view.
- **Current strengths.** Context-first inheritance is crisply specified; the reference doc (`how-to-generate-interesting-dashboards.md`) is a real playbook (discovery → palette → layout → anti-patterns); "never invent findings numbers" guard; text-widget-as-narrative discipline.
- **Weaknesses.** `context`-field table and inheritance semantics are **~90% identical to `reports`** — two copies to maintain. Grid-sizing heuristics are dashboard-only knowledge with no shared home.
- **Missing knowledge.** No cross-reference to a shared "context-first inheritance" definition; no accessibility/color guidance (compare to the `dataviz` skill available in the environment).
- **Missing business rules.** No rule for *how many widgets is too many*; no rule on when a dashboard should become a scheduled report instead.
- **Missing examples.** Multi-provider comparison dashboard; a unit-economics-first dashboard; copying a full dashboard (only single-widget copy shown).
- **Suggested refactoring.** Extract the context-first inheritance model to `knowledge/capabilities/reporting/context-inheritance.md`; both `dashboards` and `reports` render from it.
- **Dependencies.** `get_context`, `search`, `query`, `suggest_groupby`, `suggest_usage_metrics`, `create_dashboard`, `update_dashboard`, `get`.
- **Reusable components.** Context-first inheritance; widget palette; 12-col layout recipe; `compare:{}` auto-previous-period; unit-economics widget.
- **Foundation entities.** All `cos_*`, VirtualDimension, saved/usage metrics.
- **Suggested new skills.** None (well-scoped). Could absorb a `dataviz`-style color/accessibility reference.
- **Suggested playbooks.** "Investigate → persist as dashboard → schedule as report" chain.
- **Migration effort.** **Low-Medium** (shared inheritance extraction touches two skills).

### 3.3 `reports`

- **Summary.** Named workflows (Schedule / Explain / Update / Run / Explore). Eight "must-follow rules" as a contract. DIGEST change-tree with opt-in AI. Delivery safety (data-lag Tuesday rule, ask-before-build, destinations-last).
- **Capability.** Reporting (+ Cost Intelligence via DIGEST).
- **Business purpose.** Deliver the right FinOps narrative to the right channel on the right cadence — safely.
- **Current strengths.** The strongest *operational-safety* skill in the repo: explicit confirm-gates, `datePreset`-never-frozen-dates on schedules, the ~2-day data-lag → Tuesday/`TRAILING_7_DAYS` rule, AI-opt-in trade-off spoken aloud, preview=`widget` vs create=`widgets[]` Zod trap. Self-aware about stale lettered routing.
- **Weaknesses.** Shares the context/inheritance model with `dashboards` (duplication). DIGEST thresholds `100/5%/20` and the DIGEST widget block are re-stated in recipes (`explain-period-change`, `service-cost-weekly`).
- **Missing knowledge.** No shared "delivery-safety" doc (the data-lag rule is gold and should be Foundation-level, reusable by alerts/automation).
- **Missing business rules.** No rule for report *ownership hygiene* at scale (visibility defaults per audience); no escalation rule (what to do when a scheduled report keeps failing a destination).
- **Missing examples.** Teams and email destination payloads (only Slack `channelId` shown); a multi-widget report combining DIGEST + GRAPH + TEXT.
- **Suggested refactoring.** Extract (a) context-inheritance and (b) delivery-safety rules to `knowledge/`; keep the DIGEST semantics here but source the thresholds from Foundation so recipes stop copying them.
- **Dependencies.** `get_context`, `list_teams`, `suggest_groupby`, `list_available_destinations`, `preview_report_widget`, `create_report`/`update_report`, execution tools.
- **Reusable components.** Delivery-safety rules; DIGEST hierarchy mapping; AI-opt-in presets; TOP_FLOP rank-vs-movers convention.
- **Foundation entities.** All `cos_*`, VirtualDimension, Team/scope, Destination.
- **Suggested new skills.** `alerts` (shares delivery-safety + data-lag knowledge).
- **Suggested playbooks.** Explain → (if recurring) Schedule; DIGEST → drill node in `query`.
- **Migration effort.** **Low-Medium.**

### 3.4 `virtual-dimensions`

- **Summary.** Build custom cost axes from ordered CEL rules (first-match-wins) with `dimensionValue`/`existingColumn`/`splitCost`/`telemetry` allocations; draft→preview→publish lifecycle; leftover & overlap/shadowing analysis.
- **Capability.** Cost Allocation (+ Governance).
- **Business purpose.** Make cloud spend answer to the *business's* structure (Environment, Team, Prod/R&D, Product line) when providers ship no clean axis.
- **Current strengths.** Excellent state-machine rigor: `draftPersisted` semantics, sticky rule ids, "strategy approval ≠ rule approval," `bqName` immutability, `computeStatus` polling, shadowing detection. Strong "ask for expected values, don't invent buckets" guard.
- **Weaknesses.** Dense (single 203-line wall); the VDIM lifecycle and `bqName` rule are duplicated into `prod-vs-rnd-vdim` and `reallocate-by-external-metric` recipes.
- **Missing knowledge.** No worked `regexMapping` example (only prose); no guidance on VDIM versioning/rollback strategy.
- **Missing business rules.** No target leftover threshold as a *policy* (10–20% is a heuristic, not a governance SLO); no rule on who may publish (Clerk-only is stated, but no approval workflow).
- **Missing examples.** Full `telemetry` `regexMapping` payload; `existingColumn` end-to-end; overlap-matrix output interpretation walk-through.
- **Suggested refactoring.** Extract the lifecycle + `bqName` rule to `knowledge/capabilities/cost-allocation/vdim-lifecycle.md`; recipes reference it.
- **Dependencies.** `search`, `query`, `suggest_groupby`, `list_metrics`, VDIM tool family.
- **Reusable components.** VDIM lifecycle; `bqName` rule; allocation-shape catalog; leftover/shadowing heuristics.
- **Foundation entities.** VirtualDimension (defines Environment/Team/CostCenter/BU/Owner in practice), all `cos_*`, telemetry datasources.
- **Suggested new skills.** `governance` (allocation-coverage SLOs build on VDIM leftover + untagged-coverage).
- **Suggested playbooks.** Build axis → explore → schedule exec report (the prod-vs-rnd triangle formalized).
- **Migration effort.** **Medium** (lifecycle extraction + recipe re-link).

### 3.5 `recipes` *(meta-skill / router)*

- **Summary.** Outcome→recipe→mechanics-skill router. 14 cards, each a payload skeleton + handoff. Regular structure: When/Audience/Outcome · Tool sequence · Payload skeleton · Confirm · Gotchas · Brief · Hand off.
- **Capability.** Automation / Playbook router (spans all capabilities).
- **Business purpose.** Turn a stated *business outcome* ("explain the bill jump", "showback K8s by namespace") into a confirmed, buildable design without the user knowing the tool surface.
- **Current strengths.** The "Pick a recipe" table with triggers + "not this if" + quick-disambiguation is excellent routing UX. Cards are business-outcome-first (inputs are Team/App/Env, not CSV/table). Hand-authored cousin cross-references form a usable recipe graph.
- **Weaknesses.** **Recipes are single-hop.** Each routes to *one* mechanics skill; there is no multi-step orchestration. Heavy cross-recipe duplication (12 patterns — see §5). `index.json` `category` is a flat single tag and doesn't cover the "dashboard" outcome (`budget-vs-actual` is tagged `budget`).
- **Missing knowledge.** No recipe-authoring schema beyond prose; no machine-readable card structure (the regular template begs for a schema).
- **Missing business rules.** No rule for composing two recipes (explicitly deferred: "don't blend until asked") — which is exactly what playbooks need.
- **Missing examples.** No multi-skill playbook card.
- **Suggested refactoring.** (a) Add a `playbooks/` tier above recipes for multi-step orchestration (§7); (b) extract the shared skeleton fragments (report skeleton, DIGEST block, VDIM lifecycle, null-CEL caveat, TOP_FLOP convention) to `knowledge/`; (c) formalize the card structure as a schema and validate `index.json` against the files in CI.
- **Dependencies.** All mechanics skills; all discovery tools.
- **Reusable components.** The card template itself; the routing table; the cousin-graph.
- **Foundation entities.** All (recipes are the demand-side catalog of Foundation usage).
- **Suggested new skills.** Recipes for the missing capabilities once their mechanics skills exist: `forecast-spend`, `recommend-savings`, `analyze-anomaly`, `analyze-deployment-impact`.
- **Suggested playbooks.** This skill becomes the natural home for the playbook index.
- **Migration effort.** **Medium** (extraction + schema + new playbook tier).

---

## 4. Prompt-quality assessment (cross-cutting)

Evaluated per the checklist (ambiguity, verbosity, hidden assumptions, hallucination risk, missing constraints):

- **Ambiguity:** Very low. Routing tables, "not this if" columns, and named (not lettered) workflows disambiguate aggressively. `reports` even flags its own stale lettered routing.
- **Verbosity:** Occasionally high (`query` 548 lines, `virtual-dimensions` dense). Acceptable given self-containment, but a shared-knowledge layer would let each skill shrink to its unique content.
- **Hidden assumptions:** Few. Confirm-gates surface most. One latent one: skills assume `cos_*` fields exist for the org — mitigated by mandatory `search` discovery.
- **Hallucination risk:** **Actively engineered down** — "never invent a `datePreset` token / CEL field / findings number / VDIM bucket." This is the repo's best trait and should be a Foundation-level *shared rule set* so new skills inherit it automatically.
- **Missing constraints:** Multi-currency handling, forecast confidence, and governance thresholds (leftover %, coverage %) are under-specified as *policy*.

**Prompt quality is the standout dimension — 5/5.** The knowledge-engineering work is about *not letting it rot* as the surface grows.

---

## 5. Knowledge-engineering — duplication catalog → extraction targets

The subagent audit found 12 recurring patterns. Grouped by extraction target, **with the self-containment constraint applied** (what stays inline vs what becomes a loadable reference):

| # | Duplicated knowledge | Appears in | Extraction target | Inline or reference? |
|---|----------------------|-----------|-------------------|----------------------|
| 1 | `DatePreset` 16-value enum | query (auth), recipes, dashboards, reports | `knowledge/.../datepreset.md` | **Source → rendered inline** (runtime-critical) |
| 2 | SCOPE vs SPLIT (filterCel/groupBy) | query, compute-drilldown, dashboards ref, MCP header | `.../scope-vs-split.md` | Source → rendered inline |
| 3 | Context-first inheritance model | dashboards, reports (≈90% identical) | `capabilities/reporting/context-inheritance.md` | Source → rendered inline in both |
| 4 | CEL null-exclusion rule (`== null`, never `is_null`/`"null"`) | query, virtual-dimensions, namespace-cost, untagged | `.../cel-conventions.md` | Source → rendered inline |
| 5 | `bqName` (immutable) vs `name` rule | virtual-dimensions + 4 recipes | `capabilities/cost-allocation/vdim-lifecycle.md` | Source → rendered inline |
| 6 | VDIM lifecycle (draft→preview→publish→poll) | virtual-dimensions, prod-vs-rnd-vdim, reallocate | same as #5 | Reference (recipes link) |
| 7 | DIGEST thresholds `100/5%/20` + widget block | reports, explain-period-change, service-cost-weekly | `capabilities/cost-intelligence/digest.md` | Source → rendered inline in reports; recipes reference |
| 8 | Standard scheduled-report skeleton | 6 report recipes | `examples/report-skeleton.json` | Reference (recipe fragment) |
| 9 | TOP_FLOP rank-vs-movers convention (`10/0` vs `10/10`) | 6 recipes | business rule in `business-rules.md` | Reference |
| 10 | Two-legs-`a/b` formula family (coverage/utilization/unit-cost) | untagged, reallocate, budget-vs-actual, dashboards ref | `metrics.md` derived-metrics | Reference |
| 11 | Canonical CEL constants (`compute` service list, `cos_marketplace_purchase`, `cos_charge_category`) | compute-drilldown, ec2-alert, marketplace, untagged, credits | `examples/cel-constants.md` | Reference |
| 12 | Cousin cross-reference network (hand-maintained) | ~9 recipes | generated `recipe-graph.json` from card metadata | Reference |
| 13 | "Never invent token/field/number/bucket" guards | every skill | `business-rules.md` → shared guard set | Source → rendered inline |
| 14 | Data-lag → Tuesday/`TRAILING_7_DAYS` rule | reports, (should also govern alerts) | `capabilities/reporting/delivery-safety.md` | Source → rendered inline |

**The mechanism, not just the targets.** Because skills must stay self-contained:

1. Author each convention **once** under `knowledge/`.
2. A small build step **renders** the runtime-critical ones into a `<!-- BEGIN foundation:datepreset -->…<!-- END -->` block inside each `SKILL.md` (same pattern the Beads block already uses in `AGENTS.md` — this repo already trusts generated blocks).
3. **CI lint** (extend the existing `.github/workflows/lint.yml`) fails if a rendered block drifts from its source, and if `index.json` disagrees with the recipe files.
4. Deeper/optional knowledge (lifecycle detail, skeleton fragments, CEL constants) stays as **loadable references** — `get_skill` can already load by path (`dashboards` does exactly this for its reference doc).

This gives DRY *authoring* without sacrificing self-contained *delivery* — the only way to do knowledge extraction here without breaking compatibility.

---

## 6. Missing skills (mapped to existing tools vs product gaps)

Split by whether the MCP surface already supports them:

### Buildable **today** (tools already exist — highest ROI)

| Proposed skill | Capability | Backing tools (present) | Serves Costory pillar |
|----------------|-----------|--------------------------|------------------------|
| **`alerts` / `analyze-anomaly`** | Automation / Governance | `create_alert`, `preview_alert`, `list_alerts` | "make FinOps decisions" / anomaly |
| **`events` / `analyze-deployment-impact`** | Cost Intelligence | `create_event`, `update_event`, `list_events` + `query` | **"correlate costs with engineering events"** (a stated core pillar, currently orphaned) |
| **`recommendations`** (`RecommendSavingsPlan`, `RecommendRightsizing`, `PrioritizeRecommendations`, `ExplainRecommendation`) | Recommendations / Optimization | `suggest_actions` + `query` H (effective savings) | "generating recommendations" |
| **`docs-lookup`** (minor) | — | `search_documentation`, `get_documentation_page` | self-service help |

`ec2-cost-spike-alert` is proof the alert tools work — it just lives as a one-off recipe with no owning mechanics skill to generalize from.

### Blocked on product capability (flag, don't build)

| Proposed skill | Capability | Gap |
|----------------|-----------|-----|
| **`forecast-spend`** (`ForecastSpend`, `DetectCostRegression`) | Forecasting | No forecast tool in the MCP surface. Costory claims forecasting — confirm whether the backend exposes it; if yes, wrap it; if no, this is a product gap to escalate. |
| **`unit-economics`** (first-class) | Unit Economics | Partially covered by `query` E + reallocate; separate `finops-unit-economics*` skills exist in other plugins — decide whether to import/alias or keep delegated. |

### Cross-cutting capability skills worth their own home

- **`governance`** — allocation-coverage SLOs (build on VDIM leftover + `untagged-coverage`), budget/commitment governance, tagging policy, anomaly-alert policy. Ties together three things that today are scattered.
- **`optimization`** — rightsizing + commitment coverage + effective-savings *actions* (not just the `query` H analysis).

**Priority order:** `events` (orphaned core pillar) > `recommendations` (orphaned tool + stated pillar) > `alerts` (generalize the working recipe) > `governance` > `forecast` (verify product support first).

---

## 7. Playbooks — the orchestration tier that doesn't exist yet

Today's recipes are **single-hop**: outcome → one mechanics skill. The mission's canonical playbook requires **multi-step orchestration** across skills, which no card expresses. This is the biggest *capability-shaped* opportunity.

### Canonical playbook (from the mandate) — feasibility today

```
Bill increased
  ↓ ExplainCostIncrease      → explain-period-change ✅ exists
  ↓ CorrelateDeployments     → events skill          ❌ missing (tools exist)
  ↓ CorrelateIncidents       → events skill          ❌ missing (tools exist)
  ↓ FindCostDrivers          → query / DIGEST drill   ✅ exists
  ↓ EstimateSavings          → recommendations skill  ❌ missing (suggest_actions exists)
  ↓ GenerateSummary          → reports DIGEST summary  ✅ exists
```

**Three of six steps are missing** — and all three are backed by existing tools (§6). Delivering `events` + `recommendations` unlocks this entire playbook.

### Playbooks worth defining (in priority order)

1. **Spend-spike triage** (the canonical one above) — the flagship; unlocks once `events` + `recommendations` exist.
2. **Monthly close** — `explain-period-change` DIGEST → exec summary → schedule (`env-costs-cto`/`invoice close`). Expressible *today* by chaining existing recipes.
3. **Allocation campaign** — `untagged-coverage` baseline → build/extend VDIM → re-measure coverage → schedule the trend. Expressible today (VDIM + untagged + reports).
4. **Unit-economics rollout** — `query` E validate → `reallocate-by-external-metric` VDIM → dashboard + weekly report. Expressible today.
5. **Commitment optimization** — effective-savings analysis (`query` H) → `recommendations` → estimate → track. Needs `recommendations`.

**Recommendation:** add a `playbooks/` tier that composes recipes/skills with explicit gates between steps (each step's output is the next step's input; confirm before any mutation). The recipe card template already has the fields to support this — a playbook is a card whose "Hand off" is an *ordered list* of recipes rather than one mechanics skill. This is additive; recipes keep working unchanged.

---

## 8. Repository maturity assessment

Scored 1 (absent) – 5 (excellent), with justification.

| Dimension | Score | Justification |
|-----------|:----:|---------------|
| **Knowledge Model** | **4** | Deep, explicit *procedural* knowledge with anti-patterns and worked examples. Loses a point: *declarative* knowledge (entities, glossary, derived metrics) is implicit and re-derived per skill. |
| **Business Model** | **3** | Rich model in practice (`cos_*`, VDIMs, budgets, events) but never declared. No Customer Foundation artifact. |
| **Skill Reuse** | **3** | Excellent *handoff* reuse (recipes→mechanics). Poor *content* reuse: 14 duplication patterns, hand-synced, no source of truth. |
| **Prompt Quality** | **5** | Standout. Precise triggers, disambiguation, confirm-gates, hallucination guards, self-aware about stale routing. |
| **Architecture** | **4** | Clean plugin/marketplace layout, version-lockstep discipline, lint CI, deliberate self-containment, elegant recipe router. Missing a knowledge layer + drift control. |
| **Customer Foundation** | **2** | Essentially absent as an explicit layer — the highest-leverage gap. |
| **Playbooks** | **3** | Recipes are strong *proto-playbooks* (routing + single handoff) but no multi-step orchestration; canonical playbook not expressible. |
| **Governance** | **3** | *Operational safety* discipline is 5/5 (confirm-gates, delivery safety, data-lag, mutation guards). *FinOps governance capability* (policy, SLOs, commitment governance) is ~1. Averaged. |
| **Maintainability** | **3** | Version lockstep + lint + regular templates help. But duplication without a source of truth + a hand-maintained cross-ref graph is a maintenance tax that grows with every new skill. |

**Aggregate ≈ 3.4 / 5.** Interpretation: *a top-tier execution and prompt layer sitting on an unstated knowledge layer.* The path to 4.5+ is entirely additive — declare the Foundation, single-source the conventions, close the tool-backed skill gaps, add the playbook tier.

---

## 9. Roadmap

Every phase is **additive and compatibility-preserving**. Nothing rewrites a working skill; extractions become the *source* that renders back into the existing self-contained bodies.

### Phase 1 — Quick wins *(days; no behavior change)*

- Extend `.github/workflows/lint.yml`: (a) validate `index.json` ↔ recipe files agree; (b) assert the `DatePreset` enum text is identical everywhere it appears.
- Fix `index.json` category coverage (add a `dashboards`/`explore` tag for `budget-vs-actual`); document the flat-category limitation.
- Add a `metrics.md` derived-formula reference (`effective savings`, `waste ratio`, `coverage`, `utilization`, `unit cost`) — pure documentation, link from `query`.
- Write `entities.md` (the §2 table) as the first Customer Foundation file. Highest leverage per hour.

### Phase 2 — Knowledge extraction *(source-of-truth + render + lint)*

- Stand up `knowledge/` (tree below). Move the 14 duplicated patterns to canonical sources.
- Introduce the **render + drift-lint** mechanism (reuse the `<!-- BEGIN … -->` generated-block pattern already used for the Beads block). Runtime-critical conventions render inline; deeper knowledge becomes loadable references.
- Result: each skill shrinks to its unique content; conventions change in one place.

### Phase 3 — Customer Foundation *(complete the spine)*

- Complete `entities.md`, `glossary.md`, `business-rules.md` (TOP_FLOP rank-vs-movers, leftover thresholds, coverage denominator rules, data-lag), `finops-taxonomy.md` (the capability model), `metrics.md`.
- Model the three absent entities — **Recommendation, Forecast, typed Event (Deployment/Incident)** — which directly unblock the missing skills.

### Phase 4 — Playbooks *(orchestration tier)*

- Add `playbooks/`. Ship the expressible-today playbooks first (Monthly close, Allocation campaign, Unit-economics rollout).
- Build the tool-backed missing skills (`events`, `recommendations`, `alerts`) to unlock **Spend-spike triage** — the flagship playbook.

### Phase 5 — AI-native FinOps platform

- Close remaining capability gaps (`forecast` pending product confirmation; `governance`, `optimization` skills).
- The playbook tier + Customer Foundation + recommendations make the platform *proactive*: detect anomaly → correlate event → find drivers → estimate savings → recommend → summarize — end to end, which is the mission's north star.

### Proposed knowledge architecture (example)

```
knowledge/
├── customer-foundation/
│   ├── entities.md            # entity → canonical cos_* field → cardinality → VDIM status  (§2)
│   ├── glossary.md            # FinOps + Costory vocabulary (showback, runway, leftover, movers…)
│   ├── business-rules.md      # TOP_FLOP 10/0 vs 10/10, leftover %, coverage denom, data-lag, "never invent" guards
│   ├── finops-taxonomy.md     # the 10-capability model + skill→capability map
│   └── metrics.md             # cost columns + derived formulas (effective savings, waste ratio, coverage, utilization, unit cost)
│
├── capabilities/
│   ├── cost-intelligence/     # datepreset.md, scope-vs-split.md, digest.md, cel-conventions.md
│   ├── cost-allocation/       # vdim-lifecycle.md (bqName rule, draft→publish→poll), allocation-shapes.md
│   ├── reporting/             # context-inheritance.md (shared by dashboards+reports), delivery-safety.md
│   ├── optimization/          # (new) effective-savings, rightsizing, commitment coverage
│   ├── forecasting/           # (new, pending product) trend projection, regression detection
│   └── governance/            # (new) coverage SLOs, budget/commitment governance, tagging policy
│
├── skills/                    # the existing self-contained SKILL.md bodies (render targets)
│
├── playbooks/                 # (new) multi-step orchestration: spend-spike-triage, monthly-close, allocation-campaign, …
│
├── prompts/                   # reusable prompt fragments (confirm-gates, discovery preamble)
│
└── examples/                  # report-skeleton.json, cel-constants.md, worked payloads, good/bad/edge cases
```

Mapping to what exists: today's `plugins/costory/skills/*` **is** the `skills/` layer; `dashboards/references/` is the seed of the `capabilities/` layer; `recipes/` splits into `examples/` (skeletons) + `playbooks/` (orchestration). Nothing moves without a compatibility shim — the render step keeps the shipped `SKILL.md` bodies intact.

---

## 10. What NOT to do (compatibility guardrails)

- **Do not** de-duplicate skills into runtime imports — `get_skill` may not load `references/`; self-containment is a delivery contract, not an oversight.
- **Do not** rename skill folders / MCP `skillId`s — they are wired in `skills.json` and cross-referenced by name.
- **Do not** skip the three-place version bump (`marketplace.json`, `plugin.json`, `skills.json`) on any change.
- **Do not** weaken the confirm-gates or delivery-safety rules when consolidating — those are the repo's crown jewels; make them *shared*, not *softer*.
- **Do not** invent forecast behavior before confirming the backend exposes it.

---

*Prepared as an additive review. Every recommendation extends the existing repository; none deletes working knowledge.*
