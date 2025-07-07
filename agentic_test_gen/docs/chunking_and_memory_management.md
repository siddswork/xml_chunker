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

## Advanced Memory Management Techniques

### 1. Enhanced Context Summarization
```python
class ContextSummarizer:
    def __init__(self, compression_target=0.7):
        self.compression_target = compression_target
        self.rule_priorities = {
            'business_critical': 1.0,
            'transformation_rules': 0.8,
            'helper_templates': 0.6,
            'variable_definitions': 0.4
        }
    
    def summarize_chunk(self, chunk_analysis):
        """Create concise summary of chunk analysis with priority weighting"""
        summary = {
            'business_rules': self.extract_key_rules(chunk_analysis),
            'variables_defined': self.get_variable_definitions(chunk_analysis),
            'templates_called': self.get_template_calls(chunk_analysis),
            'xpath_patterns': self.get_xpath_patterns(chunk_analysis),
            'dependencies': self.extract_dependencies(chunk_analysis),
            'metadata': self.create_metadata(chunk_analysis)
        }
        
        # Apply compression if needed
        if self.calculate_size(summary) > self.compression_target:
            summary = self.compress_summary(summary)
            
        return summary
    
    def compress_summary(self, summary):
        """Compress summary based on priority weighting"""
        compressed = {}
        for key, value in summary.items():
            priority = self.rule_priorities.get(key, 0.5)
            if priority >= 0.6:  # Keep high priority items
                compressed[key] = value
            else:
                compressed[key] = self.compress_value(value)
        return compressed
```

### 2. Intelligent Context Loading
```python
class IntelligentContextLoader:
    def __init__(self, memory_limit_mb=512):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        self.context_cache = {}
        self.access_patterns = {}
        self.memory_usage = 0
    
    def get_context_for_chunk(self, chunk_id, chunk_content):
        """Load only relevant context with memory management"""
        # Check memory usage before loading
        if self.memory_usage > self.memory_limit * 0.8:
            self.cleanup_old_context()
        
        # Analyze dependencies
        dependencies = self.analyze_dependencies(chunk_content)
        
        # Load context with priority
        relevant_context = {}
        for dep in dependencies:
            context_data = self.load_context_item(dep)
            if context_data:
                relevant_context[dep] = context_data
                self.update_access_pattern(dep)
        
        return relevant_context
    
    def cleanup_old_context(self):
        """Remove least recently used context items"""
        # Sort by access frequency and recency
        sorted_items = sorted(
            self.context_cache.items(),
            key=lambda x: (self.access_patterns[x[0]]['frequency'], 
                          self.access_patterns[x[0]]['last_access'])
        )
        
        # Remove bottom 30% of items
        items_to_remove = int(len(sorted_items) * 0.3)
        for item_id, _ in sorted_items[:items_to_remove]:
            del self.context_cache[item_id]
            self.memory_usage -= self.calculate_item_size(item_id)
```

### 3. Advanced Context Compression
```python
class AdvancedContextCompressor:
    def __init__(self):
        self.compression_algorithms = {
            'business_rules': self.compress_business_rules,
            'xpath_patterns': self.compress_xpath_patterns,
            'variable_definitions': self.compress_variables,
            'template_calls': self.compress_template_calls
        }
    
    def compress_context(self, full_context):
        """Compress context using specialized algorithms"""
        compressed = {}
        
        for context_type, context_data in full_context.items():
            if context_type in self.compression_algorithms:
                compressed[context_type] = self.compression_algorithms[context_type](context_data)
            else:
                compressed[context_type] = self.generic_compress(context_data)
        
        # Add compression metadata
        compressed['_compression_info'] = {
            'original_size': self.calculate_size(full_context),
            'compressed_size': self.calculate_size(compressed),
            'compression_ratio': self.calculate_compression_ratio(full_context, compressed)
        }
        
        return compressed
    
    def compress_business_rules(self, rules):
        """Compress business rules using pattern recognition"""
        patterns = self.identify_rule_patterns(rules)
        compressed_rules = []
        
        for rule in rules:
            if rule['pattern'] in patterns:
                # Store reference to pattern instead of full rule
                compressed_rules.append({
                    'pattern_ref': rule['pattern'],
                    'specific_data': rule['specific_data']
                })
            else:
                compressed_rules.append(rule)
        
        return {
            'patterns': patterns,
            'rules': compressed_rules
        }
```

