# MAESTRO Disaster Recovery Plan

**Document**: DR-PLAN-001
**Status**: Draft
**Author**: MSTR-12 (DevOps & SRE)
**Date**: 2026-05-20
**Approved by**: Pending CTA (MSTR-02) review
**References**: ADR-001-tech-stack.md, N2 (RPO <=24h, RTO <=4h), N4 (99.5% school-hours availability)

---

## 1. Recovery Objectives

### 1.1 Recovery Point Objective (RPO): <= 24 hours

Maximum acceptable data loss is 24 hours, achieved through:

- **PostgreSQL**: Daily full backup (pg_dump, custom format, compressed) at 02:00 UTC + continuous WAL archiving to Scaleway Object Storage (fr-par). Effective RPO for database is the time since the last WAL segment was archived (typically minutes, worst case 24h if WAL archiving fails silently).
- **Redis**: No RPO guarantee. Redis serves as a cache layer (LRU eviction, session cache, semantic cache). All data is rebuildable from PostgreSQL. RDB snapshots are taken every 60 seconds for convenience but are not DR-critical.
- **Keycloak**: Backed up as part of PostgreSQL (Keycloak uses a dedicated schema in the same PG instance). Realm configuration is additionally exported as JSON and stored in version control.
- **Application code**: Immutable Docker images stored in GHCR (tagged by git SHA). Source code in GitHub. RPO = 0 (no data stored in application containers).
- **Terraform state**: Versioned in Scaleway Object Storage bucket with versioning enabled. RPO = 0 for infrastructure-as-code definitions.
- **Monitoring data**: Metrics (Mimir) have 30-day retention. Grafana dashboards are provisioned from git. Loss of monitoring data does not impact service recovery.

### 1.2 Recovery Time Objective (RTO): <= 4 hours

Maximum acceptable downtime is 4 hours (full service restoration), broken down as:

| Phase | Target | Description |
|---|---|---|
| Detection | 0-15 min | Automated alerting via Grafana/Mimir (ServiceDown alert fires after 2 min) |
| Assessment | 15-30 min | On-call engineer assesses scope, identifies scenario |
| Infrastructure provisioning | 30-90 min | Terraform apply for new server (Hetzner API typical: 30s for server, 5 min for volume) |
| Data restoration | 60-180 min | pg_restore from Scaleway S3 + WAL replay for PITR |
| Service startup | 15-30 min | Docker compose up + health checks + smoke tests |
| Verification | 15-30 min | End-to-end verification, DNS propagation check |
| **Total** | **<= 4 hours** | |

### 1.3 Recovery Point Timeline

| Component | Latest Recovery Point | Recovery Method |
|---|---|---|
| PostgreSQL (data) | Minutes ago (WAL) | PITR via WAL replay |
| PostgreSQL (data) | Last night 02:00 UTC | Full pg_dump restore |
| Keycloak (config) | Last night 02:00 UTC | PG restore + realm JSON from git |
| Redis (cache) | N/A (rebuildable) | Cold start, cache warms organically |
| Application | Current git SHA | Pull Docker image from GHCR |
| Terraform state | Last infra change | Versioned in Scaleway S3 |
| Grafana dashboards | Current git commit | Provisioned from git on startup |
| Lesson materials | Current version | Scaleway Object Storage (versioned bucket) |

---

## 2. Backup Strategy

### 2.1 PostgreSQL

**Daily full backup** (runs at 02:00 UTC via cron):
- Script: `infra/scripts/backup.sh full`
- Format: pg_dump custom format, compression level 9
- Destination: Scaleway Object Storage `s3://maestro-backups-production/full/`
- Retention: 30 days (lifecycle rule on bucket), transition to ONEZONE_IA after 7 days
- Verification: Upload verified via `aws s3 ls` after each backup; monthly restore test

**Continuous WAL archiving**:
- PostgreSQL `archive_mode=on` with `archive_command` copying WAL segments to `/archive/`
- Script: `infra/scripts/backup.sh wal` pushes WAL segments to `s3://maestro-backups-production/wal/`
- Enables Point-in-Time Recovery (PITR) to any moment between full backups

