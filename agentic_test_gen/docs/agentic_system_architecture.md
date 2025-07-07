# Agentic XSLT Test Case Generation System Architecture

## Project Overview

This document outlines the architecture for an agentic system that automatically analyzes XSLT transformations and generates comprehensive test cases. The system is inspired by manual analysis that successfully generated 132+ test cases from analyzing OrderCreate_MapForce_Full.xslt.

## Manual Analysis Insights

Based on the manual analysis documented in `inspiration_docs/`, the following key insights guide our agentic design:

### Manual Analysis Methodology
- **Progressive Depth Analysis**: Started with file overview, then structural analysis, then deep dive into business logic
- **Pattern Recognition**: Identified 8 major business logic patterns and 45+ specific business rules
- **Cross-Reference Validation**: Verified XSLT XPath expressions against input/output schemas
- **Comprehensive Test Generation**: Created 132 test cases across 10 categories with XML input/output samples

### Success Factors
- **Systematic Approach**: Grep + focused read combinations for type discovery
- **Context Switching**: Efficiently moved between related files while maintaining context
- **Business Logic Extraction**: Extracted implicit business rules from complex conditional logic
- **Schema Relationship Mapping**: Connected transformations to schema structures

## Agentic System Architecture

### Core Agent Types

#### 1. File Analyzer Agent
**Purpose**: Initial file assessment and structural analysis
**Role**: Entry point for understanding file types, dependencies, and overall structure

**Tools & Functions**:
- `read_file_lines(file_path, start_line, end_line)` - Progressive file reading with line ranges
- `detect_file_type(file_path)` - Identify XSLT, XSD, XML, or other file types
- `extract_file_metadata(file_path)` - Get file size, encoding, namespaces, generator info
- `identify_dependencies(file_path)` - Find xsl:include, xsl:import, xs:include, xs:import
- `create_file_summary(file_path)` - Generate structural overview and initial assessment
- `count_file_elements(file_path)` - Count templates, variables, choose blocks, etc.

**Input**: File paths to analyze
**Output**: File metadata, dependency map, structural summary

#### 2. Schema Mapper Agent
**Purpose**: Map relationships between input/output schemas and extract type definitions
**Role**: Understand data structures and element relationships across schemas

**Tools & Functions**:
- `parse_xsd_structure(xsd_path)` - Extract complete type definitions and element hierarchy
- `map_element_relationships(input_schema, output_schema)` - Cross-reference element mappings
- `identify_complex_types(schema_path)` - Find business object definitions (TTR_ActorType, etc.)
- `extract_type_constraints(schema_path)` - Get minOccurs, maxOccurs, patterns, restrictions
- `build_schema_dependency_graph(schema_paths)` - Create complete dependency visualization
- `find_element_by_name(schema_path, element_name)` - Locate specific elements and their definitions
- `extract_business_documentation(schema_path)` - Parse xs:documentation and comments

**Input**: XSD schema file paths
**Output**: Schema structure maps, type definitions, element relationships, constraints

#### 3. Business Logic Extractor Agent
**Purpose**: Extract business rules and transformation logic from XSLT files
**Role**: Core agent for understanding what the transformation actually does

**Tools & Functions**:
- `extract_template_logic(xslt_path, template_name)` - Analyze specific named templates
- `identify_conditional_patterns(xslt_path)` - Find all xsl:choose, xsl:when, xsl:if structures
- `extract_variable_mappings(xslt_path)` - Map input XPath expressions to output elements
- `find_business_constants(xslt_path)` - Identify hardcoded values, defaults, and literals
- `analyze_target_specific_logic(xslt_path)` - Find conditional processing (UA/UAD targets)
- `extract_helper_template_logic(xslt_path)` - Analyze vmf:vmf1-4 type helper functions
- `map_xpath_to_business_rules(xslt_path)` - Convert XPath conditions to business rule descriptions
- `identify_data_transformations(xslt_path)` - Find concat, substring, normalize-space operations

**Input**: XSLT file paths, template names
**Output**: Business rules catalog, transformation mappings, conditional logic patterns

#### 4. Pattern Hunter Agent
**Purpose**: Identify recurring patterns and logic structures across transformations
**Role**: Recognize common transformation patterns for systematic test generation

