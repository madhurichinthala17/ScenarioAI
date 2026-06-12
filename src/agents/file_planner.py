import json
import re
from src.core.llm_client import LLMClient
from src.prompts.file_planner_prompt import SYSTEM_PROMPT
from src.models.state import FilePlan
from src.utils.file_scanner import scan_existing_files


class FilePlannerAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, gherkin: str) -> FilePlan:
        existing_files = scan_existing_files()

        # Token optimization: only send file names first
        # If no files exist, skip entirely
        if existing_files:
            file_summary = "Existing test files:\n" + "\n".join(
                f"- {path}" for path in existing_files.keys()
            )
        else:
            file_summary = "No existing test files."

        user_prompt = f"""
        
        New Gherkin scenarios:

        {gherkin}

            ---

        {file_summary}

        Analyze and return your decision as JSON.
        """

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
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