# Spend-spike triage (playbook)

**When:** *"the bill jumped — why, and what do we do about it?"* — a reactive, end-to-end investigation, not just an explanation or just a build.
**Audience:** FinOps lead / platform on-call reacting to a spike or a scary invoice.
**Outcome:** a short brief that says **what moved**, **what caused it** (correlated event, if any), **what's driving it**, **what it would save to fix**, and **a summary to share** — with any standing monitor set up.

## Steps

Run in order. Each step names the owning skill (`get_skill` it for mechanics). Honor the gate before any mutation/delivery.

1. **Explain what moved** — `recipes` → `explain-period-change` (DIGEST change tree, preview-first). Establishes the delta, the top movers, and the resolved comparison period.
   *Gate:* present the preview fields; confirm the period/scope before going further.
2. **Correlate the cause** — `events` → `list_events` over the movement's date range + scope. A deploy/incident/pricing event that lines up is a **candidate driver** (correlation, not proof).
   *Branch:* if a benign known cause explains it (planned migration, one-off) → note it and **stop** — no recommendation needed. Optionally `create_event` to annotate for next time.
3. **Find the drivers** — `query` on the largest DIGEST node (`filterCel`), `suggest_groupby` to pick the axis. Pin the specific service/resource/scope responsible.
4. **Estimate the fix** — `recommendations`: derive and quantify the opportunity (commitment coverage / rightsizing / waste) from the driver's `query` figures. Rank by saving × confidence ÷ effort.
   *Gate:* every saving is an estimate tied to an observed figure — state the basis period.
5. **Summarize & (optionally) monitor** — `reports` DIGEST with `display: "summary"` for the shareable narrative; offer an `alerts` monitor so the spike self-reports if it recurs.
   *Gate:* confirm channel type + `NOW`/`SCHEDULED` before delivery; confirm before `create_alert`.

## Branches / Stop conditions

- **Stop at step 2** if the movement has a known benign cause — annotate, don't recommend.
- **Skip step 4** if the driver is expected/committed spend with no realistic action.
- **Skip step 5 delivery** if the user only wanted the answer in chat.

## Brief

*"Bill up $X: DIGEST shows \<movers\>; correlates with \<event or none\>; driver is \<service/scope\>; ≈$Y/mo recoverable via \<action\>; summary shared to \<channel\>, monitor set."*
