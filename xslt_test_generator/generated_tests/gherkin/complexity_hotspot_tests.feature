Feature: Complexity Hotspot Tests for OrderCreate_MapForce_Full
  As a QA engineer
  I want to test complexity hotspot scenarios
  So that I can ensure XSLT transformation quality

  Background:
    Given the XSLT transformation file "/home/sidd/dev/xml_chunker/resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    And the transformation engine is initialized

  @high_priority @complexity_hotspot
  Scenario: Test high-complexity template / with score 7
    Given an input XML with structure "Complex input XML with multiple conditions"
    When the XSLT transformation is executed
    And Verify / handles complex conditions
    And Test performance under load
