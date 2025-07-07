# Agentic XSLT Test Generator - Complete Workflow Guide

## Overview

This document explains how the agentic XSLT test generator system works, from file upload to test case generation. The system uses multiple specialized AI agents working together to analyze XSLT transformations and automatically generate comprehensive test cases.

## System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Orchestrator    │───▶│   File Analyzer │
│ (XSLT + Schemas)│    │     Agent        │    │     Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Memory Management│◀───│   Error Recovery │───▶│ Schema Mapper   │
│     Agent       │    │      Agent       │    │     Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Business Logic   │◀───│  Pattern Hunter  │───▶│ Test Case       │
│Extractor Agent  │    │     Agent        │    │Generator Agent  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Cross-Reference  │◀───│    Streamlit     │───▶│   Generated     │
│Validator Agent  │    │       UI         │    │  Test Cases     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Complete Workflow Process

### Phase 1: User Interaction & File Processing

#### Step 1: File Upload (Streamlit UI)
```
User uploads through Streamlit interface:
├── XSLT transformation file (e.g., OrderCreate_MapForce_Full.xslt)
├── Input XSD schema (e.g., AMA_ConnectivityLayerRQ.xsd)
└── Output XSD schema (e.g., OrderCreateRS.xsd)
```

**What happens:**
- Files are validated for correct format and structure
- Temporary workspace is created for analysis
- File dependencies are automatically detected
- Memory usage baseline is established

#### Step 2: Orchestrator Planning
```
Orchestrator Agent creates analysis plan:
├── Determines optimal chunking strategy based on file size
├── Allocates memory resources for each agent
├── Creates workflow execution schedule
└── Sets up error recovery checkpoints
```

**Memory Management:**
- Monitors available system memory (target: <1GB total usage)
- Plans chunk sizes (15K-20K tokens each)
- Sets up context compression strategies
- Establishes disk spillover thresholds

### Phase 2: File Analysis & Chunking

#### Step 3: File Analyzer Agent Processing
```
File Analyzer performs initial assessment:
├── Detects file type and encoding
├── Identifies XSLT template boundaries
├── Maps file dependencies and imports
├── Counts elements (templates, variables, choose blocks)
└── Creates initial file metadata
```

**Chunking Process:**
```python
# Example chunking logic
chunks = [
    {
        "id": "chunk_1",
        "type": "helper_template", 
        "name": "vmf:vmf1_inputtoresult",
        "lines": "12-25",
        "tokens": 150,
        "dependencies": ["input_param"]
    },
    {
        "id": "chunk_2",
        "type": "main_template_section",
        "name": "passenger_processing", 
        "lines": "249-767",
        "tokens": 18500,
        "dependencies": ["TTR_ActorType", "contact_data"]
    }
]
```

#### Step 4: Schema Mapper Agent Processing
```
Schema Mapper analyzes XSD files:
├── Parses input schema structure (AMA_ConnectivityLayerRQ.xsd)
├── Extracts complex types (TTR_ActorType, ContactType, etc.)
├── Maps element relationships and constraints
├── Parses output schema structure (OrderCreateRS.xsd)
└── Creates schema-to-XSLT mapping
```

**Schema Analysis Output:**
```json
{
  "input_schema": {
    "complex_types": [
      {
        "name": "TTR_ActorType",
        "elements": ["PassengerType", "ContactInfo", "DocumentInfo"],
        "constraints": {"minOccurs": 1, "maxOccurs": "unbounded"}
      }
    ],
    "root_elements": ["ConnectivityLayerRQ"]
  },
  "mappings": [
    {
      "input_xpath": "//TTR_ActorType/PassengerType",
      "xslt_template": "passenger_processing",
      "output_element": "Passenger"
    }
  ]
}
```

### Phase 3: Deep Analysis & Pattern Recognition

#### Step 5: Business Logic Extractor Agent
```
Business Logic Extractor processes chunks sequentially:
├── Analyzes helper templates (vmf:vmf1, vmf:vmf2, etc.)
├── Extracts transformation rules from main template
├── Identifies conditional logic patterns
├── Maps input→output transformations
└── Catalogs business rules with context
```

**Progressive Analysis with Memory Management:**
```python
for chunk in chunks:
    # Load relevant context from previous chunks
    context = context_manager.get_relevant_context(chunk.id)
    
    # Compress context if memory usage > 70%
    if memory_monitor.get_usage_ratio() > 0.7:
        context = context_compressor.compress(context)
    
    # Analyze chunk with LLM
    analysis = llm_analyzer.analyze_chunk(chunk, context)
    
    # Store results and update context
    context_manager.store_analysis(chunk.id, analysis)
    
    # Cleanup old context if needed
    memory_manager.cleanup_if_needed()
```