**Tools & Functions**:
- `search_pattern_occurrences(xslt_path, pattern_type)` - Find repeated logic patterns
- `identify_string_manipulation_patterns(xslt_path)` - Find address concatenation, phone sanitization
- `find_conditional_processing_patterns(xslt_path)` - Identify business rule pattern types
- `analyze_data_validation_patterns(xslt_path)` - Find input validation and sanitization
- `extract_error_handling_patterns(xslt_path)` - Identify fallback and default value logic
- `categorize_transformation_patterns(xslt_path)` - Group similar transformation types
- `identify_loop_and_iteration_patterns(xslt_path)` - Find xsl:for-each and template recursion
- `map_pattern_to_test_categories(patterns)` - Associate patterns with test case categories

**Input**: XSLT transformations, identified business rules
**Output**: Pattern catalog, transformation categories, test case groupings

#### 5. Test Case Generator Agent
**Purpose**: Create comprehensive test cases from business rules and patterns
**Role**: Generate actual test scenarios with input/output XML samples

**Tools & Functions**:
- `generate_test_cases_from_rules(business_rules, patterns)` - Create test scenarios
- `create_xml_input_samples(test_case, input_schema)` - Generate valid input XML
- `create_xml_output_samples(test_case, output_schema)` - Generate expected output XML
- `categorize_test_cases(test_cases)` - Group by business logic type (helper templates, etc.)
- `generate_edge_case_tests(business_rules)` - Create boundary, error, and negative tests
- `create_multi_scenario_tests(business_rules)` - Generate complex multi-passenger scenarios
- `generate_target_specific_tests(business_rules)` - Create UA/UAD target-specific tests
- `validate_test_case_coverage(test_cases, business_rules)` - Ensure comprehensive coverage

**Input**: Business rules, transformation patterns, schema definitions
**Output**: Complete test case catalog with XML samples, categorized by business logic

#### 6. Cross-Reference Validator Agent
**Purpose**: Validate relationships between files and ensure consistency
**Role**: Quality assurance for generated test cases and business rule accuracy

**Tools & Functions**:
- `validate_xpath_expressions(xslt_path, input_schema)` - Verify XPath validity against schema
- `check_schema_compliance(xml_sample, schema_path)` - Validate XML against XSD
- `verify_transformation_logic(input_xml, xslt_path, expected_output)` - End-to-end validation
- `identify_missing_mappings(input_schema, xslt_path, output_schema)` - Find transformation gaps
- `validate_business_rule_consistency(rules_list)` - Check for conflicting rules
- `cross_reference_test_cases(test_cases, business_rules)` - Ensure test case accuracy
- `validate_helper_template_logic(xslt_path, test_cases)` - Verify helper template test cases
- `check_transformation_completeness(analysis_results)` - Identify missing analysis areas

**Input**: All agent outputs, schemas, XSLT files, generated test cases
**Output**: Validation reports, error identification, coverage analysis

#### 7. Memory Management Agent
**Purpose**: Manage memory usage, context compression, and resource optimization
**Role**: Ensure efficient memory usage and prevent resource exhaustion

**Tools & Functions**:
- `monitor_memory_usage()` - Real-time memory monitoring with alerts
- `compress_context(context_data)` - Intelligent context compression
- `manage_context_cache(cache_operations)` - Cache management and cleanup
- `detect_memory_leaks()` - Memory leak detection and prevention
- `trigger_cleanup_strategies(memory_pressure)` - Emergency cleanup when needed
- `optimize_chunk_sizes(performance_metrics)` - Adaptive chunk sizing
- `manage_disk_spillover(context_data)` - Spill old context to disk
- `validate_memory_integrity()` - Ensure context data integrity

**Input**: Memory usage metrics, context data, performance requirements
**Output**: Memory optimization reports, context compression metrics, cleanup actions

#### 8. Error Recovery Agent
**Purpose**: Handle errors, implement fallback strategies, and ensure system resilience
**Role**: Maintain system stability and recover from various failure scenarios

**Tools & Functions**:
- `detect_error_conditions(system_state)` - Identify error conditions and types
- `implement_fallback_strategies(error_type)` - Execute appropriate recovery strategies
- `retry_failed_operations(operation_context)` - Retry operations with backoff
- `validate_recovery_success(recovery_metrics)` - Verify recovery effectiveness
- `log_error_patterns(error_history)` - Track and analyze error patterns
- `optimize_error_handling(performance_data)` - Improve error handling efficiency
- `graceful_degradation(system_limits)` - Reduce functionality when needed
- `system_health_monitoring(health_metrics)` - Monitor overall system health

**Input**: Error conditions, system state, recovery requirements
**Output**: Error recovery reports, fallback strategy execution, system health metrics

