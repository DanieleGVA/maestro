# MAESTRO Terraform Variables
# All infrastructure runs in EU-only locations (non-negotiable).

# ---------------------------------------------------------------------------
# Provider credentials
# ---------------------------------------------------------------------------

variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "scaleway_access_key" {
  description = "Scaleway access key"
  type        = string
  sensitive   = true
}

variable "scaleway_secret_key" {
  description = "Scaleway secret key"
  type        = string
  sensitive   = true
}

variable "scaleway_project_id" {
  description = "Scaleway project ID"
  type        = string
}

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "maestro"
}

variable "environment" {
  description = "Deployment environment (staging, production)"
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be 'staging' or 'production'."
  }
}

# ---------------------------------------------------------------------------
# Hetzner Cloud
# ---------------------------------------------------------------------------

variable "hcloud_location" {
  description = "Hetzner Cloud location. EU-only: fsn1 (Falkenstein DE), nbg1 (Nuremberg DE), hel1 (Helsinki FI)"
  type        = string
  default     = "fsn1"

  validation {
    condition     = contains(["fsn1", "nbg1", "hel1"], var.hcloud_location)
    error_message = "EU data residency: location must be fsn1, nbg1, or hel1."
  }
}

variable "app_server_type" {
  description = "Server type for application server (backend + DB)"
  type        = string
  default     = "ccx33" # 8 vCPU, 32GB RAM, ~EUR 55/mo
}

variable "monitoring_server_type" {
  description = "Server type for monitoring server"
  type        = string
  default     = "cx22" # 2 vCPU, 4GB RAM, ~EUR 5/mo
}

variable "postgres_volume_size_gb" {
  description = "Size of PostgreSQL data volume in GB"
  type        = number
  default     = 50
}

variable "monitoring_volume_size_gb" {
  description = "Size of monitoring data volume in GB"
  type        = number
  default     = 20
}

# ---------------------------------------------------------------------------
# SSH
# ---------------------------------------------------------------------------

variable "ssh_public_key" {
  description = "SSH public key for server access"
  type        = string
}

variable "ssh_allowed_ips" {
  description = "IP addresses allowed SSH access (CIDR notation)"
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"] # Restrict in production
}

# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------

variable "domain" {
  description = "Domain name for the MAESTRO deployment"
  type        = string
  default     = "maestro.example.com"
}
