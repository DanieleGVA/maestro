# MAESTRO Scaleway Object Storage (EU — France)
#
# S3-compatible object storage for:
#   - Database backups (WAL archives + pg_dump)
#   - Lesson materials (uploads up to 500MB per F2.1)
#   - Generated content cache
#
# Scaleway is a French company (Iliad Group). No CLOUD Act exposure.
# Region: fr-par (Paris, France) — EU data residency enforced.

# ---------------------------------------------------------------------------
# Backup Bucket
# ---------------------------------------------------------------------------

resource "scaleway_object_bucket" "backups" {
  name   = "${var.project_name}-backups-${var.environment}"
  region = "fr-par"

  tags = {
    project     = var.project_name
    environment = var.environment
    purpose     = "database-backups"
    eu_resident = "true"
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    # Keep daily backups for 30 days
    expiration {
      days = 30
    }

    # Move to infrequent access after 7 days
    transition {
      days          = 7
      storage_class = "ONEZONE_IA"
    }
  }
}

# ---------------------------------------------------------------------------
# Lesson Materials Bucket
# ---------------------------------------------------------------------------

resource "scaleway_object_bucket" "materials" {
  name   = "${var.project_name}-materials-${var.environment}"
  region = "fr-par"

  tags = {
    project     = var.project_name
    environment = var.environment
    purpose     = "lesson-materials"
    eu_resident = "true"
  }

  versioning {
    enabled = false
  }
}

# ---------------------------------------------------------------------------
# Bucket Policies — restrict to private access only
# ---------------------------------------------------------------------------

resource "scaleway_object_bucket_acl" "backups" {
  bucket = scaleway_object_bucket.backups.name
  acl    = "private"
}

resource "scaleway_object_bucket_acl" "materials" {
  bucket = scaleway_object_bucket.materials.name
  acl    = "private"
}