#### 9. Orchestrator Agent
**Purpose**: Coordinate workflow and manage agent interactions
**Role**: Master coordinator that manages the entire analysis and generation process

**Tools & Functions**:
- `create_analysis_plan(file_paths, analysis_goals)` - Design multi-phase analysis workflow
- `coordinate_agent_workflow(agents, tasks)` - Manage agent execution and dependencies
- `aggregate_analysis_results(agent_outputs)` - Combine and synthesize findings
- `generate_final_report(analysis_results)` - Create comprehensive documentation
- `manage_context_sharing(agents)` - Share relevant findings between agents
- `track_analysis_progress(workflow_state)` - Monitor completion and quality metrics
- `handle_workflow_errors(error_state)` - Manage failures and recovery strategies
- `optimize_agent_execution(performance_metrics)` - Improve workflow efficiency
- `manage_resource_allocation(resource_requirements)` - Allocate system resources efficiently
- `coordinate_memory_management(memory_agents)` - Coordinate with memory management

**Input**: Analysis objectives, file sets, agent capabilities, system resources
**Output**: Complete analysis reports, test case collections, workflow documentation

## Agent Coordination Workflow

### Phase 1: Discovery & Assessment
1. **File Analyzer** → Initial file assessment and dependency mapping
2. **Schema Mapper** → Extract schema structures and relationships  
3. **Orchestrator** → Create detailed analysis plan based on findings

### Phase 2: Deep Analysis
1. **Business Logic Extractor** → Extract transformation rules and business logic
2. **Pattern Hunter** → Identify recurring patterns and helper functions
3. **Cross-Reference Validator** → Validate XPath expressions and schema compliance

### Phase 3: Test Generation & Validation
1. **Test Case Generator** → Create comprehensive test scenarios
2. **Cross-Reference Validator** → Validate generated test cases
3. **Orchestrator** → Aggregate and organize final deliverables

## Enhanced Context Management Strategy

### Shared Context Objects
- **File Dependency Graph**: Relationships between XSLT, input XSD, output XSD
- **Business Rules Catalog**: Extracted rules with line references and descriptions
- **Schema Element Maps**: Cross-references between input/output elements
- **Pattern Library**: Identified transformation patterns and their characteristics
- **Test Case Registry**: Generated test cases with metadata and categorization
- **Memory Usage Metrics**: Real-time memory usage and optimization data
- **Error Context History**: Historical error patterns and recovery strategies
- **Performance Benchmarks**: System performance metrics and optimization targets

### Advanced Context Sharing Mechanisms
- **Agent-to-Agent Communication**: Structured data exchange between agents
- **Centralized Context Store**: Shared memory for analysis results with compression
- **Workflow State Management**: Track progress and dependencies with persistence
- **Error Context Propagation**: Share error information for debugging and recovery
- **Memory-Aware Context Loading**: Load context based on memory availability
- **Context Compression Pipeline**: Automatic context compression with priority weighting
- **Disk Spillover Management**: Spill old context to disk when memory is limited
- **Context Integrity Validation**: Ensure context data integrity across operations

### Context Optimization Strategies
- **Hierarchical Context Storage**: Multi-level context with different priorities
- **Context Summarization**: Compress context to essential elements
- **Selective Context Loading**: Load only relevant context for current operations
- **Context Caching**: Cache frequently accessed context with LRU eviction
- **Context Lifecycle Management**: Automatic cleanup of old context data

## Quality Assurance Framework

### Validation Layers
1. **Schema Compliance**: All generated XML validated against XSD
2. **XPath Validation**: All XPath expressions verified against input schemas
3. **Business Rule Consistency**: Cross-validation of extracted rules
4. **Test Case Coverage**: Comprehensive coverage of identified patterns
5. **End-to-End Validation**: Actual XSLT transformation testing

### Success Metrics
- **Business Rule Extraction**: Number of rules extracted vs manual analysis baseline
- **Test Case Generation**: Test case count and categorization completeness
- **Schema Coverage**: Percentage of schema elements covered by test cases
- **Pattern Recognition**: Identification of known transformation patterns
- **Validation Accuracy**: Percentage of test cases that pass validation

## Control Flow Graph & Cyclomatic Complexity

### Control Flow Analysis
**Purpose**: Generate control flow graphs from XSLT transformations to ensure complete test coverage

**XSLT Control Flow Elements**:
- `xsl:choose/xsl:when/xsl:otherwise` - Decision blocks
- `xsl:if` - Conditional statements
- `xsl:for-each` - Iteration loops
- Template calls and recursion
- Variable dependencies and data flow