**Cron configuration** (on app server):
```
# /etc/cron.d/maestro-backup
0 2 * * * root /opt/maestro/scripts/backup.sh full >> /var/log/maestro-backup.log 2>&1
```

### 2.2 Redis

- **Type**: RDB snapshots (appendonly yes, appendfsync everysec)
- **Criticality**: Low. Redis is a cache layer with LRU eviction policy
- **Recovery**: Redis starts empty; cache warms through normal application usage
- **No S3 backup**: Redis data is not backed up to S3 because all authoritative data lives in PostgreSQL

### 2.3 Keycloak

- **Database**: Keycloak stores all data in the PostgreSQL `keycloak` schema, backed up with the daily pg_dump
- **Realm export**: Monthly realm configuration export via Keycloak admin CLI:
  ```bash
  docker exec maestro-keycloak /opt/keycloak/bin/kc.sh export \
    --dir /tmp/keycloak-export --realm maestro
  ```
  Exported JSON committed to `infra/keycloak/realm-export/` in git
- **Recovery**: Restore PG database; if realm config is corrupted, import from git-stored JSON

### 2.4 Application (Docker Images)

- **Registry**: GitHub Container Registry (GHCR)
- **Tagging**: Images tagged with git short SHA + `production` tag
- **Immutability**: Images are never overwritten; each deployment creates a new SHA tag
- **Recovery**: `docker pull ghcr.io/<org>/maestro-backend:<sha>`
- **Retention**: GHCR retains all tagged images indefinitely

### 2.5 Terraform State

- **Backend**: Local state file, backed up to Scaleway Object Storage
- **Versioning**: Bucket versioning enabled on `maestro-backups-production`
- **Location**: `s3://maestro-backups-production/terraform/terraform.tfstate`
- **Recovery**: Download latest version from S3; run `terraform plan` to verify consistency

### 2.6 Monitoring Data

- **Grafana dashboards**: Provisioned from git (`infra/monitoring/grafana/dashboards/`). No backup needed.
- **Metrics (Mimir)**: 30-day retention. Loss is non-critical; metrics are operational, not business data.
- **Logs (Loki)**: 14-day retention. Loss is non-critical for DR purposes.
- **Traces (Tempo)**: 7-day retention. Loss is non-critical.

### 2.7 Lesson Materials

- **Storage**: Scaleway Object Storage `maestro-materials-production` bucket
- **Versioning**: Disabled (materials are teacher-uploaded, original source exists with teacher)
- **Recovery**: Re-upload from teacher's original files if bucket is lost (Scaleway provides 99.999% durability)

---

## 3. Failure Scenarios & Recovery Procedures

### S1: Application Server Failure (Single Server)

**Impact**: Complete service outage (backend, PostgreSQL, Keycloak all run on app server)
**Detection**: `ServiceDown` alert fires within 2 minutes; `up{job="maestro-backend"} == 0`
**RPO**: Minutes (WAL segments archived to S3)
**RTO**: 2-3 hours

**Recovery procedure**:

1. **Assess**: SSH to server (if reachable) or check Hetzner console
   ```bash
   ssh deploy@<app-server-ip> "docker compose ps" || echo "Server unreachable"
   ```

2. **If server is reachable but services are down**:
   ```bash
   cd /opt/maestro
   docker compose -f docker-compose.yml -f docker-compose.prod.yml down
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   # Wait for health check
   curl -sf https://<domain>/api/v1/health
   ```

