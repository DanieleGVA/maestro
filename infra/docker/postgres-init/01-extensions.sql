-- MAESTRO PostgreSQL Init Script
-- Runs automatically on first container start (via docker-entrypoint-initdb.d)
--
-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- Note: Apache AGE requires a custom PostgreSQL image or manual install.
-- For MVP dev, we use pgvector for embeddings and skip AGE (use standard SQL for graph queries).

-- Create application schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS kmm;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant schema access to app user
GRANT ALL ON SCHEMA core TO maestro_app;
GRANT ALL ON SCHEMA kmm TO maestro_app;
GRANT ALL ON SCHEMA content TO maestro_app;
GRANT ALL ON SCHEMA audit TO maestro_app;
