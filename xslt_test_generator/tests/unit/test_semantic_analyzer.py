"""Unit tests for Semantic Analyzer."""

import pytest
from unittest.mock import Mock, patch

from xslt_test_generator.analysis.semantic_analyzer import (
    SemanticAnalyzer, SemanticPattern, DataFlowNode, DataFlowType
)
from xslt_test_generator.analysis.template_parser import XSLTTemplate, XSLTVariable


class TestSemanticAnalyzer:
    """Test cases for Semantic Analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create semantic analyzer instance."""
        return SemanticAnalyzer()
    
    @pytest.fixture
    def sample_templates(self):
        """Create sample templates for testing."""
        return {
            'root': XSLTTemplate(
                name=None,
                match_pattern='/',
                calls_templates=['processItems', 'generateHeader'],
                uses_variables=['$title', '$mode'],
                defines_variables=['$processedCount'],
                xpath_expressions=['//item', '@type'],
                conditional_logic=[
                    {'type': 'if', 'condition': '@enabled="true"', 'line': 10}
                ],
                output_elements=['html', 'head', 'body'],
                complexity_score=8
            ),
            'processItems': XSLTTemplate(
                name='processItems',
                match_pattern=None,
                calls_templates=['formatItem', 'validateItem'],
                uses_variables=['$items', '$format'],
                defines_variables=['$validItems'],
                xpath_expressions=['item[@valid="true"]', 'count(//item)', 'sum(@value)'],
                conditional_logic=[
                    {'type': 'choose', 'conditions': ['@type="A"', '@type="B"'], 'line': 25},
                    {'type': 'if', 'condition': 'count(item) > 0', 'line': 30}
                ],
                output_elements=['items', 'item'],
                complexity_score=12
            ),
            'formatItem': XSLTTemplate(
                name='formatItem',
                match_pattern='item',
                calls_templates=[],
                uses_variables=['$format'],
                defines_variables=[],
                xpath_expressions=['@name', 'text()'],
                conditional_logic=[],
                output_elements=['span', 'div'],
                complexity_score=4
            ),
            'recursiveProcessor': XSLTTemplate(
                name='recursiveProcessor',
                match_pattern=None,
                calls_templates=['recursiveProcessor'],  # Self-call
                uses_variables=['$depth'],
                defines_variables=['$newDepth'],
                xpath_expressions=['child::*'],
                conditional_logic=[
                    {'type': 'if', 'condition': '$depth < 10', 'line': 50}
                ],
                output_elements=['level'],
                complexity_score=15,
                is_recursive=True
            ),
            'errorHandler': XSLTTemplate(
                name='errorHandler',
                match_pattern=None,
                template_content='<xsl:message>Error occurred</xsl:message><xsl:fallback>Default content</xsl:fallback>',
                calls_templates=[],
                uses_variables=[],
                defines_variables=[],
                xpath_expressions=[],
                conditional_logic=[],
                output_elements=['error'],
                complexity_score=6
            )
        }
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables for testing."""
        return {
            'title': XSLTVariable(
                name='title',
                variable_type='variable',
                select_expression="'Document Title'",
                scope='global',
                line_number=5,
                used_by_templates=['root', 'generateHeader']
            ),
            'mode': XSLTVariable(
                name='mode',
                variable_type='parameter',
                select_expression="'production'",
                scope='global',
                line_number=6,
                used_by_templates=['root']
            ),
            'localVar': XSLTVariable(
                name='localVar',
                variable_type='variable',
                scope='template',
                line_number=15,
                used_by_templates=[]  # Unused variable
            )
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.templates == {}
        assert analyzer.variables == {}
        assert analyzer.data_flow_graph == {}
        assert analyzer.semantic_patterns == []
        assert analyzer.file_path is None
    
    def test_analyze_semantics_success(self, analyzer, sample_templates, sample_variables):
        """Test successful semantic analysis."""
        result = analyzer.analyze_semantics(
            sample_templates, sample_variables, "/test/file.xsl"
        )
        
        # Check basic structure
        assert 'data_flow_graph' in result
        assert 'semantic_patterns' in result
        assert 'variable_analysis' in result
        assert 'interaction_analysis' in result
        assert 'transformation_hotspots' in result
        assert 'test_implications' in result
        assert 'analysis_summary' in result
        assert 'error' not in result
        
        # Check patterns were identified
        patterns = result['semantic_patterns']
        assert len(patterns) > 0
        
        # Check specific pattern types
        pattern_types = [p.pattern_type for p in patterns]
        assert 'conditional_processing' in pattern_types  # Due to conditional logic
        assert 'recursive_processing' in pattern_types   # Due to recursive template
        assert 'template_orchestration' in pattern_types # Due to multiple calls
        
        # Check data flow graph was built
        assert len(result['data_flow_graph']) > 0
    
    def test_transformation_pipeline_detection(self, analyzer, sample_templates, sample_variables):
        """Test transformation pipeline pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect transformation pipeline
        pipeline_patterns = [p for p in patterns if p.pattern_type == 'transformation_pipeline']
        assert len(pipeline_patterns) > 0
        
        pipeline = pipeline_patterns[0]
        assert pipeline.confidence_score > 0.5
        assert len(pipeline.templates_involved) >= 2
        assert len(pipeline.test_implications) > 0
    
    def test_conditional_processing_detection(self, analyzer, sample_templates, sample_variables):
        """Test conditional processing pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect conditional processing
        conditional_patterns = [p for p in patterns if p.pattern_type == 'conditional_processing']
        assert len(conditional_patterns) > 0
        
        conditional = conditional_patterns[0]
        assert conditional.confidence_score == 0.9  # High confidence
        assert 'root' in conditional.templates_involved
        assert 'processItems' in conditional.templates_involved
        assert 'Test all conditional branches' in conditional.test_implications
    
    def test_recursive_processing_detection(self, analyzer, sample_templates, sample_variables):
        """Test recursive processing pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect recursive processing
        recursive_patterns = [p for p in patterns if p.pattern_type == 'recursive_processing']
        assert len(recursive_patterns) > 0
        
        recursive = recursive_patterns[0]
        assert recursive.confidence_score == 1.0  # Perfect confidence
        assert 'recursiveProcessor' in recursive.templates_involved
        assert 'Test recursion base cases' in recursive.test_implications
        assert 'Test recursion termination conditions' in recursive.test_implications
    
    def test_data_aggregation_detection(self, analyzer, sample_templates, sample_variables):
        """Test data aggregation pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect data aggregation (due to count() and sum() functions)
        aggregation_patterns = [p for p in patterns if p.pattern_type == 'data_aggregation']
        assert len(aggregation_patterns) > 0
        
        aggregation = aggregation_patterns[0]
        assert aggregation.confidence_score >= 0.8
        assert 'processItems' in aggregation.templates_involved
        assert 'Test with empty data sets' in aggregation.test_implications
    
    def test_template_orchestration_detection(self, analyzer, sample_templates, sample_variables):
        """Test template orchestration pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect orchestration (templates calling multiple others)
        orchestration_patterns = [p for p in patterns if p.pattern_type == 'template_orchestration']
        assert len(orchestration_patterns) > 0
        
        orchestration = orchestration_patterns[0]
        assert 'processItems' in orchestration.templates_involved  # Calls 2+ templates
    
    def test_error_handling_detection(self, analyzer, sample_templates, sample_variables):
        """Test error handling pattern detection."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        patterns = result['semantic_patterns']
        
        # Should detect error handling
        error_patterns = [p for p in patterns if p.pattern_type == 'error_handling']
        assert len(error_patterns) > 0
        
        error_pattern = error_patterns[0]
        assert 'errorHandler' in error_pattern.templates_involved
        assert error_pattern.confidence_score >= 0.6
    
    def test_data_flow_graph_construction(self, analyzer, sample_templates, sample_variables):
        """Test data flow graph construction."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        data_flow = result['data_flow_graph']
        
        # Should have various node types
        node_types = set(node.node_type for node in data_flow.values())
        expected_types = {
            DataFlowType.VARIABLE_ASSIGNMENT,
            DataFlowType.TEMPLATE_CALL,
            DataFlowType.CONDITIONAL_BRANCH,
            DataFlowType.XPATH_SELECTION
        }
        assert expected_types.issubset(node_types)
        
        # Check specific nodes exist
        template_calls = [n for n in data_flow.values() if n.node_type == DataFlowType.TEMPLATE_CALL]
        assert len(template_calls) > 0
        
        variable_assignments = [n for n in data_flow.values() if n.node_type == DataFlowType.VARIABLE_ASSIGNMENT]
        assert len(variable_assignments) > 0
    
    def test_variable_scoping_analysis(self, analyzer, sample_templates, sample_variables):
        """Test variable scoping analysis."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        var_analysis = result['variable_analysis']
        
        # Check variable categorization
        assert 'global_variables' in var_analysis
        assert 'template_variables' in var_analysis
        assert 'local_variables' in var_analysis
        assert 'variable_conflicts' in var_analysis
        assert 'unused_variables' in var_analysis
        
        # Check specific variables
        assert 'title' in var_analysis['global_variables']
        assert 'mode' in var_analysis['global_variables']
        assert 'localVar' in var_analysis['unused_variables']
    
    def test_template_interaction_analysis(self, analyzer, sample_templates, sample_variables):
        """Test template interaction analysis."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        interaction = result['interaction_analysis']
        
        # Check call graph
        assert 'call_graph' in interaction
        call_graph = interaction['call_graph']
        assert 'root' in call_graph
        assert 'processItems' in call_graph['root']
        assert 'generateHeader' in call_graph['root']
        
        # Check dependencies
        assert 'template_dependencies' in interaction
        dependencies = interaction['template_dependencies']
        assert len(dependencies) > 0
        
        # Check circular dependencies
        assert 'circular_dependencies' in interaction
        
        # Check orphaned templates
        assert 'orphaned_templates' in interaction
    
    def test_transformation_hotspots_identification(self, analyzer, sample_templates, sample_variables):
        """Test transformation hotspot identification."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        hotspots = result['transformation_hotspots']
        
        # Should identify high complexity templates as hotspots
        assert len(hotspots) > 0
        
        # Check hotspot structure
        hotspot = hotspots[0]
        assert 'template_name' in hotspot
        assert 'hotspot_score' in hotspot
        assert 'reasons' in hotspot
        assert 'risk_level' in hotspot
        
        # High complexity templates should be hotspots
        hotspot_names = [h['template_name'] for h in hotspots]
        assert 'recursiveProcessor' in hotspot_names  # Should be a hotspot due to high complexity + recursion
    
    def test_test_implications_generation(self, analyzer, sample_templates, sample_variables):
        """Test test implications generation."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        test_implications = result['test_implications']
        
        # Should generate test implications
        assert len(test_implications) > 0
        
        # Check implication structure
        implication = test_implications[0]
        assert 'pattern_type' in implication
        assert 'templates' in implication
        assert 'test_requirement' in implication
        assert 'priority' in implication
        
        # High confidence patterns should have high priority
        high_priority = [imp for imp in test_implications if imp['priority'] == 'high']
        assert len(high_priority) > 0
    
    def test_variable_conflict_detection(self, analyzer):
        """Test variable conflict detection."""
        # Create conflicting variables
        conflicting_vars = {
            'var1_global': XSLTVariable(
                name='conflictVar',
                variable_type='variable',
                scope='global',
                line_number=5
            ),
            'var1_template': XSLTVariable(
                name='conflictVar',  # Same name
                variable_type='variable',
                scope='template',
                line_number=15
            )
        }
        
        result = analyzer.analyze_semantics({}, conflicting_vars, "/test/file.xsl")
        var_analysis = result['variable_analysis']
        
        # Should detect conflicts
        assert len(var_analysis['variable_conflicts']) > 0
        assert any('conflictVar' in conflict for conflict in var_analysis['variable_conflicts'])
    
    def test_circular_dependency_detection(self, analyzer):
        """Test circular dependency detection."""
        # Create circular dependency
        circular_templates = {
            'templateA': XSLTTemplate(
                name='templateA',
                calls_templates=['templateB']
            ),
            'templateB': XSLTTemplate(
                name='templateB',
                calls_templates=['templateA']  # Circular
            )
        }
        
        result = analyzer.analyze_semantics(circular_templates, {}, "/test/file.xsl")
        interaction = result['interaction_analysis']
        
        # Should detect circular dependencies
        circular_deps = interaction['circular_dependencies']
        assert len(circular_deps) > 0
        
        # Check that both templates are in the cycle
        cycle = circular_deps[0]
        assert 'templateA' in cycle
        assert 'templateB' in cycle
    
    def test_orphaned_template_detection(self, analyzer):
        """Test orphaned template detection."""
        orphaned_templates = {
            'mainTemplate': XSLTTemplate(
                name='mainTemplate',
                calls_templates=['usedTemplate']
            ),
            'usedTemplate': XSLTTemplate(
                name='usedTemplate',
                calls_templates=[]
            ),
            'orphanedTemplate': XSLTTemplate(
                name='orphanedTemplate',  # Not called by anyone
                calls_templates=[]
            )
        }
        
        result = analyzer.analyze_semantics(orphaned_templates, {}, "/test/file.xsl")
        interaction = result['interaction_analysis']
        
        # Should detect orphaned template
        orphaned = interaction['orphaned_templates']
        assert 'orphanedTemplate' in orphaned
        assert 'usedTemplate' not in orphaned  # Used by mainTemplate
        # mainTemplate is also orphaned since it's not called by anyone and has no match pattern
    
    def test_semantic_summary_generation(self, analyzer, sample_templates, sample_variables):
        """Test semantic analysis summary generation."""
        result = analyzer.analyze_semantics(sample_templates, sample_variables, "/test/file.xsl")
        summary = result['analysis_summary']
        
        # Check summary fields
        assert 'total_patterns' in summary
        assert 'pattern_types' in summary
        assert 'high_confidence_patterns' in summary
        assert 'data_flow_nodes' in summary
        assert 'transformation_complexity' in summary
        assert 'test_implications_count' in summary
        
        # Check values
        assert summary['total_patterns'] > 0
        assert len(summary['pattern_types']) > 0
        assert summary['transformation_complexity'] > 0
    
    def test_error_handling(self, analyzer):
        """Test error handling in semantic analysis."""
        # Test with None inputs
        result = analyzer.analyze_semantics(None, None, "/test/file.xsl")
        assert 'error' in result
        
        # Test with invalid data
        result = analyzer.analyze_semantics("invalid", "invalid", "/test/file.xsl")
        assert 'error' in result
    
    def test_empty_templates_handling(self, analyzer):
        """Test handling of empty template and variable sets."""
        result = analyzer.analyze_semantics({}, {}, "/test/file.xsl")
        
        # Should not error on empty inputs
        assert 'error' not in result
        assert result['semantic_patterns'] == []
        assert result['data_flow_graph'] == {}
        
        # Summary should reflect empty state
        summary = result['analysis_summary']
        assert summary['total_patterns'] == 0
        assert summary['transformation_complexity'] == 0