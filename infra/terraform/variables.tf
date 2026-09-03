variable "name" {
  description = "Droplet name"
  default     = "checklist-garden"
}

variable "region" {
  description = "DigitalOcean region slug"
  default     = "nyc1"
}

variable "size" {
  description = "Droplet size slug"
  default     = "s-2vcpu-2gb"
}

variable "image" {
  description = "Droplet image slug"
  default     = "ubuntu-24-04-x64"
}

variable "ssh_public_key" {
  description = "Path to the public key used to SSH into the droplet (and registered for deploy)"
  default     = "~/.ssh/id_ed25519.pub"
}

variable "deploy_user" {
  description = "User used for SSH (root on a plain droplet)"
  default     = "root"
}

variable "domain" {
  description = "Domain for the A record + Caddy TLS. Empty = skip DNS record."
  default     = ""
}

variable "allow_ssh_cidrs" {
  description = "CIDR blocks allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
