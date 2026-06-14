from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to_login_page(self) -> None:
        pass

    def enter_credentials(self, email: str, password: str) -> None:
        pass

    def see_dashboard(self) -> bool:
        pass

    def see_error_message(self, message: str) -> bool:
        pass

    def leave_field_empty_and_enter_value(self, field: str, value: str) -> None:
        pass

    def see_validation_error_for_field(self, field: str) -> bool:
        pass

    def enter_invalid_credentials_more_than_5_times(self, email: str, password: str) -> None:
        pass

    def account_is_locked_and_see_message(self, message: str) -> bool:
        pass