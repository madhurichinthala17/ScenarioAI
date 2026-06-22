import re
from src.core.llm_client import LLMClient
from src.core.logger import get_logger

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a QA automation engineer reviewing AI-generated test code.
A human reviewer has left an inline comment on a generated file describing a fix.
Apply exactly the fix described — nothing more, nothing less.
Return the complete corrected file. No explanations, no markdown fences."""


class ReviewAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, file_content: str, file_type: str, comment: str) -> str:
        """
        Apply a reviewer's inline comment to a generated file.

        file_type: one of "feature", "pom", "driver", "steps"
        comment:   the exact text of the reviewer's inline PR comment
        Returns:   the corrected file content
        """
        log.info("ReviewAgent: applying fix to %s file", file_type)
        log.info("  comment: %s", comment[:120])

        user_prompt = f"""File type: {file_type}

        Current file content:
        {file_content}

        Reviewer's inline comment:
        \"{comment}\"

        Apply the fix described in the comment and return the complete corrected file."""

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        # Strip any markdown fences the LLM might add despite instructions
        cleaned = re.sub(r"```(?:python|gherkin|feature)?|```", "", response).strip()
        log.info("ReviewAgent: fix applied (%d chars)", len(cleaned))
        return cleaned
