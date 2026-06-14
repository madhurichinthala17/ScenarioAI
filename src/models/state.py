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


class ScenarioAIState(TypedDict):
    requirement: str
    parsed_requirement: Optional[ParsedRequirement]
    gherkin: Optional[str]
    file_plan: Optional[FilePlan]
    pom_content: Optional[str]
    driver_content: Optional[str]
    steps_content: Optional[str]
    validation_passed: Optional[bool]
    validation_errors: Annotated[List[str], operator.add]
    retry_count: Annotated[int, operator.add]
    failed_agent: Optional[str]
    files_written: Optional[List[str]]