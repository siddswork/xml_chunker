Feature: Pattern Template Orchestration Tests for OrderCreate_MapForce_Full
  As a QA engineer
  I want to test pattern template orchestration scenarios
  So that I can ensure XSLT transformation quality

  Background:
    Given the XSLT transformation file "../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    And the transformation engine is initialized

  @high_priority @pattern_template_orchestration
  Scenario: Test for correct transformation of Request elements into OrderCreateRQ structure
    When the XSLT transformation is executed
    And Request element exists
    And ID is present and valid

  @medium_priority @pattern_template_orchestration
  Scenario: Test XPath expression for addresseeName extraction
    When the XSLT transformation is executed
    And addresseeName is present
    And Request element is structured correctly

  @high_priority @pattern_template_orchestration
  Scenario: Test edge case where Request element is missing
    When the XSLT transformation is executed
    And Request element is absent
    And Check if default handling occurs
