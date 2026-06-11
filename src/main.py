import json
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.gherkin_generator import GherkinGeneratorAgent

requirement = """
The application has a login page where users can enter their email and password.
When a user enters valid credentials and clicks the login button, they should be
redirected to the dashboard. If the credentials are invalid, an error message
should appear saying "Invalid email or password". If the user leaves the email
or password field empty and clicks login, the form should show a validation error.
After 5 failed attempts, the account should be locked and the user should see a
message saying "Account locked. Please contact support".
"""

# Agent 1 — Requirement Parser
print("--- Running Requirement Parser ---")
parser = RequirementParserAgent()
parsed = parser.run(requirement)
print(json.dumps(parsed, indent=2))

# Agent 2 — Gherkin Generator
print("\n--- Running Gherkin Generator ---")
gherkin = GherkinGeneratorAgent()
feature_file = gherkin.run(parsed)
print(feature_file)