**Additional Agent Required**:

#### 8. Control Flow Analyzer Agent
**Purpose**: Build control flow graphs and calculate cyclomatic complexity
**Role**: Ensure comprehensive path coverage in generated test cases

**Tools & Functions**:
- `build_control_flow_graph(xslt_path)` - Create directed graph of execution paths
- `calculate_cyclomatic_complexity(control_flow_graph)` - Compute complexity metrics
- `identify_decision_points(xslt_path)` - Find all conditional logic branches
- `map_execution_paths(control_flow_graph)` - Enumerate all possible execution paths
- `analyze_path_coverage(test_cases, execution_paths)` - Ensure all paths are tested
- `identify_unreachable_code(control_flow_graph)` - Find dead code or unreachable paths
- `generate_path_based_test_cases(execution_paths)` - Create test cases for each path
- `validate_test_coverage_completeness(test_cases, complexity_metrics)` - Ensure coverage

**Input**: XSLT transformations, business rules
**Output**: Control flow graphs, cyclomatic complexity metrics, path coverage analysis

## Streamlit Integration

### UI Integration Strategy
**Integration Point**: Extend existing `app.py` with new agentic analysis tab

**New UI Components**:
- **File Upload Section**: XSLT + input/output XSD schemas
- **Analysis Configuration**: Depth settings, focus areas, agent selection
- **Progress Monitoring**: Real-time agent execution status
- **Results Dashboard**: Tabbed interface for different outputs
- **Download Interface**: Generated test cases, reports, and documentation

**User Workflow**:
1. Upload XSLT transformation file
2. Upload input and output XSD schemas
3. Configure analysis parameters
4. Monitor agent execution progress
5. Review generated business rules and patterns
6. Download executable test cases

### Streamlit Implementation Details
- **New Tab**: "XSLT Test Generation" alongside existing XML generation
- **Agent Progress**: Real-time status updates with progress bars
- **Results Tabs**: Business Rules, Test Cases, Control Flow, Validation Reports
- **Interactive Elements**: Expandable sections for detailed analysis
- **Error Handling**: Clear error messages and recovery options

## Executable Test Case Generation

### Test Case Format
**Output**: Executable Python/pytest test functions, not natural language descriptions

**Test Case Structure**:
```python
import pytest
import lxml.etree as ET
from pathlib import Path

class TestXSLTTransformation:
    
    @pytest.fixture
    def xslt_transformer(self):
        """Load and compile XSLT transformation"""
        xslt_path = Path("transformations/OrderCreate_MapForce_Full.xslt")
        with open(xslt_path) as f:
            xslt_doc = ET.parse(f)
        return ET.XSLT(xslt_doc)
    
    def test_helper_template_vmf1_passport_code(self, xslt_transformer):
        """Test vmf:vmf1_inputtoresult template with passport code 'P'"""
        input_xml = """<root><type>P</type></root>"""
        expected_output = "VPT"
        
        input_doc = ET.fromstring(input_xml)
        result = xslt_transformer(input_doc)
        
        assert str(result) == expected_output
    
    @pytest.mark.parametrize("input_type,expected", [
        ("P", "VPT"),
        ("PT", "VPT"),
        ("INVALID", ""),
        ("", ""),
    ])
    def test_helper_template_vmf1_all_cases(self, xslt_transformer, input_type, expected):
        """Parameterized test for all vmf1 template cases"""
        input_xml = f"<root><type>{input_type}</type></root>"
        
        input_doc = ET.fromstring(input_xml)
        result = xslt_transformer(input_doc)
        
        assert str(result) == expected
```

### Test Case Categories
1. **Helper Template Tests**: Individual template function validation
2. **Business Rule Tests**: Conditional logic and transformation rules
3. **Edge Case Tests**: Boundary conditions and error handling
4. **Integration Tests**: End-to-end transformation validation
5. **Path Coverage Tests**: Ensure all control flow paths are tested

### Test Generation Tools
**Additional Functions for Test Case Generator Agent**:
- `generate_pytest_test_functions(test_cases)` - Create executable test code
- `create_parameterized_tests(test_scenarios)` - Generate pytest.mark.parametrize tests
- `generate_test_fixtures(schema_definitions)` - Create reusable test data
- `create_assertion_logic(expected_outputs)` - Generate appropriate assertions
- `generate_test_setup_teardown(test_requirements)` - Create test infrastructure

## Technical Implementation Notes

