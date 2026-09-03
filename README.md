# Checklist Garden

An autonomous coding agent that executes checklists — serialize tasks as structured YAML, and the agent clones your repos, sends each task to an LLM, applies code changes, runs tests, and opens a PR for morning review.

## How it works

```
checklist.yaml  →  clone repo  →  send task to LLM  →  apply code changes  →  run tests  →  commit & push  →  create PR
```

1. Define tasks in `checklist.yaml` (plain text, Markdown, or YAML)
2. The agent clones the target repo, creates a branch, and sends each task to an LLM with repo context
3. The LLM responds with structured file changes (create/edit/delete)
4. Changes are applied, tests run, and a PR is opened for human review

## Features

- Serial task execution across multiple repos, with parallel execution across repos
- Budget tracking: configurable limits per task and per run
- Multi-provider LLM support: DeepSeek, OpenAI, Anthropic
- Auto-retry on transient API errors and test failures
- Per-task logging with run summaries and diff reports
- Web dashboard for submitting tasks and monitoring runs
- Internal agent cookbook with structured task templates

## Quick Start

```bash
# 1. Clone
git clone https://github.com/planting-moon/checklist-garden.git
cd checklist-garden

# 2. Configure
cp .env.example .env
# Add API keys (DEEPSEEK_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GITHUB_PAT)

# 3. Install
pip install -r requirements.txt

# 4. Define tasks
# Edit checklist.yaml with your tasks

# 5. Run
python -m agent.runner
```

## CLI Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Plan only, no changes made |
| `--status` | Show checklist status and exit |
| `--task <id>` | Run a specific task by ID |
| `--repo <name>` | Run tasks for a specific repo |
| `--config <path>` | Path to config file (default: `config.yaml`) |
| `--checklist <path>` | Path to checklist file (default: `checklist.yaml`) |
| `--rerun-failed` | Reset failed tasks to pending and retry |

## Configuration

### `config.yaml` — main config
Defines LLM providers, budget limits, timeouts, repositories, and logging.

### `checklist.yaml` — task checklist
Each task has an ID, repository, description, and status. The agent processes tasks with status `pending`.

### `cookbook/` — internal agent templates
Structured task templates and self-review checklists that guide the coding agent:
- `cookbook/templates/` — reusable task templates (code, review, deploy, doc)
- `cookbook/coder-checklist.yaml` — self-review criteria for the coding agent

## Deployment

### Prerequisites
- Python 3.10+ (locally) or the provisioning setup below (server)
- DigitalOcean account + API token
- Domain pointed at your server (or create an A record via Terraform)
- Docker (server only — used as the agent execution harness)

### Automated droplet setup

The droplet is now provisioned reproducibly from `infra/` (Terraform +
cloud-init) instead of by hand:

```bash
export DIGITALOCEAN_TOKEN=...
cd infra/terraform
terraform init
terraform apply -var domain=checklist.garden
```

Then, once:
1. `ssh root@<droplet-ip>`, copy `.env.example` → `/opt/checklist-garden/.env`
   and fill in `DEEPSEEK_API_KEY`, `GITHUB_PAT`, `WEB_SECRET_KEY`,
   `ALLOWED_EMAILS`.
2. Configure GitHub Actions vars/secrets (`DROPLET_HOST`, `DROPLET_USER`,
   `CADDY_DOMAIN`, `DROPLET_SSH_KEY`).
3. Push to `main` — the deploy workflow pulls code, installs deps, builds the
   opencode harness image, installs Caddy, and restarts the service.

See `infra/README.md` for full details and teardown.

### Manual (legacy, no droplet)

```bash
# Install systemd service
sudo cp checklist-garden.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable checklist-garden
sudo systemctl start checklist-garden

# Configure Caddy (CADDY_DOMAIN env var must be set)
CADDY_DOMAIN=your.domain sudo -E caddy reload --config Caddyfile

# Verify
sudo systemctl status checklist-garden
```

## Architecture

```
agent/
  runner.py     — main orchestrator, loads config + checklist
  executor.py   — single task lifecycle (context → LLM → changes → test → commit)
  llm.py        — unified interface for OpenAI, Anthropic, DeepSeek
  git.py        — clone, branch, commit, push, PR creation
  process.py    — RunManager for background process lifecycle
  checklist.py  — parse markdown/YAML into task lists
  report.py     — generate markdown run reports

web/
  app.py        — FastAPI dashboard for submitting and monitoring runs
  templates/    — Jinja2 templates for the web UI

cookbook/
  templates/    — structured task templates for different work types
  coder-checklist.yaml — self-review criteria for coding agents

cloud/
  driver.py     — prototype: runs each task via an opencode container (harness)
  Dockerfile    — thin wrapper over the opencode image used by cloud/driver.py

infra/
  terraform/    — DigitalOcean droplet provisioning (droplet + firewall + DNS)
  cloud-init.yaml — first-boot bootstrap (docker, python, caddy, dirs)
```

## Roadmap

See `DEVELOPER_ROADMAP_V1.md` for planned features including:
- Multi-layer agent review (coder → reviewer → meta-reviewer)
- Docker sandbox for code execution
- Branch preview and approve/merge flow
- Database migration (SQLite → Supabase)
- Audit logging and security hardening