3. **If server is unreachable (hardware failure)**:
   ```bash
   # Provision new server via Terraform
   cd infra/terraform
   terraform apply -target=hcloud_server.app -target=hcloud_volume.postgres_data \
     -target=hcloud_volume_attachment.postgres_data

   # SSH to new server, install Docker (user_data script runs automatically)
   # Wait for user_data to complete (~2 min)
   sleep 120

   # Copy compose files and configuration
   scp -r infra/docker/ deploy@<new-ip>:/opt/maestro/
   scp infra/scripts/*.sh deploy@<new-ip>:/opt/maestro/scripts/
   scp .env.production deploy@<new-ip>:/opt/maestro/.env

   # Restore database from latest backup
   ssh deploy@<new-ip> "/opt/maestro/scripts/restore.sh full"

   # Start services
   ssh deploy@<new-ip> "cd /opt/maestro && docker compose -f docker-compose.yml \
     -f docker-compose.prod.yml up -d"

   # Update DNS if IP changed
   # Verify health
   curl -sf https://<domain>/api/v1/health
   ```

4. **Post-recovery**:
   - Verify student data integrity: run `SELECT count(*) FROM kmm_states` and compare with last known count
   - Check audit log continuity: `SELECT max(timestamp) FROM audit_log`
   - Notify school administration if outage exceeded 30 minutes during school hours

---

### S2: Database Corruption or Failure

**Impact**: Data integrity loss; all services depend on PostgreSQL
**Detection**: `DatabaseConnectionPoolExhaustion` alert or application error logs showing PG connection failures
**RPO**: Minutes (PITR) or last full backup (24h worst case)
**RTO**: 1-3 hours

**Recovery procedure**:

1. **Assess corruption scope**:
   ```bash
   # Check if PG is running
   docker exec maestro-postgres pg_isready

   # Check for corruption
   docker exec maestro-postgres psql -U maestro_app -d maestro \
     -c "SELECT datname, checksum_failures FROM pg_stat_database WHERE datname='maestro';"
   ```

2. **Option A: PITR (preferred, minimizes data loss)**:
   ```bash
   # Determine target recovery time (last known good state)
   # Stop the application to prevent further writes
   docker compose stop backend dashboard keycloak

   # Run PITR restore
   /opt/maestro/scripts/restore.sh pitr "2026-05-20 09:30:00 UTC"

   # Follow the PITR instructions output by the script
   # After PG recovery completes:
   docker compose start keycloak backend dashboard
   ```

