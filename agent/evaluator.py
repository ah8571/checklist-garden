"""
Evaluator — post-task review layer.

After the coder marks a task "done" (tests passed, changes applied),
the evaluator inspects the diff and checks against concrete criteria
from the cookbook. It produces a structured verdict:

  - "pass"           → good to commit
  - "needs-fix"      → specific issues to fix (coder loops back)
  - "needs-human"    → ambiguous or risky, flag for human review

The evaluator can use a different model/capability than the coder,
configured via config.yaml (reviewer.provider, reviewer.model).
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("agent.evaluator")

REVIEWER_SYSTEM_PROMPT = """You are a meticulous code reviewer. Your job is to inspect the diff produced
by a coding agent and verify it meets the task requirements.

You will receive:
1. The task description the agent was asked to complete
2. The git diff of all changes the agent made
3. A set of reviewer checklist items to verify against

Respond with VALID JSON ONLY using this format:
{
  "verdict": "pass" | "needs-fix" | "needs-human",
  "issues": [
    {
      "severity": "critical" | "warning",
      "description": "What's wrong and where"
    }
  ],
  "summary": "Brief overall assessment"
}

Rules:
- "passed" = task is fully addressed, no regressions, all checklist items satisfied
- "needs-fix" = there are specific, fixable issues. Provide exact descriptions so the coder can fix them.
- "needs-human" = the changes are too large, ambiguous, or risky for auto-approval
- Check for MISSING changes: files that should have been modified but weren't
- Check for INCOMPLETE changes: elements of the task that are only partially done
- Check for REGRESSIONS: broken patterns, removed functionality, hardcoded values
"""


def load_reviewer_checklist() -> str:
    """Load the reviewer checklist from cookbook/ if it exists."""
    path = Path("cookbook/reviewer-checklist.yaml")
    if not path.exists():
        return ""
    import yaml
    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            return ""
        lines = []
        for section, items in data.items():
            if isinstance(items, list):
                lines.append(f"## {section.upper()}")
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"- {item}")
                    elif isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"- {k}: {v}")
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Failed to load reviewer checklist: {e}")
        return ""


class TaskEvaluator:
    """Reviews a completed task against the task description and reviewer checklist."""

    def __init__(self, llm_client, config: dict, git_manager):
        self.llm = llm_client
        self.config = config
        self.git = git_manager
        self.reviewer_checklist = load_reviewer_checklist()
        self.max_fix_attempts = config.get("reviewer", {}).get("max_rounds", 1)
        self.reviewer_provider = (
            config.get("reviewer", {}).get("provider")
            or config.get("default_provider")
        )

    def evaluate(self, task: dict, diff: str) -> dict:
        """
        Evaluate a completed task against the reviewer checklist.

        Args:
            task: The task dict from the checklist (id, description, context_files, etc.)
            diff: The git diff of all changes made

        Returns:
            dict with verdict, issues, and summary
        """
        task_id = task.get("id")
        description = task.get("description", "")
        context_files = task.get("context_files", [])

        # Build the review prompt
        parts = [
            f"## Task Description\n{description}\n",
        ]

        if context_files:
            parts.append(f"## Files the task was supposed to touch\n{', '.join(context_files)}\n")

        if diff:
            parts.append(f"## Git Diff\n```diff\n{diff}\n```\n")
        else:
            parts.append("## Git Diff\n(No changes detected)\n")

        if self.reviewer_checklist:
            parts.append(f"## Reviewer Checklist\n{self.reviewer_checklist}\n")

        review_context = "\n".join(parts)

        logger.info(f"Evaluator: Reviewing task {task_id} ({self.reviewer_provider})")

        messages = [{"role": "user", "content": review_context}]
        response_text = self.llm.chat(
            messages,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            provider=self.reviewer_provider,
        )

        # Parse JSON from response
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            result = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Evaluator: Invalid JSON from reviewer: {e}")
            # If we can't parse, default to needs-human rather than silently passing
            result = {
                "verdict": "needs-human",
                "issues": [{"severity": "warning", "description": f"Reviewer response was not parseable: {e}"}],
                "summary": "Reviewer output could not be parsed — defaulting to human review.",
            }

        result["task_id"] = task_id
        logger.info(f"Evaluator: Task {task_id} → {result.get('verdict', 'unknown')}")
        for issue in result.get("issues", []):
            logger.info(f"  [{issue.get('severity', '?')}] {issue.get('description', '?')}")

        return result