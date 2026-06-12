import json
import re
from src.core.llm_client import LLMClient
from src.prompts.requirement_parser_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement


class RequirementParserAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, requirement: str) -> ParsedRequirement:
        user_prompt = f"Requirement:\n{requirement}\n\nReturn JSON only."
        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = re.sub(r"```json|```", "", response).strip()
        parsed = json.loads(cleaned)
        self._validate(parsed)
        return parsed

    def _validate(self, data: dict):
        for key in ["actor", "action", "preconditions", "expected_result", "edge_cases"]:
            if key not in data:
                raise ValueError(f"Parser output missing field: '{key}'")