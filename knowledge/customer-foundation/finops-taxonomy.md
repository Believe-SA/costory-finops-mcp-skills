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
| `recipes` | *(meta)* Automation / Playbook router | all |

## Coverage heatmap

| Capability | Status | Where it lives / gap |
|-----------|--------|----------------------|
| Cost Intelligence | ✅ strong | `query`, `dashboards`, `reports` DIGEST |
| Cost Allocation | ✅ strong | `virtual-dimensions`, `namespace-cost`, `reallocate-by-external-metric` |
| Reporting | ✅ strong | `reports`, `dashboards`, report recipes |
| Budget Management | 🟡 partial | `query` F + `budget-vs-actual-dashboard`; no budget *governance* skill |
| Unit Economics | 🟡 partial | `query` E + `reallocate-by-external-metric`; no dedicated skill |
| Forecasting | ❌ missing | no forecast tool in the MCP surface — verify product support |
| Cost Optimization | ❌ missing | only `query` H (contracted vs effective *analysis*), no *actions* |
| Recommendations | ❌ missing | `suggest_actions` tool has no owning skill |
| Governance | 🟡 weak | `untagged-coverage` + VDIM tagging + confirm-gates; no governance skill |
| Automation | 🟡 partial | `ec2-cost-spike-alert` recipe; `create_alert`/`create_event` tools have no owning skill |

**Rule of thumb:** every ❌/🟡 that is *not* blocked on the product is already backed by an existing MCP tool — those are buildable now (see the roadmap in [`../../docs/finops-kb-review.md`](../../docs/finops-kb-review.md) §6).

## Related

- Entities that realize these capabilities → [`entities.md`](./entities.md)
- Metrics they compute → [`metrics.md`](./metrics.md)
- Decision rules that govern them → [`business-rules.md`](./business-rules.md)
- Vocabulary → [`glossary.md`](./glossary.md)
