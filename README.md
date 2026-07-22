# finops-mcp-skills

Costory FinOps agent skills for virtual dimensions, dashboards, and reports. Packaged as a Claude Code / Codex marketplace plugin

## Layout

```
.claude-plugin/marketplace.json
skills.json                          ← MCP skillId → SKILL.md path
plugins/costory/
  .claude-plugin/plugin.json
  skills/
    virtual-dimensions/SKILL.md
    dashboards/SKILL.md
    reports/SKILL.md
```

## Skills

| MCP `skillId` | Use when |
|---------------|----------|
| `virtual-dimensions` | Create / edit / preview / publish custom cost axes |
| `dashboards` | Create or extend dashboards with context-first widgets |
| `reports` | DIGEST and other reports: preview, schedule, delivery safety |
| `query` | Cost / usage / metric investigation workflows |
| `recipes` | Outcome-based FinOps tracking designs → hand off to mechanics |

## Install (Claude Code / Codex)

```bash
# Claude Code
claude plugin marketplace add costory-io/finops-mcp-skills
claude plugin install costory@costory

# Codex
codex plugin marketplace add costory-io/finops-mcp-skills
codex plugin add costory@costory
```

## Costory MCP `get_skill`

`skills.json` maps each MCP `skillId` to a `SKILL.md` path. When wiring costory-app, load the file from this repo (or a pinned release), strip optional YAML frontmatter, and return the markdown body.

```json
{
  "skillId": "dashboards",
  "path": "plugins/costory/skills/dashboards/SKILL.md"
}
```

## Authoring

See [AGENTS.md](./AGENTS.md) for layout rules, version bumps, and validation. Use [SKILL_TEMPLATE.md](./SKILL_TEMPLATE.md) when adding a skill.

## License

Apache-2.0 — see [LICENSE](./LICENSE).
