# XSLT Test Generator - Architecture Guide for Beginners

## Table of Contents
1. [What is XSLT Test Generator?](#what-is-xslt-test-generator)
2. [High-Level Overview](#high-level-overview)
3. [Agent Architecture](#agent-architecture)
4. [Tools and Functions](#tools-and-functions)
5. [Data Flow](#data-flow)
6. [File Structure Explained](#file-structure-explained)
7. [How to Read the Code](#how-to-read-the-code)

## What is XSLT Test Generator?

### The Problem We're Solving
Imagine you have a complex recipe (XSLT file) that transforms one type of data into another. To make sure this recipe works correctly, you need to test it with different ingredients (input data) and verify the output is correct. Manually creating these tests is time-consuming and error-prone.

### Our Solution
The XSLT Test Generator is like having an AI chef that:
1. **Reads your recipe** (XSLT transformation file)
2. **Understands the ingredients** (XSD schema - what input data looks like)
3. **Automatically creates test scenarios** (Gherkin test cases)

### Key Technologies Used
- **CrewAI**: Framework for creating AI agents that work together
- **LiteLLM**: Tool to use different AI models (GPT, Claude, etc.) with one interface
- **LXML**: Python library for reading and processing XML files
- **Typer**: Tool for creating command-line interfaces
- **Rich**: Tool for beautiful terminal output

## High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XSLT File     │    │   XSD Schema    │    │  User Command   │
│ (transformation)│    │ (input format)  │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    MAIN APPLICATION      │
                    │  (orchestrates agents)   │
                    └─────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
   ┌────▼─────┐         ┌───────▼────────┐      ┌───────▼──────┐
   │  XSLT    │         │   XSD Schema   │      │ Test Case    │
   │ Analyzer │         │   Analyzer     │      │ Generator    │
   │ Agent    │         │   Agent        │      │ Agent        │
   └────┬─────┘         └───────┬────────┘      └───────┬──────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Generated Tests    │
                    │ (Gherkin scenarios)  │
                    └──────────────────────┘
```

## Agent Architecture

Think of agents as specialized workers in a team. Each agent has specific skills and responsibilities.

### 1. XSLT Analyzer Agent (`src/agents/xslt_analyzer.py`)

**What it does**: Like a detective that examines XSLT files to understand transformation logic.

**Responsibilities**:
- Finds all templates (transformation rules)
- Identifies conditional logic (if-then statements)
- Discovers value mappings (A becomes B rules)
- Analyzes XPath expressions (data selection rules)

**When to use**: Always run first when you have an XSLT file to analyze.

**Tools it uses**:
- `XSLTAnalyzer` class for structural analysis
- `llm_client.analyze_xslt()` for semantic understanding

### 2. XSD Schema Analyzer Agent (`src/agents/xsd_analyzer.py`)

**What it does**: Like a blueprint reader that understands the structure of input data.

**Responsibilities**:
- Identifies required vs optional elements
- Finds choice elements (either A or B)
- Analyzes data constraints and rules
- Maps potential test scenarios

**When to use**: Run to understand what valid input data looks like.

**Tools it uses**:
- `XSDAnalyzer` class for schema parsing
- `llm_client.analyze_xsd()` for semantic understanding

### 3. Test Case Generator Agent (`src/agents/test_case_generator.py`)

**What it does**: Like a test planner that creates comprehensive test scenarios.

**Responsibilities**:
- Combines XSLT and XSD analysis results
- Generates Gherkin test cases (Given/When/Then format)
- Creates coverage reports
- Prioritizes test scenarios

**When to use**: Run last, after both analyses are complete.

**Tools it uses**:
- `llm_client.generate_test_cases()` for test generation
- Internal analysis methods for coverage calculation

## Tools and Functions

### 1. LLM Client (`src/tools/llm_client.py`)

**Purpose**: Provides a unified way to talk to different AI models.

```python
class LLMClient:
    def __init__(self, provider="openai"):
        # Initialize with specific AI provider
    
    def analyze_xslt(self, xslt_content):
        # Analyzes XSLT using AI - returns insights about transformation logic
    
    def analyze_xsd(self, xsd_content):
        # Analyzes XSD using AI - returns insights about data structure
    
    def generate_test_cases(self, xslt_analysis, xsd_analysis):
        # Creates test cases using AI - returns Gherkin scenarios
```

**When to use each function**:
- `analyze_xslt()`: When you need to understand what an XSLT transformation does
- `analyze_xsd()`: When you need to understand input data structure
- `generate_test_cases()`: When you want to create test scenarios

**Why we need this**: Different AI models (GPT, Claude) have different interfaces. This tool makes them all work the same way.

### 2. File Manager (`src/tools/file_tools.py`)

**Purpose**: Handles all file operations safely.

```python
class FileManager:
    @staticmethod
    def read_file(file_path):
        # Safely reads any file with error handling
    
    @staticmethod
    def write_file(file_path, content, create_dirs=True):
        # Writes content to file, creates directories if needed
    
    @staticmethod
    def validate_xslt_file(file_path):
        # Checks if file is a valid XSLT transformation
    
    @staticmethod
    def validate_xsd_file(file_path):
        # Checks if file is a valid XSD schema
```

**When to use each function**:
- `read_file()`: Before processing any input file
- `write_file()`: When saving generated test cases or reports
- `validate_xslt_file()`: Before analyzing XSLT to ensure it's valid
- `validate_xsd_file()`: Before analyzing XSD to ensure it's valid

**Why we need this**: File operations can fail (file not found, permission errors). This tool handles errors gracefully.

### 3. XML Analysis Tools (`src/tools/xml_tools.py`)

**Purpose**: Provides detailed analysis of XML-based files without AI.

#### XSLTAnalyzer Class
```python
class XSLTAnalyzer:
    def extract_templates():
        # Finds all <xsl:template> elements and their properties
    
    def extract_conditional_logic():
        # Finds <xsl:choose>, <xsl:when>, <xsl:if> statements
    
    def extract_value_mappings():
        # Finds templates that map input values to output values
```

**When to use**:
- Use before AI analysis to get structured data
- When you need exact counts (number of templates, conditions)
- For validation of AI analysis results

#### XSDAnalyzer Class
```python
class XSDAnalyzer:
    def extract_root_elements():
        # Finds main elements that can appear in XML
    
    def extract_complex_types():
        # Finds complex data structures and their components
    
    def extract_choice_elements():
        # Finds elements where you can choose between options
```

**When to use**:
- Before AI analysis to understand schema structure
- When you need to know data constraints (required/optional)
- For generating test data requirements

### 4. Configuration Management (`src/config/settings.py`)

**Purpose**: Manages all application settings in one place.

```python
class Settings:
    def load_from_yaml():
        # Loads configuration from config.yaml file
    
    def get_llm_config(provider):
        # Gets settings for specific AI provider
```

**Key configurations**:
- **API Keys**: Stored in `.env` file for security
- **Agent Settings**: Behavior and retry policies
- **LLM Settings**: Which models to use, temperature, token limits
- **Output Settings**: File formats and locations

**Why we need this**: Keeps all settings organized and allows easy changes without modifying code.

## Data Flow

Here's how data flows through the system:

### Step 1: Input Validation
```
User provides XSLT + XSD files
         ↓
FileManager validates files
         ↓
Files are read into memory
```

### Step 2: Structural Analysis
```
XSLT content → XSLTAnalyzer → Templates, conditions, mappings
XSD content → XSDAnalyzer → Elements, types, constraints
```

### Step 3: AI Analysis
```
XSLT content → LLMClient.analyze_xslt() → Semantic insights
XSD content → LLMClient.analyze_xsd() → Schema insights
```

### Step 4: Test Generation
```
All analysis results → LLMClient.generate_test_cases() → Gherkin tests
```

### Step 5: Output Creation
```
Generated tests → FileManager.write_file() → Output files
Analysis reports → FileManager.write_file() → Documentation
```

## File Structure Explained

```
xslt_test_generator/
├── src/                           # All source code
│   ├── agents/                    # AI agents (workers)
│   │   ├── xslt_analyzer.py      # Analyzes XSLT transformations
│   │   ├── xsd_analyzer.py       # Analyzes XSD schemas
│   │   └── test_case_generator.py # Generates test cases
│   ├── tools/                     # Utility functions
│   │   ├── llm_client.py         # AI model interface
│   │   ├── file_tools.py         # File operations
│   │   └── xml_tools.py          # XML parsing utilities
│   ├── config/                    # Configuration management
│   │   └── settings.py           # Application settings
│   └── main.py                    # Main application entry point
├── config.yaml                   # Application configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── examples/                     # Usage examples
    └── run_example.py            # Example script
```

### Key Files Explained

#### `main.py` - The Orchestra Conductor
This file coordinates everything:
1. Validates input files
2. Creates and manages agents
3. Handles progress display
4. Writes output files
5. Provides command-line interface

#### `config.yaml` - The Settings File
Contains all configuration:
- Which AI models to use
- Agent behavior settings
- Output format preferences
- Evaluation parameters

#### `.env` - The Secrets File
Contains sensitive information:
- API keys for AI services
- Database passwords (if any)
- Other secrets

## How to Read the Code

### For Beginners: Start Here

1. **Begin with `main.py`**: Understand the overall flow
2. **Read `config/settings.py`**: See how configuration works
3. **Examine `tools/file_tools.py`**: Simple file operations
4. **Study `tools/llm_client.py`**: AI interaction patterns
5. **Analyze `agents/`**: Specialized AI workers

### Reading Strategy

#### When reading any file:
1. **Start with imports**: What libraries does this use?
2. **Find the main class**: What is the core functionality?
3. **Read method signatures**: What inputs/outputs are expected?
4. **Read docstrings**: What does each function do?
5. **Trace data flow**: How does data move through the code?

#### Example: Reading `llm_client.py`
```python
# 1. Imports tell us this uses LiteLLM for AI calls
import litellm

# 2. Main class - handles AI interactions
class LLMClient:
    
    # 3. Constructor - sets up the AI provider
    def __init__(self, provider: str = None):
        
    # 4. Core method - talks to AI about XSLT
    def analyze_xslt(self, xslt_content: str) -> str:
        # Method signature tells us:
        # Input: XSLT file content as string
        # Output: Analysis results as string
```

### Understanding Error Handling

The code uses try-catch blocks to handle errors gracefully:

```python
try:
    # Attempt the operation
    result = risky_operation()
except Exception as e:
    # Handle the error
    return f"Operation failed: {str(e)}"
```

**Why this matters**: File operations, AI calls, and XML parsing can fail. Good error handling keeps the application running.

### Understanding Agent Communication

Agents don't directly talk to each other. Instead:
1. Agent A produces results
2. Main application collects results
3. Main application passes results to Agent B

This pattern makes the system modular and testable.

## Common Patterns in the Code

### 1. Configuration Pattern
```python
# Get settings from config file
config = settings.agents.get('agent_name')

# Use settings to configure behavior
agent = Agent(
    role=config.role,
    goal=config.goal,
    verbose=config.verbose
)
```

### 2. Error Handling Pattern
```python
try:
    result = operation()
    return {'success': result}
except Exception as e:
    return {'error': f'Operation failed: {str(e)}'}
```

### 3. Analysis Pattern
```python
# Structural analysis (fast, exact)
structural = parse_xml_structure(content)

# Semantic analysis (slow, intelligent)
semantic = llm_client.analyze(content)

# Combined result
return {
    'structural': structural,
    'semantic': semantic,
    'summary': generate_summary(structural, semantic)
}
```

This architecture makes the XSLT Test Generator modular, maintainable, and extensible. Each component has a clear purpose and well-defined interfaces.