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
from src.core.text import strip_code_fences


class BaseAgent:
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient()

    @staticmethod
    def _strip(text: str) -> str:
        """Strip markdown code fences from an LLM response."""
        return strip_code_fences(text)
