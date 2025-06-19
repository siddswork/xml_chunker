# Tools and Functions Reference Guide

## Overview

This document provides a comprehensive reference for all tools and functions available to agents in the XSLT Test Generator. Each tool is explained with examples, use cases, and best practices.

## Table of Contents

1. [LLM Client Tools](#llm-client-tools)
2. [File Management Tools](#file-management-tools)
3. [XML Analysis Tools](#xml-analysis-tools)
4. [Configuration Tools](#configuration-tools)
5. [Agent Utilities](#agent-utilities)
6. [Best Practices](#best-practices)

---

## LLM Client Tools

### Location: `src/tools/llm_client.py`

The LLM Client provides AI-powered analysis capabilities to agents. It abstracts away the complexity of different AI providers.

### Core Functions

#### `LLMClient.__init__(provider=None)`

**Purpose**: Initialize the LLM client with a specific AI provider.

**Parameters**:
- `provider` (str, optional): AI provider name ('openai', 'anthropic', 'google')

**Example Usage**:
```python
from src.tools.llm_client import LLMClient

# Use default provider from config
client = LLMClient()

# Use specific provider
client = LLMClient(provider='anthropic')
```

**When to use**: At the start of any agent that needs AI analysis.

**Why**: Different AI models have different strengths. This allows switching between them easily.

---

#### `analyze_xslt(xslt_content)`

**Purpose**: Analyze XSLT transformation logic using AI to extract patterns, business rules, and testable scenarios.

**Parameters**:
- `xslt_content` (str): Complete XSLT file content

**Returns**: 
- `str`: Detailed analysis including transformation patterns, business rules, templates, and edge cases

**Example Usage**:
```python
xslt_content = FileManager.read_file('transform.xslt')
analysis = llm_client.analyze_xslt(xslt_content)
print(analysis)
```

**What it analyzes**:
- **Transformation Patterns**: How input maps to output
- **Business Rules**: Conditional logic and decision points
- **Template Functions**: Named templates and their purposes
- **XPath Expressions**: Complex data selection logic
- **Edge Cases**: Error handling and data sanitization
- **Input-Output Mapping**: Element relationships

**When to use**: 
- When you need semantic understanding of XSLT logic
- To identify business rules for test cases
- To understand transformation complexity

**Why**: XSLT can be complex. AI helps understand the intent behind the transformation logic.

**Example Output**:
```
XSLT Analysis Results:

Transformation Patterns:
1. Document Type Mapping: Maps passport types 'P' and 'PT' to 'VPT'
2. Visa Type Mapping: Converts V→VVI, R→VAEA, K→VCR
3. Phone Sanitization: Removes non-numeric characters

Business Rules:
1. Target-based Processing: UA vs UAD triggers different logic paths
2. Conditional Visa Processing: Only processes visas for specific targets
3. Gender Mapping: 'Other' type maps to 'Unspecified'

Edge Cases Identified:
1. Phone number sanitization for international formats
2. Seat number parsing (e.g., "12A" → Row=12, Column=A)
3. Missing optional element handling
```

---

#### `analyze_xsd(xsd_content)`

**Purpose**: Analyze XSD schema structure using AI to understand input constraints and validation rules.

**Parameters**:
- `xsd_content` (str): Complete XSD file content

**Returns**: 
- `str`: Detailed analysis including element structure, constraints, and test scenarios

**Example Usage**:
```python
xsd_content = FileManager.read_file('schema.xsd')
analysis = llm_client.analyze_xsd(xsd_content)
print(analysis)
```

**What it analyzes**:
- **Element Structure**: Root elements, complex types, hierarchy
- **Constraints**: Required vs optional, cardinalities
- **Data Types**: Simple types, restrictions, patterns
- **Choice Elements**: Alternative options and implications
- **Relationships**: How elements relate to each other
- **Test Scenarios**: Input variations to test

**When to use**:
- To understand valid input structure
- To identify test data requirements
- To plan validation test cases

**Why**: XSD schemas define what input is valid. Understanding this helps create comprehensive tests.

**Example Output**:
```
XSD Schema Analysis:

Element Structure:
- Root: AMA_ConnectivityLayerRQ
- Main Container: Requests (max 100)
- Request Elements: target, Context, set, actor

Constraints Identified:
- Required Elements: target, TravelAgency/Name
- Optional Elements: correlationID, docRef, contact
- Cardinalities: actor (0-198), set (1-99), product (1-99)

Choice Elements:
- Product types: FLT, HTL, CAR, etc. (25+ options)
- Document types: P, PT, MR, CPF, etc.

Test Scenarios Needed:
1. Minimum required elements only
2. Maximum cardinality testing
3. Choice element variations
4. Optional element combinations
```

---

#### `generate_test_cases(xslt_analysis, xsd_analysis)`

**Purpose**: Generate comprehensive Gherkin test scenarios based on XSLT and XSD analysis results.

**Parameters**:
- `xslt_analysis` (str): Results from XSLT analysis
- `xsd_analysis` (str): Results from XSD analysis

**Returns**: 
- `str`: Gherkin-formatted test cases with Given/When/Then structure

**Example Usage**:
```python
test_cases = llm_client.generate_test_cases(xslt_analysis, xsd_analysis)
FileManager.write_file('tests.feature', test_cases)
```

**What it generates**:
- **Feature Definitions**: High-level test categories
- **Background Steps**: Common setup for all scenarios
- **Scenario Outlines**: Parameterized tests with examples
- **Edge Case Scenarios**: Boundary and error conditions
- **Integration Tests**: Multiple elements working together

**When to use**: After completing both XSLT and XSD analysis.

**Why**: Combines understanding of transformation logic with input constraints to create comprehensive test coverage.

**Example Output**:
```gherkin
Feature: XSLT OrderCreate Transformation Testing

  Background:
    Given an XSLT transformation is available
    And the transformation uses OrderCreate_MapForce_Full.xslt
    And input XML conforms to AMA_ConnectivityLayerRQ schema

  Scenario: Transform UA target with passenger visa information
    Given input XML with target "UA"
    And passenger has visa type "V"
    And passenger has document type "P"
    When the XSLT transformation is applied
    Then the output should contain visa mapping "VVI"
    And the output should contain document mapping "VPT"

  Scenario Outline: Phone number sanitization
    Given input XML with phone number "<input_phone>"
    When the XSLT transformation is applied
    Then the output phone number should be "<expected_output>"
    
    Examples:
      | input_phone           | expected_output |
      | +1-555-123-4567      | 15551234567     |
      | (555) 123-4567       | 5551234567      |
      | 555.123.4567 ext 890 | 5551234567890   |
```

---

## File Management Tools

### Location: `src/tools/file_tools.py`

File management tools provide safe and reliable file operations with proper error handling.

### Core Functions

#### `FileManager.read_file(file_path)`

**Purpose**: Safely read file content with encoding detection and error handling.

**Parameters**:
- `file_path` (str): Absolute path to the file

**Returns**: 
- `str`: File content as string

**Raises**: 
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If path is not a file

**Example Usage**:
```python
try:
    content = FileManager.read_file('/path/to/transform.xslt')
    print(f"File size: {len(content)} characters")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error reading file: {e}")
```

**When to use**: Before any file processing operation.

**Why**: File operations can fail for many reasons. This provides consistent error handling.

**Features**:
- **Encoding Detection**: Tries UTF-8 first, falls back to Latin-1
- **Path Validation**: Ensures path exists and is a file
- **Error Handling**: Provides clear error messages

---

#### `FileManager.write_file(file_path, content, create_dirs=True)`

**Purpose**: Write content to file with automatic directory creation.

**Parameters**:
- `file_path` (str): Path where to write the file
- `content` (str): Content to write
- `create_dirs` (bool): Whether to create parent directories

**Example Usage**:
```python
test_content = "Feature: My Test..."
FileManager.write_file('./output/tests.feature', test_content)

# Without directory creation
FileManager.write_file('./existing/tests.feature', test_content, create_dirs=False)
```

**When to use**: To save generated test cases, reports, or any output.

**Why**: Ensures consistent file writing with proper directory handling.

---

#### `FileManager.validate_xslt_file(file_path)`

**Purpose**: Validate that a file is a proper XSLT transformation.

**Parameters**:
- `file_path` (str): Path to the XSLT file

**Returns**: 
- `bool`: True if valid XSLT, False otherwise

**Example Usage**:
```python
if FileManager.validate_xslt_file('transform.xslt'):
    print("Valid XSLT file")
    content = FileManager.read_file('transform.xslt')
else:
    print("Invalid XSLT file")
```

**When to use**: Before processing any XSLT file.

**Why**: Prevents processing invalid files that would cause errors later.

**Validation Checks**:
- File contains proper XML structure
- Root element is `<xsl:stylesheet>` or `<xsl:transform>`
- Uses correct XSLT namespace

---

#### `FileManager.validate_xsd_file(file_path)`

**Purpose**: Validate that a file is a proper XSD schema.

**Parameters**:
- `file_path` (str): Path to the XSD file

**Returns**: 
- `bool`: True if valid XSD, False otherwise

**Example Usage**:
```python
if FileManager.validate_xsd_file('schema.xsd'):
    print("Valid XSD file")
else:
    print("Invalid XSD file")
```

**When to use**: Before processing any XSD file.

**Validation Checks**:
- File contains proper XML structure
- Root element is `<xs:schema>`
- Uses correct XML Schema namespace

---

#### `FileManager.extract_file_info(file_path)`

**Purpose**: Extract metadata about a file for logging and reporting.

**Parameters**:
- `file_path` (str): Path to the file

**Returns**: 
- `dict`: File information including name, size, extension, etc.

**Example Usage**:
```python
info = FileManager.extract_file_info('transform.xslt')
print(f"File: {info['name']}, Size: {info['size']} bytes")
```

**When to use**: For logging, reporting, or debugging.

**Returned Information**:
```python
{
    'name': 'transform.xslt',
    'size': 15420,
    'extension': '.xslt',
    'absolute_path': '/full/path/to/transform.xslt',
    'exists': True
}
```

---

## XML Analysis Tools

### Location: `src/tools/xml_tools.py`

XML analysis tools provide structural analysis of XSLT and XSD files without using AI.

### XSLTAnalyzer Class

#### Purpose
Analyzes XSLT files to extract structural information like templates, conditions, and mappings.

#### Key Methods

##### `extract_templates()`

**Purpose**: Find all template definitions in the XSLT file.

**Returns**: 
- `List[Dict]`: List of template information

**Example Usage**:
```python
analyzer = XSLTAnalyzer(xslt_content)
templates = analyzer.extract_templates()

for template in templates:
    print(f"Template: {template['name']}, Match: {template['match']}")
```

**When to use**: To get exact count and details of transformation templates.

**Example Output**:
```python
[
    {
        'match': 'Request',
        'name': None,
        'mode': None,
        'has_conditions': True,
        'xpath_expressions': ['./TravelAgency/Name', './Context/correlationID']
    },
    {
        'match': None,
        'name': 'vmf:vmf1_inputtoresult',
        'mode': None,
        'has_conditions': True,
        'xpath_expressions': ["$input='P'", "$input='PT'"]
    }
]
```

---

##### `extract_conditional_logic()`

**Purpose**: Find all conditional statements (if, choose/when) in the XSLT.

**Returns**: 
- `List[Dict]`: List of conditional logic patterns

**Example Usage**:
```python
conditions = analyzer.extract_conditional_logic()
print(f"Found {len(conditions)} conditional blocks")
```

**When to use**: To identify business rules and decision points for testing.

**Example Output**:
```python
[
    {
        'type': 'choose',
        'conditions': ["$input='P'", "$input='PT'"],
        'has_otherwise': True
    },
    {
        'type': 'if',
        'test': './Name/Type = "Other"'
    }
]
```

---

##### `extract_value_mappings()`

**Purpose**: Find templates that perform value mapping (A becomes B transformations).

**Returns**: 
- `List[Dict]`: List of value mapping functions

**Example Usage**:
```python
mappings = analyzer.extract_value_mappings()
for mapping in mappings:
    print(f"Mapping function: {mapping['template_name']}")
```

**When to use**: To identify data transformation rules for testing.

**Example Output**:
```python
[
    {
        'template_name': 'vmf:vmf1_inputtoresult',
        'mappings': [
            {'condition': "$input='P'", 'output': 'VPT'},
            {'condition': "$input='PT'", 'output': 'VPT'}
        ]
    }
]
```

### XSDAnalyzer Class

#### Purpose
Analyzes XSD schema files to extract structural information about input data format.

#### Key Methods

##### `extract_root_elements()`

**Purpose**: Find all root-level element definitions.

**Returns**: 
- `List[Dict]`: List of root element information

**Example Usage**:
```python
analyzer = XSDAnalyzer(xsd_content)
elements = analyzer.extract_root_elements()
```

**Example Output**:
```python
[
    {
        'name': 'AMA_ConnectivityLayerRQ',
        'type': 'ConnectivityLayerBomType',
        'min_occurs': '1',
        'max_occurs': '1',
        'nillable': False
    }
]
```

---

##### `extract_complex_types()`

**Purpose**: Find all complex type definitions and their components.

**Returns**: 
- `List[Dict]`: List of complex type information

**Example Usage**:
```python
types = analyzer.extract_complex_types()
for type_info in types:
    print(f"Type: {type_info['name']}, Elements: {len(type_info['elements'])}")
```

**When to use**: To understand data structure for test data creation.

---

##### `extract_choice_elements()`

**Purpose**: Find all choice elements where you can select between options.

**Returns**: 
- `List[Dict]`: List of choice element information

**Example Usage**:
```python
choices = analyzer.extract_choice_elements()
for choice in choices:
    print(f"Choice has {len(choice['options'])} options")
```

**When to use**: To identify alternative scenarios for testing.

---

## Configuration Tools

### Location: `src/config/settings.py`

Configuration tools manage application settings and provide access to configuration data.

### Settings Class

#### `Settings.load_from_yaml(config_path=None)`

**Purpose**: Load application configuration from YAML file.

**Parameters**:
- `config_path` (Path, optional): Path to config file (defaults to config.yaml)

**Returns**: 
- `Settings`: Configured settings object

**Example Usage**:
```python
from src.config.settings import settings

# Access agent configuration
xslt_config = settings.agents.get('xslt_analyzer')
print(f"Agent role: {xslt_config.role}")

# Access LLM configuration
llm_config = settings.get_llm_config('openai')
print(f"Model: {llm_config.model}")
```

**When to use**: At application startup to load configuration.

---

#### `get_llm_config(provider=None)`

**Purpose**: Get LLM configuration for specific provider.

**Parameters**:
- `provider` (str, optional): Provider name (uses default if None)

**Returns**: 
- `LLMConfig`: Provider-specific configuration

**Example Usage**:
```python
# Get default provider config
config = settings.get_llm_config()

# Get specific provider config
anthropic_config = settings.get_llm_config('anthropic')
```

**When to use**: When initializing LLM clients or switching providers.

---

## Agent Utilities

### Agent Communication Patterns

Agents don't communicate directly. Instead, they follow this pattern:

```python
# Agent A produces results
result_a = agent_a.process_data(input_data)

# Main application collects results
all_results = {
    'agent_a_result': result_a,
    'metadata': {...}
}

# Agent B receives combined results
result_b = agent_b.process_data(all_results)
```

### Error Handling in Agents

All agents follow consistent error handling:

```python
def agent_method(self, input_data):
    try:
        # Structural analysis (fast, reliable)
        structural = self._do_structural_analysis(input_data)
        
        # AI analysis (slower, may fail)
        semantic = llm_client.analyze(input_data)
        
        return {
            'structural_analysis': structural,
            'semantic_analysis': semantic,
            'summary': self._generate_summary(structural, semantic)
        }
    except Exception as e:
        return {
            'error': f'Analysis failed: {str(e)}',
            'fallback_result': self._generate_fallback(input_data)
        }
```

### Agent Configuration

Each agent reads its configuration from `config.yaml`:

```python
def __init__(self):
    agent_config = settings.agents.get('agent_name')
    
    self.agent = Agent(
        role=agent_config.role,
        goal=agent_config.goal,
        backstory="Detailed backstory...",
        verbose=agent_config.verbose,
        max_retries=agent_config.max_retries,
        allow_delegation=False  # Agents work independently
    )
```

---

## Best Practices

### 1. Error Handling

**Always use try-catch blocks for operations that can fail:**

```python
# Good
try:
    result = risky_operation()
    return {'success': result}
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return {'error': str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {'error': f'Unexpected error: {str(e)}'}

# Bad
result = risky_operation()  # May crash the application
return result
```

### 2. Input Validation

**Always validate inputs before processing:**

```python
# Good
def process_file(file_path):
    if not file_path:
        raise ValueError("File path is required")
    
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not FileManager.validate_xslt_file(file_path):
        raise ValueError(f"Invalid XSLT file: {file_path}")
    
    # Process the file...

# Bad
def process_file(file_path):
    content = open(file_path).read()  # May fail silently
    # Process without validation...
```

### 3. Configuration Management

**Use configuration for all settings:**

```python
# Good
temperature = settings.get_llm_config().temperature
max_tokens = settings.get_llm_config().max_tokens

# Bad
temperature = 0.3  # Hard-coded value
max_tokens = 4000  # Hard-coded value
```

### 4. Logging and Debugging

**Provide detailed logging for debugging:**

```python
# Good
def analyze_xslt(self, content):
    logger.info(f"Starting XSLT analysis, content length: {len(content)}")
    
    try:
        result = self._do_analysis(content)
        logger.info(f"Analysis completed, found {len(result['templates'])} templates")
        return result
    except Exception as e:
        logger.error(f"XSLT analysis failed: {e}")
        raise

# Bad
def analyze_xslt(self, content):
    return self._do_analysis(content)  # No logging
```

### 5. Resource Management

**Clean up resources properly:**

```python
# Good
def process_large_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        # File automatically closed
        return process_content(content)
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        raise

# Bad
def process_large_file(file_path):
    f = open(file_path, 'r')  # File may not be closed
    content = f.read()
    return process_content(content)
```

### 6. Function Design

**Keep functions focused and testable:**

```python
# Good - Single responsibility
def extract_templates(self, xslt_doc):
    """Extract template information from XSLT document."""
    templates = []
    template_elements = xslt_doc.xpath('//xsl:template', namespaces=self.namespaces)
    
    for template in template_elements:
        template_info = self._parse_template_element(template)
        templates.append(template_info)
    
    return templates

def _parse_template_element(self, template):
    """Parse a single template element."""
    return {
        'match': template.get('match'),
        'name': template.get('name'),
        'mode': template.get('mode')
    }

# Bad - Multiple responsibilities
def extract_and_analyze_templates(self, xslt_content):
    """Extract templates and analyze them and generate report."""
    # Parse XSLT
    # Extract templates
    # Analyze templates
    # Generate report
    # Write to file
    pass  # Too many responsibilities
```

This comprehensive reference should help beginners understand how to use each tool effectively and follow best practices when extending the system.