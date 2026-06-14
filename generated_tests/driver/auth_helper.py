from pages.auth_page import AuthPage

def setup_navigate_to_login_page(page_object: AuthPage) -> None:
    page_object.navigate()

def perform_enter_credentials(page_object: AuthPage, email: str, password: str) -> None:
    page_object.enter_email(email)
    page_object.enter_password(password)

def perform_validate_and_submit(page_object: AuthPage) -> None:
    page_object.submit_form()

def setup_account_lockout(page_object: AuthPage) -> None:
    for _ in range(5):
        perform_enter_credentials(page_object, "invalid@example.com", "wrongpassword")
        perform_validate_and_submit(page_object)