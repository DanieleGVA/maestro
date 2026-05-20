# MAESTRO EU Data Residency Architecture

**Document**: EU-RESID-001
**Status**: Draft
**Author**: MSTR-12 (DevOps & SRE)
**Date**: 2026-05-20
**Approved by**: Pending CTA (MSTR-02) + Privacy (MSTR-16) review
**References**: ADR-001-tech-stack.md, GDPR Art. 44-49, CLAUDE.md (EU data residency is non-negotiable)

---

## 1. Executive Summary

MAESTRO processes personal data of minors (13-19) including special category data (native language, GDPR Art. 9). EU data residency is a non-negotiable requirement. This document proves that every infrastructure layer keeps data within EU jurisdiction and that no data transfer to non-EU countries occurs for stored or processed data.

**Key architectural decisions**:
- Compute: Hetzner Cloud (German company, DE/FI datacenters) -- no CLOUD Act exposure
- Storage: Scaleway Object Storage (French company, FR datacenter) -- no CLOUD Act exposure
- Monitoring: Self-hosted Grafana stack within Hetzner -- no external data transfer
- LLM APIs: Pseudonymized before API call; no PII crosses any border
- Container registry: GHCR (contains only application code, no PII)

---

## 2. Layer-by-Layer EU Residency Proof

### 2.1 Compute: Hetzner Cloud

| Property | Detail |
|---|---|
| Provider | Hetzner Online GmbH |
| Headquarters | Gunzenhausen, Germany |
| Legal jurisdiction | German law (BGB, BDSG) |
| Parent company | None (independent German company) |
| CLOUD Act exposure | **None** -- no US parent company, no US legal jurisdiction |
| Datacenter locations used | fsn1 (Falkenstein, Saxony, DE), nbg1 (Nuremberg, Bavaria, DE), hel1 (Helsinki, FI) |
| Terraform enforcement | `variables.tf` validates `hcloud_location` to `["fsn1", "nbg1", "hel1"]` only |
| Server labels | All servers tagged `eu_resident = "true"` |
| Data processed | All application data, database, authentication, monitoring |

**Terraform validation** (from `infra/terraform/variables.tf`):
```hcl
variable "hcloud_location" {
  validation {
    condition     = contains(["fsn1", "nbg1", "hel1"], var.hcloud_location)
    error_message = "EU data residency: location must be fsn1, nbg1, or hel1."
  }
}
```

This hard constraint prevents any non-EU location from being provisioned, even accidentally.

### 2.2 Storage: Scaleway Object Storage

| Property | Detail |
|---|---|
| Provider | Scaleway SAS (Iliad Group) |
| Headquarters | Paris, France |
| Legal jurisdiction | French law |
| Parent company | Iliad Group (French, publicly traded on Euronext Paris) |
| CLOUD Act exposure | **None** -- no US parent company |
| Region used | fr-par (Paris, France) |
| Terraform enforcement | `region = "fr-par"` hardcoded in `storage.tf` |
| Data stored | Database backups (encrypted pg_dump), WAL archives, lesson materials |
| Bucket ACL | Private (no public access) |
| Versioning | Enabled on backup bucket |

### 2.3 DNS

| Property | Detail |
|---|---|
| Requirement | DNS records must resolve to EU IP addresses |
| A/AAAA records | Point to Hetzner server IPs (EU) |
| DNS provider | To be selected; must be EU-based or support EU-only resolution |
| Recommended options | Hetzner DNS (free, included), Cloudflare (EU-only mode with data localization suite), or self-hosted |
| Data at risk | DNS query logs may contain client IPs |
| Mitigation | Use DNS provider that does not log queries outside EU, or self-host |

**Recommendation**: Use Hetzner DNS (free, included with Hetzner account, German company, no CLOUD Act exposure). Hetzner DNS provides authoritative DNS with anycast from EU locations.

### 2.4 TLS Certificates

