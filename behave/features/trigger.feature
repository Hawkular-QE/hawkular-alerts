Feature: Trigger

Scenario: create a valid trigger
    Given hawkular alerts is installed and working
    When create a valid trigger
    Then trigger will be created

 Scenario: create a trigger with existing ID
    Given hawkular alerts is installed and working
    When create a trigger with a existing ID
    Then trigger won't be created


  Scenario: update threshold condition on trigger
    Given hawkular alerts is installed and working
    When update a existing trigger with threshold condition
    then trigger will have a threshold condition


# TODO Group Trigger
