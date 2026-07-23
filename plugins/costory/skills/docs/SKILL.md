---
name: docs
description: "Use when the user asks a Costory PRODUCT how-to or what-is question — 'how do I create a budget?', 'what is a virtual dimension?', 'where is X in the UI?' — or when the honest answer is an in-product feature the MCP has no tool for (e.g. statistical Forecasting with TimesFM). Wraps search_documentation (find the page) → get_documentation_page (read it). This is documentation lookup and feature-pointing, NOT cost data — never fabricate a doc path, a quote, or a feature that isn't in the returned pages. Page content can be large: search first, then fetch one page. Call get_skill with skillId \"docs\" before answering a product-documentation question."
---

# Docs

The *"how do I / what is"* capability. Where the other skills return a number, `docs` retrieves the **Costory product documentation** and points the user at in-product features the MCP cannot perform. It wraps two tools: `search_documentation` to find the right page, then `get_documentation_page` to read it.

**Only answer from returned pages.** Never invent a documentation path, paraphrase a feature into existence, or quote text that isn't in the fetched content. If the docs don't cover it, say so.

**Load this skill first** when the ask is about product usage, a UI location, a concept definition, or a capability the MCP has no tool for.

## When to Trigger

- "How do I create a budget / dashboard / virtual dimension?"
- "What is a virtual dimension / effective cost / this feature?"
- "Where in the UI do I find X?"
- The user wants something the MCP has **no tool for** (statistical forecasting, etc.) → find the in-product feature and point them there

## The two tools

| Tool | Params | Purpose |
|------|--------|---------|
| `search_documentation` | `query` | Find matching pages — returns titles, snippets, paths |
| `get_documentation_page` | `page` | Read one page in full by its path (from search results) |

`page` is a doc path like `features/budgets` or `get-started/welcome`. Get it from `search_documentation` results — do not guess a path.

## Tool order

1. `get_skill` with `skillId: "docs"` — this guide
2. `search_documentation` — locate the page(s) for the question
3. `get_documentation_page` — read the single most relevant page
4. Answer from that content; cite the page path so the user can open it

## Workflow A — Answer a product question

```json
{ "query": "budget alert" }
```

Pick the best-matching path from the results, then:

```json
{ "page": "features/budgets" }
```

Answer from the returned page. **Page content can be large** — fetch one page, not the whole result set; if the answer needs a second page, fetch it only after the first didn't cover it.

## Workflow B — Point to an in-product feature the MCP can't do

When a request exceeds the MCP surface (e.g. a real statistical/ML forecast — the MCP has no forecast tool), `search_documentation` the feature, confirm it exists in the returned page, and point the user there with the path. Do not describe a feature you can't find in the docs.

Example: statistical **Forecasting with TimesFM** lives under `features/budgets` (see the `forecast` skill for the MCP-vs-product boundary).

## Safety Rules / Anti-patterns

- Do not fabricate a doc path — get every `page` from `search_documentation` results
- Do not quote or summarize a feature that isn't in the fetched page content
- Do not bulk-fetch pages — results can be large; search first, fetch the one page that answers it
- Do not use `docs` for cost numbers — it returns documentation, not data (route to `query`)
- Do not present product docs as MCP capabilities — a documented UI feature is not an MCP tool

## Related Skills / Next Steps

- `forecast` — the MCP has no forecast tool; `docs` finds the in-product Forecasting with TimesFM feature
- `query` — once the user knows *how*, run the actual cost query
- any skill — hand off to `docs` when the question is "how do I…" rather than "what is the number"