3. **Option B: Full restore (if WAL segments are unavailable)**:
   ```bash
   /opt/maestro/scripts/restore.sh full

   # Restart all services
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Post-recovery**:
   - Run data integrity checks on KMM state tables
   - Verify Keycloak authentication works (test login)
   - Check audit_log for gaps
   - Document data loss window in incident report

---

### S3: Redis Cache Failure

**Impact**: Degraded performance (cache miss on every request); no data loss
**Detection**: Application latency increase; `HighP95Latency` alert
**RPO**: N/A (cache is rebuildable)
**RTO**: 5-15 minutes

**Recovery procedure**:

1. **Restart Redis**:
   ```bash
   docker compose restart redis
   ```

2. **If persistent failure**:
   ```bash
   # Remove Redis data and restart fresh
   docker compose stop redis
   docker volume rm maestro_redis_data
   docker compose up -d redis
   ```

3. **Post-recovery**: Cache warms organically through normal usage. No manual intervention needed.

---

### S4: Keycloak Authentication Failure

**Impact**: No new user logins; existing authenticated sessions may continue (JWT validity)
**Detection**: Login failures reported by users or monitoring
**RPO**: Last PG backup (Keycloak data is in PG)
**RTO**: 15-60 minutes

**Recovery procedure**:

1. **Restart Keycloak**:
   ```bash
   docker compose restart keycloak
   # Check Keycloak health
   curl -sf http://localhost:8080/health/ready
   ```

2. **If realm is corrupted**:
   ```bash
   # Import realm from git-stored export
   docker exec maestro-keycloak /opt/keycloak/bin/kc.sh import \
     --dir /opt/maestro/keycloak/realm-export/
   docker compose restart keycloak
   ```

3. **If Keycloak DB schema is corrupted**: Follow S2 (Database Corruption) procedure, restoring only the keycloak schema if possible.

4. **Post-recovery**:
   - Test login flow for student, teacher, and admin roles
   - Verify SAML/OIDC federation with school IdP
   - Check that MFA is functional for admin accounts

---

### S5: Complete Datacenter Loss (Hetzner DE -> Hetzner FI Failover)

**Impact**: Complete infrastructure loss at primary location
**Detection**: All Hetzner DE monitoring endpoints unreachable
**RPO**: Last WAL segment archived to Scaleway S3 (typically minutes)
**RTO**: 3-4 hours

**Recovery procedure**:

1. **Confirm datacenter loss** (not a transient network issue):
   - Check Hetzner status page
   - Attempt SSH from multiple networks
   - Wait 15 minutes before declaring datacenter loss

2. **Provision infrastructure in Helsinki (hel1)**:
   ```bash
   cd infra/terraform

   # Update location variable
   export TF_VAR_hcloud_location="hel1"

   # Apply full infrastructure
   terraform apply
   ```

3. **Restore data**:
   ```bash
   # All backups are in Scaleway fr-par (unaffected by Hetzner DC loss)
   ssh deploy@<new-hel1-ip> "/opt/maestro/scripts/restore.sh full"

   # If PITR is needed, WAL segments are also in Scaleway
   ssh deploy@<new-hel1-ip> "/opt/maestro/scripts/restore.sh pitr '<target_time>'"
   ```

4. **Deploy application**:
   ```bash
   ssh deploy@<new-hel1-ip> "cd /opt/maestro && \
     docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && \
     docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
   ```

5. **Update DNS**: Point `maestro.<domain>` to new hel1 server IP

6. **Post-recovery**:
   - Full data integrity verification
   - End-to-end test of all user flows
   - Notify school administration
   - File incident report

**Key architectural note**: Backups are stored in Scaleway (France), completely independent of Hetzner. A total Hetzner failure does not affect backup availability.

---

### S6: LLM API Provider Outage (Claude -> GPT-4o-mini Fallback)

**Impact**: Content generation degraded (lower quality) but not halted
**Detection**: `LLMHighLatency` alert or LLM error rate increase in application logs
**RPO**: N/A (no data loss)
**RTO**: 5 minutes (automatic fallback) to 30 minutes (manual intervention)

**Recovery procedure**:

1. **Automatic fallback** (built into LLMGateway):
   - The LLMGateway service detects Claude API errors/timeouts
   - Routes all requests to GPT-4o-mini as fallback
   - Quality is lower but service continues

2. **If both Claude and GPT-4o-mini are unavailable**:
   ```bash
   # Enable cached-only mode via environment variable
   ssh deploy@<app-server> "cd /opt/maestro && \
     echo 'MAESTRO_LLM_CACHE_ONLY=true' >> .env && \
     docker compose restart backend"
   ```
   In cache-only mode, previously generated content is served but no new generation occurs.

3. **If extended outage (>2 hours)**:
   - Notify teachers that new content generation is temporarily unavailable
   - Students can continue accessing previously generated materials
   - Quiz and remediation content from cache continues to work

4. **Post-recovery**:
   - Monitor LLM provider status pages
   - Disable cache-only mode when provider recovers
   - Review any queued generation requests

---

### S7: Scaleway Storage Failure

**Impact**: Backup availability compromised; lesson materials unavailable for new downloads
**Detection**: Backup script failure alerts; S3 API errors in logs
**RPO**: At risk (no new backups can be stored)
**RTO**: Backups: immediate switch to local retention; materials: depends on Scaleway recovery

**Recovery procedure**:

1. **Switch to local-only backup retention**:
   ```bash
   # Modify backup script to skip S3 upload and extend local retention
   ssh deploy@<app-server> "cd /opt/maestro && \
     export MAESTRO_BACKUP_RETENTION_DAYS=7 && \
     /opt/maestro/scripts/backup.sh full"
   ```

2. **For lesson materials**: Scaleway provides 99.999% durability. If a genuine region failure occurs:
   - Teachers re-upload materials from their local copies
   - Generated content is re-generated from the content pipeline

3. **Post-recovery**:
   - Sync local backups to Scaleway once restored
   - Verify backup integrity with restore test
   - Review Scaleway incident report

---

### S8: DNS Failure

**Impact**: Service unreachable by domain name; IP-based access still works
**Detection**: External monitoring (uptime check on domain) fails; direct IP health check succeeds
**RPO**: N/A
**RTO**: 5 minutes to 4 hours (DNS propagation)

**Recovery procedure**:

1. **Verify it is a DNS issue**:
   ```bash
   # Check if service responds on IP directly
   curl -sf -H "Host: maestro.<domain>" https://<server-ip>/api/v1/health

   # Check DNS resolution
   dig maestro.<domain>
   ```

2. **If DNS provider is down**:
   - Switch to backup DNS provider (if configured)
   - Update NS records at registrar (propagation: up to 48h, typically 1-4h)
   - As interim measure, distribute direct IP to school IT administrators

3. **If DNS record is incorrect**:
   - Update A/AAAA record at DNS provider
   - Reduce TTL to 300s temporarily for faster propagation

---

### S9: TLS Certificate Expiry

**Impact**: HTTPS errors for all clients; browsers refuse connection
**Detection**: Certificate expiry monitoring alert (7 days before expiry)
**RPO**: N/A
**RTO**: 5-30 minutes

**Recovery procedure**:

1. **Renew certificate** (Let's Encrypt via Caddy/certbot):
   ```bash
   # If using certbot
   ssh deploy@<app-server> "certbot renew --force-renewal"

   # If using Caddy (auto-renewal)
   ssh deploy@<app-server> "docker compose restart caddy"
   ```

2. **If auto-renewal is broken**:
   ```bash
   # Manual certificate issuance
   ssh deploy@<app-server> "certbot certonly --standalone \
     -d maestro.<domain> --agree-tos -m ops@<domain>"

   # Copy certificate to appropriate location and restart reverse proxy
   ```

3. **Prevention**: Alert rule fires 7 days before expiry. Let's Encrypt certificates are valid for 90 days and auto-renew at 60 days.

---

### S10: Security Breach / Data Exfiltration

**Impact**: Potential exposure of student PII (minors 13-19); GDPR Art. 33/34 obligations triggered
**Detection**: Anomalous database queries in audit log; IDS/monitoring alerts; external report
**RPO**: Forensic preservation required (no data destruction)
**RTO**: Service may remain offline until security clearance

**Recovery procedure**:

1. **Immediate containment (first 30 minutes)**:
   ```bash
   # Isolate the compromised server -- block all inbound except SSH from trusted IP
   # Via Hetzner firewall API or:
   ssh deploy@<app-server> "ufw default deny incoming && ufw allow from <trusted-ip> to any port 22"

   # Preserve evidence -- snapshot the server
   hcloud server create-image --type=snapshot <server-id> --description="incident-$(date +%Y%m%d)"

   # Rotate all credentials immediately
   # - Database passwords
   # - API keys (Anthropic, OpenAI)
   # - Keycloak admin password
   # - SSH keys
   # - Scaleway access keys
   ```

2. **Assessment (hours 1-4)**:
   - Review audit_log for unauthorized access patterns
   - Check PostgreSQL pg_stat_activity for suspicious queries
   - Review Loki logs for unusual API calls
   - Determine scope: which data was accessed, which students affected

3. **Notification obligations (GDPR Art. 33: 72-hour window)**:
   - **Garante per la protezione dei dati personali**: Notify within 72 hours if personal data breach confirmed
   - **School administration**: Notify immediately
   - **Affected students/families**: Notify if high risk to rights and freedoms (Art. 34)
   - Use notification templates in Section 5 of this document

4. **Recovery**:
   - Provision new server infrastructure from scratch (do not reuse compromised server)
   - Restore from last known clean backup
   - Deploy with rotated credentials
   - Engage MSTR-13 (Security Engineer) for forensic review

5. **Post-incident**:
   - File formal incident report
   - Conduct root cause analysis
   - Update security controls based on findings
   - Schedule additional penetration test

---

## 4. Testing Schedule

### 4.1 Monthly: Backup Restore Verification

**What**: Restore the latest daily backup to a staging environment and verify data integrity.

**Procedure**:
1. Provision a temporary staging server on Hetzner (same location)
2. Download latest backup from Scaleway S3
3. Run `restore.sh full` on staging server
4. Execute data integrity checks:
   - Row counts on critical tables (kmm_states, kmm_transitions, audit_log, consents)
   - Sample query: verify a known student's KMM state matches production
   - Keycloak: verify realm configuration and test login
5. Tear down staging server
6. Log results in `.maestro/tests/dr-backup-verify-<date>.md`

**Success criteria**: Backup restores without errors; data integrity checks pass; total restore time < 2 hours.

### 4.2 Quarterly: Full DR Drill (Staging Environment)

**What**: Simulate a complete server failure and execute recovery procedure end-to-end.

**Procedure**:
1. Create a staging environment mirroring production (Terraform with `environment=staging`)
2. Populate staging with synthetic student data
3. Run daily backup + WAL archiving for 1 week
4. Simulate failure: destroy the staging app server (`terraform destroy -target=hcloud_server.app`)
5. Execute S1 (Application Server Failure) recovery procedure
6. Measure and document:
   - Time to detect (simulated: immediate)
   - Time to provision new infrastructure
   - Time to restore data
   - Time to full service availability
   - Data integrity post-recovery
7. Log results in `.maestro/tests/dr-drill-<date>.md`

**Success criteria**: Full recovery in < 4 hours (RTO); no data loss beyond RPO; all user flows functional.

### 4.3 Annually: Datacenter Failover Test

**What**: Test S5 (Complete Datacenter Loss) by failing over from fsn1 (DE) to hel1 (FI).

**Procedure**:
1. Create full production mirror in staging at fsn1
2. Run workload for 1 week with synthetic data
3. Execute datacenter failover to hel1
4. Measure:
   - Total failover time
   - Data integrity
   - DNS propagation time
   - All service functionality in new location
5. Fail back to fsn1
6. Log results in `.maestro/tests/dr-failover-<date>.md`

**Success criteria**: Failover completes in < 4 hours; failback completes in < 4 hours; zero data loss within RPO.

### 4.4 DR Test Calendar

| Month | Test Type | Scenario |
|---|---|---|
| January | Monthly backup verify | Standard |
| February | Monthly backup verify | Standard |
| March | Quarterly DR drill | S1: Server failure |
| April | Monthly backup verify | Standard |
| May | Monthly backup verify | Standard |
| June | Quarterly DR drill | S2: Database corruption |
| July | Monthly backup verify | Standard |
| August | Monthly backup verify + Annual failover | S5: Datacenter loss |
| September | Quarterly DR drill | S5: Datacenter failover (staging) |
| October | Monthly backup verify | Standard |
| November | Monthly backup verify | Standard |
| December | Quarterly DR drill | S10: Security breach (tabletop) |

---

## 5. Communication Plan

### 5.1 Internal Escalation Chain

| Severity | First Responder | Escalation (15 min) | Escalation (60 min) |
|---|---|---|---|
| P1 (service down) | MSTR-12 (DevOps/SRE) | MSTR-02 (CTA) | MSTR-01 (Director) -> Daniele (Human) |
| P2 (degraded) | MSTR-12 (DevOps/SRE) | MSTR-02 (CTA) | -- |
| P3 (non-critical) | MSTR-12 (DevOps/SRE) | -- | -- |
| Security breach | MSTR-13 (Security) + MSTR-12 | MSTR-02 + MSTR-16 (Privacy) | MSTR-01 -> Daniele |
| Safeguarding alert | MSTR-19 (Safeguarding) | MSTR-01 (Director) | Daniele (Human) |

### 5.2 School Notification Templates

**Template A: Planned Maintenance**
```
Oggetto: MAESTRO -- Manutenzione programmata

