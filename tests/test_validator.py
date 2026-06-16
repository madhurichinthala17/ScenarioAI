"""
Tests for ValidatorAgent.

"""
from src.agents.validator import ValidatorAgent

VALID_GHERKIN = """\
Feature: Login

  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    Then the user should see the dashboard
"""

VALID_POM = """\
class LoginPage:
    def __init__(self, page):
        self.page = page

    def navigate_to_login_page(self):
        self.page.goto("/login")

    def enter_credentials(self, email, password):
        self.page.fill("#email", email)
        self.page.fill("#password", password)
        self.page.click("#submit")

    def see_dashboard(self):
        self.page.wait_for_url("**/dashboard")
"""

VALID_DRIVER = """\
def setup_navigate_to_login_page(page):
    login_page = LoginPage(page)
    login_page.navigate_to_login_page()
    return login_page

def perform_enter_credentials(login_page, email, password):
    login_page.enter_credentials(email, password)
"""

VALID_STEPS = """\
from behave import given, when, then

@given('the user is on the login page')
def step_given(context):
    context.login_page = setup_navigate_to_login_page(context.page)

@when('the user enters valid credentials')
def step_when(context):
    perform_enter_credentials(context.login_page, 'user@test.com', 'pass123')

@then('the user should see the dashboard')
def step_then(context):
    context.login_page.see_dashboard()
"""


def test_valid_inputs_pass():
    result = ValidatorAgent().run(VALID_GHERKIN, VALID_POM, VALID_DRIVER, VALID_STEPS)
    assert result["passed"] is True
    assert result["errors"] == []


def test_pom_with_assertion_fails_purity_check():
    bad_pom = VALID_POM + "\n    assert self.page.url == '/dashboard'\n"
    result = ValidatorAgent().run(VALID_GHERKIN, bad_pom, VALID_DRIVER, VALID_STEPS)
    assert result["passed"] is False
    assert any("POM purity" in e for e in result["errors"])


def test_missing_gherkin_step_fails_coverage():
    gherkin_with_extra = VALID_GHERKIN + """\
  Scenario: Extra scenario
    Given the user is on the login page
    When the user enters invalid credentials
    Then an error message should appear
"""
    result = ValidatorAgent().run(gherkin_with_extra, VALID_POM, VALID_DRIVER, VALID_STEPS)
    assert result["passed"] is False
    assert any("Step coverage" in e for e in result["errors"])


def test_requirement_validation_rejects_empty():
    from src.main import validate_requirement
    try:
        validate_requirement("   ")
        assert False, "Should have raised"
    except ValueError as e:
        assert "empty" in str(e).lower()


def test_requirement_validation_rejects_too_long():
    from src.main import validate_requirement
    try:
        validate_requirement("x" * 2001)
        assert False, "Should have raised"
    except ValueError as e:
        assert "long" in str(e).lower()


def test_requirement_validation_strips_whitespace():
    from src.main import validate_requirement
    result = validate_requirement("  login flow  ")
    assert result == "login flow"
