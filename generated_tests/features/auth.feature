Feature: Subscribe to the newsletter

  Scenario: User successfully subscribes to the newsletter
    Given the user is on the signup form
    When the user enters a valid email address and submits the form
    Then the user sees "Thanks for subscribing!"

  Scenario: User submits an invalid email address
    Given the user is on the signup form
    When the user enters an invalid email address and submits the form
    Then the user sees "Please enter a valid email address"

  Scenario: User tries to subscribe with an already registered email
    Given the user is on the signup form
    When the user enters an email address that is already on the list and submits the form
    Then the user sees "You're already on the list"

  Scenario: User submits the form without an email address
    Given the user is on the signup form
    When the user submits the form without entering an email address
    Then the user sees "Email is required"