| Property | Detail |
|---|---|
| Provider | Let's Encrypt (ISRG) |
| Headquarters | San Francisco, USA |
| Data stored by provider | **None** -- Let's Encrypt does not store user data |
| ACME challenge | HTTP-01 or DNS-01 (no PII transmitted) |
| Certificate generation | Automated on EU server (certbot/Caddy) |
| Private keys | Generated and stored on Hetzner server only; never leave EU |
| EU residency impact | **None** -- certificates are public cryptographic artifacts; private keys stay on EU servers |

### 2.5 LLM API Providers

| Property | Claude (Anthropic) | GPT-4o-mini (OpenAI) |
|---|---|---|
| Headquarters | San Francisco, USA | San Francisco, USA |
| CLOUD Act exposure | Yes (US company) | Yes (US company) |
| Data sent | **Pseudonymized prompts only** | **Pseudonymized prompts only** |
| PII transmitted | **None** | **None** |
| Art. 9 data transmitted | **None** (language codes only, not student identity) | **None** |

**Pseudonymization boundary** (implemented in LLMGateway service):

| Data type | Before pseudonymization | After pseudonymization (sent to LLM) |
|---|---|---|
| Student name | "Marco Rossi" | `STUDENT_0042` |
| Teacher name | "Prof. Bianchi" | `TEACHER_0003` |
| School name | "ITIS Volta Milano" | `SCHOOL_001` |
| Native language | "Ukrainian" | `uk` (ISO 639-1 code only, no student association) |
| Class | "3A Informatica" | `CLASS_001` |
| KMM state | `lacuna` on "Variabili in Python" | `lacuna` on "Variabili in Python" (concept names are not PII) |

**What crosses the EU border**: Only pseudonymized learning prompts containing concept names, state labels, and anonymized student identifiers. No PII, no special category data, no data that can be linked back to a real student without access to the pseudonymization mapping table (which exists only in-memory on the EU server and is never persisted or transmitted).

**Legal basis**: GDPR Art. 49(1)(a) -- explicit consent for profiling (consent type (a) per CLAUDE.md), combined with pseudonymization rendering data non-personal per Recital 26. Additional protection: EU DPA with both Anthropic and OpenAI required before production.

### 2.6 Monitoring Stack

| Component | Location | Data type | EU resident |
|---|---|---|---|
| Grafana | Hetzner (DE/FI) | Dashboards, user sessions | Yes |
| Mimir (metrics) | Hetzner (DE/FI) | Application/infra metrics | Yes |
| Loki (logs) | Hetzner (DE/FI) | Application logs (may contain pseudonymized IDs) | Yes |
| Tempo (traces) | Hetzner (DE/FI) | Distributed traces | Yes |
| OTel Collector | Hetzner (DE/FI) | Telemetry pipeline | Yes |

All monitoring components are self-hosted within the Hetzner infrastructure. No telemetry data leaves the EU.

### 2.7 Container Registry

| Property | Detail |
|---|---|
| Provider | GitHub Container Registry (GHCR) |
| Headquarters | GitHub (Microsoft), USA |
| Data stored | Docker images (application code only) |
| PII in images | **None** -- images contain compiled application code, no student data |
| EU residency impact | **None** -- no personal data in container images |
| Alternative | Self-hosted registry on Hetzner (if GHCR is deemed unacceptable) |

GHCR stores only application code artifacts. No personal data, configuration secrets, or student information is baked into Docker images. Secrets are injected at runtime via environment variables stored on the EU server.

### 2.8 Email/Notifications

| Property | Detail |
|---|---|
| Requirement | Notifications to families (F14.7) must use EU provider |
| Recommended provider | Mailgun EU (EU datacenter option) or self-hosted Postfix on Hetzner |
| Data in notifications | Student name, class, learning progress summary |
| Constraint | Must use EU-based sending infrastructure; no US relay |

**MVP note**: For MVP (1 school, 1 class), email notifications may be deferred. When implemented, the email provider must be EU-resident or self-hosted.

### 2.9 Source Code & CI/CD

