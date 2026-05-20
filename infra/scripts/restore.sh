#!/usr/bin/env bash
# MAESTRO Database Restore Script
#
# Restores a PostgreSQL database from Scaleway Object Storage backup.
# Supports both full pg_dump restore and point-in-time recovery (PITR) via WAL.
# RTO target: <= 4 hours per N2 requirement.
#
# Usage:
#   ./restore.sh full [backup_filename]         -- Restore from latest (or specific) full backup
#   ./restore.sh pitr "2026-05-20 10:00:00 UTC" -- Point-in-time recovery
#
# EU data residency: backups retrieved from Scaleway fr-par (Paris, France).

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESTORE_TYPE="${1:-full}"
DB_NAME="${MAESTRO_DB_NAME:-maestro}"
DB_USER="${MAESTRO_DB_USER:-maestro_app}"
DB_HOST="${MAESTRO_DB_HOST:-localhost}"
DB_PORT="${MAESTRO_DB_PORT:-5432}"
BACKUP_DIR="${MAESTRO_BACKUP_DIR:-/opt/maestro/backups}"
BACKUP_BUCKET="${MAESTRO_BACKUP_BUCKET:-maestro-backups-production}"
S3_ENDPOINT="${MAESTRO_S3_ENDPOINT:-https://s3.fr-par.scw.cloud}"

mkdir -p "${BACKUP_DIR}"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

# ---------------------------------------------------------------------------
# Full restore from pg_dump
# ---------------------------------------------------------------------------

do_full_restore() {
    local specific_file="${2:-}"
    local backup_file

    if [ -n "${specific_file}" ]; then
        backup_file="${BACKUP_DIR}/${specific_file}"
        log "Downloading specific backup: ${specific_file}..."
        aws s3 cp \
            "s3://${BACKUP_BUCKET}/full/${specific_file}" \
            "${backup_file}" \
            --endpoint-url="${S3_ENDPOINT}"
    else
        log "Finding latest backup..."
        local latest
        latest=$(aws s3 ls "s3://${BACKUP_BUCKET}/full/" \
            --endpoint-url="${S3_ENDPOINT}" \
            | sort -k1,2 | tail -1 | awk '{print $4}')

        if [ -z "${latest}" ]; then
            log "ERROR: No backups found in s3://${BACKUP_BUCKET}/full/"
            exit 1
        fi

        backup_file="${BACKUP_DIR}/${latest}"
        log "Downloading latest backup: ${latest}..."
        aws s3 cp \
            "s3://${BACKUP_BUCKET}/full/${latest}" \
            "${backup_file}" \
            --endpoint-url="${S3_ENDPOINT}"
    fi

    log "WARNING: This will drop and recreate database '${DB_NAME}'."
    log "Press Ctrl+C within 10 seconds to abort..."
    sleep 10

    log "Dropping existing database..."
    dropdb --host="${DB_HOST}" --port="${DB_PORT}" --username="${DB_USER}" \
        --if-exists "${DB_NAME}" || true

    log "Creating empty database..."
    createdb --host="${DB_HOST}" --port="${DB_PORT}" --username="${DB_USER}" \
        "${DB_NAME}"

    log "Restoring from backup..."
    pg_restore \
        --host="${DB_HOST}" \
        --port="${DB_PORT}" \
        --username="${DB_USER}" \
        --dbname="${DB_NAME}" \
        --verbose \
        --no-owner \
        --no-privileges \
        "${backup_file}"

    log "Full restore completed successfully."
    log "Database '${DB_NAME}' has been restored."
}

# ---------------------------------------------------------------------------
# Point-in-time recovery via WAL replay
# ---------------------------------------------------------------------------

do_pitr_restore() {
    local target_time="${2:-}"

    if [ -z "${target_time}" ]; then
        log "ERROR: Target timestamp required for PITR."
        log "Usage: ./restore.sh pitr \"2026-05-20 10:00:00 UTC\""
        exit 1
    fi

    log "Point-in-time recovery target: ${target_time}"
    log "This requires PostgreSQL to be stopped and reconfigured."
    log ""
    log "Steps for PITR:"
    log "  1. Stop PostgreSQL"
    log "  2. Download WAL segments from s3://${BACKUP_BUCKET}/wal/"
    log "  3. Restore base backup"
    log "  4. Configure recovery.conf with recovery_target_time='${target_time}'"
    log "  5. Start PostgreSQL in recovery mode"
    log ""

    # Download WAL segments
    local wal_dir="${BACKUP_DIR}/wal_restore"
    mkdir -p "${wal_dir}"

    log "Downloading WAL segments..."
    aws s3 sync \
        "s3://${BACKUP_BUCKET}/wal/" \
        "${wal_dir}/" \
        --endpoint-url="${S3_ENDPOINT}"

    log "WAL segments downloaded to ${wal_dir}"
    log ""
    log "To complete PITR, run the following on the PostgreSQL server:"
    log ""
    log "  systemctl stop postgresql"
    log "  # Restore base backup to PGDATA"
    log "  cp ${wal_dir}/* /var/lib/postgresql/17/main/pg_wal/"
    log "  echo \"recovery_target_time = '${target_time}'\" >> /var/lib/postgresql/17/main/postgresql.auto.conf"
    log "  echo \"restore_command = 'cp ${wal_dir}/%f %p'\" >> /var/lib/postgresql/17/main/postgresql.auto.conf"
    log "  touch /var/lib/postgresql/17/main/recovery.signal"
    log "  systemctl start postgresql"
    log ""
    log "Monitor pg_is_in_recovery() and promote when ready."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "${RESTORE_TYPE}" in
    full)
        do_full_restore "$@"
        ;;
    pitr)
        do_pitr_restore "$@"
        ;;
    *)
        log "ERROR: Unknown restore type '${RESTORE_TYPE}'. Use 'full' or 'pitr'."
        exit 1
        ;;
esac
