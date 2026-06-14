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

        # edge_cases must be a list of strings
        edge_cases = data.get("edge_cases") or []
        normalized = []
        for item in edge_cases:
            if isinstance(item, dict):
                normalized.append(", ".join(str(v) for v in item.values()))
            else:
                normalized.append(str(item))
        data["edge_cases"] = normalized

        # preconditions must be a list of strings
        preconditions = data.get("preconditions") or []
        data["preconditions"] = [
            ", ".join(str(v) for v in p.values()) if isinstance(p, dict) else str(p)
            for p in preconditions
        ]

        return data