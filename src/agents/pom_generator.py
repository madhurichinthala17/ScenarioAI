import re
from src.core.llm_client import LLMClient
from src.prompts.pom_generator_prompt import SYSTEM_PROMPT
from src.prompts.pom_consolidator_prompt import CONSOLIDATION_PROMPT


class POMGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, gherkin: str, functionality: str) -> str:
        user_prompt = f"""
        Generate a Page Object Model class for this functionality: {functionality}
        Based on these Gherkin scenarios:
        {gherkin}
        Analyze every Given, When, Then step and create methods for each UI interaction.
        Return Python code only."""

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = re.sub(r"```python|```", "", response).strip()

        # Step 2 — Consolidate semantic duplicates using LLM
        consolidation_prompt = f"""Review and consolidate this Page Object Model class:

        {cleaned}

        Return the consolidated Python class only.
        """
        consolidated_response = self.llm.invoke(CONSOLIDATION_PROMPT, consolidation_prompt)
        final_pom = re.sub(r"```python|```", "", consolidated_response).strip()
        self._validate(final_pom)
        return final_pom

    def _validate(self, code: str):
        if "class " not in code:
            raise ValueError("POM: No class definition found")
        if "def __init__" not in code:
            raise ValueError("POM: Missing __init__ method")
        if "self.page" not in code:
            raise ValueError("POM: Missing page reference")
        if "assert" in code.lower():
            raise ValueError("POM: Assertions found in page object — not allowed")
        if "expect(" in code:
            raise ValueError("POM: Assertions found in page object — not allowed")