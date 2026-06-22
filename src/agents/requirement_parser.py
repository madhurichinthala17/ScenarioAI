import json
from src.agents.base import BaseAgent
from src.core.text import normalize_to_str_list
from src.prompts.requirement_parser_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement


class RequirementParserAgent(BaseAgent):
    def run(self, requirement: str) -> ParsedRequirement:
        user_prompt = f"Requirement:\n{requirement}\n\nReturn JSON only."
        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(self._strip(response))
        parsed = self._normalize(parsed)
        self._validate(parsed)
        return parsed

    def _validate(self, data: dict):
        for key in ["actor", "action", "preconditions", "expected_result", "edge_cases"]:
            if key not in data:
                raise ValueError(f"Parser output missing field: '{key}'")
            
    def _normalize(self, data: dict) -> dict:
        """Force all fields to correct types regardless of LLM output."""

        # expected_result must be a string
        if isinstance(data.get("expected_result"), dict):
            data["expected_result"] = ", ".join(
                str(v) for v in data["expected_result"].values()
            )

        # edge_cases and preconditions must each be a list of strings
        data["edge_cases"] = normalize_to_str_list(data.get("edge_cases"))
        data["preconditions"] = normalize_to_str_list(data.get("preconditions"))

        return data