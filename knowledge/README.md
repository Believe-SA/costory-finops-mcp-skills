# `knowledge/` — Costory FinOps Knowledge Base

This directory is the **single source of truth** for FinOps concepts, entities, metrics, and business rules that the Costory skills rely on. It is being built out per the roadmap in [`docs/finops-kb-review.md`](../docs/finops-kb-review.md).

## Why this exists

The `plugins/costory/skills/*/SKILL.md` bodies re-teach the same conventions (the DatePreset enum, SCOPE vs SPLIT, context-first inheritance, CEL null handling, the `bqName` rule, DIGEST thresholds, …). That duplication is hand-synced and drifts. This layer holds each concept **once**, so it can be maintained in one place.

## The one rule that governs this layer

> **Skills served via Costory MCP `get_skill` must stay self-contained** (see `AGENTS.md` → *Skill authoring rules*). `get_skill` may return only the `SKILL.md` body — agents may not load `references/` or this directory at runtime.

Therefore this directory is a **source**, not a runtime dependency:

- **Runtime-critical conventions** (needed inline for a skill to work) are authored once under `fragments/` and **rendered** into each `SKILL.md` as a generated managed block. Do **not** replace the inline copy with a link — that would break delivery.
- **Deeper / optional knowledge** may live here as a **loadable reference** — `get_skill` can load a file by path (as `dashboards` already does for `references/how-to-generate-interesting-dashboards.md`).

Do **not** "DRY up" the skills by deleting their inline conventions and pointing at this directory. Self-containment is a delivery contract, not an oversight.

## Render mechanism (live)

A fragment in `fragments/<id>.md` is the single source of a snippet that must appear
inline in one or more skills. A consuming skill marks where it goes with:

```
<!-- BEGIN foundation:<id> -->
...(generated — edit knowledge/fragments/<id>.md, then re-render)...
<!-- END foundation:<id> -->
```

- Regenerate all blocks: `scripts/render-foundation.py`
- CI check (fails on drift): `scripts/render-foundation.py --check` (wired into `.github/workflows/lint.yml`)

Same managed-block pattern the Beads integration already uses in `AGENTS.md`. Editing a
skill body that contains a managed block still requires the lockstep version bump (see `AGENTS.md`).

**Adopted so far:** `cel-null` (in `recipes/namespace-cost.md`, `recipes/untagged-coverage.md`). Migrating the remaining conventions is tracked in beads (Phase 2).

## Layout (target — built incrementally)

```
knowledge/
├── customer-foundation/   # entities.md, glossary.md, business-rules.md, finops-taxonomy.md, metrics.md
├── capabilities/          # per-capability conventions (cost-intelligence, cost-allocation, reporting, …)
├── playbooks/             # multi-step orchestration above recipes
└── examples/              # shared skeletons, CEL constants, good/bad/edge cases
```

Present today: `customer-foundation/entities.md`, `customer-foundation/metrics.md`.
