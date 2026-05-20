# MAESTRO Infrastructure — Hetzner Cloud (EU-only)
#
# EU data residency is NON-NEGOTIABLE. All resources are provisioned in
# Hetzner's EU data centres (Falkenstein DE, Nuremberg DE, Helsinki FI).
# No CLOUD Act exposure -- Hetzner is a German company.
#
# Architecture (MVP):
#   - 1x CCX33 (8 vCPU, 32GB) -- backend + PostgreSQL
#   - 1x CX22 (2 vCPU, 4GB)  -- Redis + monitoring stack
#   - Scaleway Object Storage  -- backups + lesson materials
#
# Ref: ADR-001-tech-stack.md, Section 8 (Cloud Infrastructure)

terraform {
  required_version = ">= 1.7"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.49"
    }
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.46"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

provider "hcloud" {
  token = var.hcloud_token
}

provider "scaleway" {
  access_key = var.scaleway_access_key
  secret_key = var.scaleway_secret_key
  project_id = var.scaleway_project_id
  region     = "fr-par"  # Paris, France -- EU only
}

# ---------------------------------------------------------------------------
# Network -- Private network for inter-service communication
# ---------------------------------------------------------------------------

resource "hcloud_network" "maestro" {
  name     = "${var.project_name}-network"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_network_subnet" "maestro" {
  network_id   = hcloud_network.maestro.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.0.1.0/24"
}

# ---------------------------------------------------------------------------
# SSH Key
# ---------------------------------------------------------------------------

resource "hcloud_ssh_key" "deploy" {
  name       = "${var.project_name}-deploy"
  public_key = var.ssh_public_key
}

# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------

resource "hcloud_firewall" "maestro" {
  name = "${var.project_name}-firewall"

  # SSH
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = var.ssh_allowed_ips
  }

  # HTTP
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  # HTTPS
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  # ICMP (ping)
  rule {
    direction  = "in"
    protocol   = "icmp"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

# ---------------------------------------------------------------------------
# Primary Server (Backend + PostgreSQL + Keycloak)
# ---------------------------------------------------------------------------

resource "hcloud_server" "app" {
  name        = "${var.project_name}-app-${var.environment}"
  server_type = var.app_server_type
  image       = "ubuntu-24.04"
  location    = var.hcloud_location  # EU only: fsn1, nbg1, hel1
  ssh_keys    = [hcloud_ssh_key.deploy.id]
  firewall_ids = [hcloud_firewall.maestro.id]

  labels = {
    project     = var.project_name
    environment = var.environment
    role        = "app"
    eu_resident = "true"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail

    # Install Docker
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker

    # Install Docker Compose plugin
    apt-get update && apt-get install -y docker-compose-plugin

    # Create app directory
    mkdir -p /opt/maestro
    chown ubuntu:ubuntu /opt/maestro

    # Enable automatic security updates
    apt-get install -y unattended-upgrades
    dpkg-reconfigure -plow unattended-upgrades
  EOF

  network {
    network_id = hcloud_network.maestro.id
    ip         = "10.0.1.10"
  }

  depends_on = [hcloud_network_subnet.maestro]
}

# ---------------------------------------------------------------------------
# Monitoring Server (Redis + Grafana + Loki + Tempo + Mimir + OTel)
# ---------------------------------------------------------------------------

resource "hcloud_server" "monitoring" {
  name        = "${var.project_name}-mon-${var.environment}"
  server_type = var.monitoring_server_type
  image       = "ubuntu-24.04"
  location    = var.hcloud_location
  ssh_keys    = [hcloud_ssh_key.deploy.id]
  firewall_ids = [hcloud_firewall.maestro.id]

  labels = {
    project     = var.project_name
    environment = var.environment
    role        = "monitoring"
    eu_resident = "true"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    apt-get update && apt-get install -y docker-compose-plugin
    mkdir -p /opt/maestro
    chown ubuntu:ubuntu /opt/maestro
    apt-get install -y unattended-upgrades
    dpkg-reconfigure -plow unattended-upgrades
  EOF

  network {
    network_id = hcloud_network.maestro.id
    ip         = "10.0.1.20"
  }

  depends_on = [hcloud_network_subnet.maestro]
}

# ---------------------------------------------------------------------------
# Volumes (persistent storage)
# ---------------------------------------------------------------------------

resource "hcloud_volume" "postgres_data" {
  name      = "${var.project_name}-pgdata-${var.environment}"
  size      = var.postgres_volume_size_gb
  location  = var.hcloud_location
  format    = "ext4"

  labels = {
    project     = var.project_name
    environment = var.environment
    role        = "postgres-data"
    eu_resident = "true"
  }
}

resource "hcloud_volume_attachment" "postgres_data" {
  volume_id = hcloud_volume.postgres_data.id
  server_id = hcloud_server.app.id
  automount = true
}

resource "hcloud_volume" "monitoring_data" {
  name      = "${var.project_name}-mondata-${var.environment}"
  size      = var.monitoring_volume_size_gb
  location  = var.hcloud_location
  format    = "ext4"

  labels = {
    project     = var.project_name
    environment = var.environment
    role        = "monitoring-data"
    eu_resident = "true"
  }
}

resource "hcloud_volume_attachment" "monitoring_data" {
  volume_id = hcloud_volume.monitoring_data.id
  server_id = hcloud_server.monitoring.id
  automount = true
}