| Component | Provider | Location | PII | EU Impact |
|---|---|---|---|---|
| Source code | GitHub | USA | None | No PII in code |
| CI/CD runners | GitHub Actions | USA (runner) | None | No PII in CI; builds only code |
| Deployment | SSH to Hetzner | EU (target) | None in transit | Deployment transfers code, not data |

CI/CD processes handle only application code and infrastructure definitions. No student data or PII is present in the CI/CD pipeline.

---

## 3. Data Flow Diagram

```
                         EU BOUNDARY
    =====================================================
    |                                                   |
    |  +------------------+    +-------------------+    |
    |  | Hetzner DE/FI    |    | Scaleway FR       |    |
    |  |                  |    |                    |    |
    |  | +------+  +----+ |    | +---------------+ |    |
    |  | |FastAPI|  | PG | |    | | S3 Backups    | |    |
    |  | +------+  +----+ |    | | (encrypted)   | |    |
    |  |    |         |    |    | +---------------+ |    |
    |  | +------+  +----+ |    |                    |    |
    |  | |Redis |  | KC | |    | +---------------+ |    |
    |  | +------+  +----+ |    | | S3 Materials  | |    |
    |  |    |              |    | +---------------+ |    |
    |  | +------+         |    +-------------------+    |
    |  | |Grafana|        |                             |
    |  | |Loki   |        |                             |
    |  | |Mimir  |        |                             |
    |  | |Tempo  |        |                             |
    |  | +------+         |                             |
    |  +------------------+                             |
    |       |         |                                 |
    ========|=========|=================================
            |         |
    +-------+--+  +---+---------------+
    | LLMGateway|  | Pseudonymization |
    | (on EU    |  | Boundary         |
    |  server)  |  | (in-memory only) |
    +-----------+  +------------------+
            |
    --------|----- NON-EU CROSSING (pseudonymized only) ----
            |
    +-------v--------+    +------------------+
    | Anthropic API   |    | OpenAI API       |
    | (Claude)        |    | (GPT-4o-mini)    |
    | San Francisco   |    | San Francisco    |
    +-----------------+    +------------------+

    Data crossing border: ONLY pseudonymized prompts
    - No student names, no school names
    - No native language association
    - No data that can identify a natural person


    +------------------+    +------------------+
    | GitHub (GHCR)    |    | Let's Encrypt    |
    | Container images |    | TLS certs        |
    | (no PII)         |    | (no PII)         |
    +------------------+    +------------------+

    +------------------+
    | Student devices   |
    | (mobile app)      |
    | Client-side only  |
    +------------------+
```

### Data Flow Classification

| Flow | Source | Destination | Data | EU/Non-EU | PII |
|---|---|---|---|---|---|
| Student -> API | Student device | Hetzner DE/FI | Auth tokens, quiz answers | EU -> EU | Yes (pseudonymized at server) |
| API -> PostgreSQL | FastAPI | PostgreSQL (same server) | All application data | EU internal | Yes (encrypted at rest) |
| API -> Redis | FastAPI | Redis (Hetzner) | Cache entries, sessions | EU internal | Pseudonymized |
| API -> LLM | LLMGateway | Anthropic/OpenAI API | Pseudonymized prompts | EU -> US | **No PII** |
| LLM -> API | Anthropic/OpenAI | LLMGateway | Generated content | US -> EU | No PII |
| PG -> S3 backup | PostgreSQL | Scaleway fr-par | Encrypted backup | EU -> EU | Yes (encrypted) |
| Materials -> S3 | Teacher upload | Scaleway fr-par | Lesson files | EU -> EU | Minimal |
| CI/CD -> Deploy | GitHub Actions | Hetzner DE/FI | Docker images | US -> EU | **No PII** |
| Monitoring | All services | Grafana stack (Hetzner) | Metrics, logs, traces | EU internal | Pseudonymized |

---

## 4. EU Residency Enforcement Mechanisms

### 4.1 Infrastructure Level

