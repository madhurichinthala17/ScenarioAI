# =============================================================================
# WARNING: ScenarioAI validation failed — this file was written as FAIL-OPEN
# Review the errors listed in the PR description before merging.
# =============================================================================

from playwright.sync_api import Page

class SignupPage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to_signup_form(self) -> None:
        pass

    def enter_email(self, email: str) -> None:
        pass

    def submit_form(self) -> None:
        pass

    def get_confirmation_message(self) -> str:
        pass

    def get_error_message(self) -> str:
        pass