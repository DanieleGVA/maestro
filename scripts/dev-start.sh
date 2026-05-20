#!/usr/bin/env bash
# Start MAESTRO development environment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Copy .env if not exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "Created .env from .env.example"
fi

# Start all services
docker compose -f "$PROJECT_ROOT/infra/docker/docker-compose.yml" --env-file "$PROJECT_ROOT/.env" up -d --build

echo ""
echo "MAESTRO is starting..."
echo "  Backend API: http://localhost:8000"
echo "  Dashboard:   http://localhost:3000"
echo "  Keycloak:    http://localhost:8080 (admin/admin_dev)"
echo "  PostgreSQL:  localhost:5432"
echo ""
echo "Demo credentials (all passwords: 'password'):"
echo "  Teacher: m.rossi@pantanelli.edu.it"
echo "  Student: s.bianchi@studenti.pantanelli.edu.it"
echo ""
echo "Logs: docker compose -f $PROJECT_ROOT/infra/docker/docker-compose.yml logs -f"
