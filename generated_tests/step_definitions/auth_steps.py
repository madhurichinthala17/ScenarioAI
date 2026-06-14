from behave import given, when, then
from driver.auth_helper import *

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user enters valid email and password")
def step_impl(context):
    perform_enter_credentials(context.AuthPage, "valid.email@example.com", "validpassword")

@then("the user is redirected to the dashboard")
def step_impl(context):
    assert context.AuthPage.see_dashboard()

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user enters an invalid email or password")
def step_impl(context):
    perform_enter_credentials(context.AuthPage, "invalid.email@example.com", "wrongpassword")

@then("the user sees the error message 'Invalid email or password'")
def step_impl(context):
    assert context.AuthPage.see_error_message("Invalid email or password")

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user leaves the email field empty and enters a password")
def step_impl(context):
    context.AuthPage.leave_field_empty_and_enter_value("email", "testpassword")

@then("the user sees a validation error for the email field")
def step_impl(context):
    assert context.AuthPage.see_validation_error_for_field("email")

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user leaves the password field empty and enters an email")
def step_impl(context):
    context.AuthPage.leave_field_empty_and_enter_value("password", "testemail@example.com")

@then("the user sees a validation error for the password field")
def step_impl(context):
    assert context.AuthPage.see_validation_error_for_field("password")

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user leaves both the email and password fields empty")
def step_impl(context):
    context.AuthPage.leave_field_empty_and_enter_value("email", "")
    context.AuthPage.leave_field_empty_and_enter_value("password", "")

@then("the user sees validation errors for both the email and password fields")
def step_impl(context):
    assert context.AuthPage.see_validation_error_for_field("email") and context.AuthPage.see_validation_error_for_field("password")

@given("the user navigates to the login page")
def step_impl(context):
    setup_navigate_to_login_page(context.AuthPage)

@when("the user enters invalid credentials more than 5 times")
def step_impl(context):
    for _ in range(6):
        perform_enter_credentials(context.AuthPage, "invalid.email@example.com", "wrongpassword")

@then("the account is locked and the user sees the message 'Account locked. Please contact support'")
def step_impl(context):
    assert context.AuthPage.account_is_locked_and_see_message("Account locked. Please contact support")