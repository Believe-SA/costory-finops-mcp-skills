# Allocation campaign (playbook)

**When:** *"improve our tag coverage"*, *"run a tagging/allocation push and track progress"* — a governance campaign to make more of the bill attributable, over time.
**Audience:** FinOps lead / platform team driving allocation hygiene.
**Outcome:** a coverage baseline, the missing axis built as a virtual dimension, a re-measured coverage lift, and a standing trend so the campaign is visible.

Expressible with existing skills today — no new mechanics required.

## Steps

1. **Baseline the coverage** — `recipes` → `untagged-coverage`. Confirm which tag/label defines coverage; validate the `tagged / in-scope` ratio in `query`. Record the starting %.
   *Gate:* confirm the tag field and the un-taggable exclusions before trusting the ratio.
2. **Build/extend the allocation axis** — `virtual-dimensions` (or `recipes` → `prod-vs-rnd-vdim`): add rules that claim the largest unallocated buckets; drive leftover down.
   *Gate:* strategy approval ≠ rule approval — confirm the rule set; publish only on explicit confirm; wait for `computeStatus: COMPLETED`.
3. **Re-measure** — re-run the step-1 `query` (now including the new axis / tags) → quantify the coverage lift.
4. **Track it** — `reports` (Schedule) the coverage ratio trend + worst services (MONTHLY, or WEEKLY during an active push).
   *Gate:* confirm channel type → destination, `SCHEDULED`, before `create_report`.

## Branches / Stop conditions

- **Stop after step 1** if coverage is already acceptable — report and done.
- If the gap is genuinely un-taggable spend, **exclude it and say so** (it caps the ratio) rather than chasing it with rules.

## Brief

*"Coverage baseline \<X%\> → build \<axis\> VDIM to claim the gaps → re-measure lift → schedule the trend to \<channel\>."*
