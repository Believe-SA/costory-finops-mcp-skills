# Anomaly triage (playbook)

**When:** *"the spend alert fired — is it real, what caused it, and what do we do?"* — starts from a **specific alert signal** on a defined condition + scope, not from a vague "the bill looks high". Narrower and signal-driven; for an open-ended bill-jump investigation use `spend-spike-triage` instead.
**Audience:** on-call / FinOps engineer reacting to a fired cost alert or anomaly monitor.
**Outcome:** a short brief that says whether the firing is **real or noise**, **what caused it** (correlated event, if any), **which resource drove it**, **what it would save to fix**, and closes the loop by **annotating the cause** and **re-notifying the alert's channel**.

## Steps

Run in order. Each step names the owning skill (`get_skill` it for mechanics). Honor the gate before any mutation/delivery.

1. **Confirm the firing signal** — `alerts`: read the fired alert's `condition` + scope from the notification (or `list_alerts`, `type: "cost"`, to review it). Pin the exact metric, scope, and the firing window (the alert's look-back — e.g. `TRAILING_90_DAYS` evaluated daily).
   *Gate:* confirm the scope + firing window before investigating; if the alert is a known chronically-noisy monitor, do not re-triage — see Stop.
2. **Correlate the cause** — `events` → `list_events` over the firing window + scope (optionally `category: "TECHNICAL"` for deploys). An event that lines up in time + scope is a **candidate driver** (correlation, not proof).
   *Branch:* if a benign known cause explains it (planned migration, one-off) → annotate and **stop** — no remediation needed.
3. **Find the driver** — `query` on the alert's scope (`filterCel`), `suggest_groupby` to pick the axis; if you need the change tree, `recipes` → `explain-period-change` (DIGEST). Pin the specific service/resource responsible.
4. **Estimate remediation** — `recommendations`: quantify the fix from the driver's `query` figures (anomaly follow-up = the recurring excess vs baseline). Rank by saving × confidence ÷ effort.
   *Gate:* every saving is an estimate tied to an observed figure — state the basis period.
5. **Annotate & close the loop** — `events` → `create_event` (with a widget scoped to the movement) to record the cause on the timeline so the next firing is self-explaining; then re-notify the alert's channel with the resolution + estimate.
   *Gate:* confirm the event details (name, date, scope) before `create_event` — it writes to the shared cost timeline the whole org sees.

## Branches / Stop conditions

- **Stop at step 2** if the firing has a known benign cause — annotate, don't recommend.
- **Skip step 4** if the driver is expected/committed spend with no realistic action.
- **Stop and tune instead** if the alert fires on normal variance (chronically noisy): the fix is tuning the monitor's threshold/`dedup` in the UI (`alerts` are create-only), not a remediation.

## Brief

*"Alert \<name\> fired (\<condition\> over \<scope\>): real, correlates with \<event or none\>; driver is \<service/resource\>; ≈$Y/mo recoverable via \<action\>; cause annotated, \<channel\> re-notified."*
