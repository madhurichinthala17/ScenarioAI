from typing import TypedDict, List, Optional

class RequirementInput(TypedDict):
    title: str
    description: str
    acceptance_criteria: Optional[str]
    source: str
    ticket_id: str

class ParsedRequirement(TypedDict):
    actor: str
    action: str
    preconditions: List[str]
    expected_result: str
    edge_cases: Optional[List[str]]