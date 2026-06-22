import argparse
import sys

from src.graph.workflow import build_graph
from src.utils.file_scanner import ensure_folders_exist
from src.core.logger import get_logger

log = get_logger(__name__)

DEFAULT_REQUIREMENT = """
The application has a login page where users can enter their email and password.
When a user enters valid credentials and clicks the login button, they should be
redirected to the dashboard. If the credentials are invalid, an error message
should appear saying "Invalid email or password". If the user leaves the email
or password field empty and clicks login, the form should show a validation error.
After 5 failed attempts, the account should be locked and the user should see a
message saying "Account locked. Please contact support".
"""


def validate_requirement(req: str) -> str:
    if not req or not req.strip():
        raise ValueError("Requirement cannot be empty")
    if len(req) > 2000:
        raise ValueError(f"Requirement too long ({len(req)} chars, max 2000)")
    return req.strip()


def run(requirement: str, app_url: str = None) -> dict:
    requirement = validate_requirement(requirement)
    ensure_folders_exist()

    log.info("Starting ScenarioAI pipeline (app_url=%s)", app_url or "none")
    graph = build_graph()

    final_state = graph.invoke({
        "requirement": requirement,
        "app_url": app_url,
        "parsed_requirement": None,
        "exploration_report": None,
        "gherkin": None,
        "file_plan": None,
        "pom_content": None,
        "driver_content": None,
        "steps_content": None,
        "validation_passed": None,
        "validation_errors": [],
        "validation_phase": 1,
        "retry_count": 0,
        "failed_agent": None,
        "files_written": [],
        "fail_open": False,
    })

    log.info(
        "Pipeline complete — validation_passed=%s, files_written=%d",
        final_state["validation_passed"],
        len(final_state.get("files_written", [])),
    )
    for f in final_state.get("files_written", []):
        log.info("  -> generated_tests/%s", f)

    return final_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ScenarioAI — generate BDD tests from a natural language requirement"
    )
    parser.add_argument(
        "--requirement", "-r",
        type=str,
        default=None,
        help="Natural language requirement to generate tests for",
    )
    parser.add_argument(
        "--app-url",
        type=str,
        default=None,
        help="URL of a running app for the Explorer to collect real locators (optional)",
    )
    args = parser.parse_args()

    requirement = args.requirement or DEFAULT_REQUIREMENT
    final_state = run(requirement, app_url=args.app_url)

    if not final_state.get("validation_passed"):
        errors = final_state.get("validation_errors", [])
        if final_state.get("fail_open"):
            # Files were written with WARNING headers — PR will be created as draft.
            # Exit 0 so the GitHub Actions workflow still commits and creates the PR.
            log.warning("Pipeline completed as fail-open — %d error(s) in generated files", len(errors))
        else:
            log.error("Pipeline failed — %d validation error(s)", len(errors))
            for e in errors:
                log.error("  %s", e)
            sys.exit(1)
