"""Small text helpers shared across agents.

Centralizes two things that were previously copy-pasted across nearly every
agent: stripping markdown code fences from LLM responses, and coercing a
loosely-typed list (the LLM sometimes returns dicts) into a list of strings.
"""
import re

# Matches an opening fence with an optional language hint (```python, ```json,
# ```gherkin, ```feature, or a bare ```) as well as a closing fence.
_FENCE_RE = re.compile(r"```(?:python|json|gherkin|feature)?")


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from an LLM response and trim whitespace."""
    return _FENCE_RE.sub("", text).strip()


def normalize_to_str_list(items) -> list[str]:
    """Coerce a list that may contain dicts into a flat list of strings.

    The LLM occasionally returns list items as objects (e.g. an edge case as
    ``{"case": "...", "expected": "..."}``) instead of plain strings. Dict
    items are flattened by joining their values.
    """
    normalized: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            normalized.append(", ".join(str(v) for v in item.values()))
        else:
            normalized.append(str(item))
    return normalized
