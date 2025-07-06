# Chunking Strategy & Memory Management for Large XSLT Files

## Problem Statement

Large XSLT files (10,000+ lines) present significant challenges:
- **Context Window Limits**: OpenAI GPT-4 has ~128K token limit (≈100K words)
- **Large Files**: 10,000 lines ≈ 500K+ tokens (4-5x the limit)
- **Context Dependencies**: Business rules and transformations span multiple sections
- **Memory Management**: Need to maintain relevant context across chunks

## Chunking Strategy

### 1. Intelligent File Sectioning

**Template-Based Chunking**:
- **Helper Templates**: Process each named template separately (vmf:vmf1, vmf:vmf2, etc.)
- **Main Template Sections**: Break main template into logical sections
- **Variable Declarations**: Group related variable definitions
- **Import/Include Sections**: Process dependencies separately

**Section Boundaries**:
```xml
<!-- Natural XSLT boundaries -->
<xsl:template name="vmf:vmf1_inputtoresult">  <!-- Start new chunk -->
  <!-- Process this template completely -->
</xsl:template>  <!-- End chunk -->

<xsl:template match="/">  <!-- Start main template chunk -->
  <!-- Break into sub-sections based on business logic -->
</xsl:template>
```

### 2. Context-Aware Chunking

**Smart Boundary Detection**:
- **Template Boundaries**: Never split within a template
- **Choose Block Boundaries**: Keep xsl:choose/when/otherwise together
- **Variable Scope**: Maintain variable declarations with their usage
- **XPath Context**: Keep related XPath expressions together

**Chunk Size Management**:
- **Target Size**: 15,000-20,000 tokens per chunk (safe margin)
- **Overlap Strategy**: Include 500-1000 tokens of overlap between chunks
- **Dependency Tracking**: Maintain cross-references between chunks

### 3. Memory Management Architecture

#### Context Persistence Layer
```python
class ContextManager:
    def __init__(self):
        self.global_context = {}
        self.chunk_contexts = {}
        self.cross_references = {}
        self.business_rules = {}
        
    def save_chunk_analysis(self, chunk_id, analysis):
        """Save analysis results for a chunk"""
        self.chunk_contexts[chunk_id] = analysis
        
    def get_relevant_context(self, chunk_id):
        """Get relevant context for analyzing a chunk"""
        return {
            'variables': self.get_variables_in_scope(chunk_id),
            'templates': self.get_referenced_templates(chunk_id),
            'business_rules': self.get_related_rules(chunk_id)
        }
```

#### Hierarchical Context Storage
```python
class HierarchicalContext:
    def __init__(self):
        self.file_level = {}      # File metadata, imports, global variables
        self.template_level = {}  # Template definitions and parameters
        self.section_level = {}   # Business logic sections
        self.rule_level = {}      # Individual transformation rules
```

## Implementation Strategy

### Phase 1: File Preprocessing
1. **Parse XSLT Structure**: Identify templates, variables, imports
2. **Create Dependency Map**: Track template calls and variable usage
3. **Identify Chunk Boundaries**: Find natural breaking points
4. **Generate Chunk Metadata**: Create context summaries for each chunk

### Phase 2: Chunked Analysis
1. **Process Chunks Sequentially**: Analyze one chunk at a time
2. **Context Injection**: Provide relevant context from previous chunks
3. **Cross-Reference Tracking**: Maintain relationships between chunks
4. **Progressive Context Building**: Build comprehensive understanding

### Phase 3: Context Synthesis
1. **Aggregate Analysis**: Combine results from all chunks
2. **Resolve Dependencies**: Link business rules across chunks
3. **Validate Completeness**: Ensure no analysis gaps
4. **Generate Final Report**: Comprehensive analysis results

## Chunking Strategies by XSLT Section

### Helper Templates (Lines 12-64)
**Strategy**: Process each helper template as separate chunk
**Context Needed**: Template parameters, return values
**Size**: Small chunks (500-1000 tokens each)

### Main Template Structure (Lines 66-1868)
**Strategy**: Break into business logic sections
**Natural Boundaries**:
- Point of Sale processing (lines 82-91)
- Travel Agency data (lines 95-180)
- Order Query (lines 182-248)
- Passenger Data (lines 249-767)
- Contact Lists (lines 769-1227)
- Metadata Generation (lines 1229-1863)