1. **Terraform validation**: `hcloud_location` variable constrained to `["fsn1", "nbg1", "hel1"]`; any other value is rejected at plan time
2. **Resource labels**: All Hetzner resources tagged with `eu_resident = "true"`
3. **Scaleway region**: Hardcoded to `fr-par` in Terraform; no variable substitution
4. **CI/CD check**: Deployment pipeline verifies target server is in Hetzner EU location

### 4.2 Application Level

1. **LLMGateway pseudonymization**: All PII stripped before any external API call
2. **Pseudonymization mapping**: In-memory only, never persisted to disk, never logged
3. **Audit log**: Records pseudonymized versions, not original PII
4. **PII encryption key**: Stored as environment variable on EU server only

### 4.3 Operational Level

1. **No manual console changes**: All infrastructure changes through Terraform (IaC)
2. **SSH access**: Restricted to whitelisted IPs via Hetzner firewall
3. **Backup encryption**: pg_dump with custom format (not plaintext)
4. **Monitoring data**: All telemetry stays on self-hosted Grafana within Hetzner

### 4.4 Compliance Audit Trail

Every infrastructure change is tracked through:
- Terraform state (versioned in Scaleway S3)
- Git history (all IaC in `infra/` directory)
- Deployment logs (GitHub Actions audit trail)
- Hetzner Cloud audit log (API call history)

---

## 5. Compliance Attestation Template

### EU Data Residency Self-Assessment

**Assessment date**: ____________________
**Assessor**: ____________________
**Role**: ____________________

| # | Check | Pass/Fail | Evidence |
|---|---|---|---|
| 1 | All compute resources are in EU Hetzner locations (fsn1/nbg1/hel1) | | Hetzner console / `terraform show` |
| 2 | All object storage is in Scaleway fr-par | | Scaleway console / `terraform show` |
| 3 | PostgreSQL data volume is attached to EU server only | | `hcloud volume list` |
| 4 | No PII is transmitted to LLM providers | | LLMGateway code review + audit log sample |
| 5 | Pseudonymization mapping is in-memory only | | Code review of LLMGateway service |
| 6 | Monitoring stack is self-hosted on EU infrastructure | | `docker compose ps` on monitoring server |
| 7 | Container images contain no PII | | Dockerfile review |
| 8 | Backup encryption is enabled | | Backup script review + sample backup inspection |
| 9 | DNS resolves to EU IP addresses | | `dig maestro.<domain>` |
| 10 | TLS private keys are stored on EU server only | | Server file inspection |
| 11 | Terraform location constraint is enforced | | `variables.tf` review |
| 12 | No US-based services store PII | | Architecture review |
| 13 | Email provider (when implemented) is EU-based | | Provider contract review |
| 14 | Audit log is stored on EU infrastructure only | | PostgreSQL location verification |
| 15 | Right to erasure deletes from all EU locations | | Erasure procedure test |

**Attestation**: I confirm that all checks above have been verified and MAESTRO infrastructure maintains EU data residency for all personal data processing.

Signature: ____________________
Date: ____________________

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hetzner acquired by US company | Low | High | Terraform IaC enables migration to alternative EU provider (Scaleway, OVH) within days |
| Scaleway acquired by US company | Low | High | Migrate backups to Hetzner Backup or alternative EU S3 provider |
| LLM pseudonymization bypass (bug) | Medium | Critical | Code review by MSTR-13; automated PII detection tests in CI; audit log monitoring |
| Developer accidentally uses non-EU region | Low | High | Terraform validation prevents non-EU locations; CI check validates |
| GHCR stores metadata that constitutes PII | Very Low | Low | Container images contain only code; switch to self-hosted registry if needed |
| DNS provider logs queries outside EU | Medium | Medium | Use Hetzner DNS (German company, EU logs) |

---

## 7. Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-05-20 | MSTR-12 | Initial draft |

**Review schedule**: Reviewed annually or when infrastructure providers change.
**Required reviewers**: MSTR-02 (CTA), MSTR-13 (Security), MSTR-16 (Privacy)
