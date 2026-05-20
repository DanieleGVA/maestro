# Runbook: Incident Response

**Runbook ID**: RUN-INCIDENT-001
**Author**: MSTR-12 (DevOps & SRE)
**Last updated**: 2026-05-20
**Audience**: All engineering team members

---

## Overview

This runbook defines the incident management process for MAESTRO production, including classification, response procedures, communication, and post-mortem process.

---

## 1. Incident Classification

| Severity | Definition | Response Time | Examples |
|---|---|---|---|
| P1 - Critical | Service completely unavailable; data integrity at risk; security breach | Immediate (within 15 min) | Server down, database corruption, data breach, safeguarding alert |
| P2 - Major | Service degraded; significant feature unavailable | Within 30 min | LLM generation failing, authentication broken, high error rate |
| P3 - Minor | Minor feature impact; workaround available | Within 2 hours | Slow performance, minor UI issue, non-critical alert |
| P4 - Low | Cosmetic issue; no user impact | Next business day | Log noise, minor monitoring gap |

### Special Classifications

- **Security incident**: Always treated as P1 regardless of apparent scope. Follow S10 procedure in DR plan.
- **Safeguarding incident**: Always treated as P1. Immediate human escalation per CLAUDE.md.
- **Data breach (GDPR)**: P1 with 72-hour Garante notification obligation.

---

## 2. Response Procedure

### Phase 1: Detection and Triage (0-15 minutes)

1. **Alert received** via Grafana/Mimir alerting or user report
2. **Acknowledge** the incident:
   - Check Grafana dashboards for scope assessment
   - Identify affected components
   - Assign severity level
3. **Create incident record**:
   ```
   Incident: INC-YYYYMMDD-NNN
   Severity: P1/P2/P3/P4
   Detected: YYYY-MM-DD HH:MM UTC
   Affected: [components]
   Impact: [user impact description]
   IC: [incident commander name]
   ```

### Phase 2: Containment (15-60 minutes)

1. **Identify the failure scenario**: Match to DR plan scenarios S1-S10
2. **Execute the appropriate recovery procedure** from DR plan
3. **Communicate status**: Notify stakeholders per escalation chain

### Phase 3: Resolution

1. **Restore service** to normal operation
2. **Verify**: Health checks pass, no residual errors
3. **Monitor**: Watch dashboards for 30 minutes post-resolution
4. **Close incident**: Update incident record with resolution details

### Phase 4: Post-Incident (within 48 hours)

1. **Write post-mortem** (see template below)
2. **Identify action items**: Preventive measures, monitoring improvements
3. **Share with team**: Post-mortem review meeting for P1/P2 incidents

---

## 3. Escalation Matrix

| Time since detection | P1 | P2 | P3 |
|---|---|---|---|
| 0 min | MSTR-12 (DevOps) | MSTR-12 | MSTR-12 |
| 15 min | + MSTR-02 (CTA) | MSTR-12 continues | -- |
| 30 min | + MSTR-13 (Security, if security-related) | + MSTR-02 | -- |
| 60 min | + MSTR-01 (Director) | MSTR-02 decides | -- |
| 120 min | + Daniele (Human) | + MSTR-01 | -- |
| During school hours (08-16 CET) | School notified if outage >30 min | -- | -- |

---

## 4. Communication Templates

### Internal Status Update

```
[INC-YYYYMMDD-NNN] Status Update #N
Severity: P[1-4]
Status: Investigating / Identified / Mitigating / Resolved
Impact: [current user impact]
Next update: [time]
Actions: [what is being done]
```

### School Notification

Use templates from DR plan Section 5.2 (Planned Maintenance, Unplanned Outage, Service Restored).

---

## 5. Post-Mortem Template

```markdown
# Post-Mortem: INC-YYYYMMDD-NNN

## Summary
- **Date**: YYYY-MM-DD
- **Duration**: HH:MM
- **Severity**: P[1-4]
- **Impact**: [number of users affected, features impacted]
- **IC**: [incident commander]

## Timeline (UTC)
| Time | Event |
|---|---|
| HH:MM | [event] |
| HH:MM | [event] |

## Root Cause
[Description of the root cause]

## Resolution
[What was done to resolve the incident]

## What Went Well
- [item]

## What Went Wrong
- [item]

## Action Items
| # | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| 1 | [action] | [owner] | [date] | Open |

## Lessons Learned
[Key takeaways]
```

---

## 6. On-Call Responsibilities

### During school hours (08:00-16:00 CET, weekdays)

- MSTR-12 is primary on-call
- Response to P1/P2 alerts within 15 minutes
- Monitor Grafana dashboards at start of school day

### Outside school hours

- Automated alerting still active
- P1 alerts: respond within 30 minutes
- P2-P4 alerts: respond next business day (unless affecting next morning's availability)

### On-call handoff checklist

1. Review current alert state in Grafana
2. Check for any pending deployments
3. Verify backup ran successfully overnight
4. Note any known issues or upcoming maintenance

---

## 7. Useful Commands for Incident Response

### Quick diagnostics

```bash
# Check all services
ssh deploy@<app-server> "docker compose ps"

# Check backend logs (last 100 lines)
ssh deploy@<app-server> "docker compose logs --tail=100 backend"

# Check PostgreSQL health
ssh deploy@<app-server> "docker exec maestro-postgres pg_isready"

# Check disk usage
ssh deploy@<app-server> "df -h"

# Check memory usage
ssh deploy@<app-server> "free -h"

# Check CPU usage
ssh deploy@<app-server> "top -bn1 | head -5"

# Check network connectivity to LLM providers
ssh deploy@<app-server> "curl -sf -o /dev/null -w '%{http_code}' https://api.anthropic.com"

# Check Redis
ssh deploy@<app-server> "docker exec maestro-redis redis-cli ping"

# Check Keycloak
ssh deploy@<app-server> "curl -sf http://localhost:8080/health/ready"
```

### Emergency actions

```bash
# Restart a single service
ssh deploy@<app-server> "docker compose restart <service>"

# Restart all services
ssh deploy@<app-server> "cd /opt/maestro && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml restart"

# Full stop and start
ssh deploy@<app-server> "cd /opt/maestro && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml down && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"

# Emergency database backup
ssh deploy@<app-server> "/opt/maestro/scripts/backup.sh full"

# Block all traffic except SSH (emergency isolation)
ssh deploy@<app-server> "ufw default deny incoming && ufw allow 22/tcp && ufw --force enable"
```
