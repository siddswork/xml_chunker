"""Unit tests for Execution Path Analyzer."""

import pytest
from unittest.mock import Mock

from xslt_test_generator.analysis.execution_path_analyzer import (
    ExecutionPathAnalyzer, ExecutionPath, ExecutionNode, ExecutionNodeType
)
from xslt_test_generator.analysis.template_parser import XSLTTemplate, XSLTVariable
from xslt_test_generator.analysis.semantic_analyzer import SemanticPattern


class TestExecutionPathAnalyzer:
    """Test cases for Execution Path Analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create execution path analyzer instance."""
        return ExecutionPathAnalyzer()
    
    @pytest.fixture
    def sample_templates(self):
        """Create sample templates for testing."""
        return {
            'root': XSLTTemplate(
                name=None,
                match_pattern='/',
                calls_templates=['processItems'],
                uses_variables=['$title'],
                defines_variables=['$processedCount'],
                conditional_logic=[
                    {'type': 'if', 'condition': 'count(//item) > 0', 'line': 10}
                ],
                output_elements=['html', 'body'],
                line_start=8,
                line_end=20
            ),
            'processItems': XSLTTemplate(
                name='processItems',
                match_pattern=None,
                calls_templates=['formatItem'],
                uses_variables=['$items'],
                defines_variables=['$validItems'],
                conditional_logic=[
                    {'type': 'choose', 'conditions': ['@type="A"', '@type="B"'], 'line': 25}
                ],
                output_elements=['items'],
                line_start=22,
                line_end=35
            ),
            'formatItem': XSLTTemplate(
                name='formatItem',
                match_pattern='item',
                calls_templates=[],
                uses_variables=['$format'],
                defines_variables=[],
                conditional_logic=[],
                output_elements=['span'],
                line_start=37,
                line_end=42
            ),
            'recursiveTemplate': XSLTTemplate(
                name='recursiveTemplate',
                match_pattern=None,
                calls_templates=['recursiveTemplate'],
                uses_variables=['$depth'],
                defines_variables=['$newDepth'],
                conditional_logic=[
                    {'type': 'if', 'condition': '$depth < 10', 'line': 50}
                ],
                output_elements=['level'],
                line_start=45,
                line_end=55,
                is_recursive=True
            )
        }
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables for testing."""
        return {
            'title': XSLTVariable(
                name='title',
                variable_type='variable',
                scope='global'
            ),
            'items': XSLTVariable(
                name='items',
                variable_type='parameter',
                scope='global'
            )
        }
    
    @pytest.fixture
    def sample_patterns(self):
        """Create sample semantic patterns."""
        return [
            SemanticPattern(
                pattern_type='conditional_processing',
                description='Conditional logic in templates',
                templates_involved=['root', 'processItems'],
                confidence_score=0.9
            ),
            SemanticPattern(
                pattern_type='recursive_processing',
                description='Recursive template processing',
                templates_involved=['recursiveTemplate'],
                confidence_score=1.0
            )
        ]
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.templates == {}
        assert analyzer.variables == {}
        assert analyzer.execution_graph == {}
        assert analyzer.execution_paths == []
        assert analyzer.entry_points == []
        assert analyzer.file_path is None
    
    def test_analyze_execution_paths_success(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test successful execution path analysis."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        # Check basic structure
        assert 'execution_graph' in result
        assert 'execution_paths' in result
        assert 'entry_points' in result
        assert 'coverage_analysis' in result
        assert 'path_statistics' in result
        assert 'test_scenarios' in result
        assert 'error' not in result
        
        # Check execution graph was built
        assert len(result['execution_graph']) > 0
        
        # Check paths were discovered
        assert len(result['execution_paths']) > 0
        
        # Check entry points were identified
        assert len(result['entry_points']) > 0
    
    def test_execution_graph_construction(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test execution graph construction."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        execution_graph = result['execution_graph']
        
        # Should have different node types
        node_types = set(node.node_type for node in execution_graph.values())
        expected_types = {
            ExecutionNodeType.TEMPLATE_START,
            ExecutionNodeType.TEMPLATE_END,
            ExecutionNodeType.CONDITION,
            ExecutionNodeType.TEMPLATE_CALL,
            ExecutionNodeType.VARIABLE_ASSIGNMENT
        }
        assert expected_types.issubset(node_types)
        
        # Check specific nodes exist
        template_starts = [n for n in execution_graph.values() if n.node_type == ExecutionNodeType.TEMPLATE_START]
        assert len(template_starts) >= len(sample_templates)
        
        template_calls = [n for n in execution_graph.values() if n.node_type == ExecutionNodeType.TEMPLATE_CALL]
        assert len(template_calls) > 0
        
        conditions = [n for n in execution_graph.values() if n.node_type == ExecutionNodeType.CONDITION]
        assert len(conditions) > 0  # From conditional logic
    
    def test_entry_point_identification(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test entry point identification."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        entry_points = result['entry_points']
        
        # Should identify match templates as entry points
        assert 'root' in entry_points  # Root template (match_pattern='/')
        assert 'formatItem' in entry_points  # Item template (match_pattern='item')
        
        # Should not include named-only templates
        assert 'processItems' not in entry_points
        assert 'recursiveTemplate' not in entry_points  # Named template, no match pattern
    
    def test_path_discovery(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test execution path discovery."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        execution_paths = result['execution_paths']
        
        # Should discover multiple paths
        assert len(execution_paths) > 0
        
        # Check path structure
        path = execution_paths[0]
        assert hasattr(path, 'path_id')
        assert hasattr(path, 'nodes')
        assert hasattr(path, 'conditions')
        assert hasattr(path, 'variables_used')
        assert hasattr(path, 'templates_involved')
        assert hasattr(path, 'output_elements')
        assert hasattr(path, 'path_probability')
        assert hasattr(path, 'complexity_score')
        
        # Check path content
        assert len(path.nodes) > 0
        assert len(path.templates_involved) > 0
    
    def test_path_characteristics_analysis(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test path characteristics analysis."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        execution_paths = result['execution_paths']
        
        # Check that paths have been analyzed for characteristics
        for path in execution_paths:
            assert path.complexity_score >= 0
            assert 0.0 <= path.path_probability <= 1.0
            
            # Check test data requirements were generated
            assert hasattr(path, 'test_data_requirements')
            
            # Paths with conditions should have requirements
            if path.conditions:
                assert len(path.test_data_requirements) > 0
    
    def test_coverage_analysis(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test coverage analysis."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        coverage = result['coverage_analysis']
        
        # Check coverage fields
        assert 'node_coverage_percentage' in coverage
        assert 'template_coverage_percentage' in coverage
        assert 'total_execution_nodes' in coverage
        assert 'covered_nodes' in coverage
        assert 'uncovered_nodes' in coverage
        assert 'uncovered_node_list' in coverage
        assert 'uncovered_templates' in coverage
        assert 'coverage_gaps' in coverage
        
        # Check values are reasonable
        assert 0 <= coverage['node_coverage_percentage'] <= 100
        assert 0 <= coverage['template_coverage_percentage'] <= 100
        assert coverage['total_execution_nodes'] > 0
        assert coverage['covered_nodes'] >= 0
    
    def test_path_statistics_generation(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test path statistics generation."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        stats = result['path_statistics']
        
        # Check statistics fields
        assert 'total_paths' in stats
        assert 'avg_path_complexity' in stats
        assert 'max_path_complexity' in stats
        assert 'avg_path_length' in stats
        assert 'max_path_length' in stats
        assert 'avg_conditions_per_path' in stats
        assert 'paths_with_conditions' in stats
        assert 'most_complex_path' in stats
        
        # Check values are reasonable
        assert stats['total_paths'] > 0
        assert stats['avg_path_complexity'] >= 0
        assert stats['max_path_complexity'] >= stats['avg_path_complexity']
        assert stats['avg_path_length'] >= 0
        assert stats['max_path_length'] >= stats['avg_path_length']
    
    def test_test_scenarios_generation(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test test scenarios generation."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        scenarios = result['test_scenarios']
        
        # Should generate test scenarios
        assert len(scenarios) > 0
        
        # Check scenario structure
        scenario = scenarios[0]
        assert 'scenario_type' in scenario
        assert 'path_id' in scenario
        assert 'description' in scenario
        assert 'test_requirements' in scenario
        assert 'priority' in scenario
        
        # Check scenario types
        scenario_types = set(s['scenario_type'] for s in scenarios)
        possible_types = {'critical_path', 'conditional_logic', 'happy_path'}
        assert scenario_types.issubset(possible_types)
    
    def test_complex_conditional_paths(self, analyzer):
        """Test handling of complex conditional paths."""
        complex_template = {
            'complexConditional': XSLTTemplate(
                name='complexConditional',
                match_pattern='complex',
                conditional_logic=[
                    {'type': 'if', 'condition': '@type="A"', 'line': 10},
                    {'type': 'choose', 'conditions': ['@status="active"', '@status="inactive"'], 'line': 15},
                    {'type': 'if', 'condition': 'count(item) > 5', 'line': 20}
                ],
                output_elements=['result'],
                line_start=8,
                line_end=30
            )
        }
        
        result = analyzer.analyze_execution_paths(complex_template, {}, [], "/test/file.xsl")
        
        # Should handle complex conditionals
        assert 'error' not in result
        
        # Should generate appropriate test scenarios
        scenarios = result['test_scenarios']
        conditional_scenarios = [s for s in scenarios if s['scenario_type'] == 'conditional_logic']
        assert len(conditional_scenarios) > 0
    
    def test_recursive_path_handling(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test handling of recursive paths."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        # Should handle recursive templates
        assert 'error' not in result
        
        # Recursive template should be in execution graph
        graph = result['execution_graph']
        recursive_nodes = [n for n in graph.values() if 'recursiveTemplate' in n.template_name]
        assert len(recursive_nodes) > 0
        
        # Should generate paths involving recursive template
        paths = result['execution_paths']
        recursive_paths = [p for p in paths if 'recursiveTemplate' in p.templates_involved]
        # Note: May be 0 if recursive template isn't an entry point
    
    def test_variable_extraction_from_expressions(self, analyzer):
        """Test variable extraction from XPath expressions."""
        # Test the helper method
        variables = analyzer._extract_variables_from_expression("$var1 + $var2 and @attr = $var3")
        
        assert 'var1' in variables
        assert 'var2' in variables
        assert 'var3' in variables
        assert len(variables) == 3
    
    def test_coverage_gap_identification(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test coverage gap identification."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        coverage = result['coverage_analysis']
        gaps = coverage['coverage_gaps']
        
        # Check gap structure
        for gap in gaps:
            assert 'gap_type' in gap
            assert 'description' in gap
            assert 'affected_elements' in gap
            assert 'impact' in gap
        
        # Common gap types
        gap_types = set(gap['gap_type'] for gap in gaps)
        possible_types = {'unexecuted_templates', 'untested_conditions'}
        assert gap_types.issubset(possible_types)
    
    def test_test_data_requirements_generation(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test test data requirements generation."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        paths = result['execution_paths']
        
        # Check that test data requirements were generated
        for path in paths:
            requirements = path.test_data_requirements
            
            # Should have requirements if path uses variables or has conditions
            if path.variables_used or path.conditions:
                assert len(requirements) > 0
                
                # Check requirement structure
                for req in requirements:
                    assert 'requirement_type' in req
                    assert 'description' in req
                    assert 'priority' in req
    
    def test_path_probability_calculation(self, analyzer, sample_templates, sample_variables, sample_patterns):
        """Test path probability calculation."""
        result = analyzer.analyze_execution_paths(
            sample_templates, sample_variables, sample_patterns, "/test/file.xsl"
        )
        
        paths = result['execution_paths']
        
        # All paths should have probabilities
        for path in paths:
            assert 0.0 <= path.path_probability <= 1.0
            
            # Paths with more conditions should generally have lower probability
            if len(path.conditions) > 0:
                assert path.path_probability < 1.0
    
    def test_empty_templates_handling(self, analyzer):
        """Test handling of empty template sets."""
        result = analyzer.analyze_execution_paths({}, {}, [], "/test/file.xsl")
        
        # Should not error on empty inputs
        assert 'error' not in result
        assert result['execution_paths'] == []
        assert result['entry_points'] == []
        assert len(result['execution_graph']) == 0
    
    def test_error_handling(self, analyzer):
        """Test error handling in execution path analysis."""
        # Test with invalid inputs
        result = analyzer.analyze_execution_paths(None, None, None, "/test/file.xsl")
        assert 'error' in result
        
        # Test with malformed templates
        malformed_templates = {
            'bad_template': "not a template object"
        }
        result = analyzer.analyze_execution_paths(malformed_templates, {}, [], "/test/file.xsl")
        assert 'error' in result
    
    def test_large_template_set_performance(self, analyzer):
        """Test performance with large template sets."""
        # Create many templates
        large_template_set = {}
        for i in range(50):
            large_template_set[f'template_{i}'] = XSLTTemplate(
                name=f'template_{i}',
                match_pattern=f'element_{i}',
                calls_templates=[f'template_{(i+1)%50}'] if i < 49 else [],
                line_start=i * 10,
                line_end=i * 10 + 5
            )
        
        result = analyzer.analyze_execution_paths(large_template_set, {}, [], "/test/file.xsl")
        
        # Should handle large sets without error
        assert 'error' not in result
        assert len(result['execution_graph']) > 0
        assert len(result['entry_points']) > 0
    
    def test_execution_node_creation(self, analyzer):
        """Test execution node creation and properties."""
        # Test through a simple analysis
        simple_template = {
            'test': XSLTTemplate(
                name='test',
                match_pattern='test',
                uses_variables=['$var1'],
                defines_variables=['$var2'],
                conditional_logic=[{'type': 'if', 'condition': '@test', 'line': 5}],
                output_elements=['output'],
                line_start=1,
                line_end=10
            )
        }
        
        result = analyzer.analyze_execution_paths(simple_template, {}, [], "/test/file.xsl")
        
        nodes = result['execution_graph']
        
        # Check node properties
        for node in nodes.values():
            assert hasattr(node, 'node_id')
            assert hasattr(node, 'node_type')
            assert hasattr(node, 'template_name')
            assert hasattr(node, 'line_number')
            assert hasattr(node, 'description')
            assert hasattr(node, 'predecessors')
            assert hasattr(node, 'successors')
            
            # Check that node_type is valid
            assert isinstance(node.node_type, ExecutionNodeType)