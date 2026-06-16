class ScenarioAIError(Exception):
    """Base exception for all ScenarioAI errors."""


class LLMError(ScenarioAIError):
    """Raised when an LLM call fails."""


class ValidationError(ScenarioAIError):
    """Raised when generated code fails validation after max retries."""


class FileWriteError(ScenarioAIError):
    """Raised when writing generated files to disk fails."""
