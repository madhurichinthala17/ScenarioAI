"""
CLI entry point called by the review-feedback GitHub Actions workflow.

What it does:
  1. Fetches all inline comments from a specific PR review via gh CLI
  2. Groups comments by file path (one reviewer may comment on multiple lines of the same file)
  3. Runs ReviewAgent for each file with ALL its comments in one LLM call
  4. Writes the fixed files back to disk (GitHub Actions commits them)

Usage:
    python -m src.cli.apply_review --repo owner/repo --pr 42 --review-id 987654321
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from src.agents.review_agent import ReviewAgent
from src.core.logger import get_logger
from src.utils.file_types import infer_file_type

log = get_logger(__name__)


def gh_api(path: str) -> list | dict:
    """Call the gh CLI and return parsed JSON. Exits on failure."""
    result = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("gh api %s failed: %s", path, result.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply all inline review comments to generated files")
    parser.add_argument("--repo",      required=True, help="owner/repo e.g. madhurichinthala17/ScenarioAI")
    parser.add_argument("--pr",        required=True, type=int, help="PR number")
    parser.add_argument("--review-id", required=True, help="GitHub review ID")
    args = parser.parse_args()

    # Fetch all inline comments from this specific review
    comments_data = gh_api(
        f"repos/{args.repo}/pulls/{args.pr}/reviews/{args.review_id}/comments"
    )

    if not comments_data:
        log.info("No inline comments found in review %s — nothing to fix", args.review_id)
        sys.exit(0)

    # Group comments by file path.
    # One reviewer may have left 3 comments on auth_steps.py and 2 on auth_page.py —
    # we fix each file in one LLM call with all its comments, not one call per comment.
    file_comments: dict[str, list[str]] = defaultdict(list)
    for comment in comments_data:
        file_path = comment.get("path", "")
        body = comment.get("body", "").strip()
        if file_path and body:
            file_comments[file_path].append(body)

    log.info(
        "Review %s: %d comment(s) across %d file(s)",
        args.review_id, len(comments_data), len(file_comments),
    )

    agent = ReviewAgent()
    files_fixed = []

    for file_path, comments in file_comments.items():
        p = Path(file_path)
        if not p.exists():
            log.warning("Skipping %s — file not found in working tree", file_path)
            continue

        original = p.read_text(encoding="utf-8")
        file_type = infer_file_type(file_path)

        log.info("Fixing %s (%d comment(s))...", file_path, len(comments))
        fixed = agent.run(original, file_type, comments)

        p.write_text(fixed, encoding="utf-8")
        files_fixed.append(file_path)
        log.info("  Fixed: %s", file_path)

    if not files_fixed:
        log.warning("No files were fixed — all commented files may be missing from the working tree")
        sys.exit(1)

    log.info("Done — fixed %d file(s): %s", len(files_fixed), files_fixed)
