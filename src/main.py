import json
from src.graph.workflow import build_graph
from src.utils.file_scanner import ensure_folders_exist

ensure_folders_exist()

requirement = """
The application has a login page where users can enter their email and password.
When a user enters valid credentials and clicks the login button, they should be
redirected to the dashboard. If the credentials are invalid, an error message
should appear saying "Invalid email or password". If the user leaves the email
or password field empty and clicks login, the form should show a validation error.
After 5 failed attempts, the account should be locked and the user should see a
message saying "Account locked. Please contact support".
"""

graph = build_graph()

final_state = graph.invoke({
    "requirement": requirement,
    "parsed_requirement": None,
    "gherkin": None,
    "file_plan": None,
    "pom_content": None,
    "driver_content": None,
    "steps_content": None,
    "validation_passed": None,
    "validation_errors": [],
    "retry_count": 0
})

print("\n--- Parsed Requirement ---")
print(json.dumps(final_state["parsed_requirement"], indent=2))

print("\n--- Gherkin ---")
print(final_state["gherkin"])

print("\n--- File Plan ---")
print(json.dumps(final_state["file_plan"], indent=2))

print("\n--- POM ---")
print(final_state["pom_content"])

print("\n--- Driver ---")
print(final_state["driver_content"])