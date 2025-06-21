"""Tests for TestCaseFormatter component."""

import pytest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock

from xslt_test_generator.agents.test_case_formatter import (
    TestCaseFormatter, FormattedTestCase
)
from xslt_test_generator.agents.intelligent_test_generator import (
    TestScenario, TestSuite
)


class TestTestCaseFormatter:
    """Test TestCaseFormatter functionality."""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return TestCaseFormatter()
    
    @pytest.fixture
    def sample_test_suite(self):
        """Create sample test suite."""
        scenarios = [
            TestScenario(
                scenario_id="hotspot_formatOrder_1",
                scenario_type="complexity_hotspot",
                description="Test high complexity formatOrder template",
                priority="high",
                input_requirements={
                    "xml_structure": "<order type='premium'><items><item id='1'/></items></order>",
                    "data_values": {"order_type": "premium", "item_count": 1},
                    "conditions": ["Premium order processing"]
                },
                expected_outputs={
                    "xml_structure": "<processedOrder status='completed'><result/></processedOrder>",
                    "data_values": {"status": "completed"},
                    "xpath_assertions": ["//result[@status='completed']", "//processedOrder[@status]"]
                },
                test_conditions=[
                    "Verify premium order processing logic",
                    "Ensure recursive template handling works correctly",
                    "Validate complex conditional paths"
                ],
                source_templates=["formatOrder", "processItem"],
                semantic_patterns=["recursive_processing"],
                execution_paths=["premium_path_1"],
                hotspot_reasons=["high_complexity", "recursive_processing"]
            ),
            TestScenario(
                scenario_id="pattern_conditional_1",
                scenario_type="pattern_conditional",
                description="Test conditional processing pattern",
                priority="medium",
                input_requirements={
                    "xml_structure": "<order type='standard'><discount>10</discount></order>",
                    "data_values": {"order_type": "standard", "discount": 10},
                    "conditions": ["Standard order with discount"]
                },
                expected_outputs={
                    "xml_structure": "<result type='standard'><discountApplied>10</discountApplied></result>",
                    "data_values": {"discount_applied": 10},
                    "xpath_assertions": ["//result[@type='standard']", "//discountApplied[text()='10']"]
                },
                test_conditions=[
                    "Verify conditional pattern execution",
                    "Ensure discount calculation is correct"
                ],
                source_templates=["formatOrder"],
                semantic_patterns=["conditional_processing"],
                execution_paths=["standard_path_1"]
            ),
            TestScenario(
                scenario_id="integration_1",
                scenario_type="integration",
                description="Test template interaction flow",
                priority="medium",
                input_requirements={
                    "xml_structure": "<order><items><item price='100'/><item price='200'/></items></order>",
                    "conditions": ["Multiple item processing"]
                },
                expected_outputs={
                    "xml_structure": "<output><totalPrice>300</totalPrice><itemCount>2</itemCount></output>",
                    "xpath_assertions": ["//totalPrice[text()='300']", "//itemCount[text()='2']"]
                },
                test_conditions=[
                    "Verify template integration works",
                    "Ensure data flows correctly between templates",
                    "Validate aggregation calculations"
                ],
                source_templates=["formatOrder", "calculateTotal", "processItem"],
                semantic_patterns=["data_aggregation"],
                execution_paths=["integration_path_1"]
            )
        ]
        
        return TestSuite(
            xslt_file="/test/OrderProcess.xslt",
            total_scenarios=3,
            scenarios_by_priority={"high": 1, "medium": 2, "low": 0},
            scenarios_by_type={"complexity_hotspot": 1, "pattern_conditional": 1, "integration": 1},
            scenarios=scenarios,
            template_coverage=0.85,
            path_coverage=0.78,
            pattern_coverage=1.0,
            estimated_execution_time="6s"
        )
    
    def test_format_test_suite_all_formats(self, formatter, sample_test_suite):
        """Test formatting to all supported formats."""
        output_formats = ['cucumber', 'pytest', 'xml_unit', 'json']
        
        result = formatter.format_test_suite(sample_test_suite, output_formats)
        
        # Should have all requested formats
        assert set(result.keys()) == set(output_formats)
        
        # Each format should have test cases
        for format_name, test_cases in result.items():
            assert len(test_cases) > 0
            assert all(isinstance(tc, FormattedTestCase) for tc in test_cases)
            assert all(tc.format_type == format_name for tc in test_cases)
    
    def test_format_to_cucumber(self, formatter, sample_test_suite):
        """Test Cucumber/Gherkin format generation."""
        result = formatter._format_to_cucumber(sample_test_suite)
        
        assert len(result) > 0
        
        # Should have separate feature files for different scenario types
        file_names = [tc.file_name for tc in result]
        assert any('complexity_hotspot' in name for name in file_names)
        assert any('pattern_conditional' in name for name in file_names)
        assert any('integration' in name for name in file_names)
        
        # Check first test case
        cucumber_test = result[0]
        assert cucumber_test.format_type == 'cucumber'
        assert cucumber_test.file_name.endswith('.feature')
        
        # Verify Gherkin content structure
        content = cucumber_test.content
        assert 'Feature:' in content
        assert 'Background:' in content
        assert 'Scenario:' in content
        assert 'Given' in content
        assert 'When' in content
        assert 'Then' in content
        
        # Check for XSLT-specific content
        assert 'XSLT transformation' in content
        assert 'OrderProcess' in content
        
        # Verify scenario priorities are tagged
        assert '@high_priority' in content or '@medium_priority' in content
        
        # Check metadata
        assert 'scenario_count' in cucumber_test.metadata
        assert 'priority_distribution' in cucumber_test.metadata
    
    def test_generate_cucumber_scenario(self, formatter):
        """Test individual Cucumber scenario generation."""
        scenario = TestScenario(
            scenario_id="test_scenario_1",
            scenario_type="complexity_hotspot",
            description="Test complex transformation scenario",
            priority="high",
            input_requirements={
                "xml_structure": "<order type='premium'/>",
                "data_values": {"type": "premium"},
                "conditions": ["Premium processing"]
            },
            expected_outputs={
                "xml_structure": "<result status='processed'/>",
                "data_values": {"status": "processed"},
                "xpath_assertions": ["//result[@status='processed']"]
            },
            test_conditions=[
                "Verify premium processing logic",
                "Ensure status is set correctly"
            ],
            source_templates=["formatOrder"],
            semantic_patterns=["premium_processing"],
            execution_paths=["premium_path"]
        )
        
        lines = formatter._generate_cucumber_scenario(scenario)
        
        # Check structure
        assert any('@high_priority' in line for line in lines)
        assert any('@complexity_hotspot' in line for line in lines)
        assert any('Scenario: Test complex transformation scenario' in line for line in lines)
        
        # Check Given/When/Then structure
        given_lines = [line for line in lines if line.strip().startswith('Given')]
        when_lines = [line for line in lines if line.strip().startswith('When')]
        then_lines = [line for line in lines if line.strip().startswith('Then')]
        and_lines = [line for line in lines if line.strip().startswith('And')]
        
        assert len(given_lines) >= 1
        assert len(when_lines) >= 1
        assert len(then_lines) >= 1
        
        # Check content includes input/output requirements
        content = ' '.join(lines)
        assert 'premium' in content
        assert 'processed' in content
        assert 'XPath' in content
    
    def test_format_to_pytest(self, formatter, sample_test_suite):
        """Test pytest format generation."""
        result = formatter._format_to_pytest(sample_test_suite)
        
        assert len(result) == 1  # Single pytest file
        
        pytest_test = result[0]
        assert pytest_test.format_type == 'pytest'
        assert pytest_test.file_name == 'test_OrderProcess.py'
        
        # Check Python/pytest content
        content = pytest_test.content
        assert 'import pytest' in content
        assert 'class TestXSLTTransformation:' in content
        assert '@pytest.fixture' in content
        assert 'def xslt_processor(self):' in content
        
        # Check test methods are generated
        assert 'def test_hotspot_formatOrder_1(' in content
        assert 'def test_pattern_conditional_1(' in content
        assert 'def test_integration_1(' in content
        
        # Check pytest markers
        assert '@pytest.mark.high_priority' in content
        assert '@pytest.mark.medium_priority' in content
        assert '@pytest.mark.complexity_hotspot' in content
        
        # Check test structure (Arrange/Act/Assert)
        assert '# Arrange' in content
        assert '# Act' in content
        assert '# Assert' in content
        
        # Check metadata
        assert 'total_tests' in pytest_test.metadata
        assert 'test_classes' in pytest_test.metadata
    
    def test_generate_pytest_method(self, formatter):
        """Test individual pytest method generation."""
        scenario = TestScenario(
            scenario_id="test-scenario-1",
            scenario_type="complexity_hotspot",
            description="Test complex scenario with special characters",
            priority="high",
            input_requirements={
                "xml_structure": "<order type='premium'/>",
                "data_values": {"type": "premium"}
            },
            expected_outputs={
                "xml_structure": "<result/>",
                "data_values": {"status": "completed"}
            },
            test_conditions=[
                "Verify complex processing",
                "Ensure proper error handling"
            ],
            source_templates=["formatOrder"],
            semantic_patterns=[],
            execution_paths=[]
        )
        
        lines = formatter._generate_pytest_method(scenario)
        
        # Check method signature (should replace hyphens with underscores)
        assert any('def test_test_scenario_1(' in line for line in lines)
        
        # Check pytest markers
        assert any('@pytest.mark.high_priority' in line for line in lines)
        assert any('@pytest.mark.complexity_hotspot' in line for line in lines)
        
        # Check docstring
        assert any('"""Test complex scenario with special characters"""' in line for line in lines)
        
        # Check test structure
        content = ' '.join(lines)
        assert 'input_requirements' in content
        assert 'expected_outputs' in content
        assert 'create_test_input' in content
        assert 'validate_transformation_output' in content
    
    def test_format_to_json(self, formatter, sample_test_suite):
        """Test JSON format generation."""
        result = formatter._format_to_json(sample_test_suite)
        
        assert len(result) == 1  # Single JSON file
        
        json_test = result[0]
        assert json_test.format_type == 'json'
        assert json_test.file_name == 'OrderProcess_test_specification.json'
        
        # Parse JSON content
        json_data = json.loads(json_test.content)
        
        # Check top-level structure
        assert 'test_suite_metadata' in json_data
        assert 'test_scenarios' in json_data
        
        # Check metadata
        metadata = json_data['test_suite_metadata']
        assert metadata['xslt_file'] == '/test/OrderProcess.xslt'
        assert metadata['total_scenarios'] == 3
        assert 'scenarios_by_priority' in metadata
        assert 'scenarios_by_type' in metadata
        assert 'coverage_metrics' in metadata
        
        # Check scenarios
        scenarios = json_data['test_scenarios']
        assert len(scenarios) == 3
        
        # Check first scenario structure
        scenario = scenarios[0]
        required_fields = [
            'scenario_id', 'scenario_type', 'description', 'priority',
            'input_requirements', 'expected_outputs', 'test_conditions',
            'analysis_context'
        ]
        for field in required_fields:
            assert field in scenario
        
        # Check analysis context
        context = scenario['analysis_context']
        assert 'source_templates' in context
        assert 'semantic_patterns' in context
        assert 'execution_paths' in context
        assert 'hotspot_reasons' in context
        
        # Check metadata
        assert 'format' in json_test.metadata
        assert 'total_scenarios' in json_test.metadata
    
    def test_format_to_xml_unit(self, formatter, sample_test_suite):
        """Test XML unit test format generation."""
        result = formatter._format_to_xml_unit(sample_test_suite)
        
        assert len(result) == 1  # Single XML file
        
        xml_test = result[0]
        assert xml_test.format_type == 'xml_unit'
        assert xml_test.file_name == 'OrderProcess_unit_tests.xml'
        
        # Parse XML content
        root = ET.fromstring(xml_test.content)
        
        # Check root element
        assert root.tag == 'TestSuite'
        assert root.get('xslt_file') == '/test/OrderProcess.xslt'
        assert root.get('total_scenarios') == '3'
        
        # Check metadata
        metadata = root.find('Metadata')
        assert metadata is not None
        
        coverage = metadata.find('Coverage')
        assert coverage is not None
        assert coverage.get('template_coverage') == '0.85'
        assert coverage.get('path_coverage') == '0.78'
        assert coverage.get('pattern_coverage') == '1.0'
        
        # Check test scenarios
        scenarios_elem = root.find('TestScenarios')
        assert scenarios_elem is not None
        
        scenarios = scenarios_elem.findall('TestScenario')
        assert len(scenarios) == 3
        
        # Check first scenario
        scenario = scenarios[0]
        assert scenario.get('id') == 'hotspot_formatOrder_1'
        assert scenario.get('type') == 'complexity_hotspot'
        assert scenario.get('priority') == 'high'
        
        # Check scenario elements
        desc = scenario.find('Description')
        assert desc is not None
        assert desc.text == 'Test high complexity formatOrder template'
        
        inputs = scenario.find('InputRequirements')
        assert inputs is not None
        assert inputs.text is not None
        
        outputs = scenario.find('ExpectedOutputs')
        assert outputs is not None
        assert outputs.text is not None
        
        conditions = scenario.find('TestConditions')
        assert conditions is not None
        
        condition_elems = conditions.findall('Condition')
        assert len(condition_elems) >= 2  # Should have multiple test conditions
        
        # Check metadata
        assert 'format' in xml_test.metadata
        assert 'total_scenarios' in xml_test.metadata
    
    def test_priority_distribution_calculation(self, formatter):
        """Test priority distribution calculation."""
        scenarios = [
            Mock(priority='high'),
            Mock(priority='high'),
            Mock(priority='medium'),
            Mock(priority='low')
        ]
        
        distribution = formatter._get_priority_distribution(scenarios)
        
        assert distribution['high'] == 2
        assert distribution['medium'] == 1
        assert distribution['low'] == 1
    
    def test_unsupported_format(self, formatter, sample_test_suite):
        """Test handling of unsupported output format."""
        result = formatter.format_test_suite(sample_test_suite, ['unsupported_format'])
        
        # Should return empty result for unsupported format
        assert 'unsupported_format' not in result or len(result['unsupported_format']) == 0
    
    def test_empty_test_suite(self, formatter):
        """Test formatting empty test suite."""
        empty_suite = TestSuite(
            xslt_file="/test/empty.xslt",
            total_scenarios=0,
            scenarios_by_priority={"high": 0, "medium": 0, "low": 0},
            scenarios_by_type={},
            scenarios=[],
            template_coverage=0.0,
            path_coverage=0.0,
            pattern_coverage=0.0,
            estimated_execution_time="0s"
        )
        
        result = formatter.format_test_suite(empty_suite, ['cucumber', 'pytest'])
        
        # Should handle empty suite gracefully
        assert isinstance(result, dict)
        # May have empty or minimal content for empty suite
    
    def test_complex_scenario_data(self, formatter):
        """Test formatting with complex input/output data."""
        scenario = TestScenario(
            scenario_id="complex_scenario_1",
            scenario_type="complex_test",
            description="Test with complex nested data structures",
            priority="high",
            input_requirements={
                "xml_structure": "<order><customer><name>John Doe</name><address><street>123 Main St</street></address></customer></order>",
                "data_values": {
                    "customer": {
                        "name": "John Doe",
                        "preferences": ["premium", "express"],
                        "discount_rate": 0.15
                    }
                },
                "conditions": ["Complex nested data", "Multiple value types"]
            },
            expected_outputs={
                "xml_structure": "<result><processedCustomer><name>John Doe</name><discountApplied>0.15</discountApplied></processedCustomer></result>",
                "xpath_assertions": [
                    "//processedCustomer/name[text()='John Doe']",
                    "//discountApplied[text()='0.15']",
                    "count(//processedCustomer) = 1"
                ]
            },
            test_conditions=[
                "Verify complex nested structure processing",
                "Ensure all customer data is preserved",
                "Validate discount calculation with decimal precision"
            ],
            source_templates=["processCustomer", "calculateDiscount"],
            semantic_patterns=["nested_processing", "financial_calculation"],
            execution_paths=["customer_processing_path"]
        )
        
        test_suite = TestSuite(
            xslt_file="/test/complex.xslt",
            total_scenarios=1,
            scenarios_by_priority={"high": 1, "medium": 0, "low": 0},
            scenarios_by_type={"complex_test": 1},
            scenarios=[scenario],
            template_coverage=1.0,
            path_coverage=1.0,
            pattern_coverage=1.0,
            estimated_execution_time="2s"
        )
        
        # Test all formats handle complex data
        result = formatter.format_test_suite(test_suite, ['cucumber', 'pytest', 'json', 'xml_unit'])
        
        for format_name, test_cases in result.items():
            assert len(test_cases) > 0
            
            # Check that complex data is preserved in content
            content = test_cases[0].content
            
            if format_name == 'json':
                # JSON should preserve complex data structures
                json_data = json.loads(content)
                scenario_data = json_data['test_scenarios'][0]
                assert 'customer' in str(scenario_data['input_requirements'])
                assert 'discount_rate' in str(scenario_data['input_requirements'])
            
            # All formats should contain key identifying information
            assert 'John Doe' in content
            assert 'complex' in content.lower() or 'nested' in content.lower()