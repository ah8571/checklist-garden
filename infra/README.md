# Checklist Garden droplet provisioning

Reproducible infrastructure for the droplet. The previous droplet was created
by hand and this repo's artifacts drifted (deploy workflow pointed at a dead IP,
service name mismatches, Caddyfile placeholder domain). This directory makes the
box reproducible end-to-end.

## Layout

```
infra/
  terraform/
    main.tf          droplet + SSH key + firewall + optional DNS A record
    variables.tf     region / size / image / domain / ssh key path
    outputs.tf       IP + ssh command
  cloud-init.yaml    first-boot bootstrap: packages, docker, caddy, dirs
```

## What the box ends up running

| Layer | Detail |
|-------|--------|
| App | FastAPI `web.app` under systemd, uvicorn on `127.0.0.1:8000`, venv at `/opt/checklist-garden/.venv` |
| TLS | Caddy reverse-proxying the domain → localhost:8000 (cert auto via Let's Encrypt) |
| Coding harness | Docker daemon on the box; `cloud/driver.py` runs per-task `cg-opencode` containers |
| Data | `/opt/checklist-garden/{workspace,logs,runs}` |

## One-time setup

```bash
export DIGITALOCEAN_TOKEN=your_api_token_with_write
# optional: create a domain record pointing at the droplet first, or let
# terraform create the A record by passing -var domain=...
cd infra/terraform
terraform init
terraform plan -var domain=checklist.garden
terraform apply -var domain=checklist.garden
```

Notes:
- `size` defaults to `s-2vcpu-2gb`; the agent run loads benefit from 2GB+.
- `ssh_public_key` defaults to `~/.ssh/id_ed25519.pub` — that same key pair's
  private key will be used by CI as `DROPLET_SSH_KEY`.
- `allow_ssh_cidrs` defaults to `0.0.0.0/0` — restrict it to your IP before
  opening the app publicly if you like.

## After first boot (manual, one time)

```bash
ssh root@<ip>

# 1. Put secrets on the box (never in git):
cp /opt/checklist-garden/.env.example /opt/checklist-garden/.env
nano /opt/checklist-garden/.env        # add DEEPSEEK_API_KEY, GITHUB_PAT, WEB_SECRET_KEY, ALLOWED_EMAILS

# 2. Deploy once so the repo + venv + image + service exist:
#    push to main (the workflow below) OR run the workflow's ssh script by hand.
```

## Deploying

The `.github/workflows/deploy.yml` workflow runs on push to `main`. Set repo
settings first:

| Setting | Value |
|---------|-------|
| `vars.DROPLET_HOST` | droplet public IP |
| `vars.DROPLET_USER` | default `root` |
| `vars.CADDY_DOMAIN` | e.g. `checklist.garden` |
| `secrets.DROPLET_SSH_KEY` | private key matching the public key in terraform |
| `secrets.DROPLET_SSH_PASSPHRASE` | passphrase if the key has one |

Deploy steps: pull `main` → pip install → `docker build` the opencode image →
install repo Caddyfile + reload caddy → restart `checklist-garden.service`.

## Teardown

```bash
cd infra/terraform
terraform destroy -var domain=checklist.garden
```

## Stale files replaced by this setup

- `.github/workflows/deploy.yml` — old version hardcoded the dead IP
  `161.35.119.24`, the obsolete `redeye` service name, and `/root/agent`.
- `checklist-garden.service` — now points at `/opt/checklist-garden` and waits
  on `docker.service`.
- `Caddyfile` — single block driven by `CADDY_DOMAIN` env var, copied to
  `/etc/caddy/Caddyfile` at deploy time (no placeholder duplicates).
