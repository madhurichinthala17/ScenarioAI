from src.agents.base import BaseAgent
from src.core.logger import get_logger

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a QA automation engineer reviewing AI-generated test code.
A human reviewer has left inline comments on a generated file requesting specific changes.
Apply ALL of the requested changes in one pass — nothing more, nothing less.
Return the complete corrected file. No explanations, no markdown fences."""


class ReviewAgent(BaseAgent):
    def run(self, file_content: str, file_type: str, comments: list[str]) -> str:
        """
        Apply all of a reviewer's inline comments to a generated file in one pass.

        file_type: one of "feature", "pom", "driver", "steps"
        comments:  list of inline comment texts from the PR review
        Returns:   the fully corrected file content
        """
        log.info("ReviewAgent: applying %d comment(s) to %s file", len(comments), file_type)
        for i, c in enumerate(comments, 1):
            log.info("  [%d] %s", i, c[:100])

        # Number each comment so the LLM sees them as a clear checklist
        numbered = "\n".join(f'{i}. "{c}"' for i, c in enumerate(comments, 1))

        user_prompt = f"""File type: {file_type}

Current file content:
{file_content}

Reviewer requested these {len(comments)} change(s):
{numbered}

Apply ALL of the above changes in one pass and return the complete corrected file."""

        response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
        cleaned = self._strip(response)
        log.info("ReviewAgent: fixed file written (%d chars)", len(cleaned))
        return cleaned
