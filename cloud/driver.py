"""
Checklist Garden cloud driver - prototype.

Runs opencode (inside a throwaway container) as the coding harness for each
pending task in a checklist. Git stays on the host: the host clones the repo,
creates one run branch, and commits each task's changes after the container
finishes editing the mounted workspace.

This is the drop-in replacement for the hand-rolled LLM harness in
agent/executor.py. The web layer should call this (via subprocess, like it
currently calls `python -m agent.runner`) to start a run.

Usage:
    python cloud/driver.py                              # all pending tasks
    python cloud/driver.py --config config.local.yaml   # custom config
    python cloud/driver.py --task 2                     # one task
    python cloud/driver.py --dry-run                    # print, don't run
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.git import GitManager
from agent.runner import load_config, load_checklist, save_checklist

logger = logging.getLogger("cloud.driver")

# Built from cloud/Dockerfile on the host (deploy workflow) or locally.
# Override with --image to use the upstream image directly.
DEFAULT_IMAGE = "cg-opencode"

# config default_provider -> opencode provider id + expected env var
PROVIDER_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )


def docker_available() -> bool:
    """Return True if the docker CLI can talk to a daemon."""
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
        return False


def pick_repo(repo_name: str, config: dict) -> dict | None:
    for repo_cfg in config.get("repos", []):
        if repo_cfg["name"] == repo_name:
            return repo_cfg
    return None


def build_prompt(repo_cfg: dict, task: dict) -> str:
    """Compose the instruction handed to opencode for one task.

    opencode explores the repo itself, so we only give it the task plus the
    list of files it's expected to touch. Avoid dumping whole file contents -
    opencode reads files with its own tools and that keeps context lean.
    """
    lines = [
        f"You are a coding agent working in the repository '{repo_cfg['name']}'.",
        "",
        "Complete the task below. Inspect the relevant code yourself, make the",
        "changes, and verify your work before finishing.",
        "",
        "## Task",
        task["description"].strip(),
    ]

    context_files = task.get("context_files") or []
    if context_files:
        lines.append("")
        lines.append("## Files expected to be relevant")
        lines.append("(inspect these first; you may need to touch more):")
        for f in context_files:
            lines.append(f"- {f}")

    test_cmd = repo_cfg.get("test_command")
    if test_cmd:
        lines.append("")
        lines.append("## Verification")
        lines.append(
            f"After making changes, run the test command and iterate until it "
            f"passes:\n```\n{test_cmd}\n```"
        )

    lines.append("")
    lines.append(
        "Do NOT commit or push anything, and do NOT create pull requests or "
        "branches - git is handled for you outside this session."
    )
    return "\n".join(lines)


def build_docker_cmd(image: str, repo_cfg: dict, prompt: str, model: str, task_id: int) -> list[str]:
    """Build the `docker run` invocation for one task."""
    workspace = Path(repo_cfg["workspace_dir"]).resolve()
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace}:/repo",
        "-w", "/repo",
        "--name", f"cg-task-{task_id}-{int(time.time())}",
    ]

    # Pass ONLY LLM keys into the container. Never GITHUB_PAT or other host secrets.
    for env_name in PROVIDER_KEY_ENV.values():
        value = os.environ.get(env_name)
        if value:
            cmd += ["-e", f"{env_name}={value}"]

    # If only a subset of keys map cleanly, allow generic pass-through too.
    for env_name in os.environ:
        if env_name.endswith("_API_KEY") and env_name not in PROVIDER_KEY_ENV.values():
            cmd += ["-e", env_name]

    cmd += [image, "run", "--auto", "--model", model, prompt]
    return cmd


def run_task_container(cmd: list[str], timeout_seconds: int) -> tuple[bool, str]:
    """Run the container; returns (success, combined output)."""
    logger.info("Starting container: %s", " ".join(cmd[:6]) + " ...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired as e:
        return False, (e.stdout or "") + (e.stderr or "") + f"\n[timeout after {timeout_seconds}s]"


def _mask_secrets(cmd: list[str]) -> list[str]:
    """Redact -e KEY=value pairs before echoing a docker command."""
    masked: list[str] = []
    skip_next = False
    for part in cmd:
        if skip_next:
            key, _, _ = part.partition("=")
            masked.append(f"{key}=***")
            skip_next = False
        elif part == "-e":
            masked.append(part)
            skip_next = True
        else:
            masked.append(part)
    return masked


def commit_if_changed(git: GitManager, message: str) -> bool:
    """Commit the mounted workspace's changes on the host."""
    if not git.stage_and_commit(message):
        return False
    return True


