# Runbook: Deployment Procedure

**Runbook ID**: RUN-DEPLOY-001
**Author**: MSTR-12 (DevOps & SRE)
**Last updated**: 2026-05-20
**Audience**: DevOps, Backend Engineers

---

## Overview

This runbook covers deploying MAESTRO to the production environment on Hetzner Cloud. Deployments use the GitHub Actions workflow (`.github/workflows/deploy-production.yml`) with manual approval.

---

## Prerequisites

- [ ] All CI checks passing on `main` branch
- [ ] Image tag (git short SHA) from staging deployment verified
- [ ] No active incidents (check Grafana dashboard)
- [ ] Deployment window: outside school hours (before 08:00 or after 16:00 CET) when possible
- [ ] GitHub environment `production` approval configured

---

## Standard Deployment (via GitHub Actions)

### Step 1: Identify the image tag

```bash
# Find the latest staging-verified image tag
git log --oneline -5 main
# Use the short SHA of the commit to deploy
```

### Step 2: Trigger deployment

1. Go to GitHub Actions > "Deploy Production" workflow
2. Click "Run workflow"
3. Enter the image tag (git short SHA)
4. Set "Skip build" to `true` (use pre-built staging images)
5. Click "Run workflow"
6. Approve the deployment in the `production` environment gate

### Step 3: Monitor deployment

1. Watch the GitHub Actions run for progress
2. The workflow automatically:
   - Captures rollback state
   - Pulls new images on the production server
   - Runs `docker compose up -d`
   - Executes health checks (30 attempts, 10s interval)
   - Rolls back automatically if health checks fail

### Step 4: Verify deployment

```bash
# Check service health
curl -sf https://<domain>/api/v1/health

# Check running containers
ssh deploy@<production-ip> "docker compose ps"

# Check application version
curl -sf https://<domain>/api/v1/version

# Verify no error spike in logs
ssh deploy@<production-ip> "docker compose logs --tail=50 backend"
```

### Step 5: Post-deployment monitoring

- Watch Grafana dashboards for 15 minutes post-deploy
- Check for elevated error rates (`HighErrorRate` alert)
- Check latency (`HighP95Latency` alert)
- Verify LLM generation is working (test a content generation request)

---

## Manual Deployment (Emergency / GitHub Actions Unavailable)

Use this only if the CI/CD pipeline is unavailable.

### Step 1: Build and push images manually

```bash
# Build backend image
docker build -t ghcr.io/<org>/maestro-backend:<tag> -f infra/docker/Dockerfile.backend src/backend
docker push ghcr.io/<org>/maestro-backend:<tag>

# Build dashboard image
docker build -t ghcr.io/<org>/maestro-dashboard:<tag> -f infra/docker/Dockerfile.dashboard src/dashboard
docker push ghcr.io/<org>/maestro-dashboard:<tag>
```

### Step 2: Capture rollback state

```bash
ssh deploy@<production-ip> "cd /opt/maestro && \
  docker compose ps --format json > /opt/maestro/rollback-state.json && \
  docker compose config --images > /opt/maestro/rollback-images.txt"
```

### Step 3: Deploy

```bash
ssh deploy@<production-ip> "cd /opt/maestro && \
  export IMAGE_TAG=<tag> && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans"
```

### Step 4: Health check

```bash
for i in $(seq 1 30); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://<domain>/api/v1/health)
  if [ "$STATUS" = "200" ]; then
    echo "Healthy (attempt $i)"
    break
  fi
  echo "Attempt $i: HTTP $STATUS"
  sleep 10
done
```

---

## Rollback Procedure

### Automatic rollback (via GitHub Actions)

The deployment workflow automatically rolls back if health checks fail. No manual action needed.

### Manual rollback

```bash
ssh deploy@<production-ip> "cd /opt/maestro && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml down && \
  while IFS= read -r img; do docker pull \"\$img\" 2>/dev/null || true; done < rollback-images.txt && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
```

### Rollback to a specific version

```bash
ssh deploy@<production-ip> "cd /opt/maestro && \
  export IMAGE_TAG=<previous-sha> && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
```

---

## Database Migrations

If the deployment includes database schema changes:

1. **Before deployment**: Ensure migrations are backward-compatible (no column drops in the same release)
2. **Run migrations**:
   ```bash
   ssh deploy@<production-ip> "docker exec maestro-backend alembic upgrade head"
   ```
3. **Verify**: Check migration status
   ```bash
   ssh deploy@<production-ip> "docker exec maestro-backend alembic current"
   ```
4. **Rollback migrations** (if needed):
   ```bash
   ssh deploy@<production-ip> "docker exec maestro-backend alembic downgrade -1"
   ```

---

## Deployment Checklist

- [ ] Image tag identified and verified on staging
- [ ] Database backup taken before deployment
- [ ] Deployment triggered via GitHub Actions (preferred) or manual procedure
- [ ] Health checks pass
- [ ] No error rate increase on Grafana
- [ ] No latency increase on Grafana
- [ ] LLM generation functional
- [ ] Keycloak authentication functional
- [ ] Deployment logged in incident/change log
