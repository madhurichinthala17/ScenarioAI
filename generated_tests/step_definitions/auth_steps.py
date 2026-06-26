# =============================================================================
# WARNING: ScenarioAI validation failed — this file was written as FAIL-OPEN
# Review the errors listed in the PR description before merging.
# =============================================================================

from behave import given, when, then
from driver.auth_helper import *

@given("the user is on the signup form")
def step_impl(context):
    setup_navigate_to_signup_form(context.auth_page)

@when("the user enters a valid email address and submits the form")
def step_impl(context):
    perform_subscribe_to_newsletter(context.auth_page, "valid@example.com")

@then('the user sees "Thanks for subscribing!"')
def step_impl(context):
    assert context.auth_page.get_confirmation_message() == "Thanks for subscribing!"

@when("the user enters an invalid email address and submits the form")
def step_impl(context):
    perform_subscribe_to_newsletter(context.auth_page, "invalid-email")

@then('the user sees "Please enter a valid email address"')
def step_impl(context):
    assert context.auth_page.get_error_message() == "Please enter a valid email address"

@when("the user enters an email address that is already on the list and submits the form")
def step_impl(context):
    perform_subscribe_to_newsletter(context.auth_page, "registered@example.com")

@then('the user sees "You\'re already on the list"')
def step_impl(context):
    assert context.auth_page.get_error_message() == "You're already on the list"

@when("the user submits the form without entering an email address")
def step_impl(context):
    perform_subscribe_to_newsletter(context.auth_page, "")

@then('the user sees "Email is required"')
def step_impl(context):
    assert context.auth_page.get_error_message() == "Email is required"