### 4. Memory Monitoring and Management
```python
class MemoryManager:
    def __init__(self, memory_limit_mb=1024):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        self.usage_history = []
        self.alert_thresholds = {
            'warning': 0.7,
            'critical': 0.9
        }
        self.cleanup_strategies = [
            self.emergency_context_cleanup,
            self.compress_all_contexts,
            self.spill_to_disk
        ]
    
    def monitor_memory(self):
        """Monitor memory usage and trigger cleanup if needed"""
        current_usage = psutil.Process().memory_info().rss
        usage_ratio = current_usage / self.memory_limit
        
        self.usage_history.append({
            'timestamp': datetime.now(),
            'usage': current_usage,
            'ratio': usage_ratio
        })
        
        # Keep only last 100 measurements
        if len(self.usage_history) > 100:
            self.usage_history = self.usage_history[-100:]
        
        # Trigger cleanup if needed
        if usage_ratio > self.alert_thresholds['critical']:
            self.trigger_emergency_cleanup()
        elif usage_ratio > self.alert_thresholds['warning']:
            self.trigger_gradual_cleanup()
    
    def trigger_emergency_cleanup(self):
        """Trigger emergency cleanup strategies"""
        for strategy in self.cleanup_strategies:
            try:
                strategy()
                # Check if cleanup was successful
                if self.get_memory_usage_ratio() < self.alert_thresholds['critical']:
                    break
            except Exception as e:
                logging.warning(f"Cleanup strategy failed: {e}")
    
    def detect_memory_leaks(self):
        """Detect potential memory leaks"""
        if len(self.usage_history) < 20:
            return False
        
        # Check for consistent upward trend
        recent_usage = [u['usage'] for u in self.usage_history[-20:]]
        trend = self.calculate_trend(recent_usage)
        
        # If memory usage is consistently increasing
        if trend > 0.1:  # 10% increase over 20 measurements
            logging.warning(f"Potential memory leak detected. Trend: {trend:.2%}")
            return True
        
        return False
```

