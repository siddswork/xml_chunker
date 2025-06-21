"""Test Case Formatter - Converts intelligent test scenarios into executable test formats."""

from typing import Dict, List, Any, Optional
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass

from ..core.base import LoggerMixin
from .intelligent_test_generator import TestSuite, TestScenario


@dataclass
class FormattedTestCase:
    """Represents a test case in a specific format."""
    test_id: str
    format_type: str  # 'cucumber', 'pytest', 'xml_unit', 'json'
    content: str
    file_name: str
    metadata: Dict[str, Any]


class TestCaseFormatter(LoggerMixin):
    """
    Formats intelligent test scenarios into various executable test formats.
    
    Supports multiple output formats:
    - Cucumber/Gherkin (.feature files)
    - Pytest test cases (.py files) 
    - XML unit tests (.xml files)
    - JSON test specifications (.json files)
    """
    
    def __init__(self):
        super().__init__()
    
    def format_test_suite(self, test_suite: TestSuite, output_formats: List[str]) -> Dict[str, List[FormattedTestCase]]:
        """
        Format complete test suite into multiple output formats.
        
        Args:
            test_suite: Intelligent test suite to format
            output_formats: List of desired formats ['cucumber', 'pytest', 'xml_unit', 'json']
            
        Returns:
            Dictionary mapping format names to formatted test cases
        """
        formatted_tests = {}
        
        for format_type in output_formats:
            self.logger.info(f"Formatting test suite to {format_type} format")
            
            if format_type in ['cucumber', 'gherkin']:
                formatted_tests[format_type] = self._format_to_cucumber(test_suite)
            elif format_type == 'pytest':
                formatted_tests[format_type] = self._format_to_pytest(test_suite)
            elif format_type == 'xml_unit':
                formatted_tests[format_type] = self._format_to_xml_unit(test_suite)
            elif format_type == 'json':
                formatted_tests[format_type] = self._format_to_json(test_suite)
            else:
                self.logger.warning(f"Unsupported format: {format_type}")
        
        return formatted_tests
    
    def _format_to_cucumber(self, test_suite: TestSuite) -> List[FormattedTestCase]:
        """Format test suite as Cucumber/Gherkin feature files."""
        test_cases = []
        
        # Group scenarios by type for better organization
        scenarios_by_type = {}
        for scenario in test_suite.scenarios:
            scenario_type = scenario.scenario_type
            if scenario_type not in scenarios_by_type:
                scenarios_by_type[scenario_type] = []
            scenarios_by_type[scenario_type].append(scenario)
        
        # Create feature file for each scenario type
        for scenario_type, scenarios in scenarios_by_type.items():
            feature_content = self._generate_cucumber_feature(scenario_type, scenarios, test_suite)
            
            test_case = FormattedTestCase(
                test_id=f"feature_{scenario_type}",
                format_type='cucumber',
                content=feature_content,
                file_name=f"{scenario_type}_tests.feature",
                metadata={
                    'scenario_count': len(scenarios),
                    'scenario_type': scenario_type,
                    'priority_distribution': self._get_priority_distribution(scenarios)
                }
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_cucumber_feature(self, scenario_type: str, scenarios: List[TestScenario], test_suite: TestSuite) -> str:
        """Generate Cucumber feature file content."""
        xslt_name = Path(test_suite.xslt_file).stem
        
        feature_lines = [
            f"Feature: {scenario_type.replace('_', ' ').title()} Tests for {xslt_name}",
            f"  As a QA engineer",
            f"  I want to test {scenario_type.replace('_', ' ')} scenarios",
            f"  So that I can ensure XSLT transformation quality",
            "",
            f"  Background:",
            f"    Given the XSLT transformation file \"{test_suite.xslt_file}\"",
            f"    And the transformation engine is initialized",
            ""
        ]
        
        for scenario in scenarios:
            feature_lines.extend(self._generate_cucumber_scenario(scenario))
            feature_lines.append("")
        
        return "\n".join(feature_lines)
    
    def _generate_cucumber_scenario(self, scenario: TestScenario) -> List[str]:
        """Generate individual Cucumber scenario."""
        lines = [
            f"  @{scenario.priority}_priority @{scenario.scenario_type}",
            f"  Scenario: {scenario.description}",
        ]
        
        # Add Given steps for input requirements
        if scenario.input_requirements:
            if 'xml_structure' in scenario.input_requirements:
                lines.append(f"    Given an input XML with structure \"{scenario.input_requirements['xml_structure']}\"")
            if 'data_values' in scenario.input_requirements:
                lines.append(f"    And input data values: {json.dumps(scenario.input_requirements['data_values'])}")
            if 'conditions' in scenario.input_requirements:
                for condition in scenario.input_requirements['conditions']:
                    lines.append(f"    And input condition: {condition}")
        
        # Add When step for transformation
        lines.append(f"    When the XSLT transformation is executed")
        
        # Add Then steps for expected outputs
        if scenario.expected_outputs:
            if 'xml_structure' in scenario.expected_outputs:
                lines.append(f"    Then the output should have structure \"{scenario.expected_outputs['xml_structure']}\"")
            if 'data_values' in scenario.expected_outputs:
                lines.append(f"    And output should contain values: {json.dumps(scenario.expected_outputs['data_values'])}")
            if 'xpath_assertions' in scenario.expected_outputs:
                for xpath in scenario.expected_outputs['xpath_assertions']:
                    lines.append(f"    And XPath \"{xpath}\" should be valid")
        
        # Add test condition validations
        for condition in scenario.test_conditions:
            lines.append(f"    And {condition}")
        
        return lines
    
    def _format_to_pytest(self, test_suite: TestSuite) -> List[FormattedTestCase]:
        """Format test suite as pytest test cases."""
        test_cases = []
        
        # Generate main test file
        pytest_content = self._generate_pytest_file(test_suite)
        
        test_case = FormattedTestCase(
            test_id="pytest_suite",
            format_type='pytest',
            content=pytest_content,
            file_name=f"test_{Path(test_suite.xslt_file).stem}.py",
            metadata={
                'total_tests': len(test_suite.scenarios),
                'test_classes': len(set(s.scenario_type for s in test_suite.scenarios)),
                'priority_distribution': test_suite.scenarios_by_priority
            }
        )
        test_cases.append(test_case)
        
        return test_cases
    
    def _generate_pytest_file(self, test_suite: TestSuite) -> str:
        """Generate pytest test file content."""
        xslt_name = Path(test_suite.xslt_file).stem
        
        lines = [
            f'"""Intelligent test cases for {xslt_name} XSLT transformation."""',
            "",
            "import pytest",
            "import xml.etree.ElementTree as ET",
            "from pathlib import Path",
            "import json",
            "",
            f'XSLT_FILE = "{test_suite.xslt_file}"',
            "",
            "",
            "class TestXSLTTransformation:",
            f'    """Test cases generated using intelligent analysis."""',
            "",
            "    @pytest.fixture",
            "    def xslt_processor(self):",
            '        """Initialize XSLT processor."""',
            "        # TODO: Initialize your XSLT processor here",
            "        return None",
            "",
        ]
        
        # Group scenarios by type for organized test methods
        scenarios_by_type = {}
        for scenario in test_suite.scenarios:
            scenario_type = scenario.scenario_type
            if scenario_type not in scenarios_by_type:
                scenarios_by_type[scenario_type] = []
            scenarios_by_type[scenario_type].append(scenario)
        
        # Generate test methods for each scenario
        for scenario in test_suite.scenarios:
            method_lines = self._generate_pytest_method(scenario)
            lines.extend(method_lines)
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_pytest_method(self, scenario: TestScenario) -> List[str]:
        """Generate individual pytest test method."""
        method_name = f"test_{scenario.scenario_id.replace('-', '_')}"
        
        lines = [
            f"    @pytest.mark.{scenario.priority}_priority",
            f"    @pytest.mark.{scenario.scenario_type}",
            f"    def {method_name}(self, xslt_processor):",
            f'        """{scenario.description}"""',
            "",
            "        # Arrange",
        ]
        
        # Add input setup
        if scenario.input_requirements:
            lines.append(f"        input_requirements = {json.dumps(scenario.input_requirements, indent=8)}")
            lines.append("        # TODO: Create input XML based on requirements")
            lines.append("        input_xml = create_test_input(input_requirements)")
            lines.append("")
        
        # Add action
        lines.extend([
            "        # Act", 
            "        result = xslt_processor.transform(input_xml)",
            ""
        ])
        
        # Add assertions
        lines.append("        # Assert")
        if scenario.expected_outputs:
            lines.append(f"        expected_outputs = {json.dumps(scenario.expected_outputs, indent=8)}")
            lines.append("        # TODO: Validate outputs based on expectations")
            lines.append("        validate_transformation_output(result, expected_outputs)")
        
        for condition in scenario.test_conditions:
            lines.append(f"        # {condition}")
            lines.append("        # TODO: Implement specific test condition")
        
        return lines
    
    def _format_to_json(self, test_suite: TestSuite) -> List[FormattedTestCase]:
        """Format test suite as JSON specification."""
        test_cases = []
        
        # Convert test suite to JSON format
        json_content = {
            "test_suite_metadata": {
                "xslt_file": test_suite.xslt_file,
                "total_scenarios": test_suite.total_scenarios,
                "scenarios_by_priority": test_suite.scenarios_by_priority,
                "scenarios_by_type": test_suite.scenarios_by_type,
                "coverage_metrics": {
                    "template_coverage": test_suite.template_coverage,
                    "path_coverage": test_suite.path_coverage,
                    "pattern_coverage": test_suite.pattern_coverage
                },
                "estimated_execution_time": test_suite.estimated_execution_time
            },
            "test_scenarios": []
        }
        
        for scenario in test_suite.scenarios:
            scenario_json = {
                "scenario_id": scenario.scenario_id,
                "scenario_type": scenario.scenario_type,
                "description": scenario.description,
                "priority": scenario.priority,
                "input_requirements": scenario.input_requirements,
                "expected_outputs": scenario.expected_outputs,
                "test_conditions": scenario.test_conditions,
                "analysis_context": {
                    "source_templates": scenario.source_templates,
                    "semantic_patterns": scenario.semantic_patterns,
                    "execution_paths": scenario.execution_paths,
                    "hotspot_reasons": scenario.hotspot_reasons
                }
            }
            json_content["test_scenarios"].append(scenario_json)
        
        json_string = json.dumps(json_content, indent=2)
        
        test_case = FormattedTestCase(
            test_id="json_specification",
            format_type='json',
            content=json_string,
            file_name=f"{Path(test_suite.xslt_file).stem}_test_specification.json",
            metadata={
                "format": "JSON Test Specification",
                "schema_version": "1.0",
                "total_scenarios": len(test_suite.scenarios)
            }
        )
        test_cases.append(test_case)
        
        return test_cases
    
    def _format_to_xml_unit(self, test_suite: TestSuite) -> List[FormattedTestCase]:
        """Format test suite as XML unit test specification."""
        test_cases = []
        
        # Create XML structure
        root = ET.Element("TestSuite")
        root.set("xslt_file", test_suite.xslt_file)
        root.set("total_scenarios", str(test_suite.total_scenarios))
        
        # Add metadata
        metadata = ET.SubElement(root, "Metadata")
        coverage = ET.SubElement(metadata, "Coverage")
        coverage.set("template_coverage", str(test_suite.template_coverage))
        coverage.set("path_coverage", str(test_suite.path_coverage))
        coverage.set("pattern_coverage", str(test_suite.pattern_coverage))
        
        # Add scenarios
        scenarios_elem = ET.SubElement(root, "TestScenarios")
        
        for scenario in test_suite.scenarios:
            scenario_elem = ET.SubElement(scenarios_elem, "TestScenario")
            scenario_elem.set("id", scenario.scenario_id)
            scenario_elem.set("type", scenario.scenario_type)
            scenario_elem.set("priority", scenario.priority)
            
            desc = ET.SubElement(scenario_elem, "Description")
            desc.text = scenario.description
            
            # Input requirements
            if scenario.input_requirements:
                inputs = ET.SubElement(scenario_elem, "InputRequirements")
                inputs.text = json.dumps(scenario.input_requirements)
            
            # Expected outputs
            if scenario.expected_outputs:
                outputs = ET.SubElement(scenario_elem, "ExpectedOutputs")
                outputs.text = json.dumps(scenario.expected_outputs)
            
            # Test conditions
            if scenario.test_conditions:
                conditions = ET.SubElement(scenario_elem, "TestConditions")
                for condition in scenario.test_conditions:
                    cond_elem = ET.SubElement(conditions, "Condition")
                    cond_elem.text = condition
        
        xml_string = ET.tostring(root, encoding='unicode')
        
        test_case = FormattedTestCase(
            test_id="xml_unit_tests",
            format_type='xml_unit',
            content=xml_string,
            file_name=f"{Path(test_suite.xslt_file).stem}_unit_tests.xml",
            metadata={
                "format": "XML Unit Test Specification",
                "total_scenarios": len(test_suite.scenarios)
            }
        )
        test_cases.append(test_case)
        
        return test_cases
    
    def _get_priority_distribution(self, scenarios: List[TestScenario]) -> Dict[str, int]:
        """Get priority distribution for a list of scenarios."""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for scenario in scenarios:
            distribution[scenario.priority] = distribution.get(scenario.priority, 0) + 1
        return distribution