#!/usr/bin/env bash
# MAESTRO Database Backup Script
#
# Creates a PostgreSQL backup and uploads to Scaleway Object Storage (FR).
# Designed to run daily via cron on the app server.
# Supports RPO <= 24h per N2 requirement.
#
# Usage: ./backup.sh [full|wal]
#   full  -- pg_dump compressed backup (default)
#   wal   -- WAL archive push (called by PostgreSQL archive_command)
#
# Prerequisites:
#   - s3cmd or aws-cli configured for Scaleway endpoint
#   - PGPASSWORD or .pgpass configured
#   - BACKUP_BUCKET env var set
#
# EU data residency: backups stored in Scaleway fr-par (Paris, France).

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKUP_TYPE="${1:-full}"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%SZ)"
DB_NAME="${MAESTRO_DB_NAME:-maestro}"
DB_USER="${MAESTRO_DB_USER:-maestro_app}"
DB_HOST="${MAESTRO_DB_HOST:-localhost}"
DB_PORT="${MAESTRO_DB_PORT:-5432}"
BACKUP_DIR="${MAESTRO_BACKUP_DIR:-/opt/maestro/backups}"
BACKUP_BUCKET="${MAESTRO_BACKUP_BUCKET:-maestro-backups-production}"
S3_ENDPOINT="${MAESTRO_S3_ENDPOINT:-https://s3.fr-par.scw.cloud}"
RETENTION_DAYS="${MAESTRO_BACKUP_RETENTION_DAYS:-30}"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

# ---------------------------------------------------------------------------
# Full backup (pg_dump)
# ---------------------------------------------------------------------------

do_full_backup() {
    local backup_file="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

    log "Starting full backup of database '${DB_NAME}'..."

    pg_dump \
        --host="${DB_HOST}" \
        --port="${DB_PORT}" \
        --username="${DB_USER}" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="${backup_file}" \
        "${DB_NAME}"

    local size
    size=$(du -h "${backup_file}" | cut -f1)
    log "Backup created: ${backup_file} (${size})"

    # Upload to Scaleway Object Storage
    log "Uploading to s3://${BACKUP_BUCKET}/full/${DB_NAME}_${TIMESTAMP}.sql.gz ..."
    aws s3 cp \
        "${backup_file}" \
        "s3://${BACKUP_BUCKET}/full/${DB_NAME}_${TIMESTAMP}.sql.gz" \
        --endpoint-url="${S3_ENDPOINT}"

    log "Upload complete."

    # Verify upload
    aws s3 ls \
        "s3://${BACKUP_BUCKET}/full/${DB_NAME}_${TIMESTAMP}.sql.gz" \
        --endpoint-url="${S3_ENDPOINT}" > /dev/null

    log "Upload verified."

    # Clean up local backup older than retention period
    find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete
    log "Cleaned local backups older than ${RETENTION_DAYS} days."

    log "Full backup completed successfully."
}

# ---------------------------------------------------------------------------
# WAL archive (called by PostgreSQL archive_command)
# ---------------------------------------------------------------------------

do_wal_backup() {
    local wal_file="${2:-}"
    if [ -z "${wal_file}" ]; then
        log "ERROR: WAL file path required as second argument"
        exit 1
    fi

    aws s3 cp \
        "${wal_file}" \
        "s3://${BACKUP_BUCKET}/wal/$(basename "${wal_file}")" \
        --endpoint-url="${S3_ENDPOINT}"

    log "WAL segment archived: $(basename "${wal_file}")"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "${BACKUP_TYPE}" in
    full)
        do_full_backup
        ;;
    wal)
        do_wal_backup "$@"
        ;;
    *)
        log "ERROR: Unknown backup type '${BACKUP_TYPE}'. Use 'full' or 'wal'."
        exit 1
        ;;
esac
