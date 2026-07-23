# Skills review — issues to tackle (beads backlog)

Output of the all-skills review (workflow `costory-skills-review`, 38 agents, adversarial verify). **17 verified findings were fixed in the same pass** (v0.10.1); the items below are the remaining backlog to file in beads.

> **These 22 issues were filed live in beads** (IDs assigned — e.g. Unit Economics `…-31a`, Rate/Commitment `…-8wv`, get_dashboard_widget_image `…-55n`, disambiguation `…-dnn`, team-groupBy bug `…-6ac`). The Dolt write lock is **intermittent**, so the commands below are retained for reference only — **do not re-run them blindly, they would create duplicates**. A separate set of Phase 1–5 completion closes/deps still needs replaying when the lock frees (see `finops-kb-progress.md`).

## Fixed in this pass (v0.10.1)

| # | File(s) | Fix |
|---|---------|-----|
| Playbook misroute | events, recommendations, governance | `recipes` → `playbooks` for spend-spike-triage / allocation-campaign |
| Dead link | forecast | removed broken `../../knowledge/...entities.md` link |
| Dead pointer | recommendations | dropped `metrics.md` pointer → cite `query` H & G |
| Stale status | knowledge/entities.md | recommendations/forecast/events skills now exist |
| Boundary | optimization | reconciled sizing overlap with recommendations |
| Dimension naming | reports | bare `environment` → `cos_environment` (3 spots) |
| Catalog label | recipes/index.json | "Weekly Environment Costs" → "Monthly Environment Costs" |
| EMAIL destination | reports + 5 recipes | EMAIL uses `email` not `channelId`; documented all 3 shapes |
| Telemetry accuracy | reallocate-by-external-metric | live external metric validates only; split needs a saved datasource |
| Safety gate | events | confirm before create_event / update_event |
| Browse surface | marketplace.json, plugin.json | descriptions now list all 12 skills |


## Open backlog

| Priority | Value/Effort | Capability | Title |
|---|---|---|---|
| P2 | medium/low | reports correctness | reports DIGEST examples: confirm the `team` groupBy dimension name |
| P1 | high/medium | Report-execution lifecycle: retry a fa | Flesh out reports Run workflow with retry/transfer/archive tool steps |
| P1 | high/medium | Cost Optimization | Add Rate & Commitment Optimization skill (coverage + effective-savings-rate) |
| P1 | high/medium | Unit Economics | Add dedicated Unit Economics skill (cost-per-unit via query formula) |
| P1 | high/medium | Router discoverability / onboarding | Extend recipes router to cover the 7 new capability skills + surface playbooks tier |
| P1 | high/medium | Disambiguation | Add a cross-skill disambiguation table for recommendations/optimization/governance/forecas |
| P1 | high/low | Enumerate the org's reports with statu | Add report-inventory workflow using list_reports |
| P1 | high/low | Render a saved dashboard widget as a P | Add get_dashboard_widget_image share-as-image workflow to dashboards skill |
| P1 | high/low | Answer 'how do I / what is' Costory pr | Add docs-lookup capability and wire it into forecast product-boundary handoffs |
| P1 | high/low | Safer defaults / guardrails | events skill: gate create_event/update_event behind explicit user confirmation |
| P2 | medium/medium | Budget Management | Add budget governance / burn-rate skill (pace, projected breach, breach alert) |
| P2 | medium/medium | Unit Economics | Add AI/LLM cost skill (spend visibility + cost-per-token unit economics) |
| P2 | medium/low | A standing alert that fires on budget  | Add budget-pace alert worked example to alerts skill |
| P2 | medium/low | Deliver an alert notification or a rep | Add Slack DM (U… id) delivery note to alerts and reports destination guidance |
| P2 | medium/low | Remove obsolete or duplicate event tag | Add delete_tag cleanup step to events/governance tagging hygiene |
| P2 | medium/low | Scope a query or an alert to a saved t | Document scopeId team scoping in query and alerts skills |
| P2 | medium/low | Automation | Add anomaly triage & attribution playbook (spike to root-cause annotation) |
| P2 | medium/low | Better handoffs | Audit and update recipe 'Hand off' targets now that alerts/events/recommendations/forecast |
| P2 | medium/low | Browse/install discoverability | Sync README and marketplace/plugin descriptions with the full 12-skill roster |
| P3 | low/medium | Unit Economics | Investigate sustainability/carbon-vs-cost view (gated on carbon metric ingestion) |
| P3 | low/low | Fetch the cost data behind an existing | Add get_dashboard_widget_data re-run-saved-widget mini-workflow |
| P3 | low/low | Render a period-over-period comparison | Add KPI_BREAKDOWN when-to-use note and example to dashboards/query compare |