### Variable Declarations
**Strategy**: Group related variables together
**Context Needed**: Variable scope and usage patterns
**Cross-References**: Track variable usage across chunks

## Memory Management Techniques

### 1. Context Summarization
```python
class ContextSummarizer:
    def summarize_chunk(self, chunk_analysis):
        """Create concise summary of chunk analysis"""
        return {
            'business_rules': self.extract_key_rules(chunk_analysis),
            'variables_defined': self.get_variable_definitions(chunk_analysis),
            'templates_called': self.get_template_calls(chunk_analysis),
            'xpath_patterns': self.get_xpath_patterns(chunk_analysis)
        }
```

### 2. Selective Context Loading
```python
class SelectiveContextLoader:
    def get_context_for_chunk(self, chunk_id, chunk_content):
        """Load only relevant context for current chunk"""
        relevant_context = {}
        
        # Analyze current chunk for dependencies
        dependencies = self.analyze_dependencies(chunk_content)
        
        # Load only relevant context
        for dep in dependencies:
            relevant_context[dep] = self.context_store.get(dep)
            
        return relevant_context
```

### 3. Context Compression
```python
class ContextCompressor:
    def compress_context(self, full_context):
        """Compress context to essential information"""
        return {
            'key_patterns': self.extract_patterns(full_context),
            'essential_rules': self.prioritize_rules(full_context),
            'critical_dependencies': self.identify_critical_deps(full_context)
        }
```

## LLM Interaction Strategy

### 1. Context-Aware Prompting
```python
def create_analysis_prompt(chunk_content, relevant_context):
    prompt = f"""
    Analyze this XSLT chunk with the following context:
    
    PREVIOUS ANALYSIS CONTEXT:
    {relevant_context}
    
    CURRENT CHUNK TO ANALYZE:
    {chunk_content}
    
    ANALYSIS INSTRUCTIONS:
    1. Identify business rules in this chunk
    2. Note any references to previous context
    3. Extract transformation patterns
    4. Identify dependencies for future chunks
    """
    return prompt
```

### 2. Progressive Context Building
```python
class ProgressiveAnalyzer:
    def analyze_file(self, xslt_file):
        chunks = self.create_chunks(xslt_file)
        analysis_results = []
        
        for i, chunk in enumerate(chunks):
            # Get relevant context from previous chunks
            context = self.get_cumulative_context(analysis_results)
            
            # Analyze current chunk with context
            result = self.analyze_chunk(chunk, context)
            analysis_results.append(result)
            
            # Update global context
            self.update_global_context(result)
            
        return self.synthesize_results(analysis_results)
```

## Updated MVP Plan Considerations

### MVP 1: Add Chunking Foundation
- **File Chunker**: Create intelligent XSLT file sectioning
- **Context Manager**: Basic context storage and retrieval
- **Chunk Analyzer**: Process individual chunks

### MVP 2: Memory Management
- **Context Summarization**: Compress analysis results
- **Selective Loading**: Load only relevant context
- **Cross-Reference Tracking**: Maintain chunk relationships

### MVP 3: Progressive Analysis
- **Sequential Processing**: Process chunks with context
- **Context Synthesis**: Combine results from multiple chunks
- **Validation**: Ensure completeness across chunks

## Performance Considerations

### Token Usage Optimization
- **Chunk Size**: 15K-20K tokens per chunk (safe for context limits)
- **Context Compression**: Reduce context to essential elements
- **Batch Processing**: Process multiple small chunks in single LLM call

### Memory Usage
- **Streaming Processing**: Process chunks without loading entire file
- **Context Cleanup**: Remove old context when no longer needed
- **Garbage Collection**: Regular cleanup of unused analysis data

## Quality Assurance

### Completeness Validation
- **Coverage Mapping**: Ensure all lines analyzed
- **Dependency Checking**: Verify all cross-references resolved
- **Business Rule Validation**: Confirm all rules identified

### Context Integrity
- **Context Consistency**: Ensure context remains accurate across chunks
- **Dependency Resolution**: Verify all dependencies properly tracked
- **Cross-Chunk Validation**: Validate analysis across chunk boundaries

This chunking strategy ensures we can handle large XSLT files while maintaining analysis quality and managing LLM context constraints effectively.