from typing import TypedDict, List, Optional, Annotated
from enum import Enum
import operator


class FileDecision(str, Enum):
    SKIP = "skip"
    INSERT = "insert"
    CREATE = "create"
    OVERWRITE = "overwrite"


class ParsedRequirement(TypedDict):
    actor: str
    action: str
    preconditions: List[str]
    expected_result: str
    edge_cases: Optional[List[str]]


class FilePlan(TypedDict):
    functionality: str
    decision: str
    feature_file: str
    steps_file: str
    pages_file: str
    driver_file: str
    existing_scenarios: List[str]
    new_scenarios: List[str]
    reason: str


class ElementInfo(TypedDict):
    role: str      # input / button / a / select
    label: str     # aria-label, placeholder, or visible text
    locator: str   # best Playwright locator e.g. input[name='email']


class ExplorationReport(TypedDict):
    page_url: str
    page_title: str
    elements: List[ElementInfo]
    # Maps human action descriptions to real locators.
    # e.g. {"enter email": "input[name='email']", "click submit": "button[type='submit']"}
    # Injected into the POM generator prompt so LLM uses real locators, not guesses.
    locator_map: dict


class ScenarioAIState(TypedDict):
    # ── Inputs ─────────────────────────────────────────────────────────────
    requirement: str
    # Optional URL of a running app. If set, ExplorerAgent runs and collects
    # real locators. If None, explorer is skipped and POM uses LLM-guessed locators.
    app_url: Optional[str]

    # ── Pipeline stages ────────────────────────────────────────────────────
    parsed_requirement: Optional[ParsedRequirement]
    # Populated by ExplorerAgent when app_url is provided. Passed to POM generator.
    exploration_report: Optional[ExplorationReport]
    gherkin: Optional[str]
    file_plan: Optional[FilePlan]
    pom_content: Optional[str]
    driver_content: Optional[str]
    steps_content: Optional[str]

    # ── Validation ─────────────────────────────────────────────────────────
    validation_passed: Optional[bool]
    validation_errors: Annotated[List[str], operator.add]
    # 1 = phase 1 failed (AST/Ruff/Gherkin), 2 = phase 2 failed (behave --dry-run)
    validation_phase: int
    retry_count: Annotated[int, operator.add]
    failed_agent: Optional[str]

    # ── Output ─────────────────────────────────────────────────────────────
    files_written: Optional[List[str]]
    # True when files were written despite validation failures (fail-open path).
    # Signals the GitHub Actions workflow to create the PR with a warning label.
    fail_open: bool
