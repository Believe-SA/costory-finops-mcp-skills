# FinOps KB transformation — progress & handoff

Resume-state for the knowledge-base roadmap in [`finops-kb-review.md`](./finops-kb-review.md).

> **Beads note.** The beads Dolt store was **read-only** for the whole implementation session
> (write lock held by another checkout/session), so completed tasks could not be closed and
> dependency edges could not be written. The roadmap issues themselves *do* exist. Replay the
> writes below once the lock clears.

## Branch / git state

- Branch: `worktree-finops-kb-review` (worktree). **Not pushed** — an earlier `git push` was declined.
- Commits (on top of `main`):
  - `49152de` docs: FinOps KB review (`docs/finops-kb-review.md`)
  - `7e3e798` Phase 1 — DatePreset drift lint + Customer Foundation seed
  - Phase 2 commit (this change) — render mechanism + `cel-null` migration + v0.8.4
- To ship: `git push -u origin worktree-finops-kb-review` then `gh pr create --draft`.

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
| Phase 4/5 tasks | open (not started) |

### Replay once beads is writable

```bash
bd close costory-finops-mcp-skills-dzl.1 costory-finops-mcp-skills-dzl.2 costory-finops-mcp-skills-dzl.3 \
  --reason="Implemented in 7e3e798"
bd close costory-finops-mcp-skills-3g0.2 costory-finops-mcp-skills-3g0.3 \
  --reason="render-foundation.py + drift-lint CI (Phase 2 commit)"
bd close costory-finops-mcp-skills-zzi.1 costory-finops-mcp-skills-zzi.2 costory-finops-mcp-skills-zzi.3 costory-finops-mcp-skills-zzi.4 \
  --reason="Customer Foundation docs (Phase 3 commit)"
# dependency edges that failed to write:
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.1   # spend-spike <- events
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.2   # spend-spike <- recommendations
bd dep add costory-finops-mcp-skills-aj9.6 costory-finops-mcp-skills-aj9.4   # spend-spike <- playbooks tier
bd dep add costory-finops-mcp-skills-3g0 costory-finops-mcp-skills-dzl        # phase 2 <- phase 1
bd dep add costory-finops-mcp-skills-zzi costory-finops-mcp-skills-3g0        # phase 3 <- phase 2
bd dep add costory-finops-mcp-skills-aj9 costory-finops-mcp-skills-zzi        # phase 4 <- phase 3
bd dep add costory-finops-mcp-skills-8le costory-finops-mcp-skills-aj9        # phase 5 <- phase 4
```

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
