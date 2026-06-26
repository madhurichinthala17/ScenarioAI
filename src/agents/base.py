"""Base class for all LLM-backed agents.

Provides a shared LLM client and the code-fence stripping helper that every
generator agent needs, so individual agents only implement their own prompt
construction and validation logic (Template Method style).

The LLM client is injected: ``build_graph`` creates a single ``LLMClient`` and
passes it to every agent, avoiding one client (and one provider handshake) per
agent. When no client is supplied, one is created lazily so agents remain
usable standalone (e.g. the review CLIs).
"""
from typing import Optional

from src.core.llm_client import LLMClient
from src.core.logger import get_logger
from src.core.text import strip_code_fences


class BaseAgent:
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient()
        self.log = get_logger(self.__class__.__module__)

    @staticmethod
    def _strip(text: str) -> str:
        """Strip markdown code fences from an LLM response."""
        return strip_code_fences(text)

    def _soft_validate(self, content: str) -> None:
        """Run the agent's own ``_validate`` without crashing the pipeline.

        Generator agents used to ``raise`` straight out of ``run()`` when the
        LLM produced slightly-off code, which killed the entire graph before it
        could reach the ValidatorAgent node — bypassing the retry / fail-open
        machinery the whole architecture is built around. Instead we log the
        problem and let the content flow downstream: ValidatorAgent will catch
        it and route back here for a retry, or fail open after MAX_RETRIES.
        """
        try:
            self._validate(content)
        except ValueError as e:
            self.log.warning(
                "%s self-validation flagged an issue (deferring to ValidatorAgent): %s",
                self.__class__.__name__, e,
            )

    def _validate(self, content: str) -> None:  # pragma: no cover - overridden
        """Subclasses override with their own checks; default is a no-op."""
        return None
