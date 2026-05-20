#!/usr/bin/env bash
# Stop MAESTRO development environment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

docker compose -f "$PROJECT_ROOT/infra/docker/docker-compose.yml" down

echo "MAESTRO stopped."
