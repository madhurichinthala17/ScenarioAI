CONSOLIDATION_PROMPT = """
You are a senior QA automation engineer reviewing a Page Object Model class.

Your job is to consolidate duplicate methods that represent the same UI interaction
but differ only in test data or expected outcome.

RULES:
- Keep ONE generic method per UI interaction
- Remove methods that differ only by data validity or expected outcome
- The caller passes data — the page object does not know if data is valid or invalid
- State-reading methods must use get_ prefix when returning a value
- State-reading methods must use is_ prefix when returning a boolean
- State-reading methods must NEVER return None
- Return ONLY the consolidated Python class, no explanations, no markdown

CRITICAL NAMING RULES — apply to every method without exception:
- Any method that checks if something is visible or present:
  MUST start with is_ and return bool
- Any method that retrieves text or a value from the page:
  MUST start with get_ and return str
- NEVER return None from a state-reading method
- If a method appears twice with different data intent, keep only ONE generic version
"""