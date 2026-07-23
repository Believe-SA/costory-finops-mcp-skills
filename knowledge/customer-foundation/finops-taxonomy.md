# Customer Foundation — FinOps Taxonomy

The capability model the Costory skills are organized against, and the map of which skill delivers which capability. Every skill should belong to **exactly one** primary capability.

## Capabilities

| Capability | One-line definition | Question it answers |
|-----------|---------------------|---------------------|
| **Cost Intelligence** | Explain and break down what was spent and why. | "What are we spending on X, and why did it move?" |
| **Cost Allocation** | Attribute shared/untagged spend to business owners. | "Whose cost is this?" |
| **Cost Optimization** | Reduce spend without losing capability (rightsizing, commitments, waste). | "Where can we cut safely?" |
| **Budget Management** | Track spend against a plan. | "Are we on budget / on pace?" |
| **Forecasting** | Project future spend from history + drivers. | "What will we spend?" |
| **Unit Economics** | Cost per unit of business value. | "What does one X cost us?" |
| **Governance** | Enforce policy: tagging, budgets, commitments, anomaly response. | "Are we within policy?" |
| **Recommendations** | Concrete, prioritized actions with estimated impact. | "What should we do next?" |
| **Reporting** | Deliver the right view to the right audience/cadence. | "How do stakeholders see this?" |
| **Automation** | Detect and notify without a human polling. | "Tell me when something moves." |

## Skill → capability map

| Skill | Primary capability | Secondary |
|-------|-------------------|-----------|
| `query` | Cost Intelligence | Unit Economics, Budget Management |
| `dashboards` | Reporting | Cost Intelligence |
| `reports` | Reporting | Cost Intelligence (DIGEST = explanation) |
| `virtual-dimensions` | Cost Allocation | Governance (tagging) |
| `recipes` | *(meta)* single-skill outcome router | all |
| `events` | Cost Intelligence (event correlation) | Automation |
| `recommendations` | Recommendations | Cost Optimization |
| `alerts` | Automation | Governance |
| `playbooks` | *(meta)* multi-step orchestration | all |
| `forecast` | Forecasting | Budget Management |
| `governance` | Governance | Cost Allocation, Budget Management |
| `optimization` | Cost Optimization | Recommendations |
| `unit-economics` | Unit Economics | Cost Allocation |
| `docs` | *(meta)* documentation lookup | — |

## Coverage heatmap

| Capability | Status | Where it lives / gap |
|-----------|--------|----------------------|
| Cost Intelligence | ✅ strong | `query`, `dashboards`, `reports` DIGEST |
| Cost Allocation | ✅ strong | `virtual-dimensions`, `namespace-cost`, `reallocate-by-external-metric` |
| Reporting | ✅ strong | `reports`, `dashboards`, report recipes |
| Budget Management | 🟡 partial | `query` F + `budget-vs-actual-dashboard`; no budget *governance* skill |
| Unit Economics | ✅ strong | `unit-economics` skill (cost-per-unit + KPI-vs-reallocate decision) + `query` E + `reallocate-by-external-metric` |
| Forecasting | 🟡 partial | `forecast` skill = run-rate / budget-pace from `query` + `alerts`; statistical forecast is **in-product only** (Forecasting with TimesFM), not on the MCP surface |
| Cost Optimization | ✅ strong | `optimization` (per-lever sizing method) + `recommendations` (ranked plan); analysis only — the action is the owner's |
| Recommendations | 🟡 partial | `recommendations` skill (analyst-derived from the data); no vendor recommendation engine in the MCP surface |
| Governance | 🟡 partial | `governance` skill sets coverage/budget/commitment SLOs and monitors adherence (composes `untagged-coverage`, VDIM leftover, `query` H, `alerts`, `reports`); adherence is advisory, not enforced |
| Automation | ✅ strong | `alerts` (create/preview/list) + `events` (correlate) skills now own the tools; `ec2-cost-spike-alert` recipe |

**Rule of thumb:** every ❌/🟡 that is *not* blocked on the product is already backed by an existing MCP tool — those are buildable now (see the roadmap in [`../../docs/finops-kb-review.md`](../../docs/finops-kb-review.md) §6).

## Related

- Entities that realize these capabilities → [`entities.md`](./entities.md)
- Metrics they compute → [`metrics.md`](./metrics.md)
- Decision rules that govern them → [`business-rules.md`](./business-rules.md)
- Vocabulary → [`glossary.md`](./glossary.md)