### OpenAI ChatGPT Integration
- Each agent implemented as specialized ChatGPT conversation
- Function calling for tool execution
- Context management through conversation history
- Error handling and retry mechanisms

### Enhanced File Processing Strategy
- **Progressive file reading** (inspired by manual analysis)
- **Streaming file processing** for memory efficiency
- **Line-range based analysis** for large files with memory mapping
- **Grep-style search** for targeted analysis
- **Cross-file reference tracking** with persistent storage
- **Adaptive chunking** based on memory usage and file complexity
- **Memory-mapped file access** for very large files (>100MB)
- **Buffered reading** with configurable buffer sizes
- **Progress tracking** for long-running operations

### Output Generation
- **Executable Python/pytest test files** (primary output)
- Structured business rule documentation
- Control flow graphs and complexity metrics
- XML input/output sample generation
- Analysis methodology documentation

### Streamlit Integration Architecture
- **Backend**: Agentic system runs as separate service/module
- **Frontend**: Streamlit UI for configuration and results
- **Communication**: Progress updates via callbacks or websockets
- **File Management**: Temporary directories for analysis artifacts
- **Results Storage**: Structured output for UI consumption

## Enhanced Scalability Considerations

### Multi-File Analysis
- **Batch processing** of multiple XSLT files with resource management
- **Parallel agent execution** where possible with memory coordination
- **Shared pattern library** across analyses with persistent storage
- **Cumulative learning** from multiple analyses with pattern recognition
- **Distributed processing** for very large file sets
- **Resource pooling** for efficient memory and CPU usage

### Memory Scalability
- **Adaptive memory allocation** based on file size and complexity
- **Memory pool management** for efficient resource utilization
- **Garbage collection optimization** with generational strategies
- **Memory-mapped file processing** for files exceeding memory limits
- **Streaming analysis** for unlimited file sizes
- **Context spillover** to disk for large analysis contexts

### Performance Scalability
- **Performance monitoring** with real-time metrics
- **Adaptive algorithms** that adjust based on system performance
- **Caching strategies** for frequently accessed data
- **Parallel processing** where analysis can be parallelized
- **Resource optimization** based on available system resources

### Extensibility
- **Plugin architecture** for new agent types with memory management
- **Configurable analysis depth** and focus with resource awareness
- **Custom pattern recognition** rules with performance optimization
- **Integration with external validation** tools with resource coordination
- **Modular memory management** for different analysis types
- **Configurable fallback strategies** for different failure scenarios

## Enhanced Success Criteria

The agentic system should achieve:
1. **Match or exceed manual analysis quality**: Generate comprehensive test cases from similar XSLT files
2. **Comprehensive business rule extraction**: Identify all conditional logic and transformation patterns
3. **Valid test case generation**: All generated XML samples should be schema-compliant
4. **Systematic analysis approach**: Replicate the progressive depth methodology
5. **Efficient execution**: Complete analysis in significantly less time than manual approach
6. **Memory efficiency**: Process files of any size within memory constraints (< 1GB)
7. **Robust error handling**: Gracefully handle all error conditions with recovery
8. **Performance targets**: < 10 seconds per 1000 lines of XSLT processing
9. **Context preservation**: Maintain > 95% accuracy in context across chunks
10. **System resilience**: Handle failures and recover without data loss

## Memory Management Success Metrics

### Memory Usage Targets
- **Total memory usage**: < 1GB regardless of file size
- **Memory growth per chunk**: < 10MB per chunk processed
- **Context compression ratio**: > 70% compression achieved
- **Cache hit rate**: > 80% for repeated analysis
- **Garbage collection overhead**: < 5% of total processing time

### Performance Targets
- **Processing speed**: < 10 seconds per 1000 lines of XSLT
- **Memory allocation time**: < 100ms for context loading
- **Context compression time**: < 500ms per chunk
- **Error recovery time**: < 2 seconds for standard errors
- **Fallback strategy execution**: < 5 seconds for emergency cleanup

### Quality Assurance Metrics
- **Analysis accuracy**: > 95% compared to manual analysis
- **Test case validity**: > 98% generated tests pass execution
- **Schema compliance**: 100% generated XML validates against schemas
- **Business rule coverage**: > 90% of transformation rules identified
- **Context integrity**: 100% context data integrity maintained

This enhanced architecture provides a robust, scalable, and memory-efficient foundation for automated XSLT test case generation while maintaining the quality and comprehensiveness demonstrated by the manual analysis approach, with comprehensive memory management and error recovery capabilities.