Gentile Dirigente/Referente IT,

La piattaforma MAESTRO sara' in manutenzione il giorno [DATA]
dalle ore [ORA_INIZIO] alle ore [ORA_FINE] (CET).

Durante questo periodo il servizio non sara' disponibile.
I dati degli studenti non saranno interessati.

Per qualsiasi domanda: [CONTATTO_SUPPORTO]

Cordiali saluti,
Il team MAESTRO
```

**Template B: Unplanned Outage**
```
Oggetto: MAESTRO -- Disservizio in corso

Gentile Dirigente/Referente IT,

Stiamo riscontrando un disservizio sulla piattaforma MAESTRO
a partire dalle ore [ORA_INIZIO] (CET).

Il nostro team sta lavorando alla risoluzione.
Tempo stimato di ripristino: [STIMA].

I dati degli studenti sono al sicuro.
Forniremo aggiornamenti ogni [30/60] minuti.

Per qualsiasi domanda: [CONTATTO_SUPPORTO]

Cordiali saluti,
Il team MAESTRO
```

**Template C: Service Restored**
```
Oggetto: MAESTRO -- Servizio ripristinato

Gentile Dirigente/Referente IT,

Il servizio MAESTRO e' stato ripristinato alle ore [ORA] (CET).

Causa del disservizio: [CAUSA_BREVE]
Durata totale: [DURATA]
Impatto sui dati: [NESSUNO / DESCRIZIONE]

