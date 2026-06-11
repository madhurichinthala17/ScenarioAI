from src.core.llm_client import LLMClient
from src.prompts.gherkin_generator_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement

class GherkinGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, parsed: ParsedRequirement) -> str:
        user_prompt = f"""
            Convert this structured requirement into a Gherkin feature file:

            Actor: {parsed['actor']}
            Action: {parsed['action']}
            Preconditions: {parsed['preconditions']}
            Expected Result: {parsed['expected_result']}
            Edge Cases: {parsed['edge_cases']}

            Return Gherkin only.
            """
        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)

        self._validate(response)

        return response

    def _validate(self, gherkin: str):
        required = ["Feature:", "Scenario:", "Given", "When", "Then"]
        for keyword in required:
            if keyword not in gherkin:
                raise ValueError(f"Generated Gherkin missing required keyword: '{keyword}'")