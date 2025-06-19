# XSLT Test Generator Examples

This document provides practical examples of using the XSLT Test Generator with different types of XSLT transformations and XSD schemas.

## Table of Contents

1. [Basic Usage Examples](#basic-usage-examples)
2. [Real-World Example: OrderCreate Transformation](#real-world-example-ordercreate-transformation)
3. [Example Outputs Explained](#example-outputs-explained)
4. [Different Scenarios](#different-scenarios)
5. [Best Practices](#best-practices)

## Basic Usage Examples

### Example 1: Simple Command Line Usage

```bash
# Basic usage with minimal options
python -m src.main transform.xslt schema.xsd ./output

# With verbose output for debugging
python -m src.main transform.xslt schema.xsd ./output --verbose

# Using specific LLM provider
python -m src.main transform.xslt schema.xsd ./output --provider anthropic
```

### Example 2: Using the Provided Example Script

```bash
# Run the built-in example with OrderCreate files
cd xslt_test_generator/examples
python run_example.py
```

This script automatically:
- Locates the OrderCreate XSLT and XSD files
- Runs the test generator
- Saves output to `examples/output/`

## Real-World Example: OrderCreate Transformation

### Input Files

**XSLT File**: `OrderCreate_MapForce_Full.xslt`
- **Purpose**: Transforms AMA Connectivity Layer requests to IATA NDC OrderCreate format
- **Complexity**: High (100+ templates, conditional logic, value mappings)
- **Business Rules**: Target-based processing, visa handling, phone sanitization

**XSD File**: `AMA_ConnectivityLayerRQ.xsd`
- **Purpose**: Defines structure for travel booking requests
- **Elements**: Request, Context, TravelAgency, actor (passengers), set (offers)
- **Constraints**: Required elements, cardinalities, choice elements

### Running the Example

```bash
python -m src.main \
  ../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt \
  ../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd \
  ./output/orderCreate \
  --verbose
```

### Expected Output

```
🚀 Starting XSLT Test Generator
🤖 Initializing AI agents...

📊 XSLT Analysis Summary:
  • Templates: 15
  • Conditional blocks: 8
  • Value mappings: 4
  • Complexity: high

📋 XSD Analysis Summary:
  • Root elements: 1
  • Complex types: 12
  • Choice elements: 3
  • Optional elements: Yes

🧪 Test Generation Summary:
  • Features: 1
  • Scenarios: 12
  • Test steps: 48
  • Has examples: Yes

🎉 Test generation completed successfully!
📁 Output location: ./output/orderCreate
```

## Example Outputs Explained

### Generated Gherkin Test File

**File**: `OrderCreate_MapForce_Full_AMA_ConnectivityLayerRQ_tests.feature`

```gherkin
Feature: OrderCreate XSLT Transformation Testing
  As a travel booking system
  I want to transform AMA connectivity requests to IATA NDC format
  So that I can process orders through the NDC standard

  Background:
    Given an XSLT transformation "OrderCreate_MapForce_Full.xslt" is available
    And input XML conforms to "AMA_ConnectivityLayerRQ.xsd" schema
    And the transformation produces IATA NDC OrderCreateRQ format

  Scenario: Transform basic UA target request with passenger data
    Given input XML contains:
      | Element | Value |
      | target  | UA    |
      | passenger PTC | ADT |
      | passenger name | John Doe |
    When the XSLT transformation is applied
    Then the output should contain PointOfSale with CountryCode "FR"
    And the output should contain CityCode "NCE"
    And the output should contain AgentUserID "xmluser001"
    And the transformation should complete without errors

  Scenario: Handle document type mapping for passports
    Given input XML with passenger document type "P"
    When the XSLT transformation is applied
    Then the output should contain IdentityDocument with DocumentType "VPT"
    And the document mapping should be applied correctly

  Scenario: Handle document type mapping for passport travel documents
    Given input XML with passenger document type "PT"
    When the XSLT transformation is applied
    Then the output should contain IdentityDocument with DocumentType "VPT"
    And both P and PT types should map to VPT

  Scenario Outline: Process visa type mappings
    Given input XML with visa type "<input_visa_type>"
    When the XSLT transformation is applied
    Then the output should contain visa mapping "<expected_output>"
    
    Examples:
      | input_visa_type | expected_output |
      | V               | VVI             |
      | R               | VAEA            |
      | K               | VCR             |

  Scenario: Handle phone number sanitization
    Given input XML with phone number "+1-555-123-4567 ext.890"
    When the XSLT transformation is applied
    Then the output phone number should be "15551234567890"
    And all non-numeric characters should be removed
    And the sanitization should handle international formats

  Scenario: Process seat selection data
    Given input XML with seat number "12A"
    When the XSLT transformation is applied
    Then the output should contain Row "12"
    And the output should contain Column "A"
    And the seat parsing should handle alphanumeric formats

  Scenario: Handle target-specific processing for UAD
    Given input XML with target "UAD"
    And passenger has visa type "K"
    When the XSLT transformation is applied
    Then the UAD-specific processing logic should be triggered
    And visa type K should be mapped to "VCR"
    And special UAD business rules should be applied

  Scenario: Process multiple passengers with different contact types
    Given input XML contains:
      | Passenger | Contact Type | Email Domain |
      | PAX001   | CTC          | business.com |
      | PAX002   | GST          | personal.com |
    When the XSLT transformation is applied
    Then each passenger should have unique ContactID
    And contact types should be properly mapped
    And email labels should be set to "Voperational"

  Scenario: Handle missing optional elements gracefully
    Given input XML with minimal required elements only
    And optional elements like correlationID are missing
    When the XSLT transformation is applied
    Then the transformation should complete successfully
    And default values should be applied where appropriate
    And no errors should be generated for missing optional elements

  Scenario: Process tax identifier information
    Given input XML with passenger tax identifier
    And fiscal type is "SSN"
    And fiscal number is "123-45-6789"
    When the XSLT transformation is applied
    Then a FOID special service request should be generated
    And the tax identifier should be included in metadata

  Scenario: Handle gender mapping including edge cases
    Given input XML with passenger gender type "Other"
    When the XSLT transformation is applied
    Then the output should contain Gender "Unspecified"
    And non-standard gender types should be handled appropriately

  Scenario: Process address information for special service requests
    Given input XML with complete passenger address
    And address contains company name and multiple lines
    When the XSLT transformation is applied
    Then appropriate special service request codes should be generated
    And address information should be properly formatted
    And GSTN, GSTA, GSTP, or GSTE codes should be created as needed
```

### Analysis Report

**File**: `OrderCreate_MapForce_Full_AMA_ConnectivityLayerRQ_analysis.md`

```markdown
# XSLT Test Generation Report

## Input Files
- **XSLT File**: ../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt
- **XSD File**: ../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd
- **Generation Date**: 2024-01-01

## Test Case Statistics
- **Features Generated**: 1
- **Scenarios Generated**: 12
- **Total Test Steps**: 48

## Quality Indicators
- **Proper Gherkin Structure**: ✅
- **Has Background**: ✅
- **Has Scenario Outlines**: ✅
- **Has Examples**: ✅

## Coverage Analysis

### Template Coverage
- **Total Templates**: 15
- **Coverage**: 87%

### Condition Coverage  
- **Total Conditions**: 8
- **Coverage**: 100%

### Schema Coverage
- **Total Elements**: 12
- **Coverage**: 75%

## Coverage Areas
- transformation_logic
- conditional_branching
- data_validation
- edge_cases
- error_scenarios

## Key Business Rules Identified
1. **Target-Based Processing**: UA vs UAD triggers different transformation paths
2. **Document Type Mapping**: P/PT passport types map to VPT
3. **Visa Type Conversion**: V→VVI, R→VAEA, K→VCR mappings
4. **Phone Sanitization**: Removes all non-numeric characters
5. **Seat Number Parsing**: Splits alphanumeric seat numbers (e.g., "12A" → Row=12, Column=A)
6. **Gender Handling**: Maps "Other" gender type to "Unspecified"
7. **Contact Processing**: Email/mobile labels map to "Voperational"

## Next Steps
1. Review generated test cases for business rule accuracy
2. Create XML test data files matching the scenarios
3. Execute XSLT transformation with test data
4. Validate outputs against expected IATA NDC format
5. Add additional edge cases if identified during testing
```

### Metadata File

**File**: `OrderCreate_MapForce_Full_AMA_ConnectivityLayerRQ_metadata.yaml`

```yaml
generation_timestamp: '2024-01-01'
xslt_complexity:
  has_named_templates: true
  has_conditional_logic: true
  has_value_mappings: true
  xpath_complexity: high
xsd_characteristics:
  has_optional_elements: true
  has_unbounded_elements: true
  has_choice_constructs: true
  has_complex_nesting: true
coverage_areas:
- transformation_logic
- conditional_branching
- data_validation
- edge_cases
- error_scenarios
```

## Different Scenarios

### Scenario 1: Simple XSLT with Basic Transformations

**Use Case**: Converting customer data format

**XSLT Characteristics**:
- Few templates (2-5)
- Simple value mappings
- Minimal conditional logic

**Expected Test Output**:
```gherkin
Feature: Customer Data Transformation
  Scenario: Transform basic customer information
    Given customer XML with name and address
    When transformation is applied
    Then output should contain formatted customer data
```

### Scenario 2: Complex XSLT with Business Rules

**Use Case**: Financial transaction processing

**XSLT Characteristics**:
- Many templates (20+)
- Complex business rules
- Multiple conditional paths
- Data validation

**Expected Test Output**:
- Multiple feature files
- Scenario outlines with examples
- Edge case scenarios
- Error handling tests

### Scenario 3: XSLT with External Dependencies

**Use Case**: Integration with multiple systems

**XSLT Characteristics**:
- External schema imports
- Namespace handling
- System-specific mappings

**Expected Test Output**:
- Integration test scenarios
- Namespace validation tests
- Dependency handling tests

## Best Practices

### 1. File Organization

```bash
# Organize by project/domain
./projects/
├── orderCreate/
│   ├── input/
│   │   ├── transform.xslt
│   │   └── schema.xsd
│   └── output/
│       ├── tests.feature
│       ├── analysis.md
│       └── metadata.yaml
└── invoiceProcessing/
    ├── input/
    └── output/
```

### 2. Version Control

```bash
# Track both input and output files
git add projects/orderCreate/input/*.xslt
git add projects/orderCreate/input/*.xsd
git add projects/orderCreate/output/*.feature
git commit -m "Add OrderCreate test generation results"
```

### 3. Batch Processing

```bash
#!/bin/bash
# Process multiple XSLT/XSD pairs

for project in orderCreate invoiceProcessing customerData; do
  echo "Processing $project..."
  python -m src.main \
    ./projects/$project/input/transform.xslt \
    ./projects/$project/input/schema.xsd \
    ./projects/$project/output \
    --verbose
done
```

### 4. Continuous Integration

```yaml
# GitHub Actions example
name: Generate XSLT Tests
on: [push]
jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Generate tests
      run: |
        python -m src.main \
          ./xslt/transform.xslt \
          ./xsd/schema.xsd \
          ./tests/generated
    - name: Upload test artifacts
      uses: actions/upload-artifact@v2
      with:
        name: generated-tests
        path: ./tests/generated/
```

### 5. Quality Assurance

#### Review Checklist
- [ ] All major business rules covered
- [ ] Edge cases identified and tested
- [ ] Error scenarios included
- [ ] Gherkin syntax is correct
- [ ] Test scenarios are realistic
- [ ] Examples are comprehensive

#### Validation Process
1. **Technical Review**: Verify XSLT/XSD analysis accuracy
2. **Business Review**: Confirm test scenarios match requirements
3. **Test Execution**: Run actual tests with generated scenarios
4. **Results Validation**: Compare outputs with expectations

### 6. Maintenance

#### Regular Updates
- Re-generate tests when XSLT changes
- Update scenarios when business rules change
- Review coverage reports periodically
- Archive old test versions

#### Performance Monitoring
- Track generation time trends
- Monitor LLM API usage and costs
- Measure test coverage improvements
- Collect user feedback

This comprehensive example guide should help users understand how to effectively use the XSLT Test Generator in various real-world scenarios.