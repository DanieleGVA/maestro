# Runbook: Scaling Procedures

**Runbook ID**: RUN-SCALE-001
**Author**: MSTR-12 (DevOps & SRE)
**Last updated**: 2026-05-20
**Audience**: DevOps, CTA

---

## Overview

This runbook covers vertical and horizontal scaling of MAESTRO infrastructure. The MVP architecture runs on two Hetzner Cloud servers. Scaling is triggered by monitoring alerts or anticipated load increases (e.g., new school onboarding).

---

## When to Scale

| Alert / Indicator | Action |
|---|---|
| `HighCPUUsage` (>85% for 10 min) | Vertical scale: upgrade server type |
| `HighMemoryUsage` (>90% for 10 min) | Vertical scale: upgrade server type |
| `DiskUsageHigh` (>85%) | Extend volume or clean up |
| `DatabaseConnectionPoolExhaustion` (>85%) | Increase PG max_connections or add read replica |
| `HighP95Latency` (>2s for 5 min) | Investigate; may need vertical scale or optimization |
| New school onboarding (V1) | Plan horizontal scale |

---

## Vertical Scaling (Single Server)

### Upgrade App Server

Hetzner server type upgrade requires a reboot (~30s downtime).

1. **Schedule maintenance window** (outside school hours):
   ```
   Maintenance window: [DATE] [TIME]-[TIME] CET
   ```

2. **Take a backup**:
   ```bash
   ssh deploy@<app-server> "/opt/maestro/scripts/backup.sh full"
   ```

3. **Stop services gracefully**:
   ```bash
   ssh deploy@<app-server> "cd /opt/maestro && docker compose down"
   ```

4. **Resize via Terraform**:
   ```bash
   cd infra/terraform
   # Edit terraform.tfvars or pass variable
   terraform apply -var="app_server_type=ccx43"
   # CCX43: 16 vCPU, 64 GB RAM, ~EUR 110/mo
   ```

5. **Restart services**:
   ```bash
   ssh deploy@<app-server> "cd /opt/maestro && \
     docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
   ```

6. **Verify**: Run health checks and monitor Grafana.

### Available Hetzner Server Types (EU)

| Type | vCPU | RAM | Monthly EUR | Use Case |
|---|---|---|---|---|
| CX22 | 2 (shared) | 4 GB | ~5 | Monitoring (current) |
| CCX33 | 8 (dedicated) | 32 GB | ~55 | App server (current MVP) |
| CCX43 | 16 (dedicated) | 64 GB | ~110 | App server (V1: 3 schools) |
| CCX53 | 32 (dedicated) | 128 GB | ~210 | App server (V2: 10+ schools) |

### Extend Volume

No downtime required for volume extension on Hetzner.

```bash
cd infra/terraform
terraform apply -var="postgres_volume_size_gb=100"

# Resize filesystem on the server
ssh deploy@<app-server> "resize2fs /dev/disk/by-id/scsi-0HC_Volume_<id>"
```

---

## Horizontal Scaling

### Separate Database from Application

When the single-server MVP can no longer handle both application and database workloads, separate them.

1. **Provision a dedicated database server**:
   ```hcl
   # Add to main.tf
   resource "hcloud_server" "db" {
     name        = "maestro-db-production"
     server_type = "ccx33"   # 8 vCPU, 32 GB
     image       = "ubuntu-24.04"
     location    = var.hcloud_location
     # ... (same config pattern)
   }
   ```

2. **Migrate PostgreSQL**:
   - Take full backup from current server
   - Set up PostgreSQL on new dedicated server
   - Restore backup
   - Update application `MAESTRO_DATABASE_URL` to point to new server's private IP
   - Set up WAL archiving on new server
   - Update backup cron

3. **Update docker-compose.prod.yml**: Remove PostgreSQL from app server compose, update connection strings.

### Add Application Replicas

For V1+ (multiple schools), add application server replicas behind a load balancer.

1. **Add Hetzner Load Balancer**:
   ```hcl
   resource "hcloud_load_balancer" "maestro" {
     name               = "maestro-lb-production"
     load_balancer_type = "lb11"
     location           = var.hcloud_location
   }
   ```

2. **Provision additional app servers**: Clone app server configuration in Terraform with unique names.

3. **Configure session affinity**: Required for WebSocket connections (chat feature).

4. **Update deployment workflow**: Deploy to all app servers (rolling deployment).

---

## Redis Scaling

Redis is a cache layer with LRU eviction. If cache performance degrades:

1. **Increase memory allocation**:
   ```yaml
   # docker-compose.prod.yml
   redis:
     command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
   ```

2. **Move Redis to dedicated server**: Same procedure as separating the database.

3. **Redis Cluster**: Not needed for MVP or V1. Consider only if cache size exceeds 8 GB or if cache hit rate drops below 70%.

---

## LLM Cost Scaling

When student count increases, LLM costs scale linearly. Mitigation strategies:

1. **Increase cache coverage**: Analyze cache miss patterns, add pre-generated content for common requests.
2. **Shift more tasks to GPT-4o-mini**: Review which Claude tasks could be handled by the cheaper model.
3. **Batch generation**: Expand overnight pre-generation to cover more concept/state combinations.
4. **Rate limiting**: Per-student daily token budget with graceful degradation.

---

## Scaling Decision Matrix

| Students | Schools | App Server | DB Server | Redis | Monthly Infra EUR |
|---|---|---|---|---|---|
| 30 | 1 | CCX33 (shared with DB) | Same server | CX22 (shared with monitoring) | ~80 |
| 180 | 3 | CCX43 | CCX33 (dedicated) | CX22 | ~180 |
| 500 | 10 | 2x CCX43 + LB | CCX53 + read replica | CX32 | ~450 |
| 1000+ | 20+ | Kubernetes (Scaleway Kapsule) | Managed PG | Redis Cluster | ~800+ |
