# Getting Started with XSLT Test Generator

## For Complete Beginners

This guide will help you understand and use the XSLT Test Generator, even if you're new to programming or XSLT.

## Table of Contents

1. [What You Need to Know First](#what-you-need-to-know-first)
2. [Installation Guide](#installation-guide)
3. [Your First Test Generation](#your-first-test-generation)
4. [Understanding the Output](#understanding-the-output)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

## What You Need to Know First

### Key Concepts

#### XSLT (eXtensible Stylesheet Language Transformations)
Think of XSLT as a recipe that transforms one type of data into another. For example:
- Input: Customer order in one format
- XSLT: The transformation rules
- Output: Same order in a different format

#### XSD (XML Schema Definition)
Think of XSD as a blueprint that describes what valid input data looks like. It defines:
- What elements are required
- What elements are optional
- What data types are allowed
- How elements relate to each other

#### Test Cases
Test cases are scenarios that verify your XSLT transformation works correctly. They follow a pattern:
- **Given**: Starting conditions
- **When**: What action is performed
- **Then**: What should happen

#### Gherkin Format
A way of writing test cases in plain English that both humans and computers can understand:

```gherkin
Feature: Order Processing
  Scenario: Process a valid order
    Given a customer order with valid data
    When the XSLT transformation is applied
    Then the output should be a valid processed order
```

## Installation Guide

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should show 3.8 or higher
   ```

2. **Git** (to clone the repository)
   ```bash
   git --version
   ```

3. **API Key** for at least one AI service:
   - OpenAI (recommended for beginners)
   - Anthropic Claude
   - Google Gemini

### Step-by-Step Installation

#### 1. Get the Code
```bash
# Clone the repository
git clone https://github.com/siddswork/xml_wizard.git
cd xml_wizard/xslt_test_generator
```

#### 2. Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure API Keys
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite text editor
nano .env  # or use any text editor
```

Add your API key to the `.env` file:
```
OPENAI_API_KEY=your_actual_api_key_here
```

#### 5. Test Installation
```bash
python -m src.main --help
```

You should see the help message with available commands.

## Your First Test Generation

Let's generate test cases for the example XSLT transformation included in the project.

### Step 1: Locate Example Files

The project includes example files:
- **XSLT**: `../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt`
- **XSD**: `../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd`

### Step 2: Run the Generator

```bash
python -m src.main \
  ../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt \
  ../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd \
  ./output \
  --verbose
```

**What this command does**:
1. Analyzes the XSLT file to understand transformation logic
2. Analyzes the XSD file to understand input data structure
3. Generates comprehensive test cases
4. Saves results to the `./output` directory
5. Shows detailed progress with `--verbose`

### Step 3: Watch the Magic Happen

You'll see output like this:
```
🚀 Starting XSLT Test Generator
🤖 Initializing AI agents...
📖 Reading input files...
✅ Files read successfully
🔍 Analyzing XSLT transformation...
✅ XSLT analysis completed
📋 Analyzing XSD schema...
✅ XSD analysis completed
🧪 Generating test cases...
✅ Test cases generated
💾 Writing output files...
✅ Output files written

🎉 Test generation completed successfully!
📁 Output location: ./output
```

## Understanding the Output

After successful generation, you'll find these files in the output directory:

### 1. `{name}_tests.feature` - Main Test Cases

This file contains Gherkin test scenarios. Example:

```gherkin
Feature: XSLT OrderCreate Transformation Testing

  Background:
    Given an XSLT transformation is available
    And input XML conforms to AMA_ConnectivityLayerRQ schema

  Scenario: Transform UA target with passport document
    Given input XML with target "UA"
    And passenger has document type "P"
    When the XSLT transformation is applied
    Then the output should contain document mapping "VPT"
    And the transformation should complete successfully

  Scenario: Handle phone number sanitization
    Given input XML with phone number "+1-555-123-4567"
    When the XSLT transformation is applied
    Then the output phone number should be "15551234567"
    And special characters should be removed
```

### 2. `{name}_analysis.md` - Detailed Report

This file contains analysis details:

```markdown
# XSLT Test Generation Report

## Input Files
- XSLT File: OrderCreate_MapForce_Full.xslt
- XSD File: AMA_ConnectivityLayerRQ.xsd

## Test Case Statistics
- Features Generated: 3
- Scenarios Generated: 15
- Total Test Steps: 45

## Coverage Analysis
- Template Coverage: 85%
- Condition Coverage: 90%
- Schema Coverage: 75%
```

### 3. `{name}_metadata.yaml` - Technical Details

This file contains technical information about the generation process.

## Common Use Cases

### Use Case 1: Validating New XSLT Transformations

**Scenario**: You've written a new XSLT transformation and want to ensure it works correctly.

**Steps**:
1. Run the test generator on your XSLT and XSD files
2. Review the generated test cases
3. Create actual XML test data based on the scenarios
4. Run your XSLT against the test data
5. Verify the outputs match expectations

### Use Case 2: Documenting Existing Transformations

**Scenario**: You have an existing XSLT that lacks documentation.

**Steps**:
1. Generate test cases to understand what the XSLT does
2. Use the analysis report to document business rules
3. Share the Gherkin scenarios with business stakeholders
4. Use scenarios as living documentation

### Use Case 3: Regression Testing

**Scenario**: You need to modify an existing XSLT without breaking functionality.

**Steps**:
1. Generate test cases for the current XSLT
2. Create test data and capture current outputs
3. Modify the XSLT as needed
4. Run the same tests against the modified XSLT
5. Compare outputs to ensure no regressions

### Use Case 4: Code Review and Quality Assurance

**Scenario**: You're reviewing someone else's XSLT transformation.

**Steps**:
1. Generate test cases to understand the transformation logic
2. Review the analysis report for complexity indicators
3. Check if edge cases are properly handled
4. Verify business rules align with requirements

## Troubleshooting

### Common Issues and Solutions

#### Issue: "File not found" Error
```
❌ XSLT file not found: /path/to/file.xslt
```

**Solution**: Check that the file path is correct and the file exists.
```bash
ls -la /path/to/file.xslt  # Verify file exists
```

#### Issue: "Invalid XSLT file" Error
```
❌ Invalid XSLT file: transform.xslt
```

**Solution**: Ensure the file is a valid XSLT transformation:
- Should start with `<?xml version="1.0"?>`
- Should have `<xsl:stylesheet>` or `<xsl:transform>` as root element
- Should use XSLT namespace: `xmlns:xsl="http://www.w3.org/1999/XSL/Transform"`

#### Issue: "LLM generation failed" Error
```
❌ Error generating test cases: LLM generation failed: API key not found
```

**Solution**: Check your API key configuration:
1. Verify `.env` file exists and contains your API key
2. Ensure the API key is valid and has sufficient credits
3. Check internet connection

#### Issue: Low Quality Test Cases

**Symptoms**: Generated test cases are too generic or miss important scenarios.

**Solutions**:
1. Try a different LLM provider (e.g., switch from OpenAI to Anthropic)
2. Increase the `temperature` setting in `config.yaml` for more creative outputs
3. Ensure your XSLT and XSD files are complex enough to generate meaningful tests

#### Issue: Long Generation Time

**Symptoms**: The process takes more than 5 minutes.

**Solutions**:
1. Check your internet connection
2. Verify the API service isn't experiencing issues
3. Try reducing the `max_tokens` setting in `config.yaml`
4. Consider using a faster model (e.g., GPT-3.5 instead of GPT-4)

### Debug Mode

To get more detailed error information:

```bash
python -m src.main \
  your_files... \
  --verbose \
  2>&1 | tee debug.log
```

This saves all output to `debug.log` for analysis.

### Getting Help

1. **Check the logs**: Look for error messages in the verbose output
2. **Verify configuration**: Ensure `config.yaml` and `.env` are properly set up
3. **Test with examples**: Try the included example files first
4. **Check file permissions**: Ensure you can read input files and write to output directory

## Next Steps

### After Your First Success

1. **Experiment with Different Files**: Try the generator with your own XSLT/XSD files
2. **Customize Configuration**: Modify `config.yaml` to tune the output
3. **Learn Gherkin**: Understand how to read and modify the generated test cases
4. **Create Test Data**: Generate actual XML files based on the scenarios

### Advanced Usage

1. **Switch LLM Providers**: Try different AI models to compare outputs
2. **Batch Processing**: Process multiple XSLT/XSD pairs
3. **Integration**: Incorporate into your development workflow
4. **Customization**: Extend the agents for specific needs

### Learning Resources

1. **XSLT Tutorial**: https://www.w3schools.com/xml/xsl_intro.asp
2. **XSD Tutorial**: https://www.w3schools.com/xml/schema_intro.asp
3. **Gherkin Documentation**: https://cucumber.io/docs/gherkin/
4. **CrewAI Documentation**: https://docs.crewai.com/

### Contributing

If you find bugs or want to add features:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Consider submitting a pull request

### Support

For questions or issues:
1. Review this documentation
2. Check the GitHub issues
3. Create a new issue with your question

Remember: The XSLT Test Generator is a tool to help you create better tests, but you still need to understand your business requirements and validate that the generated tests meet your needs.