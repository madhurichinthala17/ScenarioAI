from src.agents.base import BaseAgent
from src.prompts.driver_generator_prompt import SYSTEM_PROMPT
from src.prompts.driver_consolidator_prompt import CONSOLIDATION_PROMPT
from src.utils.file_types import page_class_name, page_module_name


class DriverGeneratorAgent(BaseAgent):
    def run(
        self,
        gherkin: str,
        functionality: str,
        pages_file: str
    ) -> str:
        # Derive page module and class name from the file plan — shared helpers
        # keep this identical to the POM and step generators (pages/auth_page.py
        # → auth_page → AuthPage), so imports always resolve.
        page_module = page_module_name(pages_file)
        class_name = page_class_name(pages_file)

        user_prompt = f"""
        Generate a driver helper module for this functionality: {functionality}

        Page object class: {class_name}
        Page module: {page_module}

        Based on these Gherkin scenarios:

        {gherkin}

        Analyze the When and Then steps to identify:
        1. Multi-step flows that need helper functions
        2. Setup functions that establish preconditions
        3. Any repeated logic across scenarios

        Return Python code only.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = self._strip(response)
        # Step 2 — Consolidate duplicates
        consolidation_prompt = f"""
        Review and consolidate this driver helper module:
        {cleaned}
        Return the consolidated Python module only.
        """

        consolidated = self.llm.invoke(CONSOLIDATION_PROMPT, consolidation_prompt)
        final_driver = self._strip(consolidated)

        self._soft_validate(final_driver)
        return final_driver
    
    def _validate(self, code: str):
        if "def " not in code:
            raise ValueError("Driver: No functions found")

    # Check for assertions — but ignore comments and docstrings
        lines = code.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if "assert " in stripped:
                raise ValueError(
                    f"Driver: Assertion found on line: '{stripped}'\n"
                    f"Assertions belong in step definitions not driver"
                )

        if "page.click" in code or "page.fill" in code or "page.goto" in code:
            raise ValueError(
            "Driver: Direct Playwright calls found — use page object methods"
            )