## Runnable `bd create` commands

```bash
bd create --type=bug --priority=2 --title='reports DIGEST examples: confirm the `team` groupBy dimension name' --description='[reports correctness] reports/SKILL.md uses bare groupBy `team` (hierarchy table row '"'"'team → service'"'"' and the migration-tracker example). `environment` was corrected to `cos_environment`, but `team` is ambiguous — team is documented as an org scope (scopeId/list_teams), not a guaranteed cost dimension. Confirm the correct team cost-dimension bqName (e.g. cos_team or a VDIM) or convert to a discovery placeholder resolved via search type:[dimensions]/suggest_groupby.'
bd create --type=task --priority=1 --title='Flesh out reports Run workflow with retry/transfer/archive tool steps' --description='[Report-execution lifecycle: retry a failed delivery, re-deliver a rendered report to new destinations without recompute, and archive stale reports.] Gap: plugins/costory/skills/reports/SKILL.md '"'"'Workflow: Run — run, retry, transfer, archive'"'"' (lines ~163-165) is a 3-line stub naming the actions but no tools; retry_report_execution, transfer_report_execution, archive_report have 0 references across all skills.

Change: expand the Run workflow with a concrete, confirm-gated step for each:
- retry_report_execution { executionId } — retries ONE failed delivery only; first call get_report_execution to state the failed destination, then confirm. Never use run_report_now to fix a destination (already stated).
- transfer_report_execution { executionId, destinations[] } — re-delivers an already-rendered execution to 1-10 NEW destinations without recomputing widgets; resolve channels with list_available_destinations; DANGER ZONE, list every target and confirm. Note destinations use the same shape as create_report and Slack channelId accepts C... (channel) OR U... (DM).
- archive_report { reportId } — soft delete, no MCP restore; confirm before calling.

Acceptance: each has a one-line when-to-use, the exact required params, and an explicit user-confirmation gate in the anti-patterns list. Add list_available_destinations + get_report_execution to the tool-order for this workflow.'
bd create --type=feature --priority=1 --title='Add Rate & Commitment Optimization skill (coverage + effective-savings-rate)' --description='[Cost Optimization] Ship a Costory-plugin skill that delivers the FinOps Rate Optimization capability using existing query cost columns only.

Scope:
- Effective savings rate: formula over list_cost and effective_cost series (savings = list_cost - effective_cost; rate = savings / list_cost), trended with compare period-over-period.
- Commitment amortization view: amortized_cost / net_amortized_cost vs unblended_cost to show what commitments contribute vs on-demand.
- Negotiated-rate delta: contracted_cost vs list_cost.
- Coverage split by provider/service via suggest_groupby, packaged as a dashboard + scheduled report.

Grounding/constraints:
- Use ONLY query (metricId enum: cost, effective_cost, list_cost, contracted_cost, unblended_cost, net_unblended_cost, amortized_cost, net_amortized_cost), formula series, compare, rollingAggregation, search(type=dimensions), suggest_groupby, create_dashboard, create_report. No rightsizing/recommendation engine exists — analysis only.
- Before claiming RI/SP/CUD utilization, probe commitment dimensions via search(type=dimensions); if absent, degrade to effective-rate + savings-realization and say so.

Acceptance: skill maps to Cost Optimization capability; example payloads validate against live query schema; no tool outside the ground-truth inventory referenced.'
bd create --type=feature --priority=1 --title='Add dedicated Unit Economics skill (cost-per-unit via query formula)' --description='[Unit Economics] Promote unit economics from a query workflow footnote to a standalone Costory-plugin skill delivering cost-per-unit-of-business-value.

Scope:
- Denominator discovery: list_metrics for saved business metrics; suggest_usage_metrics (requires a filterCel scope) for infra usage units; externalMetric (tsuga/bigquery) when no saved metric matches.
- Unit cost: formula series '"'"'a / b'"'"' where a=cost series, b=metric/usage/externalMetric series.
- Trend + splits: compare for period-over-period unit-cost movement; groupBy team/product/environment; scopeId for saved team scopes.
- Package as dashboard widget(s) + scheduled report.

Grounding/constraints:
- query type=formula requires single-letter names (a,b,c); denominators require metricId from list_metrics (saved) or suggest_usage_metrics (usage) or full externalMetric block. Keep the ground-truth boundary: no forecast/recommendation tool.
- Clarify relationship to the Tsuga-based finops-unit-economics-* skills (this is Costory-native; those pair Tsuga metrics with GCP cost) to avoid overlap.

Acceptance: skill maps to Unit Economics primary capability; formula/denominator payloads validate against query schema; cross-links reallocate-by-external-metric for allocation-driven denominators.'
bd create --type=task --priority=1 --title='Extend recipes router to cover the 7 new capability skills + surface playbooks tier' --description='[Router discoverability / onboarding] Problem: plugins/costory/skills/recipes/SKILL.md is the outcome->skill router but references only the 14 recipe cards and the 4 original mechanics skills. It never routes to events, alerts, recommendations, forecast, governance, optimization, or the playbooks tier (confirmed by grep). Users stating outcomes served by the new skills are not routed there by the router; they rely solely on per-skill frontmatter triggering. Routing is also one-directional (playbooks links to recipes, not vice-versa), so spend-spike-triage is under-discoverable.

Do:
1. Add a top section (or new rows) in recipes/SKILL.md '"'"'Pick a recipe'"'"' mapping capability-level outcomes to the owning skill: cut/save cost -> recommendations (+ optimization for the method); on pace / month-end projection -> forecast; within policy / coverage SLO -> governance; alert me / anomaly monitor -> alerts; log a deploy / correlate a spike with an event -> events.
2. Add a signpost: single build -> recipe; multi-step investigation or rollout -> playbooks (mirror the note playbooks/SKILL.md already has pointing the other way), listing the 4 playbook cards.
3. Update the recipes frontmatter description to mention the capability skills so the router itself triggers on those outcomes.

Constraints: additive only; keep self-contained; bump version in lockstep across .claude-plugin/marketplace.json, plugins/costory/.claude-plugin/plugin.json, skills.json (patch/minor per AGENTS.md).

Acceptance: from a cold start, an outcome phrased for each of the 7 new skills and each playbook is reachable via the recipes router table, and recipes signposts up to playbooks.'
bd create --type=feature --priority=1 --title='Add a cross-skill disambiguation table for recommendations/optimization/governance/forecast/alerts' --description='[Disambiguation] Problem: the 5 capability skills added in Phase 4/5 have overlapping trigger phrases (savings, rightsizing, commitment coverage, waste, budget pace, on-pace). An agent picking a skill from frontmatter alone can load the wrong one or bounce between recommendations and optimization (which are companion skills). No central tiebreaker exists.

Do: add a '"'"'Quick disambiguation'"'"' table (same style as recipes/SKILL.md) covering the sound-alike asks and the preferred skill, e.g.:
- '"'"'how much can we save'"'"' / action plan -> recommendations (entry point); '"'"'how do I compute/size this lever'"'"' -> optimization
- '"'"'are we on pace / month-end projection'"'"' -> forecast; '"'"'notify me when spend spikes/breaches'"'"' -> alerts; '"'"'are we within our target/SLO over time'"'"' -> governance
- '"'"'commitment coverage'"'"': size it -> optimization; rank+present the plan -> recommendations; make it a target we track -> governance
Place it either in the recipes router (so it is hit centrally) and/or as a short shared '"'"'When NOT this skill, use X'"'"' block near the top of each of the 5 skills. Keep each skill self-contained.

Constraints: additive; lockstep version bump.

Acceptance: for each sound-alike ask above, the table names one preferred skill and the agent has a deterministic tiebreaker before loading a body.'
bd create --type=task --priority=1 --title='Add report-inventory workflow using list_reports' --description='[Enumerate the org'"'"'s reports with status, cadence, next run date, destination counts, and last-run health — the read side of report fleet management.] Gap: list_reports (read-only) is unused by every skill. Users cannot audit their report fleet through the skills.

Change: add a short '"'"'Review / inventory'"'"' workflow to plugins/costory/skills/reports/SKILL.md and its tool-order:
- list_reports {} for the full list; { kind: '"'"'SCHEDULED'"'"' } to see standing reports; { teamId } for one team; { includeArchived: true } to include archived.
- Surface lastRunHealth and nextRunDate to answer '"'"'which reports failed?'"'"' and '"'"'what runs next?'"'"'.
- Route health failures into the Run workflow (retry_report_execution) and stale reports into archive_report.

Acceptance: workflow shows the filter params, states it is read-only, and links a failing lastRunHealth to the retry step.'
bd create --type=feature --priority=1 --title='Add get_dashboard_widget_image share-as-image workflow to dashboards skill' --description='[Render a saved dashboard widget as a PNG and return it inline in chat (base64) plus a GCS URL, for visual snapshots and Slack/chat embeds.] Gap: plugins/costory/skills/dashboards/SKILL.md mentions get_dashboard_widget_image only as a KPI_BREAKDOWN/TABLE export caveat (line 82); there is no workflow teaching it.

Change: add a short workflow: get (dashboard) -> pick widgetId -> get_dashboard_widget_image { dashboardId, widgetId }. Note it returns imageUrl (GCS PNG) and, by default, an inline base64 PNG (set includeBinaryImage:false for URL-only when payload is large); it applies the same conditionsCel merge as get_dashboard_widget_data; it does NOT work for text or table-only widgets (UNSUPPORTED_WIDGET) — keep the existing KPI_BREAKDOWN/TABLE-not-exportable caveat.

Acceptance: workflow gives the required params, the widget-type limitation, and when to use includeBinaryImage:false.'
bd create --type=task --priority=1 --title='Add docs-lookup capability and wire it into forecast product-boundary handoffs' --description='[Answer '"'"'how do I / what is'"'"' Costory product questions from the public docs, including surfacing in-product features the MCP itself cannot perform.] Gap: search_documentation and get_documentation_page have 0 references. Product/how-to questions and in-product-feature handoffs are unsupported.

Change: (a) add a brief '"'"'Answer product questions from docs'"'"' note to a shared surface (e.g. query and/or a small addition to each skill'"'"'s Related section): search_documentation { query } -> get_documentation_page { page } for '"'"'how do I X in Costory'"'"' questions. (b) In forecast/SKILL.md, where it points users to in-product '"'"'Forecasting with TimesFM'"'"' (features/budgets), have the skill fetch that page via get_documentation_page { page: '"'"'features/budgets'"'"' } so the user gets the actual guidance instead of just a pointer.

Acceptance: forecast surfaces the TimesFM doc page content; a docs-lookup pattern (search -> get page) is documented once and referenced where product boundaries are drawn.'
bd create --type=task --priority=1 --title='events skill: gate create_event/update_event behind explicit user confirmation' --description='[Safer defaults / guardrails] Problem: plugins/costory/skills/events/SKILL.md fires create_event (Workflow A step 4) and update_event (Workflow C) with no confirm-gate, inconsistent with alerts (confirm before create_alert), reports (ask-before-build), and virtual-dimensions (publish gate), and with AGENTS.md '"'"'mutations require explicit user confirmation'"'"'. There is no delete_event tool in the MCP surface, so an accidental event write cannot be undone via MCP.

Do:
1. In Workflow A, insert a confirm step: draft the event + widget, restate it, and require explicit user confirmation before create_event.
2. Same for Workflow C before update_event.
3. Add a Safety/Anti-patterns line: '"'"'Do not create_event/update_event without explicit confirmation - there is no delete_event; a written annotation can only be edited, not removed via MCP.'"'"'

Constraints: additive; lockstep version bump; keep skill self-contained.

Acceptance: both event-writing workflows and the Safety section require an explicit confirm before the mutating tool call, matching the pattern in alerts/reports/virtual-dimensions.'
bd create --type=feature --priority=2 --title='Add budget governance / burn-rate skill (pace, projected breach, breach alert)' --description='[Budget Management] Close the Budget Management gap with a burn-rate/governance skill over EXISTING budgets (no create_budget tool exists).

Scope:
- Resolve budget: search then get to resolve budgetVersionId from the parent budget id; use costMetricId/currency from get to align actuals with the budget.
- Burn-rate: query budget series with aggBy=Day + rollingAggregation{aggregator:SUM, window:{preset:MONTH}} to show month-to-date running total vs plan and the day the budget is reached.
- Pace + projection: actual-vs-plan with compare; run-rate projection to month/quarter end (statistical forecast stays in-product TimesFM — link, don'"'"'t fake).
- Governance alerts: create_alert with monthToDateSum/rollingSum conditions; preview_alert to validate firing before saving; dedup CALENDAR MONTH.

Grounding/constraints:
- Use only query(type=budget), get, create_alert/preview_alert/list_alerts, create_dashboard. No update_alert (create-only) and no create_budget.

Acceptance: skill maps to Budget Management (secondary Governance); budget/alert payloads validate against schemas; explicitly states budgets are created in-product.'
bd create --type=feature --priority=2 --title='Add AI/LLM cost skill (spend visibility + cost-per-token unit economics)' --description='[Unit Economics] Add a skill for the FinOps '"'"'cost of AI'"'"' scope, grounded in query with a graceful-degradation contract.

Scope:
- Isolate AI spend: query filterCel on cos_service_name for AI/ML services (discover exact values via search type=dimensions on service dimension); trend + share-of-total via compare.
- Cost-per-unit: if token/inference metrics exist (suggest_usage_metrics for usage, list_metrics for saved, externalMetric for live), formula series cost / tokens (or / inferences).
- Splits by model/team/environment via groupBy.

Grounding/constraints:
- Contingent capability: cost-per-token requires an ingested token/inference metric. Skill MUST detect absence (empty suggest_usage_metrics/list_metrics for the scope) and degrade to spend-visibility-only, stating the dependency.
- Uses only query, suggest_usage_metrics, list_metrics, search, create_dashboard.

Acceptance: skill maps to Unit Economics (secondary Cost Intelligence); AI-service filter and formula payloads validate; documents the token-metric prerequisite.'
bd create --type=feature --priority=2 --title='Add budget-pace alert worked example to alerts skill' --description='[A standing alert that fires on budget pace/overspend, using a budget-type query leg — not just cost thresholds.] Gap: plugins/costory/skills/alerts/SKILL.md only shows cost-query alerts, yet '"'"'on pace to blow the budget'"'"' is an advertised trigger and governance references budget alerts. No example uses a budget query leg.

Change: add a budget-pace pattern: resolve budgetVersionId (search type budgets -> get), then preview_alert/create_alert with two query legs — a cost leg (a) and a budget leg (b, type '"'"'budget'"'"', budgetId = budgetVersionId) — and a condition comparing month-to-date cost against budget (e.g. monthToDateSum(a) > monthToDateSum(b)). Keep preview-first and destinations-last rules. Cross-link governance Workflow B.

Acceptance: one preview_alert + one create_alert JSON with a budget query leg and a pace condition, plus the search->get budgetVersionId step.'
bd create --type=task --priority=2 --title='Add Slack DM (U… id) delivery note to alerts and reports destination guidance' --description='[Deliver an alert notification or a report to a person'"'"'s Slack DM instead of a channel.] Gap: alerts/SKILL.md and reports/SKILL.md only illustrate C... channel ids; the U... DM option is undocumented although the schemas support it and list_available_destinations returns the caller'"'"'s DM target.

Change: in both skills'"'"' destination sections, note that a Slack channelId/slackChannelId may be a channel id (C...) OR a user id (U...) for a direct message, and that list_available_destinations lists both bot-accessible channels and the signed-in user'"'"'s DM. Add a one-line '"'"'DM me'"'"' example.

Acceptance: both skills state the C... vs U... distinction and where to find the DM target; existing destinations-last confirm rules still apply.'
bd create --type=task --priority=2 --title='Add delete_tag cleanup step to events/governance tagging hygiene' --description='[Remove obsolete or duplicate event tags to keep the tag vocabulary clean — the write side of the '"'"'don'"'"'t invent parallel labels'"'"' rule.] Gap: delete_tag has 0 references. Events skill enforces tag reuse but provides no cleanup path for obsolete/duplicate tags.

Change: add a short tag-hygiene note (events/SKILL.md Workflow C or governance tagging-policy row): list_tags to review usage counts, then delete_tag { tagId } for tags with zero tagged resources. State that delete_tag errors if the tag is still in use, so list_tags-first is mandatory, and that this is org-wide cleanup (confirm before deleting).

Acceptance: a documented list_tags -> delete_tag cleanup step with the zero-usage precondition and a confirm gate.'
bd create --type=task --priority=2 --title='Document scopeId team scoping in query and alerts skills' --description='[Scope a query or an alert to a saved team scope (scopeId) so results/monitors respect team ownership boundaries.] Gap: scopeId is used in reports/dashboards/recipes but never mentioned in query/SKILL.md or alerts/SKILL.md, although both query and create_alert accept it.

Change: add a short note to both skills: list_teams returns each team'"'"'s id, usable as scopeId to constrain a query or alert to that saved team scope (distinct from ad-hoc filterCel). Show one example applying a scopeId. Clarify scopeId (saved scope) vs filterCel (ad-hoc CEL) as in reports.

Acceptance: query and alerts each mention scopeId with the list_teams source and one example, and distinguish it from filterCel.'
bd create --type=feature --priority=2 --title='Add anomaly triage & attribution playbook (spike to root-cause annotation)' --description='[Automation] Wire the full FinOps anomaly-management lifecycle as a playbook composing existing tools.

Scope:
1. Detect: create_alert with rollingSum/timeShift/weekToDateSum condition (or query rollingAggregation AVG baseline for a smoothed reference); preview_alert to tune firing.
2. Triage: on the firing window, query with suggest_groupby to rank contributing dimensions (service, team, environment) and drill to the largest mover via compare (WATERFALL).
3. Attribute + annotate: create_event (category TECHNICAL/BUSINESS/PROVIDER) with a widget capturing the spike and the responsible dimension.
4. Notify/deliver: alert notificationChannel + optional report.

Grounding/constraints:
- Compose only existing tools; alerts are evaluated DAILY in BigQuery and are create-only. No native anomaly-detection ML tool — detection is window-function/baseline heuristics; state that ceiling.

Acceptance: playbook maps to Automation (secondary Cost Intelligence); references real query workflows and alert window-function grammar from ground truth; every step uses an inventory tool.'
bd create --type=task --priority=2 --title='Audit and update recipe '"'"'Hand off'"'"' targets now that alerts/events/recommendations/forecast/governance/optimization exist' --description='[Better handoffs] Problem: recipe cards predate the Phase 4/5 skills and still hand off as if those skills are absent. Confirmed in plugins/costory/skills/recipes/ec2-cost-spike-alert.md ('"'"'no separate mechanics skill'"'"') even though the alerts skill now owns that mechanics and its safety discipline (preview-first, condition-meaning guard, dedup, create-only/UI-edit).

Do:
1. Update ec2-cost-spike-alert.md to hand off to the alerts skill for mechanics/safety while keeping its frozen card defaults.
2. Sweep all 14 cards: where a card produces a savings estimate -> reference recommendations/optimization; budget pace -> forecast; coverage-as-policy -> governance; annotate/correlate a cause -> events. Add these as '"'"'Related/Next steps'"'"' or handoff refinements without changing the card'"'"'s own build.

Constraints: additive; do not weaken existing recipe skeletons; lockstep version bump.

Acceptance: no recipe claims '"'"'no mechanics skill'"'"' for a capability that now has an owning skill; each relevant card points to the mechanics skill that carries the guardrails.'
bd create --type=task --priority=2 --title='Sync README and marketplace/plugin descriptions with the full 12-skill roster' --description='[Browse/install discoverability] Problem: README.md '"'"'Skills'"'"' table and the marketplace.json/plugin.json descriptions still reflect the 5-skill era; they omit playbooks, events, alerts, recommendations, forecast, governance, optimization. skills.json already lists all 12 at v0.10.0, so the browse/install surface undercounts the plugin.

Do:
1. README.md: add the 7 missing rows to the Skills table (MCP skillId + '"'"'Use when'"'"'); update the Layout snippet if it enumerates skills.
2. plugins/costory/.claude-plugin/plugin.json description + .claude-plugin/marketplace.json metadata.description and plugins[].description: extend to mention alerts/anomaly, event correlation, savings recommendations & optimization, forecast/budget-pace, and governance/SLOs. Add matching keywords (alerts, events, recommendations, forecast, governance, optimization) to plugin.json keywords[].

Constraints: keep skillId/folder/name tokens consistent with skills.json; lockstep version bump only if a SKILL body also changes (metadata-only doc edits still bump per AGENTS.md three-place rule - verify).

Acceptance: README and both manifests list/describe all 12 skills; no capability shipped in skills.json is invisible on the browse surface.'
bd create --type=task --priority=3 --title='Investigate sustainability/carbon-vs-cost view (gated on carbon metric ingestion)' --description='[Unit Economics] Spike (not a committed build) for the FinOps Sustainability domain.

First step is a feasibility probe: call list_metrics (and includeExternal search '"'"'carbon'"'"'/'"'"'co2'"'"'/'"'"'emissions'"'"') to determine whether any carbon/emissions metric is ingested.
- If present: build a dashboard trending cost alongside the carbon metric and a formula series for carbon-per-dollar / carbon-per-unit — identical pattern to the unit-economics skill.
- If absent: close as blocked-on-data; there is no native carbon column and no product feature to synthesize one.

Grounding/constraints:
- Purely composed of existing tools (list_metrics, query type=metric/externalMetric + formula, create_dashboard); no carbon-specific tool exists. Keep effort low until data availability is confirmed.

Acceptance: probe result documented; build only proceeds if a carbon metric is found; otherwise recorded as product/data gap.'
bd create --type=task --priority=3 --title='Add get_dashboard_widget_data re-run-saved-widget mini-workflow' --description='[Fetch the cost data behind an existing dashboard widget by id, without re-specifying the query config.] Gap: get_dashboard_widget_data is only a table row in dashboards/SKILL.md (line 155); no workflow shows the get -> widgetId -> data flow.

Change: add a brief step: get (dashboard) -> get_dashboard_widget_data { dashboardId, widgetId } to return the stored widget'"'"'s series/comparison without re-specifying the query; it applies the dashboard conditionsCel unless the widget has extendDashboardConditions=false. Pair it with the widget-image workflow (data + image on the same widgetId).

Acceptance: a two-line workflow with required params and the conditionsCel-merge note.'
bd create --type=task --priority=3 --title='Add KPI_BREAKDOWN when-to-use note and example to dashboards/query compare' --description='[Render a period-over-period comparison as a headline KPI-delta view rather than a waterfall or table.] Gap: KPI_BREAKDOWN is listed as a compare.chartType enum value in dashboards/SKILL.md and query/SKILL.md but has no when-to-use or example.

Change: add a one-line guide: use compare.chartType KPI_BREAKDOWN for a headline single-number period-over-period delta (exec KPI tiles), WATERFALL (default) for driver decomposition, TABLE for a flat breakdown. Add a minimal compare: { chartType: '"'"'KPI_BREAKDOWN'"'"' } example. Keep the existing note that KPI_BREAKDOWN/TABLE cannot be exported via get_dashboard_widget_image.

Acceptance: dashboards (and query) state when to pick KPI_BREAKDOWN vs WATERFALL vs TABLE, with one example.'
```

