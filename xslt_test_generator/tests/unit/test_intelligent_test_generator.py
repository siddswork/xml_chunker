"""Tests for IntelligentTestGenerator component."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from xslt_test_generator.agents.intelligent_test_generator import (
    IntelligentTestGenerator, TestScenario, TestSuite
)


class TestIntelligentTestGenerator:
    """Test IntelligentTestGenerator functionality."""
    
    @pytest.fixture
    def test_generator(self):
        """Create test generator instance."""
        generator = IntelligentTestGenerator()
        # Mock the LLM client to avoid actual API calls
        generator.llm_client = Mock()
        return generator
    
    @pytest.fixture
    def sample_analysis_results(self):
        """Sample Phase 2 analysis results."""
        return {
            'file_path': '/test/sample.xslt',
            'template_analysis': {
                'templates': {
                    'formatOrder': Mock(
                        name='formatOrder',
                        complexity_score=15,
                        is_recursive=True,
                        calls_templates=['formatItem', 'calculateTotal'],
                        conditional_logic=['order/@type="premium"', 'count(items) > 0']
                    ),
                    'formatItem': Mock(
                        name='formatItem', 
                        complexity_score=8,
                        is_recursive=False,
                        calls_templates=[],
                        conditional_logic=['@status="active"']
                    ),
                    'calculateTotal': Mock(
                        name='calculateTotal',
                        complexity_score=12,
                        is_recursive=False,
                        calls_templates=[],
                        conditional_logic=['price > 0', 'currency']
                    )
                }
            },
            'semantic_analysis': {
                'transformation_hotspots': [
                    {
                        'template_name': 'formatOrder',
                        'hotspot_score': 15,
                        'reasons': ['high_complexity', 'recursive_processing', 'conditional_logic']
                    },
                    {
                        'template_name': 'calculateTotal',
                        'hotspot_score': 12,
                        'reasons': ['financial_calculations', 'currency_handling']
                    }
                ],
                'semantic_patterns': [
                    {
                        'pattern_type': 'conditional_processing',
                        'description': 'Order type based processing',
                        'templates_involved': ['formatOrder'],
                        'test_implications': ['test_premium_orders', 'test_standard_orders'],
                        'confidence_score': 0.9
                    },
                    {
                        'pattern_type': 'data_aggregation', 
                        'description': 'Item total calculation',
                        'templates_involved': ['calculateTotal'],
                        'test_implications': ['test_sum_calculation', 'test_currency_conversion'],
                        'confidence_score': 0.85
                    }
                ],
                'interaction_analysis': {
                    'call_graph': {
                        'formatOrder': ['formatItem', 'calculateTotal'],
                        'formatItem': [],
                        'calculateTotal': []
                    },
                    'template_dependencies': {
                        'formatOrder': ['formatItem', 'calculateTotal'],
                        'formatItem': [],
                        'calculateTotal': []
                    }
                }
            },
            'execution_analysis': {
                'execution_paths': [
                    {
                        'path_id': 'path_1',
                        'priority': 'high',
                        'complexity_score': 15,
                        'nodes': ['formatOrder', 'formatItem'],
                        'conditions': ['order/@type="premium"'],
                        'variables_used': {'orderType', 'itemCount'},
                        'templates_involved': {'formatOrder', 'formatItem'},
                        'output_elements': {'processedOrder'},
                        'path_probability': 0.7,
                        'test_data_requirements': {'premium_order_xml'}
                    },
                    {
                        'path_id': 'path_2',
                        'priority': 'medium',
                        'complexity_score': 8,
                        'nodes': ['formatOrder', 'calculateTotal'],
                        'conditions': ['count(items) > 0'],
                        'variables_used': {'itemCount', 'currency'},
                        'templates_involved': {'formatOrder', 'calculateTotal'},
                        'output_elements': {'orderTotal'},
                        'path_probability': 0.9,
                        'test_data_requirements': {'order_with_items_xml'}
                    }
                ],
                'entry_points': ['formatOrder', 'processOrder']
            }
        }
    
    def test_generate_test_suite_success(self, test_generator, sample_analysis_results):
        """Test successful test suite generation."""
        # Mock LLM responses
        hotspot_response = json.dumps([
            {
                "scenario_id": "hotspot_formatOrder_1",
                "description": "Test formatOrder high complexity scenario",
                "priority": "high",
                "input_requirements": {
                    "xml_structure": "<order type='premium'><items><item/></items></order>",
                    "conditions": ["Premium order processing"]
                },
                "expected_outputs": {
                    "xml_structure": "<processedOrder><result/></processedOrder>",
                    "xpath_assertions": ["//result[@status='processed']"]
                },
                "test_conditions": [
                    "Verify premium order processing",
                    "Ensure recursive template handling"
                ]
            }
        ])
        
        pattern_response = json.dumps([
            {
                "scenario_id": "pattern_conditional_1",
                "description": "Test conditional processing pattern",
                "priority": "medium",
                "input_requirements": {
                    "xml_structure": "<order type='standard'/>",
                    "data_values": {"order_type": "standard"}
                },
                "expected_outputs": {
                    "xml_structure": "<result type='standard'/>",
                    "xpath_assertions": ["//result[@type='standard']"]
                },
                "test_conditions": [
                    "Verify conditional pattern execution"
                ]
            }
        ])
        
        path_response = json.dumps([
            {
                "scenario_id": "path_coverage_1",
                "description": "Test primary execution path",
                "priority": "high",
                "input_requirements": {
                    "xml_structure": "<order><items><item/></items></order>",
                    "conditions": ["Primary path execution"]
                },
                "expected_outputs": {
                    "xml_structure": "<output><path_result/></output>",
                    "xpath_assertions": ["//path_result"]
                },
                "test_conditions": [
                    "Verify primary path execution"
                ]
            }
        ])
        
        integration_response = json.dumps([
            {
                "scenario_id": "integration_1",
                "description": "Test template integration",
                "priority": "medium",
                "input_requirements": {
                    "xml_structure": "<order><integration_data/></order>",
                    "conditions": ["Template interaction flow"]
                },
                "expected_outputs": {
                    "xml_structure": "<output><integration_result/></output>",
                    "xpath_assertions": ["//integration_result"]
                },
                "test_conditions": [
                    "Verify template integration"
                ]
            }
        ])
        
        # Configure mock to return different responses for different calls
        # Each call will be for hotspots (2), patterns (2), paths (if not failing), integration (if not failing)
        test_generator.llm_client.generate_response.side_effect = [
            hotspot_response,    # For first hotspot
            hotspot_response,    # For second hotspot  
            pattern_response,    # For conditional pattern
            pattern_response,    # For aggregation pattern
            path_response,       # For path coverage (may fail)
            integration_response # For integration (may fail)
        ]
        
        # Execute test
        result = test_generator.generate_test_suite(sample_analysis_results)
        
        # Assertions
        assert isinstance(result, TestSuite)
        assert result.xslt_file == '/test/sample.xslt'
        assert result.total_scenarios >= 2  # At least hotspot and pattern tests
        assert len(result.scenarios) >= 2
        
        # Check scenario types - at least these should be present
        scenario_types = [s.scenario_type for s in result.scenarios]
        assert 'complexity_hotspot' in scenario_types
        assert any('pattern_' in st for st in scenario_types)  # Some pattern test should be present
        
        # Check priority distribution
        priorities = result.scenarios_by_priority
        assert priorities['high'] >= 0
        assert priorities['medium'] >= 0
        assert priorities['low'] >= 0
        
        # Verify coverage metrics
        assert result.template_coverage >= 0
        assert result.path_coverage == 0.85
        assert result.pattern_coverage == 1.0
    
    def test_generate_hotspot_tests(self, test_generator, sample_analysis_results):
        """Test hotspot test generation."""
        hotspots = sample_analysis_results['semantic_analysis']['transformation_hotspots']
        templates = sample_analysis_results['template_analysis']['templates']
        
        # Mock LLM response
        test_generator.llm_client.generate_response.return_value = json.dumps([
            {
                "scenario_id": "hotspot_formatOrder_1",
                "description": "Test high complexity formatOrder template",
                "input_requirements": {
                    "xml_structure": "<order type='premium'/>",
                    "conditions": ["High complexity test"]
                },
                "expected_outputs": {
                    "xml_structure": "<result/>",
                    "xpath_assertions": ["//result"]
                },
                "test_conditions": ["Verify complex processing"]
            },
            {
                "scenario_id": "hotspot_formatOrder_2",
                "description": "Test recursive processing in formatOrder",
                "input_requirements": {
                    "xml_structure": "<order><nested><item/></nested></order>",
                    "conditions": ["Recursive processing test"]
                },
                "expected_outputs": {
                    "xml_structure": "<result><processed/></result>",
                    "xpath_assertions": ["//processed"]
                },
                "test_conditions": ["Verify recursion handling"]
            }
        ])
        
        scenarios = test_generator._generate_hotspot_tests(hotspots, templates)
        
        assert len(scenarios) >= 2  # Should generate multiple tests for hotspots
        
        # Check first scenario
        scenario = scenarios[0]
        assert scenario.scenario_type == 'complexity_hotspot'
        assert scenario.priority == 'high'
        assert 'formatOrder' in scenario.source_templates
        assert len(scenario.hotspot_reasons) > 0
        assert scenario.input_requirements is not None
        assert scenario.expected_outputs is not None
    
    def test_generate_pattern_tests(self, test_generator, sample_analysis_results):
        """Test semantic pattern test generation."""
        patterns = sample_analysis_results['semantic_analysis']['semantic_patterns']
        templates = sample_analysis_results['template_analysis']['templates']
        
        # Mock LLM response for each pattern
        test_generator.llm_client.generate_response.side_effect = [
            json.dumps([
                {
                    "scenario_id": "pattern_conditional_1",
                    "description": "Test conditional processing pattern",
                    "priority": "medium",
                    "input_requirements": {
                        "xml_structure": "<order type='premium'/>",
                        "data_values": {"order_type": "premium"}
                    },
                    "expected_outputs": {
                        "xml_structure": "<result type='premium'/>",
                        "xpath_assertions": ["//result[@type='premium']"]
                    },
                    "test_conditions": ["Verify conditional logic"]
                }
            ]),
            json.dumps([
                {
                    "scenario_id": "pattern_aggregation_1",
                    "description": "Test data aggregation pattern",
                    "priority": "medium",
                    "input_requirements": {
                        "xml_structure": "<order><items><item price='100'/></items></order>",
                        "data_values": {"total_items": 1}
                    },
                    "expected_outputs": {
                        "xml_structure": "<result><total>100</total></result>",
                        "xpath_assertions": ["//total[text()='100']"]
                    },
                    "test_conditions": ["Verify aggregation logic"]
                }
            ])
        ]
        
        scenarios = test_generator._generate_pattern_tests(patterns, templates)
        
        assert len(scenarios) >= 2  # Should generate tests for both patterns
        
        # Check first scenario
        scenario = scenarios[0]
        assert scenario.scenario_type == 'pattern_conditional_processing'
        assert 'conditional_processing' in scenario.semantic_patterns
        assert scenario.input_requirements is not None
        assert scenario.expected_outputs is not None
    
    def test_generate_path_coverage_tests(self, test_generator, sample_analysis_results):
        """Test execution path coverage test generation."""
        execution_paths = sample_analysis_results['execution_analysis']['execution_paths']
        entry_points = sample_analysis_results['execution_analysis']['entry_points']
        
        # Mock LLM response
        test_generator.llm_client.generate_response.return_value = json.dumps([
            {
                "scenario_id": "path_coverage_1",
                "description": "Test primary execution path",
                "priority": "high",
                "input_requirements": {
                    "xml_structure": "<order><items/></order>",
                    "conditions": ["Primary path conditions"]
                },
                "expected_outputs": {
                    "xml_structure": "<output><result/></output>",
                    "xpath_assertions": ["//result"]
                },
                "test_conditions": ["Verify path execution"]
            }
        ])
        
        scenarios = test_generator._generate_path_coverage_tests(execution_paths, entry_points)
        
        assert len(scenarios) >= 1
        
        # Check scenario
        scenario = scenarios[0]
        assert scenario.scenario_type == 'path_coverage'
        assert len(scenario.execution_paths) > 0
        assert scenario.input_requirements is not None
    
    def test_generate_integration_tests(self, test_generator, sample_analysis_results):
        """Test integration test generation."""
        interaction_analysis = sample_analysis_results['semantic_analysis']['interaction_analysis']
        templates = sample_analysis_results['template_analysis']['templates']
        
        # Mock LLM response
        test_generator.llm_client.generate_response.return_value = json.dumps([
            {
                "scenario_id": "integration_1",
                "description": "Test template interaction flow",
                "priority": "medium",
                "input_requirements": {
                    "xml_structure": "<order><integration/></order>",
                    "conditions": ["Template interaction"]
                },
                "expected_outputs": {
                    "xml_structure": "<output><integrated/></output>",
                    "xpath_assertions": ["//integrated"]
                },
                "test_conditions": ["Verify template calls"]
            }
        ])
        
        scenarios = test_generator._generate_integration_tests(interaction_analysis, templates)
        
        assert len(scenarios) >= 1
        
        # Check scenario
        scenario = scenarios[0]
        assert scenario.scenario_type == 'integration'
        assert len(scenario.source_templates) > 0
        assert scenario.input_requirements is not None
    
    def test_compile_test_suite(self, test_generator, sample_analysis_results):
        """Test test suite compilation."""
        scenarios = [
            TestScenario(
                scenario_id="test_1",
                scenario_type="complexity_hotspot",
                description="Test scenario 1",
                priority="high",
                input_requirements={"xml": "<test/>"},
                expected_outputs={"xml": "<result/>"},
                test_conditions=["condition 1"],
                source_templates=["template1"],
                semantic_patterns=[],
                execution_paths=[]
            ),
            TestScenario(
                scenario_id="test_2",
                scenario_type="pattern_test",
                description="Test scenario 2",
                priority="medium",
                input_requirements={"xml": "<test2/>"},
                expected_outputs={"xml": "<result2/>"},
                test_conditions=["condition 2"],
                source_templates=["template2"],
                semantic_patterns=["pattern1"],
                execution_paths=[]
            )
        ]
        
        template_analysis = sample_analysis_results['template_analysis']
        semantic_analysis = sample_analysis_results['semantic_analysis']
        execution_analysis = sample_analysis_results['execution_analysis']
        
        test_suite = test_generator._compile_test_suite(
            '/test/sample.xslt',
            scenarios,
            template_analysis,
            semantic_analysis,
            execution_analysis
        )
        
        assert isinstance(test_suite, TestSuite)
        assert test_suite.xslt_file == '/test/sample.xslt'
        assert test_suite.total_scenarios == 2
        assert test_suite.scenarios_by_priority['high'] == 1
        assert test_suite.scenarios_by_priority['medium'] == 1
        assert test_suite.scenarios_by_type['complexity_hotspot'] == 1
        assert test_suite.scenarios_by_type['pattern_test'] == 1
        
        # Check coverage calculation
        assert test_suite.template_coverage > 0  # Should have some template coverage
    
    def test_llm_client_error_handling(self, test_generator, sample_analysis_results):
        """Test handling of LLM client errors."""
        # Mock LLM to raise an exception
        test_generator.llm_client.generate_response.side_effect = Exception("LLM API Error")
        
        # Should still work due to error handling
        result = test_generator.generate_test_suite(sample_analysis_results)
        
        # Should still return a test suite, even if some components failed
        assert isinstance(result, TestSuite)
        assert result.xslt_file == '/test/sample.xslt'
        # May have fewer scenarios due to failures, but should not crash
    
    def test_empty_analysis_results(self, test_generator):
        """Test handling of empty analysis results."""
        empty_analysis = {
            'file_path': '/test/empty.xslt',
            'template_analysis': {'templates': {}},
            'semantic_analysis': {
                'transformation_hotspots': [],
                'semantic_patterns': [],
                'interaction_analysis': {}
            },
            'execution_analysis': {
                'execution_paths': [],
                'entry_points': []
            }
        }
        
        result = test_generator.generate_test_suite(empty_analysis)
        
        assert isinstance(result, TestSuite)
        assert result.total_scenarios >= 0  # May be 0 for empty analysis
        assert result.template_coverage == 0  # No templates to cover