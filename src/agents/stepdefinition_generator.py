import re
from src.core.llm_client import LLMClient
from src.prompts.stepdefinition_generator_prompt import SYSTEM_PROMPT


class StepDefinitionGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(
        self,
        gherkin: str,
        pom_content: str,
        driver_content: str,
        file_plan: dict
    ) -> str:
        functionality = file_plan['functionality']
        pages_file = file_plan['pages_file']
        driver_file = file_plan['driver_file']

        # Derive module and class names
        page_module = pages_file.replace("pages/", "").replace(".py", "")
        driver_module = driver_file.replace("driver/", "").replace(".py", "")
        class_name = "".join(
            word.capitalize() for word in page_module.split("_")
        )

        # Extract only method signatures from POM — not full code
        # Token optimization: don't send full implementation
        pom_signatures = self._extract_signatures(pom_content)
        driver_signatures = self._extract_signatures(driver_content)

        user_prompt = f"""
        Generate step definitions for this functionality: {functionality}

        Page object class: {class_name} from pages.{page_module}
        Driver module: {driver_module}

        Available page object methods:
        {pom_signatures}

        Available driver functions:
        {driver_signatures}

        Gherkin scenarios to implement:
        {gherkin}

        Match every Gherkin step exactly.
        Given steps → driver setup_ functions
        When steps  → driver perform_ functions
        Then steps  → assert page object get_/is_ methods

        Return Python code only.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = re.sub(r"```python|```", "", response).strip()
        self._validate(cleaned)
        return cleaned

    def _extract_signatures(self, code: str) -> str:
        """
        Extract only method/function signatures from code.
        Token optimization — don't send full implementations downstream.
        """
        lines = code.split("\n")
        signatures = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("def ") and not stripped.startswith("def __"):
                # Get just the signature line
                signatures.append(f"  {stripped}")
        return "\n".join(signatures)

    def _validate(self, code: str):
        if "from behave import" not in code:
            raise ValueError("Steps: Missing behave import")
        if "@given" not in code and "@when" not in code:
            raise ValueError("Steps: No step decorators found")
        if "def step_impl" not in code:
            raise ValueError("Steps: No step implementations found")

        # Check Then steps have assertions
        lines = code.split("\n")
        in_then = False
        then_has_assert = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("@then"):
                in_then = True
                then_has_assert = False
            elif stripped.startswith("@given") or stripped.startswith("@when"):
                in_then = False
            elif in_then and "assert" in stripped:
                then_has_assert = True

        if not then_has_assert:
            raise ValueError("Steps: Then steps missing assertions")