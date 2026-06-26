import json
from typing import Optional

from src.agents.base import BaseAgent
from src.prompts.pom_generator_prompt import SYSTEM_PROMPT
from src.prompts.pom_consolidator_prompt import CONSOLIDATION_PROMPT


class POMGeneratorAgent(BaseAgent):
    def run(
        self,
        gherkin: str,
        functionality: str,
        class_name: str,
        exploration_report: Optional[dict] = None,
    ) -> str:
        # When the Explorer ran, we have real locators from the live app.
        # Inject them so the LLM uses actual selectors instead of placeholders.
        locator_section = ""
        if exploration_report and exploration_report.get("locator_map"):
            locator_section = f"""
                REAL LOCATORS FROM THE LIVE APP (use these instead of guessing):
                {json.dumps(exploration_report['locator_map'], indent=2)}

                Replace every `pass` with the matching real locator from the list above.
                """

        # class_name is derived from the file plan and shared with the driver and
        # step generators — the class MUST be named exactly this or their imports
        # (`from pages.<module> import <class_name>`) break.
        user_prompt = f"""
            Generate a Page Object Model class for this functionality: {functionality}

            The class MUST be named exactly: {class_name}
            (do not invent a different name — other modules import this exact name)

            Based on these Gherkin scenarios:
                {gherkin}
                {locator_section}
            Analyze every Given, When, Then step and create methods for each UI interaction.
            Return Python code only.
                """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = self._strip(response)

        # Step 2 — Consolidate semantic duplicates using LLM. Restate the class
        # name so the consolidation pass can't quietly rename the class.
        consolidation_prompt = f"""Review and consolidate this Page Object Model class.
        Keep the class named exactly {class_name}.

        {cleaned}

        Return the consolidated Python class only.
        """
        consolidated_response = self.llm.invoke(CONSOLIDATION_PROMPT, consolidation_prompt)
        final_pom = self._strip(consolidated_response)
        self._soft_validate(final_pom)
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