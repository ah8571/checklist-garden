# Terraform provisioning for the Checklist Garden droplet.
#
# Prereqs:
#   - DigitalOcean API token: export DIGITALOCEAN_TOKEN=...
#   - terraform >= 1.5
#   - doctl not required (terraform uses the API directly)
#
# Usage:
#   terraform init
#   terraform plan -var domain=checklist.garden -var deploy_user=root
#   terraform apply -var domain=checklist.garden -var deploy_user=root
#
# The droplet runs cloud-init from ../cloud-init.yaml on first boot. DNS (A
# record) for the domain is created pointing at the droplet if `domain` is set.

terraform {
  required_version = ">= 1.5"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.30"
    }
  }
}

resource "digitalocean_droplet" "agent" {
  name     = var.name
  region   = var.region
  size     = var.size
  image    = var.image
  ssh_keys = [digitalocean_ssh_key.main.fingerprint]
  user_data = file("${path.module}/../cloud-init.yaml")

  lifecycle {
    ignore_changes = [user_data]  # keep reboots from re-running cloud-init
  }
}

resource "digitalocean_ssh_key" "main" {
  name       = "${var.name}-deploy"
  public_key = file(var.ssh_public_key)
}

resource "digitalocean_firewall" "agent" {
  name = "${var.name}-fw"

  droplet_ids = [digitalocean_droplet.agent.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.allow_ssh_cidrs
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Optional DNS: only created when `domain` is provided.
resource "digitalocean_record" "www" {
  count  = var.domain != "" ? 1 : 0
  domain = var.domain
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.agent.ipv4_address
  ttl    = 60
}
