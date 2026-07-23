# FinOps KB transformation — progress & handoff

Resume-state for the knowledge-base roadmap in [`finops-kb-review.md`](./finops-kb-review.md), the review/fix pass in [`finops-kb-review-issues.md`](./finops-kb-review-issues.md), and the backlog implementation round.

> **Beads note.** The beads Dolt write lock has been **intermittent** all session (read-only most
> of the time, briefly writable once — long enough to file the 22 review issues, but it closed
> again before the phase-completion closes/deps or the backlog closes could land). All work is
> committed to git regardless; only the beads bookkeeping (close + dep edges) is queued.
>
> **Single consolidated replay script** (supersedes the smaller command blocks below —
> run this one, once, when the lock is free):
> `/home/chussenot/.claude/jobs/0b97e987/tmp/bd-replay-all.sh`

## Branch / git state (PR opened)

- Branch: `worktree-finops-kb-review`, pushed to `origin` (the `Believe-SA` fork). A draft PR was intended via `gh pr create --repo Believe-SA/costory-finops-mcp-skills --base main --head worktree-finops-kb-review` — it failed once with `must be a collaborator` (gh token identity vs the SSH key used to push are different accounts); resolve via `gh auth status` / `gh auth switch` / `gh auth refresh -s repo`, or open the compare URL directly: `https://github.com/Believe-SA/costory-finops-mcp-skills/compare/main...worktree-finops-kb-review?expand=1`.
- Commits (on top of `main`), newest first:
  - `ea97ab2` Backlog implementation — unit-economics + docs skills, anomaly-triage playbook, 9 skill enhancements (v0.11.0, **14 skills**)
  - `3e8f6cf` Review fixes — 17 confirmed findings resolved + 22 issues filed in beads (v0.10.1)
  - `fa08741` Phase 5 — forecast, governance, optimization (v0.10.0)
  - `a7608a1` Phase 4 — events, recommendations, alerts, playbooks tier (v0.9.0)
  - `2a67769` Phase 3 — Customer Foundation complete
  - `5a6b0cb` Phase 2 — render mechanism + cel-null single-sourced (v0.8.4)
  - `7e3e798` Phase 1 — DatePreset drift lint + Customer Foundation seed
  - `49152de` docs: FinOps KB review (`docs/finops-kb-review.md`)
- **Pushed.** Remaining to ship: open the PR (see above — blocked on `gh` auth, not on the code).

## Beads issues (roadmap)

Epics: Phase 1 `…-dzl` · Phase 2 `…-3g0` · Phase 3 `…-zzi` · Phase 4 `…-aj9` · Phase 5 `…-8le`.

Status by task:

| Task | State |
|------|-------|
| `…-dzl.1` DatePreset drift lint | **done** (7e3e798) |
| `…-dzl.2` entities.md | **done** (7e3e798) |
| `…-dzl.3` metrics.md | **done** (7e3e798) |
| `…-dzl.4` index.json category eval | open (deferred — needs consumer confirmation) |
| `…-3g0.1` author canonical sources (14 conventions) | **in progress** — 1 of ~14 done (`cel-null`) |
| `…-3g0.2` render mechanism | **done** (`scripts/render-foundation.py`) |
| `…-3g0.3` drift-lint CI | **done** (lint.yml step) |
| `…-3g0.4` migrate skills to render-from-source | **in progress** — recipes `namespace-cost`, `untagged-coverage` migrated for `cel-null` |
| `…-zzi.1` glossary.md | **done** (Phase 3 commit) |
| `…-zzi.2` business-rules.md | **done** (Phase 3 commit) |
| `…-zzi.3` finops-taxonomy.md | **done** (Phase 3 commit) |
| `…-zzi.4` model absent entities (Recommendation/Forecast/typed Event) | **done** (Phase 3 commit — in `entities.md`) |
| `…-aj9.1` events skill | **done** (Phase 4 commit) |
| `…-aj9.2` recommendations skill | **done** (Phase 4 commit — analyst-derived; no vendor engine) |
| `…-aj9.3` alerts skill | **done** (Phase 4 commit) |
| `…-aj9.4` playbooks tier + card contract | **done** (Phase 4 commit — `playbooks/SKILL.md`) |
| `…-aj9.5` expressible-today playbooks | **done** (monthly-close, allocation-campaign, unit-economics-rollout) |
| `…-aj9.6` spend-spike-triage playbook (flagship) | **done** (Phase 4 commit) |
| `…-8le.1` forecast skill | **done** (Phase 5 commit — run-rate; statistical forecast is in-product only) |
| `…-8le.2` governance skill | **done** (Phase 5 commit) |
| `…-8le.3` optimization skill | **done** (Phase 5 commit) |

**Roadmap complete — all 5 phases implemented.** There is no Phase 6 in the review (`docs/finops-kb-review.md`); Phase 5 (AI-native) is the final phase. Remaining open items are the deferred `…-dzl.4` (index.json category eval) and the bulk of `…-3g0.1`/`…-3g0.4` (migrate the other ~13 conventions to rendered blocks — the mechanism is done, the migration is mechanical follow-on).

