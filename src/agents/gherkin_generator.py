from src.core.llm_client import LLMClient
from src.prompts.gherkin_generator_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement
import re


class GherkinGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, parsed: ParsedRequirement) -> str:
        user_prompt = f"""
        Actor: {parsed['actor']}
        Action: {parsed['action']}
        Preconditions: {', '.join(parsed['preconditions'])}
        Expected Result: {parsed['expected_result']}
        Edge Cases: {', '.join(parsed['edge_cases'] or [])}

        Return Gherkin only.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        # Strip any markdown the model added
        cleaned = re.sub(r"```gherkin|```", "", response).strip()
        self._validate(cleaned)
        return cleaned

    def _validate(self, gherkin: str):
        for keyword in ["Feature:", "Scenario", "Given", "When", "Then"]:
            if keyword not in gherkin:
                raise ValueError(f"Gherkin missing keyword: '{keyword}'")