"""
CLI entry point for the ReviewAgent.
Called by the review-feedback GitHub Actions workflow when a reviewer
posts an inline PR comment on a generated file.

Usage:
    python -m src.cli.review --file path/to/file.py --comment "fix this locator"
"""
import argparse
import sys
from pathlib import Path

from src.agents.review_agent import ReviewAgent
from src.core.logger import get_logger
from src.utils.file_types import infer_file_type

log = get_logger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Apply a reviewer inline comment to a generated file"
    )
    parser.add_argument("--file",    required=True, help="Path to the file to fix")
    parser.add_argument("--comment", required=True, help="The reviewer's inline comment text")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        log.error("File not found: %s", file_path)
        sys.exit(1)

    original = file_path.read_text(encoding="utf-8")
    file_type = infer_file_type(str(file_path))

    log.info("ReviewAgent: fixing %s (%s)", file_path, file_type)
    agent = ReviewAgent()
    # ReviewAgent.run expects a list of comments — wrap the single CLI comment.
    fixed = agent.run(original, file_type, [args.comment])

    file_path.write_text(fixed, encoding="utf-8")
    log.info("ReviewAgent: wrote fixed file to %s", file_path)
