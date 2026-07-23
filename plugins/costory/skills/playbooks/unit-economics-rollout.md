# Unit-economics rollout (playbook)

**When:** *"roll out cost per \<unit\>"*, *"showback by a business driver end to end"*, *"stand up cost-per-request / per-GB / per-delivery and keep it live"* — from validating the metric to a live, delivered view.
**Audience:** FinOps + the engineering/product team that owns the driver metric.
**Outcome:** a validated cost-per-unit formula, the shared cost reallocated by that driver, and a live dashboard + recurring report.

Expressible with existing skills today — no new mechanics required.

## Steps

1. **Validate the unit metric** — `query` Workflow E: cost `a` + the driver metric `b` (saved `type: "metric"`, or external Tsuga/BigQuery) + formula `c = a / b`. Confirm both legs are sane and the ratio is believable before building anything.
   *Gate:* if `a / b` is noisy or the metric is wrong, fix scope/metric here — do not proceed.
2. **Reallocate shared cost by the driver** — `recipes` → `reallocate-by-external-metric` (telemetry VDIM): split the shared spend proportionally to the driver.
   *Gate:* approve the mapping; publish only on explicit confirm; wait for `computeStatus: COMPLETED`; use the published `bqName`.
   *Branch:* if the user only wants the KPI (not a reallocation), skip to step 3 with the step-1 formula.
3. **Persist the view** — `dashboards`: a unit-economics widget (cost `a` + metric `b` + formula `c`) alongside the reallocated breakdown.
4. **Deliver it** — `reports` (Schedule): a weekly/monthly cost-per-unit trend.
   *Gate:* confirm channel type → destination, `SCHEDULED`, before `create_report`.

## Branches / Stop conditions

- **Stop after step 1** if the user only needed the number validated once.
- Skip step 2 (reallocation) for a pure KPI; keep it when the goal is fair showback of shared cost.

## Brief

*"Validate cost-per-\<unit\> in query → reallocate shared spend by \<driver\> (telemetry VDIM) → dashboard + weekly report to \<channel\>."*
