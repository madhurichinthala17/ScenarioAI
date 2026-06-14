Feature: Log in to the application

Scenario: User logs in with valid credentials
    Given the user navigates to the login page
    When the user enters valid email and password
    Then the user is redirected to the dashboard

Scenario: User enters invalid email or password
    Given the user navigates to the login page
    When the user enters an invalid email or password
    Then the user sees the error message 'Invalid email or password'

Scenario: User leaves email field empty and provides a password
    Given the user navigates to the login page
    When the user leaves the email field empty and enters a password
    Then the user sees a validation error for the email field

Scenario: User leaves password field empty and provides an email
    Given the user navigates to the login page
    When the user leaves the password field empty and enters an email
    Then the user sees a validation error for the password field

Scenario: User leaves both fields empty
    Given the user navigates to the login page
    When the user leaves both the email and password fields empty
    Then the user sees validation errors for both the email and password fields

Scenario: User fails login attempts more than 5 times
    Given the user navigates to the login page
    When the user enters invalid credentials more than 5 times
    Then the account is locked and the user sees the message 'Account locked. Please contact support'