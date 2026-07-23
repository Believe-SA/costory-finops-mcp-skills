# Monthly close (playbook)

**When:** *"month-end FinOps review"*, *"close the books on last month and set up the recurring readout"* — finance/leadership cadence, both the one-shot explanation and the standing report.
**Audience:** FinOps + Finance at invoice close.
**Outcome:** a one-shot explanation of last (invoice) month, plus a scheduled monthly readout so the review repeats itself.

Expressible with existing skills today — no new mechanics required.

## Steps

1. **Explain the closed month** — `recipes` → `explain-period-change` with `LAST_INVOICE_MONTH` (DIGEST change tree). Offer `display: "summary"` for the exec narrative.
   *Gate:* present preview fields; confirm scope/period.
2. **Confirm the recurring readout shape** — pick the standing report: `recipes` → `env-costs-cto` (exec cost-per-environment) or an invoice-close DIGEST. Confirm audience, hierarchy, and whether the AI summary is on.
3. **Schedule it** — `reports` (Schedule) with a `datePreset` that rolls forward (`LAST_INVOICE_MONTH` / `LAST_MONTH`), monthly cadence, `firstRunAt` set.
   *Gate:* confirm channel type → destination, and `SCHEDULED` mode, before `create_report`.

## Branches / Stop conditions

- **Stop after step 1** if they only wanted this month explained (no standing report).
- Use `LAST_MONTH` instead of `LAST_INVOICE_MONTH` if the org closes on calendar months.

## Brief

*"Explain \<invoice month\> via DIGEST, then schedule a monthly \<env-costs / invoice-close\> readout to \<channel\>."*
