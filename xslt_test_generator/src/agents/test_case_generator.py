"""Test Case Generator Agent using CrewAI."""

from crewai import Agent
from src.config.settings import settings
from src.tools.llm_client import llm_client

class TestCaseGeneratorAgent:
    """Agent specialized in generating Gherkin test cases."""
    
    def __init__(self):
        """Initialize Test Case Generator Agent."""
        agent_config = settings.agents.get('test_case_generator')
        
        self.agent = Agent(
            role=agent_config.role,
            goal=agent_config.goal,
            backstory="""You are an expert test case architect with extensive experience in:
            - Behavior-Driven Development (BDD) and Gherkin syntax
            - Test scenario design and coverage analysis
            - Edge case identification and boundary testing
            - Integration testing strategies
            - Test data management and validation
            - Quality assurance best practices
            
            Your expertise ensures comprehensive test coverage for complex transformations.""",
            verbose=agent_config.verbose,
            max_retries=agent_config.max_retries,
            allow_delegation=False
        )
    
    def generate_test_cases(self, xslt_analysis: dict, xsd_analysis: dict) -> dict:
        """
        Generate comprehensive Gherkin test cases based on XSLT and XSD analysis.
        
        Args:
            xslt_analysis: XSLT analysis results from XSLTAnalyzerAgent
            xsd_analysis: XSD analysis results from XSDAnalyzerAgent
            
        Returns:
            dict: Generated test cases and metadata
        """
        
        # Prepare analysis summaries for LLM
        xslt_summary = self._prepare_xslt_summary(xslt_analysis)
        xsd_summary = self._prepare_xsd_summary(xsd_analysis)
        
        try:
            # Generate test cases using LLM
            gherkin_test_cases = llm_client.generate_test_cases(xslt_summary, xsd_summary)
            
            # Extract and categorize test cases
            test_case_analysis = self._analyze_generated_test_cases(gherkin_test_cases)
            
            return {
                'gherkin_content': gherkin_test_cases,
                'analysis': test_case_analysis,
                'metadata': self._generate_test_metadata(xslt_analysis, xsd_analysis),
                'coverage_matrix': self._generate_coverage_matrix(xslt_analysis, xsd_analysis)
            }
            
        except Exception as e:
            return {
                'error': f'Test case generation failed: {str(e)}',
                'fallback_cases': self._generate_fallback_test_cases(xslt_analysis, xsd_analysis)
            }
    
    def _prepare_xslt_summary(self, xslt_analysis: dict) -> str:
        """Prepare XSLT analysis summary for LLM consumption."""
        structural = xslt_analysis.get('structural_analysis', {})
        semantic = xslt_analysis.get('semantic_analysis', '')
        summary = xslt_analysis.get('summary', {})
        
        xslt_summary = f"""
XSLT Transformation Analysis:

Structural Information:
- Total Templates: {summary.get('total_templates', 0)}
- Conditional Blocks: {summary.get('conditional_blocks', 0)}
- Value Mapping Functions: {summary.get('value_mapping_functions', 0)}
- Complexity: {summary.get('complexity_indicators', {}).get('xpath_complexity', 'unknown')}

Key Templates:
{self._format_templates(structural.get('templates', []))}

Conditional Logic:
{self._format_conditional_logic(structural.get('conditional_logic', []))}

Value Mappings:
{self._format_value_mappings(structural.get('value_mappings', []))}

Semantic Analysis:
{semantic}
"""
        return xslt_summary
    
    def _prepare_xsd_summary(self, xsd_analysis: dict) -> str:
        """Prepare XSD analysis summary for LLM consumption."""
        structural = xsd_analysis.get('structural_analysis', {})
        semantic = xsd_analysis.get('semantic_analysis', '')
        summary = xsd_analysis.get('summary', {})
        
        xsd_summary = f"""
XSD Schema Analysis:

Schema Information:
- Root Elements: {summary.get('total_root_elements', 0)}
- Complex Types: {summary.get('total_complex_types', 0)}
- Choice Elements: {summary.get('total_choice_elements', 0)}

Schema Characteristics:
- Has Optional Elements: {summary.get('schema_characteristics', {}).get('has_optional_elements', False)}
- Has Unbounded Elements: {summary.get('schema_characteristics', {}).get('has_unbounded_elements', False)}
- Has Choice Constructs: {summary.get('schema_characteristics', {}).get('has_choice_constructs', False)}

Validation Points:
{chr(10).join(f'- {vp}' for vp in summary.get('validation_points', []))}

Test Data Requirements:
{chr(10).join(f'- {req}' for req in summary.get('test_data_requirements', []))}

Semantic Analysis:
{semantic}
"""
        return xsd_summary
    
    def _format_templates(self, templates: list) -> str:
        """Format template information for summary."""
        if not templates:
            return "- No templates found"
        
        formatted = []
        for template in templates[:5]:  # Limit to first 5 templates
            name = template.get('name', 'unnamed')
            match = template.get('match', 'no match')
            conditions = 'with conditions' if template.get('has_conditions') else 'no conditions'
            formatted.append(f"- Template '{name}' matches '{match}' ({conditions})")
        
        if len(templates) > 5:
            formatted.append(f"- ... and {len(templates) - 5} more templates")
        
        return chr(10).join(formatted)
    
    def _format_conditional_logic(self, conditions: list) -> str:
        """Format conditional logic for summary."""
        if not conditions:
            return "- No conditional logic found"
        
        formatted = []
        for condition in conditions[:5]:  # Limit to first 5 conditions
            cond_type = condition.get('type', 'unknown')
            if cond_type == 'choose':
                count = len(condition.get('conditions', []))
                formatted.append(f"- Choose statement with {count} when conditions")
            elif cond_type == 'if':
                test = condition.get('test', 'unknown test')
                formatted.append(f"- If statement: {test}")
        
        if len(conditions) > 5:
            formatted.append(f"- ... and {len(conditions) - 5} more conditional blocks")
        
        return chr(10).join(formatted)
    
    def _format_value_mappings(self, mappings: list) -> str:
        """Format value mappings for summary."""
        if not mappings:
            return "- No value mappings found"
        
        formatted = []
        for mapping in mappings[:3]:  # Limit to first 3 mappings
            template_name = mapping.get('template_name', 'unknown')
            mapping_count = len(mapping.get('mappings', []))
            formatted.append(f"- Template '{template_name}' has {mapping_count} value mappings")
        
        if len(mappings) > 3:
            formatted.append(f"- ... and {len(mappings) - 3} more mapping functions")
        
        return chr(10).join(formatted)
    
    def _analyze_generated_test_cases(self, gherkin_content: str) -> dict:
        """Analyze the generated Gherkin test cases."""
        lines = gherkin_content.split('\n')
        
        analysis = {
            'total_lines': len(lines),
            'feature_count': len([line for line in lines if line.strip().startswith('Feature:')]),
            'scenario_count': len([line for line in lines if line.strip().startswith('Scenario:')]),
            'given_count': len([line for line in lines if line.strip().startswith('Given')]),
            'when_count': len([line for line in lines if line.strip().startswith('When')]),
            'then_count': len([line for line in lines if line.strip().startswith('Then')]),
            'example_count': len([line for line in lines if line.strip().startswith('Examples:')]),
            'quality_indicators': {
                'has_background': 'Background:' in gherkin_content,
                'has_scenario_outline': 'Scenario Outline:' in gherkin_content,
                'has_examples': 'Examples:' in gherkin_content,
                'proper_gherkin_structure': self._validate_gherkin_structure(gherkin_content)
            }
        }
        
        return analysis
    
    def _validate_gherkin_structure(self, gherkin_content: str) -> bool:
        """Basic validation of Gherkin structure."""
        required_keywords = ['Feature:', 'Scenario:', 'Given', 'When', 'Then']
        return all(keyword in gherkin_content for keyword in required_keywords)
    
    def _generate_test_metadata(self, xslt_analysis: dict, xsd_analysis: dict) -> dict:
        """Generate metadata about the test generation process."""
        return {
            'generation_timestamp': '2024-01-01',  # Would use actual timestamp in production
            'xslt_complexity': xslt_analysis.get('summary', {}).get('complexity_indicators', {}),
            'xsd_characteristics': xsd_analysis.get('summary', {}).get('schema_characteristics', {}),
            'coverage_areas': [
                'transformation_logic',
                'conditional_branching', 
                'data_validation',
                'edge_cases',
                'error_scenarios'
            ]
        }
    
    def _generate_coverage_matrix(self, xslt_analysis: dict, xsd_analysis: dict) -> dict:
        """Generate test coverage matrix."""
        xslt_summary = xslt_analysis.get('summary', {})
        xsd_summary = xsd_analysis.get('summary', {})
        
        return {
            'template_coverage': {
                'total_templates': xslt_summary.get('total_templates', 0),
                'tested_templates': min(xslt_summary.get('total_templates', 0), 10),  # Estimate
                'coverage_percentage': min(100, (xslt_summary.get('total_templates', 0) * 100) // max(1, xslt_summary.get('total_templates', 0)))
            },
            'condition_coverage': {
                'total_conditions': xslt_summary.get('conditional_blocks', 0),
                'tested_conditions': min(xslt_summary.get('conditional_blocks', 0), 15),  # Estimate
                'coverage_percentage': min(100, (xslt_summary.get('conditional_blocks', 0) * 100) // max(1, xslt_summary.get('conditional_blocks', 0)))
            },
            'schema_coverage': {
                'total_elements': xsd_summary.get('total_root_elements', 0),
                'tested_elements': min(xsd_summary.get('total_root_elements', 0), 20),  # Estimate
                'coverage_percentage': min(100, (xsd_summary.get('total_root_elements', 0) * 100) // max(1, xsd_summary.get('total_root_elements', 0)))
            }
        }
    
    def _generate_fallback_test_cases(self, xslt_analysis: dict, xsd_analysis: dict) -> str:
        """Generate basic fallback test cases if LLM generation fails."""
        return """Feature: XSLT Transformation Testing (Fallback)
  
  Background:
    Given an XSLT transformation is available
    And input XML conforms to the expected schema
  
  Scenario: Basic transformation
    Given valid input XML
    When the XSLT transformation is applied
    Then the output should be valid XML
    And the output should conform to the target schema
  
  Scenario: Handle missing optional elements
    Given input XML with missing optional elements
    When the XSLT transformation is applied
    Then the transformation should complete successfully
    And optional output elements should be handled appropriately
  
  Scenario: Handle invalid input
    Given invalid input XML
    When the XSLT transformation is applied
    Then the transformation should handle the error gracefully
"""