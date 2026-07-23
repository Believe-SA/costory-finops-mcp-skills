---
name: governance
description: "Use when the question is about FinOps POLICY adherence rather than a single number: allocation-coverage targets/SLOs (tag coverage %, VDIM leftover %), budget adherence (burn-rate / projected breach), commitment coverage, tagging policy, and standing anomaly policy. Governance sets a target and monitors it — it composes query, untagged-coverage, virtual-dimensions (leftover), alerts, forecast, reports, and recommendations. Targets are the org's to set — confirm them, never invent an SLO. Call get_skill with skillId \"governance\" for policy/SLO framing."
---

# Governance

The *"are we within policy?"* capability. Where the other skills answer a number, governance frames a **target** (SLO) and **monitors adherence** to it — allocation coverage, budget discipline, commitment coverage, tagging, and anomaly response. It **composes** existing skills; it does not add new tools.

**Targets are the organization's to set.** Confirm the SLO with the user — never invent a threshold and present it as policy. Governance surfaces adherence; remediation is an owner's decision (route to `recommendations`).

**Load this skill first** when the ask is about policy, targets, SLOs, or coverage discipline rather than a one-off figure.

## Governance domains

| Domain | Metric (SLO) | Measure with | Monitor with | Remediate with |
|--------|--------------|--------------|--------------|----------------|
| **Allocation coverage** | tag coverage % ≥ target | `recipes` → `untagged-coverage` (`tagged / in-scope`) | `reports` (coverage trend) | `virtual-dimensions`, tagging campaign |
| **Unclaimed spend** | VDIM leftover % ≤ target | `virtual-dimensions` → `preview` leftover | re-measure on publish | add VDIM rules |
| **Budget adherence** | actual ≤ budget (pace) | `query` F, `forecast` run-rate (burn rate → projected breach) | standing `alerts` on a budget leg | `recommendations` |
| **Commitment coverage** | covered / eligible on-demand ≥ target | `query` H (contracted vs effective) | `reports` trend | `recommendations` (commitment) |
| **Tagging policy** | required labels present | `query` `filterCel: "<label> == null"` | `alerts` on untagged spend growth | tagging campaign |
| **Anomaly policy** | no unreviewed spike | `alerts` (WoW/threshold) | standing `alerts` | `events` (annotate) + `recommendations` |

## Tool order

1. `get_skill` with `skillId: "governance"` — this guide
2. `get_context` — currency, budgets, popular groupBys
3. **Confirm the target(s)** with the user — the SLO is theirs to set
4. Measure the current value with the domain's skill/query
5. Monitor: schedule a `reports` trend and/or a standing `alerts` rule
6. Remediate: hand off to `recommendations` / `virtual-dimensions`

## Workflow A — Establish an allocation-coverage SLO

1. Confirm the target (e.g. "≥ 90% of in-scope spend carries a `team` tag")
2. Measure the baseline — `recipes` → `untagged-coverage` (validate the `tagged / in-scope` ratio in `query` first)
3. If below target → run the `allocation-campaign` playbook (build/extend a VDIM, re-measure)
4. Monitor — `reports` the coverage ratio trend (MONTHLY, or WEEKLY during an active push); optionally an `alerts` rule if untagged spend grows
5. Report adherence: current % vs target, trend, worst services

## Workflow B — Budget & commitment governance

1. Confirm the budget (`search` → `get` → `budgetVersionId`) and the commitment-coverage target
2. **Budget adherence — burn rate & projected breach**: pull MTD actual vs budget with `query` F (or `forecast` Workflow A), then project linearly — `run_rate_period_end = MTD_cost ÷ days_elapsed × days_in_period` — and compare to the full-period budget. State it is a **linear run-rate** (ignores seasonality / known one-offs); for a real curve, point to the in-product forecast (see `forecast`)
3. **Standing breach alert** — stand up an `alerts` rule on a **budget leg**: a cost query `a` plus a budget query `b` (same scope, `budgetId: <budgetVersionId>`), condition `monthToDateSum(a) > monthToDateSum(b)` (spent more than the to-date budget allowance → off pace to breach). `preview_alert`-backtest the firing count first; see `alerts` for the condition grammar, `dedup`, and delivery gates
4. **Commitment coverage** — `query` H (`contracted_cost` vs `effective_cost`): captured savings vs the remaining steady-state on-demand that is a coverage candidate
5. Below target on any → `recommendations` (commitment purchase / spend control), stating estimates and their basis

## Workflow C — Tagging & anomaly policy

1. **Tagging policy (read)** — `query` scoped to `<required-label> == null` to size the policy gap; feed into the allocation SLO
2. **Tag hygiene (write)** — the Costory tag taxonomy (values applied to dashboards / views / explorers / alerts / events) accrues obsolete or duplicate values after reorgs. `list_tags` shows each value's usage count; `delete_tag` removes a value with **zero** tagged resources (it refuses tags still in use, so re-tag or archive first). This cleans Costory's own taxonomy — it does **not** touch cloud resource labels
3. **Anomaly policy** — a standing `alerts` monitor per critical scope (service/team/env); when one fires, `events` annotates the cause and `recommendations` proposes a fix
4. Roll up: a governance `reports` pack (coverage + budget pace + open anomalies) on a cadence

## Safety Rules / Anti-patterns

- Do not invent an SLO/threshold — confirm the target with the user; present adherence, not a made-up policy
- Do not report coverage as dollar savings — it is a hygiene ratio (see `business-rules.md`)
- Do not include structurally un-taggable spend in a coverage denominator without calling it out (it caps the SLO)
- Do not auto-remediate — governance surfaces adherence; the owner decides the action (route via `recommendations`)
- Do not set a budget/anomaly alert without a `preview_alert` backtest first (see `alerts`)
- Do not present a burn-rate projection as a statistical forecast — it is linear pace math (state the assumption); for a real curve point to the in-product forecast (see `forecast`)
- Do not `delete_tag` a value still in use — it only removes tags with **zero** tagged resources; run `list_tags` for counts first. It cleans Costory's tag taxonomy, not cloud resource labels

## Related Skills / Next Steps

- `recipes` → `untagged-coverage` — the allocation-coverage measurement
- `virtual-dimensions` — drive leftover down to hit an unclaimed-spend SLO
- `alerts` — standing budget / anomaly / tagging monitors
- `forecast` — budget-pace adherence
- `recommendations` — remediation once an SLO is missed
- `playbooks` → `allocation-campaign` — the coverage-SLO rollout end to end
