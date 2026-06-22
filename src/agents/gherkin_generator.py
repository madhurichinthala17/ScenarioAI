from src.agents.base import BaseAgent
from src.core.text import normalize_to_str_list
from src.prompts.gherkin_generator_prompt import SYSTEM_PROMPT
from src.models.state import ParsedRequirement


class GherkinGeneratorAgent(BaseAgent):
    def run(self, parsed: ParsedRequirement) -> str:
        # Normalize edge_cases — handle both strings and dicts
        normalized = normalize_to_str_list(parsed.get('edge_cases'))

        user_prompt = f"""Actor: {parsed['actor']}
        Action: {parsed['action']}
        Preconditions: {', '.join(parsed['preconditions'])}
        Expected Result: {parsed['expected_result']}
        Edge Cases: {', '.join(normalized)}

        Return Gherkin only.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = self._strip(response)
        self._validate(cleaned)
        return cleaned

    def _validate(self, gherkin: str):
        for keyword in ["Feature:", "Scenario", "Given", "When", "Then"]:
            if keyword not in gherkin:
                raise ValueError(f"Gherkin missing keyword: '{keyword}'")