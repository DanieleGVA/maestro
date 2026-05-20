# Runbook: Backup Verification and Restore Procedures

**Runbook ID**: RUN-BACKUP-001
**Author**: MSTR-12 (DevOps & SRE)
**Last updated**: 2026-05-20
**Audience**: DevOps
**Related scripts**: `infra/scripts/backup.sh`, `infra/scripts/restore.sh`

---

## Overview

This runbook covers daily backup operations, monthly backup verification, and restore procedures for MAESTRO's PostgreSQL database. All backups are stored in Scaleway Object Storage (fr-par, France) -- EU data residency is enforced.

---

## 1. Backup Architecture

```
PostgreSQL (Hetzner DE/FI)
    |
    +-- Daily full backup (pg_dump, 02:00 UTC)
    |       |
    |       +--> Local: /opt/maestro/backups/ (30-day retention)
    |       +--> S3: s3://maestro-backups-production/full/ (30-day retention)
    |
    +-- Continuous WAL archiving
            |
            +--> S3: s3://maestro-backups-production/wal/
```

---

## 2. Daily Backup Verification

The daily backup runs automatically via cron at 02:00 UTC.

### Verify backup ran successfully

```bash
# Check cron log
ssh deploy@<app-server> "tail -20 /var/log/maestro-backup.log"

# Expected output: "[timestamp] Full backup completed successfully."

# Verify backup exists in S3
ssh deploy@<app-server> "aws s3 ls s3://maestro-backups-production/full/ \
  --endpoint-url=https://s3.fr-par.scw.cloud | tail -5"

# Check backup size (should be non-trivial, e.g., >1MB for MVP)
ssh deploy@<app-server> "aws s3 ls s3://maestro-backups-production/full/ \
  --endpoint-url=https://s3.fr-par.scw.cloud | tail -1"
```

### Troubleshoot failed backup

| Symptom | Likely cause | Resolution |
|---|---|---|
| No backup file in S3 | Cron not running | Check `crontab -l`, verify cron service is running |
| Backup file is 0 bytes | pg_dump failed | Check PG is running (`pg_isready`), check disk space |
| S3 upload failed | Scaleway credentials expired | Rotate Scaleway access keys, update `.env` |
| WAL segments not archived | archive_command failing | Check PG logs, verify S3 connectivity |

---

## 3. Monthly Backup Restore Verification

**Schedule**: First Monday of each month
**Duration**: ~1-2 hours
**Impact**: None (uses separate staging server)

### Step-by-step procedure

#### 3.1 Provision temporary staging server

```bash
cd /Users/daniele.buonaiuto/Dev/maestro/infra/terraform

# Create a staging environment (or use existing staging)
terraform workspace select staging 2>/dev/null || terraform workspace new staging
terraform apply -var="environment=staging"
```

#### 3.2 Download and restore latest backup

```bash
STAGING_IP=$(terraform output -raw staging_app_ip)

# Copy restore script to staging
scp /Users/daniele.buonaiuto/Dev/maestro/infra/scripts/restore.sh deploy@${STAGING_IP}:/opt/maestro/scripts/

# Run restore
ssh deploy@${STAGING_IP} "export MAESTRO_DB_HOST=localhost && \
  /opt/maestro/scripts/restore.sh full"
```

#### 3.3 Verify data integrity

```bash
ssh deploy@${STAGING_IP} "docker exec maestro-postgres psql -U maestro_app -d maestro" <<'SQL'
-- Row counts on critical tables
SELECT 'kmm_states' as tbl, count(*) FROM kmm_states
UNION ALL
SELECT 'kmm_transitions', count(*) FROM kmm_transitions
UNION ALL
SELECT 'audit_log', count(*) FROM audit_log
UNION ALL
SELECT 'consents', count(*) FROM consents
UNION ALL
SELECT 'students', count(*) FROM students;

-- Check latest audit log entry
SELECT max(timestamp) as latest_audit FROM audit_log;

-- Check for data corruption indicators
SELECT datname, checksum_failures FROM pg_stat_database WHERE datname='maestro';

-- Verify Keycloak schema
SELECT count(*) FROM keycloak.user_entity;
SQL
```

#### 3.4 Test application startup

```bash
# Start application against restored database
ssh deploy@${STAGING_IP} "cd /opt/maestro && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend keycloak"

# Health check
curl -sf https://${STAGING_IP}/api/v1/health

# Test Keycloak login (manual or automated)
curl -sf http://${STAGING_IP}:8080/health/ready
```

#### 3.5 Record results

