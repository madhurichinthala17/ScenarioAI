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

    def is_subscription_success_message_visible(self) -> bool:
        pass

    def is_invalid_email_message_visible(self) -> bool:
        pass

    def is_already_registered_message_visible(self) -> bool:
        pass

    def is_email_required_message_visible(self) -> bool:
        pass