def run(args) -> int:
    load_dotenv(ROOT / ".env")
    setup_logging()

    config = load_config(args.config)
    checklist = load_checklist(args.checklist)

    if not docker_available() and not args.dry_run:
        logger.error(
            "Docker is not reachable. Start Docker Desktop / the daemon, or pass --dry-run."
        )
        return 1

    image = args.image or DEFAULT_IMAGE

    tasks = checklist.get("tasks", [])
    if args.task:
        tasks = [t for t in tasks if t["id"] == args.task]
    if args.repo:
        tasks = [t for t in tasks if t.get("repo") == args.repo]
    pending = [t for t in tasks if t.get("status") == "pending"]
    logger.info("Running %d pending task(s) via opencode containers", len(pending))
    if not pending:
        logger.info("Nothing to do")
        return 0

    # Pick the model string: --model wins, else <provider>/<id> from config.
    provider = args.provider or config.get("default_provider", "deepseek")
    if args.model:
        model = args.model
    else:
        model_id = (config.get("models", {}).get(provider) or {}).get(
            "model", "deepseek-chat"
        )
        model = f"{provider}/{model_id}"

    key_env = PROVIDER_KEY_ENV.get(provider)
    if key_env and not os.environ.get(key_env):
        logger.warning("No %s set in environment - opencode may fail to authenticate", key_env)

    timeout = config.get("timeouts", {}).get("task_timeout_seconds", 900)

    # One branch per repo for the whole run (matches agent/runner.py behavior).
    repos: dict[str, GitManager] = {}
    branch_name: dict[str, str] = {}
    needed_repos = {t["repo"] for t in pending}
    for repo_name in needed_repos:
        repo_cfg = pick_repo(repo_name, config)
        if repo_cfg is None:
            logger.error("Repo '%s' not configured in %s", repo_name, args.config)
            return 1
        git = GitManager(repo_cfg)
        if not args.dry_run:
            if not git.ensure_cloned():
                logger.error("Failed to clone %s", repo_name)
                return 1
            git.pull_latest()
            bn = f"{git.branch_prefix}opencode-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            git.ensure_run_branch(bn)
            branch_name[repo_name] = bn
            repos[repo_name] = git
        else:
            repos[repo_name] = git
            branch_name[repo_name] = "(dry-run)"
        logger.info("Repo %s -> branch %s", repo_name, branch_name[repo_name])

    results = []
    try:
        for task in pending:
            task_id = task["id"]
            repo_name = task["repo"]
            repo_cfg = pick_repo(repo_name, config)
            git = repos[repo_name]
            start = time.time()

            logger.info("=" * 60)
            logger.info(f"Task {task_id}: {(task['description'][:80])}")
            logger.info("=" * 60)

            if args.dry_run:
                prompt = build_prompt(repo_cfg, task)
                print("----- prompt -----")
                print(prompt)
                cmd = build_docker_cmd(image, repo_cfg, prompt, model, task_id)
                print("----- docker -----")
                print(" ".join(_mask_secrets(cmd)))
                results.append({"task_id": task_id, "status": "dry_run"})
                continue

            task["status"] = "in_progress"
            save_checklist(checklist, args.checklist)

            prompt = build_prompt(repo_cfg, task)
            cmd = build_docker_cmd(image, repo_cfg, prompt, model, task_id)
            ok, output = run_task_container(cmd, timeout)

            elapsed = round(time.time() - start, 1)

            # Log the container output for the run detail page.
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            (log_dir / f"task_{task_id}.log").write_text(output or "", encoding="utf-8")

            if ok and commit_if_changed(git, f"Task {task_id}: {task['description'][:120]}"):
                task["status"] = "done"
                task["branch"] = branch_name[repo_name]
                task["log_file"] = f"logs/task_{task_id}.log"
                logger.info(f"Task {task_id}: done ({elapsed}s), committed")
                results.append(
                    {"task_id": task_id, "status": "done", "elapsed_seconds": elapsed,
                     "branch": branch_name[repo_name]}
                )
            else:
                task["status"] = "failed"
                task["branch"] = branch_name[repo_name]
                task["log_file"] = f"logs/task_{task_id}.log"
                reason = "no changes to commit" if ok else "opencode exited nonzero or timed out"
                logger.error(f"Task {task_id}: failed ({elapsed}s) - {reason}")
                results.append(
                    {"task_id": task_id, "status": "failed", "elapsed_seconds": elapsed,
                     "branch": branch_name[repo_name], "reason": reason}
                )
                # resetting to pending would make re-runs clean:
                task["status"] = "pending"

            save_checklist(checklist, args.checklist)

        # Push the branch and open a PR for any repo with commits.
        if not args.dry_run:
            for repo_name in needed_repos:
                git = repos[repo_name]
                git.push_branch(branch_name[repo_name])
                git.return_to_main()

    finally:
        pass

    # Summary
    print("\n== Summary ==")
    for r in results:
        print(f"  Task {r['task_id']}: {r['status']}")
    results_file = Path("logs") / "opencode_results.json"
    results_file.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    logger.info("Results -> %s", results_file)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Checklist Garden cloud driver (opencode harness)")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--checklist", default="checklist.yaml")
    parser.add_argument("--task", type=int, default=None)
    parser.add_argument("--repo", type=str, default=None)
    parser.add_argument("--image", default=None, help=f"opencode image (default {DEFAULT_IMAGE})")
    parser.add_argument("--provider", default=None, help="openai|anthropic|deepseek|openrouter")
    parser.add_argument("--model", default=None, help="full opencode model id, e.g. anthropic/claude-...")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts and docker commands only")
    args = parser.parse_args()
    try:
        sys.exit(run(args))
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()
