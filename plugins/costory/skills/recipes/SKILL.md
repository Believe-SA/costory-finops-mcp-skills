---
name: recipes
description: "Use when a user states a FinOps *outcome* rather than a tool. Route to one recipe file, then hand off: explain period change (why did the bill jump / what changed) → explain-period-change; marketplace / private-offer / invoice issuer spend → marketplace-spend; Kubernetes namespace / EKS / GKE showback → namespace-cost; credits / discounts / charge category runway → provider-credits; weekly eng pulse env→service → service-cost-weekly; tag coverage / untagged gaps → untagged-coverage; CTO / exec prod vs non-prod → env-costs-cto; reallocate shared cost by external or usage metric → reallocate-by-external-metric. Recipes say WHAT to build (payload skeletons); reports/dashboards/virtual-dimensions/query say HOW."
---

# Recipes

A **recipe** is a ready-made design for a common FinOps tracking goal — scope, split, period, widgets, delivery — as a **payload skeleton**, then a **hand off** to the mechanics skill (`reports`, `dashboards`, `virtual-dimensions`, `query`). Recipes never restate full delivery safety or live schema edge cases; fill placeholders after confirm, then build with the mechanics skill.

## How to use this skill

1. Match the user's goal using **Pick a recipe** below (triggers + "not this if").
2. **Read only that one file** under `plugins/costory/skills/recipes/`.
3. Run the card's **Tool sequence** through confirm gates — do not fire mutation/delivery tools until confirmed.
4. Fill `[PLACEHOLDERS]` from discovery + user answers; keep frozen fields as written.
5. Restate the **Brief**, then hand off the filled skeleton to the named mechanics skill.
6. If nothing matches → fall through to `reports` (or the relevant mechanics skill) and design from scratch.

## Skeleton contract

Every card has:

| Section | Role |
|---------|------|
| **When / Audience / Outcome** | routing + what "done" looks like |
| **Tool sequence** | ordered Costory MCP tool names (discover → confirm → preview → create) |
| **Payload skeleton** | JSON-shaped `context` / `widgets` / optional `query` with frozen defaults + `[PLACEHOLDERS]` |
| **Confirm before build** | gates that must be answered before preview/create/NOW/SCHEDULED |
| **Gotchas** | recipe-specific traps only |
| **Brief** | one-line restatement |
| **Hand off** | which mechanics skill owns the filled payload |

Placeholders are never invented: resolve via `get_context`, `search`, `suggest_groupby`, `list_available_destinations`, VDIM publish, or the user. Currency comes from `get_context`.

## Pick a recipe

Read the matching file. Do not improvise a blend of two cards until the user asks to combine them.

| If the user means… | Signals (phrases / audience) | You get | Not this if… | Read |
|--------------------|------------------------------|---------|--------------|------|
| **Why did spend move?** (one-shot) | "why did the bill jump", "what changed last month", "explain the spike", finance-review prep — **ad-hoc**, not recurring | DIGEST change tree (± optional AI); usually chat preview | they want a **standing** weekly/monthly channel report → pick a Schedule recipe below | `plugins/costory/skills/recipes/explain-period-change.md` |
| **Marketplace / vendor spend** | "marketplace", "private offer", "third-party on the cloud bill", "spend by seller/issuer" — Finance / procurement | Monthly marketplace-only trend + top vendors by `cos_invoice_issuer` | native cloud usage (EC2 etc.) — wrong recipe | `plugins/costory/skills/recipes/marketplace-spend.md` |
| **K8s cost per namespace** | "namespace", "EKS/GKE", "cluster showback", platform/DevOps weekly | Weekly reallocated-namespace trend + top/flop | env or account rollup without namespaces → `service-cost-weekly` or `env-costs-cto` | `plugins/costory/skills/recipes/namespace-cost.md` |
| **Credits / discounts runway** | "credits burning", "savings plan / CUDs", "promotional credits", "discount lines", charge category | Monthly charge-category trend + movers | usage-by-service operating view → `service-cost-weekly` | `plugins/costory/skills/recipes/provider-credits.md` |
| **Weekly eng FinOps pulse** | "weekly by env and service", "weekly pulse", "what moved per service" — eng/FinOps, **actionable drivers** | Weekly graph + DIGEST env/account → service, **AI on** | exec-only "prod vs staging" one number → `env-costs-cto`; one-shot "why did it jump" → explain | `plugins/costory/skills/recipes/service-cost-weekly.md` |
| **Tagging / allocation coverage** | "untagged", "tag coverage", "missing team/env tag", "can't allocate the bill" | `tagged / all` ratio trend + worst services (formula via `query` first) | absolute spend by tag value (that's a normal split, not coverage) | `plugins/costory/skills/recipes/untagged-coverage.md` |
| **Exec cost per environment** | "CTO wants env costs", "prod vs non-prod", leadership monthly readout — **simple**, not drill-down | Monthly top envs (no flop) ± yearly graph; **build `env` VDIM first** | weekly service drivers / AI narrative → `service-cost-weekly` | `plugins/costory/skills/recipes/env-costs-cto.md` |
| **Reallocate by external metric** | "split shared cost by usage", "unit economics then allocate", "showback by requests/revenue/CPU", proportional fair share | Validate cost ÷ metric in `query`, then **telemetry VDIM** publish | simple cost ÷ metric KPI only (no reallocation) → `query` Workflow E; fixed 60/40 weights → `virtual-dimensions` splitCost | `plugins/costory/skills/recipes/reallocate-by-external-metric.md` |

### Quick disambiguation

| Sound alike | Prefer |
|-------------|--------|
| "cost per environment" from a **CTO / VP** (monthly, simple) | `env-costs-cto` |
| "cost per environment **and service**" / **weekly** eng pulse | `service-cost-weekly` |
| "what changed?" **once** vs **every week/month in Slack** | explain-period-change vs the Schedule recipe that matches the topic |
| "untagged spend $" vs "tag **coverage %**" | raw untagged $ can be a scoped query; **coverage campaign** → `untagged-coverage` |
| "cost per request" KPI vs **reallocate** shared spend by requests | unit economics only → `query`; proportional split → `reallocate-by-external-metric` |

## Notes on presets

Cards use real `datePreset` tokens (`LAST_MONTH`, `LAST_WEEK`, `LAST_INVOICE_MONTH`, `TRAILING_14_WEEKS`, `LAST_12_MONTHS`) — all present in the live DatePreset enum.

## Adding a recipe

One file in `plugins/costory/skills/recipes/` + one row in **Pick a recipe** (triggers, outcome, "not this if"). Card format:

**When · Audience · Outcome · Tool sequence · Payload skeleton · Confirm before build · Gotchas · Brief · Hand off**
