Feature: Pattern Conditional Processing Tests for OrderCreate_MapForce_Full
  As a QA engineer
  I want to test pattern conditional processing scenarios
  So that I can ensure XSLT transformation quality

  Background:
    Given the XSLT transformation file "../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    And the transformation engine is initialized

  @high_priority @pattern_conditional_processing
  Scenario: Test vmf:vmf1_inputtoresult with input 'P'
    When the XSLT transformation is executed
    And $input='P'

  @high_priority @pattern_conditional_processing
  Scenario: Test vmf:vmf2_inputtoresult with input 'R'
    When the XSLT transformation is executed
    And $input='R'

  @medium_priority @pattern_conditional_processing
  Scenario: Test vmf:vmf3_inputtoresult with input 'email'
    When the XSLT transformation is executed
    And $input='email'

  @medium_priority @pattern_conditional_processing
  Scenario: Test vmf:vmf2_inputtoresult with input 'K' to verify multiple conditions
    When the XSLT transformation is executed
    And $input='K'

  @low_priority @pattern_conditional_processing
  Scenario: Test vmf:vmf1_inputtoresult with an unexpected input
    When the XSLT transformation is executed
    And $input='X'
