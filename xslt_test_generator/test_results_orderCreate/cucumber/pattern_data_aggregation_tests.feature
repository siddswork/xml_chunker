Feature: Pattern Data Aggregation Tests for OrderCreate_MapForce_Full
  As a QA engineer
  I want to test pattern data aggregation scenarios
  So that I can ensure XSLT transformation quality

  Background:
    Given the XSLT transformation file "../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    And the transformation engine is initialized

  @high_priority @pattern_data_aggregation
  Scenario: Test data aggregation for multiple Request elements
    When the XSLT transformation is executed
    And Check if multiple Request elements are processed correctly
    And Ensure Version attribute is repeated for each Request

  @medium_priority @pattern_data_aggregation
  Scenario: Test XPath expression for conditional logic based on Name/Type
    When the XSLT transformation is executed
    And Check if the condition for Type 'Other' is met
    And Verify that the output includes the Version attribute

  @low_priority @pattern_data_aggregation
  Scenario: Test edge case with empty Request element
    When the XSLT transformation is executed
    And Ensure that an empty Request does not produce any Version attributes
    And Verify that the output structure remains valid
