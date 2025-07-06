# MVP Implementation Plan - Agentic XSLT Test Generator

## Overview
This document breaks down the agentic XSLT test generation system into 10 small, incremental MVPs. Each MVP is designed to be:
- **Small enough** to implement in 1-2 days
- **Demonstrable** with concrete outputs
- **Testable** with clear success criteria
- **Buildable** on the previous MVP

## MVP Progression Strategy

### MVP 1: XSLT File Chunker & Context Manager
**Duration**: 2-3 days
**Goal**: Handle large XSLT files through intelligent chunking and context management

**What to Build**:
- `XSLTChunker` class for intelligent file sectioning
- `ContextManager` class for memory management
- Template-based chunking (helper templates, main template sections)
- Basic context storage and retrieval

**Deliverables**:
- `xslt_chunker.py` - File chunking logic
- `context_manager.py` - Context storage and retrieval
- `test_chunking.py` - Unit tests for chunking
- CLI script to demo chunking functionality

**Success Criteria**:
- Can chunk 10,000+ line XSLT files into manageable pieces
- Maintains natural boundaries (templates, choose blocks)
- Chunks are 15K-20K tokens max (safe for LLM context)
- Context manager stores and retrieves chunk metadata

**Demo**: Command line tool that shows file chunking with chunk sizes and boundaries
**Memory Management**: Handles large files without loading entire content into memory

---

### MVP 2: Context-Aware Chunk Analyzer
**Duration**: 2-3 days
**Goal**: Analyze individual chunks while maintaining context from previous chunks

**What to Build**:
- `ChunkAnalyzer` class for processing individual chunks
- Context injection for LLM prompts
- Progressive context building across chunks
- Cross-reference tracking between chunks

**Deliverables**:
- `chunk_analyzer.py` - Individual chunk analysis
- `context_injector.py` - Context-aware prompt creation
- Enhanced `ContextManager` with cross-references
- Progressive analysis workflow

**Success Criteria**:
- Can analyze chunks with relevant context from previous chunks
- Maintains cross-references between chunks
- Builds comprehensive understanding progressively
- Handles context compression for memory efficiency

**Demo**: Shows chunk-by-chunk analysis with context preservation
**Memory Management**: Selective context loading and compression

---

### MVP 3: Helper Template Logic Extractor
**Duration**: 1-2 days
**Goal**: Extract specific logic from helper templates using chunked analysis

**What to Build**:
- `HelperTemplateExtractor` class
- Parse helper template parameters and logic from chunks
- Extract input→output mappings ('P'→'VPT', 'V'→'VVI', etc.)
- Identify transformation rules and conditions

**Deliverables**:
- `helper_template_extractor.py` - Template logic extraction
- Integration with chunked analysis workflow
- JSON output with transformation rules

**Success Criteria**:
- Correctly extracts all 4 helper template mappings from chunks
- Identifies input parameters and output values
- Handles edge cases (empty input, otherwise conditions)
- Works with chunked file processing

**Demo**: Shows helper template transformation rules extracted from chunks

---

### MVP 4: Executable Pytest Code Generator
**Duration**: 1-2 days
**Goal**: Convert test case scenarios into executable Python/pytest code

**What to Build**:
- `PytestCodeGenerator` class
- Generate pytest test functions from test cases
- Create parameterized tests
- Add proper assertions and test structure

**Deliverables**:
- `pytest_code_generator.py` - Code generation logic
- Generated `test_helper_templates.py` - Executable test file
- Test execution verification

**Success Criteria**:
- Generates valid Python/pytest code
- Tests can be executed with pytest
- All generated tests pass when run against sample data

**Demo**: Shows generated pytest code and successful test execution

---

### MVP 5: Basic Streamlit UI Integration
**Duration**: 1-2 days
**Goal**: Integrate helper template analysis into Streamlit app

**What to Build**:
- New tab in existing `app.py` called "XSLT Test Generation"
- File upload for XSLT files
- Display analysis results in UI
- Download generated test cases

**Deliverables**:
- Enhanced `app.py` with new XSLT analysis tab
- UI components for file upload and results display
- Download functionality for generated tests

**Success Criteria**:
- Upload XSLT file through UI
- View helper template analysis results
- Download generated pytest code
- Integration works with existing app structure

**Demo**: Working Streamlit interface for XSLT analysis

---

### MVP 6: Schema Analysis Integration
**Duration**: 2-3 days
**Goal**: Add input/output schema analysis to understand data structures

