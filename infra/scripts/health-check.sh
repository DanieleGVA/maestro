#!/usr/bin/env bash
# MAESTRO Post-Deploy Health Verification
#
# Checks all critical services after deployment.
# Exit code 0 = healthy, non-zero = failure (triggers rollback in CI/CD).
#
# Usage: ./health-check.sh [base_url]
#   Default base_url: http://localhost:8000

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
CHECKS_PASSED=0
CHECKS_FAILED=0

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

check() {
    local name="$1"
    local result="$2"

    if [ "${result}" = "pass" ]; then
        log "PASS: ${name}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        log "FAIL: ${name} — ${result}"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
}

# ---------------------------------------------------------------------------
# 1. API Health Endpoint
# ---------------------------------------------------------------------------

log "Checking API health endpoint..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/v1/health" 2>/dev/null || echo "000")
if [ "${HTTP_STATUS}" = "200" ]; then
    check "API health endpoint" "pass"
else
    check "API health endpoint" "HTTP ${HTTP_STATUS}"
fi

# ---------------------------------------------------------------------------
# 2. API Response Content
# ---------------------------------------------------------------------------

log "Checking API response body..."
BODY=$(curl -s "${BASE_URL}/api/v1/health" 2>/dev/null || echo "{}")
if echo "${BODY}" | grep -q "ok\|healthy\|status"; then
    check "API response body" "pass"
else
    check "API response body" "unexpected body: ${BODY}"
fi

# ---------------------------------------------------------------------------
# 3. Security Headers
# ---------------------------------------------------------------------------

log "Checking security headers..."
HEADERS=$(curl -sI "${BASE_URL}/api/v1/health" 2>/dev/null || echo "")

for header in "X-Content-Type-Options" "X-Frame-Options" "Strict-Transport-Security"; do
    if echo "${HEADERS}" | grep -qi "${header}"; then
        check "Header: ${header}" "pass"
    else
        check "Header: ${header}" "missing"
    fi
done

# ---------------------------------------------------------------------------
# 4. Database Connectivity (via API)
# ---------------------------------------------------------------------------

log "Checking database connectivity..."
DB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/v1/health" 2>/dev/null || echo "000")
if [ "${DB_STATUS}" = "200" ]; then
    check "Database connectivity" "pass"
else
    check "Database connectivity" "API returned HTTP ${DB_STATUS}"
fi

# ---------------------------------------------------------------------------
# 5. Docker Container Status (if running locally)
# ---------------------------------------------------------------------------

if command -v docker &> /dev/null; then
    log "Checking Docker container status..."

    for container in maestro-backend maestro-dashboard maestro-postgres maestro-redis; do
        STATUS=$(docker inspect --format='{{.State.Status}}' "${container}" 2>/dev/null || echo "not_found")
        if [ "${STATUS}" = "running" ]; then
            check "Container: ${container}" "pass"
        else
            check "Container: ${container}" "status=${STATUS}"
        fi
    done

    # Check container health status
    for container in maestro-backend maestro-postgres maestro-redis; do
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "${container}" 2>/dev/null || echo "none")
        if [ "${HEALTH}" = "healthy" ] || [ "${HEALTH}" = "none" ]; then
            check "Health: ${container}" "pass"
        else
            check "Health: ${container}" "health=${HEALTH}"
        fi
    done
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

log "---"
log "Health check complete: ${CHECKS_PASSED} passed, ${CHECKS_FAILED} failed"

if [ "${CHECKS_FAILED}" -gt 0 ]; then
    log "DEPLOYMENT HEALTH CHECK FAILED"
    exit 1
fi

log "DEPLOYMENT HEALTHY"
exit 0
