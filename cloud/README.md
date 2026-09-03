# Checklist Garden — opencode cloud driver (prototype)

The spike that replaces the hand-rolled LLM harness (`agent/executor.py`) with
**opencode running inside a throwaway container**, while keeping your existing
git workflow and web layer intact.

## The mental model

```
Your checklist   →  cloud/driver.py (host)  →  per task:
                                                  docker run <opencode image> \
                                                    -e ANTHROPIC_API_KEY=...  \
                                                    -v <repo>:/repo            \
                                                    opencode run --auto ...
                                            →  host commits task on agent branch
                                            →  host pushes → PR for morning review
```

Division of responsibility:

| Layer | Where it runs | What it does |
|-------|---------------|--------------|
| Git (clone/branch/commit/push/PR) | **host** | reuses existing `agent/git.py` `GitManager` |
| Coding harness (opencode) | **container** | reads repo, edits files, runs tests, iterates |
| LLM keys (user's own) | **container env only** | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`, or any `*_API_KEY` |
| GitHub PAT | **host only** | never mounted into the container |

## Files

- `Dockerfile` — thin wrapper over `ghcr.io/anomalyco/opencode`.
- `driver.py` — host orchestration: clone → run branch → per-task container →
  commit → push. Drop-in replacement for the `agent.runner` subprocess the web
  layer starts today.
- `example.checklist.yaml` — tiny demo tasks (use against this repo).

## Try it

Prereqs: Docker running, a repo configured in `config.yaml`, and one LLM key in
`.env` / environment.

```powershell
# 1. Preview what would run (no Docker needed, no git changes):
python cloud/driver.py --config config.local.yaml --checklist cloud/example.checklist.yaml --dry-run

# 2. Build the image once (the driver uses it by default):
docker build -t cg-opencode cloud

# 3. Run the demo checklist for real (edit the repo copy in ./workspace):
python cloud/driver.py --config config.local.yaml --checklist cloud/example.checklist.yaml
```

Run options:

| Flag | Purpose |
|------|---------|
| `--task N` / `--repo name` | run a subset of tasks |
| `--provider openai\|anthropic\|deepseek\|openrouter` | pick key/model family (else config default) |
| `--model anthropic/claude-...` | full opencode model id |
| `--image` | opencode image to use |
| `--dry-run` | print prompts + docker commands without executing |

## Wiring into the web layer (next step)

Today `agent/process.py:RunManager.start_run()` spawns
`python -m agent.runner ...`. To switch the web app to this harness, point it
at `python cloud/driver.py --config ... --checklist <run_dir>/checklist.yaml`
instead — `driver.py` already writes `logs/task_<id>.log` and `results.json`
in the same places the dashboard reads.

## How this becomes the product ("cloud agent, bring your own key")

1. User picks a **provider + model** and pastes **their own API key** in the UI.
2. Their key is stored encrypted (see roadmap: Supabase AES) and injected only
   into that user's container(s) at run time.
3. One container per run (or per task, current prototype). Nothing of yours is
   in the container except the repo mount.
4. Kill/budget semantics stay on the host (docker `--stop-timeout`, task
   timeout, cost caps) — the container is disposable.

## Security notes / known trade-offs (do not ship as-is)

- The container can write anywhere in the mounted repo and has network egress
  (it must reach the LLM API). Repo content is *not* trusted → a malicious repo
  could prompt-inject the agent. Mitigations to add: `--network=none` via an
  HTTP proxy for the LLM endpoint, read-only repo mount + explicit output
  dir, or a per-task sandboxed filesystem.
- Any `*_API_KEY` in the host environment is passed into the container. Only run
  this on a host whose env contains exactly the keys you intend to expose.
- No cost capping inside opencode yet — the host `timeout` kills the container,
  but token spend is unbounded until a budget hook is added.