Ci scusiamo per il disagio.

Per qualsiasi domanda: [CONTATTO_SUPPORTO]

Cordiali saluti,
Il team MAESTRO
```

### 5.3 Garante Privacy Breach Notification (72h Window)

Per GDPR Art. 33, data breaches must be notified to the Garante per la protezione dei dati personali within 72 hours of becoming aware of the breach.

**Notification channel**: https://servizi.gpdp.it/databreach/s/ (Garante online portal)

**Required information**:

1. **Nature of the breach**: description of the breach, categories and approximate number of data subjects affected, categories and approximate number of personal data records affected
2. **DPO contact**: Name and contact of the Data Protection Officer or other contact point
3. **Likely consequences**: Description of the likely consequences of the breach
4. **Measures taken**: Description of the measures taken or proposed to address the breach, including measures to mitigate possible adverse effects

**MAESTRO-specific considerations**:
- All data subjects are minors (13-19): heightened notification obligation
- Native language data (GDPR Art. 9): special category breach triggers mandatory notification regardless of risk assessment
- Consent data: breach of consent records requires notification to each affected family

**Notification timeline**:
| Time | Action |
|---|---|
| T+0h | Breach detected; containment begins |
| T+1h | Initial assessment; scope determined |
| T+4h | Internal stakeholders notified (CTA, Director, Privacy, Human) |
| T+24h | Breach notification to Garante drafted |
| T+48h | Notification reviewed by MSTR-16 (Privacy) and legal counsel |
| T+72h | **DEADLINE**: Notification filed with Garante |
| T+72h | If high risk to data subjects: notify affected families |

---

## 6. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| MSTR-12 (DevOps/SRE) | Primary on-call; executes recovery procedures; maintains this plan |
| MSTR-02 (CTA) | Technical escalation; approves infrastructure decisions during incident |
| MSTR-13 (Security) | Security breach response; forensics; credential rotation |
| MSTR-16 (Privacy) | GDPR breach assessment; Garante notification drafting |
| MSTR-01 (Director) | School communication; strategic decisions; human escalation |
| Daniele (Human) | Final authority; budget decisions; vendor engagement |

---

## 7. Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-05-20 | MSTR-12 | Initial draft |

**Review schedule**: This plan must be reviewed and updated:
- After every DR drill
- After every actual incident
- At minimum annually
- When infrastructure architecture changes