### 5. Fallback Strategies
```python
class FallbackManager:
    def __init__(self):
        self.fallback_strategies = [
            self.reduce_chunk_size,
            self.increase_compression,
            self.disk_spillover,
            self.analysis_degradation
        ]
        self.current_strategy_level = 0
    
    def handle_memory_pressure(self):
        """Handle memory pressure with progressive fallback"""
        if self.current_strategy_level < len(self.fallback_strategies):
            strategy = self.fallback_strategies[self.current_strategy_level]
            success = strategy()
            
            if success:
                logging.info(f"Fallback strategy {self.current_strategy_level} successful")
                return True
            else:
                self.current_strategy_level += 1
                return self.handle_memory_pressure()
        else:
            raise MemoryError("All fallback strategies exhausted")
    
    def reduce_chunk_size(self):
        """Reduce chunk size by 50%"""
        try:
            self.chunker.reduce_chunk_size(0.5)
            return True
        except Exception:
            return False
    
    def increase_compression(self):
        """Increase compression aggressiveness"""
        try:
            self.context_compressor.increase_compression_level()
            return True
        except Exception:
            return False
    
    def disk_spillover(self):
        """Spill old context to disk"""
        try:
            self.context_manager.spill_to_disk(threshold=0.3)
            return True
        except Exception:
            return False
    
    def analysis_degradation(self):
        """Reduce analysis depth and quality"""
        try:
            self.analyzer.reduce_analysis_depth()
            return True
        except Exception:
            return False
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
- **Adaptive Chunk Size**: 15K-20K tokens per chunk (dynamically adjusted based on memory)
- **Context Compression**: Reduce context to essential elements with 70%+ compression ratio
- **Batch Processing**: Process multiple small chunks in single LLM call
- **Token Estimation**: Accurate token counting for optimal chunk sizing

### Memory Usage Optimization
- **Streaming Processing**: Process chunks without loading entire file into memory
- **Context Cleanup**: Automatic removal of old context with LRU strategy
- **Garbage Collection**: Regular cleanup of unused analysis data with monitoring
- **Memory Monitoring**: Real-time memory usage tracking with alerts
- **Adaptive Algorithms**: Adjust processing based on available memory

### Performance Benchmarks
- **Memory Usage**: < 1GB total memory usage regardless of file size
- **Processing Speed**: < 10 seconds per 1000 lines of XSLT
- **Context Compression**: > 70% compression ratio
- **Cache Hit Rate**: > 80% for repeated analysis
- **Memory Growth**: < 10MB per chunk processed
- **Garbage Collection**: < 5% time spent in GC

### Scalability Considerations
- **Large File Handling**: Files up to 100,000+ lines
- **Memory-Mapped Files**: For very large files (>100MB)
- **Parallel Processing**: Where possible for independent chunks
- **Distributed Processing**: Future consideration for massive files

## Quality Assurance

### Completeness Validation
- **Coverage Mapping**: Ensure all lines analyzed with 100% coverage
- **Dependency Checking**: Verify all cross-references resolved
- **Business Rule Validation**: Confirm all rules identified with validation
- **Gap Analysis**: Identify and fill any analysis gaps

### Context Integrity
- **Context Consistency**: Ensure context remains accurate across chunks
- **Dependency Resolution**: Verify all dependencies properly tracked
- **Cross-Chunk Validation**: Validate analysis across chunk boundaries
- **Integrity Checksums**: Verify context data integrity

### Performance Validation
- **Memory Leak Detection**: Continuous monitoring for memory leaks
- **Performance Regression**: Testing for performance degradation
- **Stress Testing**: Testing with very large files
- **Error Recovery**: Validation of error handling and recovery

### Memory Management Testing
```python
class MemoryManagementTests:
    def test_memory_limits(self):
        """Test memory usage stays within limits"""
        assert self.memory_manager.get_usage() < self.memory_manager.memory_limit
    
    def test_context_compression(self):
        """Test context compression ratios"""
        compression_ratio = self.context_compressor.get_compression_ratio()
        assert compression_ratio > 0.7
    
    def test_fallback_strategies(self):
        """Test fallback strategies work correctly"""
        # Simulate memory pressure
        self.simulate_memory_pressure()
        assert self.fallback_manager.handle_memory_pressure()
    
    def test_memory_leak_detection(self):
        """Test memory leak detection"""
        # Run analysis multiple times
        for i in range(10):
            self.run_analysis()
        
        # Check for memory leaks
        assert not self.memory_manager.detect_memory_leaks()
```

## Implementation Validation

### Success Metrics
- **Memory Efficiency**: < 1GB total memory usage
- **Processing Speed**: < 10 seconds per 1000 lines
- **Context Quality**: > 95% accuracy in context preservation
- **Error Recovery**: < 2 seconds recovery time
- **Compression Ratio**: > 70% context compression

### Monitoring and Alerting
```python
class MemoryMonitoringSystem:
    def __init__(self):
        self.alerts = {
            'memory_warning': 0.7,
            'memory_critical': 0.9,
            'performance_degradation': 2.0,  # 2x slower than baseline
            'context_corruption': 0.1  # 10% context loss
        }
    
    def monitor_continuously(self):
        """Continuous monitoring of memory and performance"""
        while True:
            metrics = self.collect_metrics()
            
            for alert_type, threshold in self.alerts.items():
                if metrics[alert_type] > threshold:
                    self.send_alert(alert_type, metrics[alert_type])
            
            time.sleep(10)  # Check every 10 seconds
```

This enhanced chunking strategy ensures robust handling of large XSLT files while maintaining analysis quality, managing memory constraints effectively, and providing comprehensive monitoring and fallback mechanisms.