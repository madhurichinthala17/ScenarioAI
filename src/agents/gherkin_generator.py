import re
from src.core.llm_client import LLMClient
from src.prompts.gherkin_generator_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement


class GherkinGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, parsed: ParsedRequirement) -> str:
        # Normalize edge_cases — handle both strings and dicts
        edge_cases = parsed.get('edge_cases') or []
        normalized = []
        for item in edge_cases:
            if isinstance(item, dict):
                # flatten dict values into a string
                normalized.append(", ".join(str(v) for v in item.values()))
            else:
                normalized.append(str(item))

        user_prompt = f"""Actor: {parsed['actor']}
        Action: {parsed['action']}
        Preconditions: {', '.join(parsed['preconditions'])}
        Expected Result: {parsed['expected_result']}
        Edge Cases: {', '.join(normalized)}

        Return Gherkin only.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = re.sub(r"```gherkin|```", "", response).strip()
        self._validate(cleaned)
        return cleaned

    def _validate(self, gherkin: str):
        for keyword in ["Feature:", "Scenario", "Given", "When", "Then"]:
            if keyword not in gherkin:
                raise ValueError(f"Gherkin missing keyword: '{keyword}'")