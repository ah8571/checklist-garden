output "droplet_ip" {
  description = "Public IPv4 of the droplet"
  value       = digitalocean_droplet.agent.ipv4_address
}

output "ssh" {
  description = "SSH command to reach the box"
  value       = "ssh root@${digitalocean_droplet.agent.ipv4_address}"
}

output "domain_record" {
  description = "Whether an A record was created"
  value       = var.domain != "" ? "http://${var.domain}" : "(none - set domain variable to create DNS)"
}
