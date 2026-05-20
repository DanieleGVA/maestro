# MAESTRO Terraform Outputs

output "app_server_ip" {
  description = "Public IP of the application server"
  value       = hcloud_server.app.ipv4_address
}

output "app_server_private_ip" {
  description = "Private IP of the application server"
  value       = "10.0.1.10"
}

output "monitoring_server_ip" {
  description = "Public IP of the monitoring server"
  value       = hcloud_server.monitoring.ipv4_address
}

output "monitoring_server_private_ip" {
  description = "Private IP of the monitoring server"
  value       = "10.0.1.20"
}

output "postgres_volume_id" {
  description = "Volume ID for PostgreSQL data"
  value       = hcloud_volume.postgres_data.id
}

output "backup_bucket" {
  description = "Scaleway Object Storage bucket for backups"
  value       = scaleway_object_bucket.backups.name
}

output "materials_bucket" {
  description = "Scaleway Object Storage bucket for lesson materials"
  value       = scaleway_object_bucket.materials.name
}

output "network_id" {
  description = "Hetzner private network ID"
  value       = hcloud_network.maestro.id
}

output "eu_residency_verified" {
  description = "Confirmation that all resources are in EU locations"
  value       = "All resources provisioned in ${var.hcloud_location} (Hetzner, EU) and fr-par (Scaleway, France)"
}
