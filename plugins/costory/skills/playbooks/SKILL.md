---
name: playbooks
description: "Use when a FinOps goal needs MORE THAN ONE skill in sequence — a multi-step investigation or rollout, not a single build. Route to one playbook card: bill spiked and you want the full loop (explain → correlate events → find drivers → estimate savings → summarize) → spend-spike-triage; a cost/anomaly alert fired and you want the targeted follow-up → anomaly-triage; finance month-end → monthly-close; tagging/allocation push → allocation-campaign; stand up cost-per-unit → unit-economics-rollout. Each card is an ORDERED chain of recipes/skills with confirm-gates between steps. For a single-skill outcome use recipes instead. Read only the one matching card."
---

# Playbooks

A **playbook** orchestrates **several skills/recipes in sequence** to reach a FinOps outcome that no single skill delivers. Where a `recipes` card hands off to **one** mechanics skill, a playbook chains steps — each step's output feeds the next, with a **confirm-gate** before any mutation or delivery.

Use a playbook when the goal is an *investigation or rollout* ("figure out why and what to do", "roll out cost-per-unit", "run the tagging campaign"), not a single build.

## How to use this skill

1. Match the goal in **Pick a playbook** below.
2. **Read only that one card** under `plugins/costory/skills/playbooks/`.
3. Run its steps in order. Each step names the owning skill — `get_skill` that skill for the mechanics.
4. **Honor the gates** — do not fire a mutation/delivery tool (VDIM publish, report `NOW`/`SCHEDULED`, `create_alert`, `create_event`) until its gate is confirmed.
5. Respect **stop conditions** — a playbook can end early (e.g. no driver found, coverage already high).

A playbook does not restate each skill's mechanics or safety rules — it sequences them. The owning skill remains the source of truth for its own payloads and gates.

## Card contract

| Section | Role |
|---------|------|
| **When / Audience / Outcome** | routing + what "done" looks like |
| **Steps** | ordered `skill/recipe → produces → gate` chain |
| **Branches / Stop conditions** | when to skip a step or end early |
| **Brief** | one-line restatement |

## Pick a playbook

| If the user means… | Signals | Steps (skills) | Read |
|--------------------|---------|----------------|------|
| **Spend spiked — full triage** | "why did the bill jump AND what do we do", "investigate + fix the spike", incident-style cost review | explain-period-change → `events` → `query` → `recommendations` → `reports` | `plugins/costory/skills/playbooks/spend-spike-triage.md` |
| **Cost alert fired — triage the anomaly** | "our spend alert fired, now what", "the anomaly monitor tripped", alert-signal-driven follow-up (narrower than spike triage) | `alerts` → `events` → `query` → `recommendations` → `events` (annotate) | `plugins/costory/skills/playbooks/anomaly-triage.md` |
| **Finance month-end close** | "month-end FinOps review", "close the books + set up the recurring readout" | explain-period-change → summary → `reports` (Schedule) | `plugins/costory/skills/playbooks/monthly-close.md` |
| **Tagging / allocation campaign** | "improve tag coverage over time", "run a tagging push and track it" | `untagged-coverage` → `virtual-dimensions` → re-measure → `reports` | `plugins/costory/skills/playbooks/allocation-campaign.md` |
| **Stand up unit economics** | "roll out cost-per-\<unit\>", "showback by a business driver end to end" | `query` E → `reallocate-by-external-metric` → `dashboards` + `reports` | `plugins/costory/skills/playbooks/unit-economics-rollout.md` |

If the goal is a single build (one dashboard, one report, one VDIM, one alert), use `recipes` — not a playbook.

## Related

- `recipes` — single-skill outcome cards (the building blocks a playbook chains)
- The Customer Foundation (entities, glossary, business-rules, taxonomy) lives under `knowledge/customer-foundation/`