### Replay once beads is writable

```bash
bd close costory-finops-mcp-skills-dzl.1 costory-finops-mcp-skills-dzl.2 costory-finops-mcp-skills-dzl.3 \
  --reason="Implemented in 7e3e798"
bd close costory-finops-mcp-skills-3g0.2 costory-finops-mcp-skills-3g0.3 \
  --reason="render-foundation.py + drift-lint CI (Phase 2 commit)"
bd close costory-finops-mcp-skills-zzi.1 costory-finops-mcp-skills-zzi.2 costory-finops-mcp-skills-zzi.3 costory-finops-mcp-skills-zzi.4 \
  --reason="Customer Foundation docs (Phase 3 commit)"
bd close costory-finops-mcp-skills-aj9.1 costory-finops-mcp-skills-aj9.2 costory-finops-mcp-skills-aj9.3 \
        costory-finops-mcp-skills-aj9.4 costory-finops-mcp-skills-aj9.5 costory-finops-mcp-skills-aj9.6 \
  --reason="events/recommendations/alerts skills + playbooks tier + 4 playbook cards (Phase 4 commit, v0.9.0)"
bd close costory-finops-mcp-skills-8le.1 costory-finops-mcp-skills-8le.2 costory-finops-mcp-skills-8le.3 \
  --reason="forecast (run-rate)/governance/optimization skills (Phase 5 commit, v0.10.0)"
# also close the phase epics now their children are done:
bd close costory-finops-mcp-skills-dzl costory-finops-mcp-skills-zzi costory-finops-mcp-skills-aj9 costory-finops-mcp-skills-8le \
  --reason="phase complete"   # leave 3g0 (Phase 2) open — migration is ongoing follow-on
# dependency edges that failed to write:
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.1   # spend-spike <- events
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.2   # spend-spike <- recommendations
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.4   # spend-spike <- playbooks tier
bd dep add costory-finops-mcp-skills-3g0 costory-finops-mcp-skills-dzl        # phase 2 <- phase 1
bd dep add costory-finops-mcp-skills-zzi costory-finops-mcp-skills-3g0        # phase 3 <- phase 2
bd dep add costory-finops-mcp-skills-aj9 costory-finops-mcp-skills-zzi        # phase 4 <- phase 3
bd dep add costory-finops-mcp-skills-8le costory-finops-mcp-skills-aj9        # phase 5 <- phase 4
```

## Review pass (post-Phase-5, v0.10.1)

Full all-skills review via the `costory-skills-review` workflow (38 agents, adversarial verify). **17 verified findings fixed** in one pass (playbook misroutes, dead links, `reports` `cos_environment`, EMAIL destination shape across reports + 5 recipes, reallocate telemetry-datasource accuracy, `events` confirm-gate, stale `entities.md`, packaging descriptions). **22 backlog issues filed live in beads** (21 state-of-the-art opportunities + 1 deferred `team`-groupBy bug `…-6ac`) — see [`finops-kb-review-issues.md`](./finops-kb-review-issues.md).

**Still to replay when the (intermittent) Dolt lock frees** — the Phase 1–5 completion closes + dep edges below did not persist this session:

## Phase 2 — how it works (for the next contributor)

The render mechanism is **live and proven** on one convention. To migrate another:

1. Author the canonical snippet as `knowledge/fragments/<id>.md`.
2. In each skill/recipe that carries it, wrap the existing text in
   `<!-- BEGIN foundation:<id> -->` … `<!-- END foundation:<id> -->`.
3. Run `scripts/render-foundation.py` (normalizes all blocks to source), then `--check`.
4. **Bump the version** in lockstep (`marketplace.json`, `plugin.json`, `skills.json`) — editing a
   skill body is a skill change (see `AGENTS.md`).

### Remaining conventions to migrate (from review §5, priority order)

Not every duplicated concept is a clean managed-block target — some are expressed in different
structures per skill (e.g. the CEL-null rule is a prose line in `query` but a table cell in
`virtual-dimensions`; those need normalization first, not a straight wrap). Candidates, easiest first:

- `bqName` rule (virtual-dimensions + 4 recipes) — appears as standalone caveats.
- TOP_FLOP rank-vs-movers convention (`10/0` vs `10/10`) — recipe Gotchas/Frozen lines.
- DIGEST thresholds `100/5%/20` + widget block (reports + `explain-period-change` + `service-cost-weekly`).
- Standard scheduled-report skeleton (6 recipes) → likely an `examples/` reference, not an inline block.
- "never invent token/field/number/bucket" guard set (every skill).
- SCOPE vs SPLIT; context-first inheritance (dashboards+reports); query-naming.

Structurally-varied conventions (like CEL-null in `query`/`virtual-dimensions`) should be normalized
to a common shape *before* wrapping, or left as a loadable reference — do not force a shared block
into a table cell.
