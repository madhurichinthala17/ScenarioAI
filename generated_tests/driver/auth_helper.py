# =============================================================================
# WARNING: ScenarioAI validation failed — this file was written as FAIL-OPEN
# Review the errors listed in the PR description before merging.
# =============================================================================

from pages.auth_page import AuthPage

def setup_navigate_to_signup_form(page_object: AuthPage) -> None:
    page_object.navigate_to_signup_form()

def perform_subscribe_to_newsletter(page_object: AuthPage, email: str) -> None:
    page_object.enter_email(email)
    page_object.submit_form()