# MAESTRO Infrastructure Cost Model

**Document**: COST-MODEL-001
**Status**: Draft
**Author**: MSTR-12 (DevOps & SRE)
**Date**: 2026-05-20
**References**: ADR-001-tech-stack.md (Section 8, Appendix), N2, R9

---

## 1. Summary

**Target budget**: EUR 300-520/month (total, including LLM API costs)
**Estimated MVP monthly cost**: EUR 315-465/month

| Category | Low Estimate | High Estimate |
|---|---|---|
| Hetzner Cloud (compute + storage) | EUR 75 | EUR 95 |
| Scaleway Object Storage | EUR 5 | EUR 15 |
| LLM APIs | EUR 200 | EUR 350 |
| Domain + TLS | EUR 2 | EUR 5 |
| Miscellaneous | EUR 3 | EUR 0 |
| **Total** | **EUR 285** | **EUR 465** |

The MVP cost comfortably fits within the EUR 300-520/month budget allocated in ADR-001.

---

## 2. Hetzner Cloud (Compute + Storage)

### 2.1 Servers

| Resource | Type | Specs | Monthly Cost (EUR) |
|---|---|---|---|
| App server (backend + PG + Keycloak) | CCX33 | 8 vCPU (dedicated), 32 GB RAM | ~55.00 |
| Monitoring server (Redis + Grafana stack) | CX22 | 2 vCPU (shared), 4 GB RAM | ~4.60 |
| **Subtotal servers** | | | **~59.60** |

### 2.2 Volumes

| Volume | Size | Purpose | Monthly Cost (EUR) |
|---|---|---|---|
| PostgreSQL data | 50 GB | Database persistent storage | ~2.40 |
| Monitoring data | 20 GB | Grafana/Loki/Mimir/Tempo storage | ~0.96 |
| **Subtotal volumes** | | | **~3.36** |

Hetzner volume pricing: EUR 0.048/GB/month.

### 2.3 Network

| Item | Included | Overage Cost |
|---|---|---|
| Inbound traffic | Unlimited free | -- |
| Outbound traffic | 20 TB/month included per server | EUR 1.00/TB after |

For MVP (1 school, ~30 students), outbound traffic will be negligible (estimated <100 GB/month). No overage expected.

### 2.4 Snapshots (DR)

| Item | Size | Frequency | Monthly Cost (EUR) |
|---|---|---|---|
| App server snapshot | ~40 GB | Weekly (4/month) | ~7.68 |
| Monitoring server snapshot | ~10 GB | Monthly (1/month) | ~0.48 |
| **Subtotal snapshots** | | | **~8.16** |

Hetzner snapshot pricing: EUR 0.048/GB/month per snapshot retained.

### 2.5 Hetzner Total

| Item | Monthly EUR |
|---|---|
| Servers | 59.60 |
| Volumes | 3.36 |
| Network | 0.00 (included) |
| Snapshots | 8.16 |
| **Hetzner total** | **~71.12** |

Rounding up for variability: **EUR 75-95/month**.

---

## 3. Scaleway Object Storage

### 3.1 Backup Bucket

| Item | Estimate | Unit Cost | Monthly EUR |
|---|---|---|---|
| Storage (full backups, 30-day retention) | ~15 GB | EUR 0.01/GB | 0.15 |
| Storage (WAL archives, 30-day retention) | ~30 GB | EUR 0.01/GB | 0.30 |
| PUT/GET operations | ~10,000/month | EUR 0.01/10K | 0.01 |
| **Subtotal backups** | | | **~0.46** |

### 3.2 Materials Bucket

| Item | Estimate | Unit Cost | Monthly EUR |
|---|---|---|---|
| Storage (lesson materials, 1 class) | ~10 GB | EUR 0.01/GB | 0.10 |
| GET operations (student downloads) | ~5,000/month | EUR 0.01/10K | 0.01 |
| Outbound bandwidth | ~20 GB/month | EUR 0.01/GB | 0.20 |
| **Subtotal materials** | | | **~0.31** |

### 3.3 Terraform State

| Item | Estimate | Unit Cost | Monthly EUR |
|---|---|---|---|
| State file storage | <1 MB | EUR 0.01/GB | ~0.00 |

### 3.4 Scaleway Total

**Scaleway total**: **~EUR 1-5/month** (MVP), scaling to ~EUR 10-15/month with more materials.

---

## 4. LLM API Costs

### 4.1 Pricing (as of May 2026)

| Model | Input (EUR/1M tokens) | Output (EUR/1M tokens) | Use Case |
|---|---|---|---|
| Claude 3.5 Sonnet | ~2.75 | ~13.75 | Primary: content generation, remediation, review docs |
| GPT-4o-mini | ~0.14 | ~0.55 | Secondary: concept mapping, error classification, quiz formatting |

### 4.2 Estimated Token Consumption (MVP: 30 students, 1 class)

| Task | Model | Requests/day | Avg tokens/req (in+out) | Daily tokens | Monthly tokens |
|---|---|---|---|---|---|
| Content generation (F5) | Claude | 15 | 4,000 | 60,000 | 1,200,000 |
| Remediation paths (F11.7) | Claude | 10 | 3,000 | 30,000 | 600,000 |
| Quiz generation (F11.8) | Claude | 20 | 2,000 | 40,000 | 800,000 |
| Chat interactions (F7) | Claude | 30 | 1,500 | 45,000 | 900,000 |
| Review doc generation (F5) | Claude | 5 | 8,000 | 40,000 | 800,000 |
| Concept mapping (F2.4) | GPT-4o-mini | 10 | 2,000 | 20,000 | 400,000 |
| Error classification (F4.2) | GPT-4o-mini | 20 | 1,000 | 20,000 | 400,000 |
| Quiz formatting | GPT-4o-mini | 15 | 1,000 | 15,000 | 300,000 |
| **Total Claude** | | | | **215,000** | **4,300,000** |
| **Total GPT-4o-mini** | | | | **55,000** | **1,100,000** |