**Extracted Business Rules Example:**
```json
{
  "helper_templates": [
    {
      "template": "vmf:vmf1_inputtoresult",
      "purpose": "Document type code transformation",
      "rules": [
        {"input": "P", "output": "VPT", "description": "Passport to VPT code"},
        {"input": "PT", "output": "VPT", "description": "Passport variant to VPT"},
        {"input": "*", "output": "", "description": "Default empty for unknown types"}
      ]
    }
  ],
  "main_template_rules": [
    {
      "section": "passenger_processing",
      "rule": "target_specific_processing",
      "conditions": [
        {"target": "UA", "processing": "enhanced_validation"},
        {"target": "UAD", "processing": "complex_transformation"}
      ]
    }
  ]
}
```

#### Step 6: Pattern Hunter Agent
```
Pattern Hunter identifies recurring patterns:
├── String manipulation patterns (address concatenation)
├── Conditional processing patterns (target-specific logic)
├── Data validation patterns (input sanitization)
├── Error handling patterns (fallback values)
└── Loop and iteration patterns (passenger lists)
```

**Pattern Catalog Example:**
```json
{
  "patterns": [
    {
      "type": "string_manipulation",
      "pattern": "address_concatenation",
      "occurrences": 15,
      "template": "concat($address1, ' ', $address2)",
      "test_scenarios": ["normal_address", "missing_address2", "special_characters"]
    },
    {
      "type": "conditional_processing", 
      "pattern": "target_specific_branching",
      "occurrences": 8,
      "template": "choose_when_target_equals",
      "test_scenarios": ["UA_target", "UAD_target", "unknown_target"]
    }
  ]
}
```

### Phase 4: Test Case Generation

#### Step 7: Test Case Generator Agent
```
Test Case Generator creates comprehensive test scenarios:
├── Generates test cases for each business rule
├── Creates edge cases and boundary conditions
├── Produces XML input/output samples
├── Generates parameterized test scenarios
└── Validates test coverage against patterns
```

**Test Case Generation Process:**
```python
# Generate test cases from business rules
test_cases = []

for rule in business_rules:
    # Generate positive test cases
    positive_tests = generate_positive_tests(rule)
    
    # Generate negative/edge test cases
    edge_tests = generate_edge_cases(rule)
    
    # Create XML input samples
    for test in positive_tests + edge_tests:
        xml_input = create_xml_input(test, input_schema)
        expected_output = create_expected_output(test, output_schema)
        
        test_cases.append({
            "name": test.name,
            "input_xml": xml_input,
            "expected_output": expected_output,
            "test_type": test.type,
            "business_rule": rule.id
        })
```

**Generated Test Cases Example:**
```python
# Generated pytest test file
import pytest
import lxml.etree as ET

class TestHelperTemplates:
    
    @pytest.fixture
    def xslt_transformer(self):
        """Load XSLT transformation"""
        xslt_path = "OrderCreate_MapForce_Full.xslt"
        with open(xslt_path) as f:
            xslt_doc = ET.parse(f)
        return ET.XSLT(xslt_doc)
    
    @pytest.mark.parametrize("input_type,expected", [
        ("P", "VPT"),
        ("PT", "VPT"), 
        ("V", "VVI"),
        ("INVALID", ""),
        ("", "")
    ])
    def test_vmf1_document_type_transformation(self, xslt_transformer, input_type, expected):
        """Test vmf:vmf1 helper template document type transformations"""
        input_xml = f"""
        <ConnectivityLayerRQ>
            <ActorInfo>
                <DocumentType>{input_type}</DocumentType>
            </ActorInfo>
        </ConnectivityLayerRQ>
        """
        
        input_doc = ET.fromstring(input_xml)
        result = xslt_transformer(input_doc)
        
        # Extract document code from result
        doc_code = result.xpath("//DocumentCode/text()")
        assert doc_code[0] if doc_code else "" == expected
    
    def test_passenger_processing_ua_target(self, xslt_transformer):
        """Test UA target-specific passenger processing"""
        input_xml = """
        <ConnectivityLayerRQ target="UA">
            <ActorInfo>
                <PassengerType>ADT</PassengerType>
                <ContactInfo>
                    <Phone>+1-555-1234</Phone>
                    <Email>test@example.com</Email>
                </ContactInfo>
            </ActorInfo>
        </ConnectivityLayerRQ>
        """
        
        input_doc = ET.fromstring(input_xml)
        result = xslt_transformer(input_doc)
        
        # Verify UA-specific processing occurred
        passengers = result.xpath("//Passenger")
        assert len(passengers) == 1
        assert passengers[0].get("enhanced_validation") == "true"
```

#### Step 8: Cross-Reference Validator Agent
```
Cross-Reference Validator ensures quality:
├── Validates XPath expressions against input schema
├── Checks generated XML against output schema
├── Verifies business rule consistency
├── Tests generated test cases for execution
└── Ensures comprehensive coverage
```

**Validation Process:**
```python
validation_results = {
    "xpath_validation": {
        "total_expressions": 247,
        "valid_expressions": 245,
        "invalid_expressions": 2,
        "validation_rate": 99.2
    },
    "schema_compliance": {
        "generated_xml_samples": 132,
        "schema_valid_samples": 132,
        "compliance_rate": 100.0
    },
    "test_execution": {
        "generated_tests": 89,
        "executable_tests": 87,
        "execution_rate": 97.8
    }
}
```

### Phase 5: Final Processing & Output

