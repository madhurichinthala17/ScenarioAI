import json
import re
from src.agents.base import BaseAgent
from src.prompts.file_planner_prompt import SYSTEM_PROMPT
from src.models.state import FilePlan
from src.tools.file_planner_tools import FILE_PLANNER_TOOLS

# Filler words dropped when turning a Feature title into a file-name slug,
# so "Subscribe to the newsletter" becomes "subscribe_newsletter" not
# "subscribe_to_the_newsletter".
_STOPWORDS = {
    "a", "an", "the", "to", "of", "for", "and", "or", "with",
    "on", "in", "via", "by", "is", "are", "be",
}


class FilePlannerAgent(BaseAgent):
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

        plan = json.loads(self._strip(response))
        # Override the LLM's functionality name with one derived from the actual
        # Feature title. The LLM tends to collapse unfamiliar features into the
        # wrong broad domain (e.g. a newsletter signup labelled "auth"), which
        # then names every file after the wrong feature.
        derived = self._derive_functionality(gherkin)
        if derived:
            plan["functionality"] = derived
        plan = self._enforce_naming(plan)
        self._validate(plan)
        return plan

    def _derive_functionality(self, gherkin: str) -> str:
        """Turn the Gherkin `Feature:` title into a concise snake_case slug."""
        match = re.search(r"^\s*Feature:\s*(.+)$", gherkin, re.MULTILINE)
        if not match:
            return ""
        words = re.findall(r"[a-z0-9]+", match.group(1).lower())
        kept = [w for w in words if w not in _STOPWORDS] or words
        return "_".join(kept[:4])

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

    def _enforce_naming(self, plan: dict) -> dict:
        """
        Force file names to match functionality field. 
        Never trust LLM for this.
        """
        name = plan["functionality"]
        plan["feature_file"] = f"features/{name}.feature"
        plan["steps_file"] = f"step_definitions/{name}_steps.py"
        plan["pages_file"] = f"pages/{name}_page.py"
        plan["driver_file"] = f"driver/{name}_helper.py"
        return plan