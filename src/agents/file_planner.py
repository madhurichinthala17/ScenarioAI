import json
import re
from src.core.llm_client import LLMClient
from src.prompts.file_planner_prompt import SYSTEM_PROMPT
from src.models.state import FilePlan
from src.tools.file_planner_tools import FILE_PLANNER_TOOLS


class FilePlannerAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, gherkin: str) -> FilePlan:
        user_prompt = f"""
        New Gherkin scenarios to process:

        {gherkin}

        First call scan_directory to check what already exists.
        If related files exist, call read_file to read their contents.
        Then return your JSON decision.
        """

        response = self.llm.invoke_with_tools(
            SYSTEM_PROMPT,
            user_prompt,
            FILE_PLANNER_TOOLS
        )

        cleaned = re.sub(r"```json|```", "", response).strip()
        plan = json.loads(cleaned)
        self._validate(plan)
        return plan

    def _validate(self, plan: dict):
        required = [
            "functionality", "decision", "feature_file",
            "steps_file", "pages_file", "driver_file",
            "existing_scenarios", "new_scenarios", "reason"
        ]
        for key in required:
            if key not in plan:
                raise ValueError(f"File plan missing field: '{key}'")

        if plan["decision"] not in ["create", "insert", "skip", "overwrite"]:
            raise ValueError(f"Invalid decision: '{plan['decision']}'")