```bash
# Create verification record
cat > /Users/daniele.buonaiuto/Dev/maestro/.maestro/tests/dr-backup-verify-$(date +%Y%m%d).md <<EOF
# Backup Restore Verification - $(date +%Y-%m-%d)

## Backup Details
- Backup file: [filename from S3 listing]
- Backup size: [size]
- Backup date: [date]

## Restore Results
- Restore time: [duration]
- Restore status: [SUCCESS/FAILURE]

## Data Integrity Checks
| Table | Row Count | Expected | Match |
|---|---|---|---|
| kmm_states | [count] | [expected] | [Y/N] |
| kmm_transitions | [count] | [expected] | [Y/N] |
| audit_log | [count] | [expected] | [Y/N] |
| consents | [count] | [expected] | [Y/N] |

## Application Startup
- Backend health: [PASS/FAIL]
- Keycloak health: [PASS/FAIL]
- Login test: [PASS/FAIL]

## Issues Found
- [None / Description of issues]

## Verified by
- Name: [verifier]
- Date: $(date +%Y-%m-%d)
EOF
```

#### 3.6 Tear down staging

```bash
cd /Users/daniele.buonaiuto/Dev/maestro/infra/terraform
terraform workspace select staging
terraform destroy
terraform workspace select default
```

---

## 4. Full Restore from Backup (Production)

**When**: Database corruption, server failure, or DR scenario.
**Impact**: Service downtime during restore.
**RTO target**: < 2 hours for database restore.

### 4.1 Restore from latest full backup

```bash
# SSH to production (or new) server
ssh deploy@<app-server>

# Stop application services (keep PG running if possible)
cd /opt/maestro
docker compose stop backend dashboard keycloak

# Run restore script
/opt/maestro/scripts/restore.sh full

# The script will:
# 1. Find the latest backup in S3
# 2. Download it to /opt/maestro/backups/
# 3. Drop and recreate the database
# 4. Restore from pg_dump backup

# Restart services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4.2 Restore from specific backup

```bash
# List available backups
aws s3 ls s3://maestro-backups-production/full/ \
  --endpoint-url=https://s3.fr-par.scw.cloud

# Restore specific backup
/opt/maestro/scripts/restore.sh full "maestro_20260520_020000Z.sql.gz"
```

### 4.3 Point-in-Time Recovery (PITR)

Use PITR when you need to recover to a specific moment (e.g., just before accidental data deletion).

```bash
# Determine the target recovery time
# Example: recover to just before the incident at 10:30 UTC

/opt/maestro/scripts/restore.sh pitr "2026-05-20 10:30:00 UTC"

# The script will:
# 1. Download WAL segments from S3
# 2. Print manual PITR instructions for PostgreSQL
# 3. Follow the printed instructions to complete recovery
```

**Important PITR notes**:
- PITR requires stopping PostgreSQL completely
- Recovery replays WAL segments up to the target time
- After PITR, PostgreSQL starts in recovery mode; promote when ready
- WAL segments must be available for the entire period between the base backup and target time

---

## 5. Keycloak Realm Restore

If Keycloak realm configuration is corrupted but the database is intact:

```bash
# Import realm from git-stored export
ssh deploy@<app-server> "docker exec maestro-keycloak \
  /opt/keycloak/bin/kc.sh import \
  --dir /opt/maestro/keycloak/realm-export/"

# Restart Keycloak
ssh deploy@<app-server> "docker compose restart keycloak"

# Verify
curl -sf http://<app-server>:8080/health/ready
```

---

## 6. Backup Retention Summary

| Backup type | Local retention | S3 retention | S3 lifecycle |
|---|---|---|---|
| Full pg_dump | 30 days | 30 days | Transition to ONEZONE_IA after 7 days, delete after 30 |
| WAL segments | N/A (archived directly to S3) | 30 days | Same as full backup |
| Keycloak realm export | In git (permanent) | N/A | N/A |
| Hetzner server snapshots | 4 weekly (app), 1 monthly (monitoring) | N/A | Managed via Hetzner API |
| Terraform state | In git + S3 (versioned) | Permanent | Versioning enabled |

---

## 7. Backup Monitoring Alerts

From `infra/monitoring/prometheus/alerts.yml`, backup-related monitoring:

| Alert | Condition | Action |
|---|---|---|
| `DiskUsageHigh` (>85%) | Backup files consuming too much local disk | Clean old backups; check retention script |
| Backup script exit code != 0 | Cron job failure | Check backup log, verify PG and S3 connectivity |
| No new backup in 26 hours | Daily backup missed | Manually trigger backup, investigate cron |

**Recommendation**: Add a dedicated backup monitoring alert:
```yaml
- alert: BackupStale
  expr: time() - maestro_last_backup_timestamp > 93600  # 26 hours
  for: 1h
  labels:
    severity: warning
    team: devops
  annotations:
    summary: "No successful backup in the last 26 hours"
```