**What to Build**:
- `SchemaAnalyzer` class
- Parse XSD schema files
- Extract element definitions and types
- Map schema elements to XSLT transformations

**Deliverables**:
- `schema_analyzer.py` - XSD analysis logic
- Enhanced UI to upload input/output schemas
- Schema-aware test case generation

**Success Criteria**:
- Correctly parses AMA_ConnectivityLayerRQ.xsd
- Identifies TTR_ActorType and other complex types
- Maps schema elements to XSLT XPath expressions

**Demo**: Shows schema structure and element mappings

---

### MVP 7: Business Rule Extraction from Main Template
**Duration**: 2-3 days
**Goal**: Extract business rules from main XSLT template (beyond helper templates)

**What to Build**:
- `BusinessRuleExtractor` class
- Identify conditional logic patterns in main template
- Extract transformation rules and mappings
- Handle complex business logic (target-specific processing)

**Deliverables**:
- `business_rule_extractor.py` - Main template analysis
- Extracted business rules catalog
- Enhanced test case generation for main template logic

**Success Criteria**:
- Identifies target-specific processing (UA/UAD)
- Extracts conditional logic patterns
- Generates test cases for main template transformations

**Demo**: Shows business rules extracted from main template

---

### MVP 8: Control Flow Analysis & Cyclomatic Complexity
**Duration**: 2-3 days
**Goal**: Build control flow graphs and calculate complexity metrics

**What to Build**:
- `ControlFlowAnalyzer` class
- Build control flow graphs from XSLT decision blocks
- Calculate cyclomatic complexity
- Ensure path coverage in test cases

**Deliverables**:
- `control_flow_analyzer.py` - Control flow analysis
- Control flow graph visualization
- Path coverage analysis and reporting

**Success Criteria**:
- Generates control flow graph for XSLT transformation
- Calculates cyclomatic complexity accurately
- Identifies all execution paths
- Validates test case coverage

**Demo**: Shows control flow graph and complexity metrics

---

### MVP 9: Agent Coordination & Workflow
**Duration**: 2-3 days
**Goal**: Implement agent coordination and workflow management

**What to Build**:
- `Orchestrator` class
- Coordinate execution of different analysis components
- Manage workflow and dependencies
- Aggregate results from multiple analyzers

**Deliverables**:
- `orchestrator.py` - Workflow coordination
- Enhanced UI with progress tracking
- Integrated analysis pipeline

**Success Criteria**:
- Coordinates execution of all analysis components
- Provides progress updates
- Produces comprehensive analysis report
- Handles errors and recovery

**Demo**: Shows complete analysis workflow with progress tracking

---

### MVP 10: Advanced Features & Polish
**Duration**: 2-3 days
**Goal**: Add advanced features and polish the system

**What to Build**:
- Enhanced error handling and validation
- Performance optimization
- Additional test case categories
- Documentation and help system

**Deliverables**:
- Optimized and polished system
- Comprehensive documentation
- Advanced configuration options
- Performance benchmarks

**Success Criteria**:
- Robust error handling
- Fast execution on large XSLT files
- Comprehensive test coverage
- User-friendly interface

**Demo**: Complete, polished system ready for production use

## Implementation Guidelines

### For Each MVP:

1. **Start Small**: Focus only on the specific MVP goals
2. **Write Tests First**: Create unit tests for each component
3. **Document Progress**: Update progress docs after each MVP
4. **Demo Early**: Create a working demo after each MVP
5. **Refactor Minimally**: Only refactor when necessary for next MVP

### File Structure Per MVP:
```
agentic_test_gen/
├── core/                 # Core analysis components
│   ├── xslt_analyzer.py
│   ├── helper_template_extractor.py
│   ├── test_case_generator.py
│   └── pytest_code_generator.py
├── tests/                # Unit tests for each component
├── examples/             # Example outputs and demos
├── docs/                 # Documentation and progress tracking
└── streamlit_ui/         # Streamlit integration components
```

### Success Metrics Per MVP:
- **Functionality**: Core feature works as specified
- **Testing**: All unit tests pass
- **Documentation**: Clear README and examples
- **Demo**: Working demonstration available
- **Integration**: Builds properly on previous MVP

### Risk Mitigation:
- **Time Boxing**: Strict 1-3 day limits per MVP
- **Scope Creep**: Only implement MVP requirements
- **Dependencies**: Each MVP should be independently testable
- **Rollback**: Easy to rollback to previous MVP if needed

This plan ensures tight control while making steady, demonstrable progress toward the complete system.