### 4.3 Cost Calculation

**Claude (assuming 50% input, 50% output tokens)**:
- Input: 2,150,000 tokens x EUR 2.75/1M = EUR 5.91
- Output: 2,150,000 tokens x EUR 13.75/1M = EUR 29.56
- **Claude monthly**: ~EUR 35.47

**GPT-4o-mini (assuming 60% input, 40% output tokens)**:
- Input: 660,000 tokens x EUR 0.14/1M = EUR 0.09
- Output: 440,000 tokens x EUR 0.55/1M = EUR 0.24
- **GPT-4o-mini monthly**: ~EUR 0.33

**Raw LLM cost**: ~EUR 36/month

### 4.4 Cost with Safety Margins

The raw estimate above assumes optimal caching. Applying multipliers for:

| Factor | Multiplier | Reason |
|---|---|---|
| Cache misses | 2x | Not all requests hit semantic/deterministic cache |
| Prompt engineering iterations | 1.5x | Retry on quality failures |
| Safeguarding re-checks | 1.2x | Content re-generation after safeguarding filter |
| Usage variability | 2x | Some days heavier than others; exam periods |

**Adjusted estimate**: EUR 36 x 2 x 1.5 x 1.2 x 2 = **EUR 259/month** (worst case)

**Realistic range**: **EUR 100-350/month** depending on caching effectiveness and usage patterns.

### 4.5 Cost Optimization Levers

| Lever | Savings | Implementation |
|---|---|---|
| Semantic cache (pgvector, cosine >= 0.95) | 30-50% | Built into LLMGateway |
| Deterministic cache (Redis, exact match) | 10-20% | Built into LLMGateway |
| Batch generation (overnight, off-peak) | 15-25% | Cron job for top-20 lacuna nodes |
| Tiered routing (GPT-4o-mini for simple tasks) | 20-30% | LLMGateway routing rules |
| Prompt optimization (shorter, more focused) | 10-15% | Ongoing engineering effort |

### 4.6 Budget Alerts

From `infra/monitoring/prometheus/alerts.yml`:
- **Warning** at EUR 320/month (80% of EUR 400 budget): `LLMMonthlyBudgetWarning`
- **Critical** at EUR 400/month: `LLMMonthlyBudgetCritical`

### 4.7 Per-Student-Per-Day Cost Tracking

Monitored via `maestro_llm_cost_euros_total` metric with labels:
- `agent`: which agent made the call (content_orchestrator, diagnostic, quiz_generator, etc.)
- `model`: claude-3.5-sonnet, gpt-4o-mini
- `student_id`: pseudonymized student identifier

**Per-student-per-day target**: EUR 0.50-1.50 (EUR 200-350 / 30 students / 20 school days)

---

## 5. Domain + TLS

| Item | Annual Cost | Monthly EUR |
|---|---|---|
| Domain registration (.it or .com) | EUR 10-20/year | ~1.25 |
| TLS certificate (Let's Encrypt) | Free | 0.00 |
| DNS hosting (Hetzner DNS) | Free | 0.00 |
| **Subtotal** | | **~1.25** |

---

## 6. Total Cost Summary

### 6.1 MVP Monthly Budget (1 school, 1 class, ~30 students)

| Category | Low | Expected | High |
|---|---|---|---|
| Hetzner Cloud | 71 | 80 | 95 |
| Scaleway Storage | 1 | 3 | 15 |
| LLM APIs (Claude + GPT-4o-mini) | 100 | 200 | 350 |
| Domain + TLS | 1 | 1 | 2 |
| Miscellaneous (bandwidth overages, etc.) | 0 | 2 | 3 |
| **Total** | **173** | **286** | **465** |

### 6.2 V1 Projection (3 schools, 6 classes, ~180 students)

| Category | Estimated Monthly EUR |
|---|---|
| Hetzner Cloud (upgrade to CCX43 or add server) | 150-200 |
| Scaleway Storage | 20-40 |
| LLM APIs (6x MVP, with improved caching) | 500-1,200 |
| Domain + TLS | 2 |
| **Total** | **672-1,442** |

V1 cost scales primarily with LLM API usage. Infrastructure costs remain modest.

### 6.3 Cost vs Budget

| Phase | Budget (EUR/month) | Estimated (EUR/month) | Status |
|---|---|---|---|
| MVP (1 school) | 300-520 | 173-465 | Within budget |
| V1 (3 schools) | TBD | 672-1,442 | Requires budget increase |

---

## 7. Cost Monitoring Dashboard

The Grafana LLM cost dashboard (provisioned from `infra/monitoring/grafana/dashboards/`) tracks:

1. **Total LLM spend (30-day rolling)**: vs EUR 400 budget line
2. **Daily spend by model**: Claude vs GPT-4o-mini breakdown
3. **Per-agent token consumption**: which agents are most expensive
4. **Per-student daily cost**: identify outlier usage patterns
5. **Cache hit rate**: semantic + deterministic cache effectiveness
6. **Generation latency P95**: per content type vs N4 targets

---

## 8. Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-05-20 | MSTR-12 | Initial draft |

**Review schedule**: Monthly review against actual spend. Adjust projections after first month of pilot data.
