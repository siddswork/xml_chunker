Feature: Complexity Hotspot Tests for OrderCreate_MapForce_Full
  As a QA engineer
  I want to test complexity hotspot scenarios
  So that I can ensure XSLT transformation quality

  Background:
    Given the XSLT transformation file "../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    And the transformation engine is initialized

  @high_priority @complexity_hotspot
  Scenario: Test the XPath expression for 'address/addresseeName' to ensure correct extraction.
    When the XSLT transformation is executed
    And Input XML contains valid address structure

  @high_priority @complexity_hotspot
  Scenario: Test the conditional logic for Name/Type being 'Other'.
    When the XSLT transformation is executed
    And Name/Type is 'Other'

  @high_priority @complexity_hotspot
  Scenario: Test the output of the PointOfSale element generation.
    When the XSLT transformation is executed
    And Valid Request structure with Context and correlationID

  @high_priority @complexity_hotspot
  Scenario: Test the XPath expression for 'ID' to ensure correct extraction.
    When the XSLT transformation is executed
    And Input XML contains valid ID element

  @high_priority @complexity_hotspot
  Scenario: Test edge case where correlationID is missing.
    When the XSLT transformation is executed
    And CorrelationID element is absent in the input XML