#### Step 9: Context Aggregation & Reporting
```
Orchestrator aggregates all analysis results:
├── Combines business rules from all agents
├── Merges pattern libraries and test cases
├── Creates comprehensive analysis report
├── Generates execution statistics
└── Prepares downloadable artifacts
```

#### Step 10: Streamlit UI Output
```
User receives through Streamlit interface:
├── Analysis summary dashboard
├── Business rules catalog (JSON/HTML)
├── Generated test cases (Python/pytest files)
├── Coverage analysis report
├── Performance metrics
└── Downloadable ZIP package
```

## Memory Management Throughout Workflow

### Real-Time Memory Monitoring
```python
class WorkflowMemoryManager:
    def monitor_throughout_workflow(self):
        """Continuous memory monitoring during workflow"""
        checkpoints = [
            "file_upload", "chunking", "schema_analysis", 
            "business_extraction", "pattern_recognition", 
            "test_generation", "validation"
        ]
        
        for checkpoint in checkpoints:
            memory_usage = self.get_current_usage()
            
            if memory_usage > self.warning_threshold:
                self.trigger_cleanup()
                
            if memory_usage > self.critical_threshold:
                self.trigger_emergency_fallback()
            
            self.log_checkpoint(checkpoint, memory_usage)
```

### Adaptive Processing
- **Chunk size adjusts** based on available memory
- **Context compression** increases as memory fills
- **Disk spillover** for old analysis results
- **Graceful degradation** if memory limits approached

## Error Handling & Recovery

### Error Scenarios & Recovery
```python
error_recovery_strategies = {
    "llm_api_failure": {
        "strategy": "exponential_backoff_retry",
        "max_retries": 3,
        "fallback": "cached_analysis_patterns"
    },
    "memory_exhaustion": {
        "strategy": "emergency_context_cleanup",
        "actions": ["compress_all_contexts", "spill_to_disk"],
        "fallback": "reduced_analysis_depth"
    },
    "file_parsing_error": {
        "strategy": "alternative_parser",
        "fallback": "manual_chunk_boundaries"
    },
    "schema_validation_failure": {
        "strategy": "relaxed_validation",
        "fallback": "best_effort_generation"
    }
}
```

## Performance Characteristics

### Expected Performance Metrics
```
File Size: 10,000 lines XSLT
├── Total Processing Time: ~15-20 minutes
├── Memory Usage: 800MB peak
├── Generated Test Cases: 80-120 test cases
├── Business Rules Extracted: 45-60 rules
└── Test Coverage: >90% of transformation logic

Large File: 50,000 lines XSLT  
├── Total Processing Time: ~45-60 minutes
├── Memory Usage: 950MB peak (with spillover)
├── Generated Test Cases: 200-300 test cases
├── Business Rules Extracted: 150-200 rules
└── Test Coverage: >85% of transformation logic
```

### Quality Assurance Metrics
- **Analysis Accuracy**: >95% compared to manual analysis
- **Test Execution Success**: >98% of generated tests pass
- **Schema Compliance**: 100% of generated XML validates
- **Memory Efficiency**: <1GB total usage regardless of file size

## User Experience Flow

### Streamlit Interface Journey
```
1. Upload Files Tab
   ├── Drag & drop XSLT file
   ├── Upload input XSD schema  
   ├── Upload output XSD schema
   └── Click "Start Analysis"

2. Progress Monitoring
   ├── Real-time progress bar
   ├── Current phase indicator
   ├── Memory usage display
   ├── Estimated time remaining
   └── Agent activity log

3. Results Dashboard
   ├── Analysis Summary
   ├── Business Rules Catalog
   ├── Generated Test Cases Preview
   ├── Coverage Analysis
   └── Download Options

4. Download Artifacts
   ├── Complete test suite (Python files)
   ├── Business rules documentation
   ├── Analysis report (PDF/HTML)
   ├── Coverage metrics
   └── Raw analysis data (JSON)
```

## Integration with Existing XML Wizard

The agentic XSLT test generator integrates seamlessly with the existing XML Wizard application:

```
XML Wizard Tabs:
├── XML Generation (existing)
├── XSLT Test Generation (new agentic system)
└── Schema Analysis (shared components)
```

**Shared Components:**
- File upload mechanisms
- XSD parsing utilities  
- XML validation tools
- Progress tracking UI
- Download functionality

## Success Criteria Validation

### Automated Quality Checks
```python
def validate_workflow_success(results):
    """Validate that workflow met success criteria"""
    checks = {
        "business_rules_extracted": len(results.business_rules) >= 40,
        "test_cases_generated": len(results.test_cases) >= 80, 
        "memory_usage_ok": results.peak_memory < 1024 * 1024 * 1024,  # 1GB
        "processing_time_ok": results.total_time < 1800,  # 30 minutes
        "test_execution_rate": results.executable_tests / results.total_tests > 0.95
    }
    
    return all(checks.values()), checks
```

This comprehensive workflow ensures that the agentic XSLT test generator delivers high-quality, executable test cases while maintaining efficient memory usage and providing a smooth user experience through the Streamlit interface.