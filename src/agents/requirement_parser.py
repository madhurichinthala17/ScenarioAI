import json
from src.core.llm_client import LLMClient
from src.prompts.requirement_parser_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement

class RequirementParserAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, description: str) -> ParsedRequirement:
        user_prompt = f"""
Requirement:
{description}

Return JSON only.
"""
        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)

        parsed = json.loads(response)

        self._validate(parsed)

        return parsed

    def _validate(self, data: dict):
        required_keys = ["actor", "action", "preconditions", "expected_result", "edge_cases"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Parser output missing required field: '{key}'")