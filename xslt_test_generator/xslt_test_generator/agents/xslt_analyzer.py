"""XSLT Analyzer Agent using CrewAI."""

from crewai import Agent
from xslt_test_generator.config.settings import settings
from xslt_test_generator.tools.llm_client import llm_client
from xslt_test_generator.tools.xml_tools import XSLTAnalyzer

class XSLTAnalyzerAgent:
    """Agent specialized in analyzing XSLT transformations."""
    
    def __init__(self):
        """Initialize XSLT Analyzer Agent."""
        agent_config = settings.agents.get('xslt_analyzer')
        
        self.agent = Agent(
            role=agent_config.role,
            goal=agent_config.goal,
            backstory="""You are an expert XSLT transformation analyst with deep knowledge of:
            - XPath expressions and their business logic
            - XSLT template matching and conditional logic
            - Data transformation patterns and value mappings
            - Edge cases in XML data processing
            - Performance optimization techniques
            
            Your expertise helps identify all testable scenarios in XSLT transformations.""",
            verbose=agent_config.verbose,
            max_retries=agent_config.max_retries,
            allow_delegation=False
        )
    
    def analyze_xslt_file(self, xslt_content: str) -> dict:
        """
        Analyze XSLT file and extract comprehensive transformation information.
        
        Args:
            xslt_content: The XSLT file content as string
            
        Returns:
            dict: Comprehensive analysis including patterns, rules, and test scenarios
        """
        
        # First, do structural analysis using XML parsing
        try:
            xslt_analyzer = XSLTAnalyzer(xslt_content)
            structural_analysis = {
                'templates': xslt_analyzer.extract_templates(),
                'conditional_logic': xslt_analyzer.extract_conditional_logic(),
                'value_mappings': xslt_analyzer.extract_value_mappings()
            }
        except Exception as e:
            structural_analysis = {'error': f'Structural analysis failed: {str(e)}'}
        
        # Then, do LLM-based semantic analysis
        try:
            semantic_analysis = llm_client.analyze_xslt(xslt_content)
        except Exception as e:
            semantic_analysis = f'Semantic analysis failed: {str(e)}'
        
        return {
            'structural_analysis': structural_analysis,
            'semantic_analysis': semantic_analysis,
            'summary': self._generate_analysis_summary(structural_analysis, semantic_analysis)
        }
    
    def _generate_analysis_summary(self, structural: dict, semantic: str) -> dict:
        """Generate a summary of the XSLT analysis."""
        summary = {
            'total_templates': len(structural.get('templates', [])),
            'conditional_blocks': len(structural.get('conditional_logic', [])),
            'value_mapping_functions': len(structural.get('value_mappings', [])),
            'complexity_indicators': {
                'has_named_templates': any(t.get('name') for t in structural.get('templates', [])),
                'has_conditional_logic': len(structural.get('conditional_logic', [])) > 0,
                'has_value_mappings': len(structural.get('value_mappings', [])) > 0,
                'xpath_complexity': 'high' if any(len(t.get('xpath_expressions', [])) > 3 for t in structural.get('templates', [])) else 'low'
            }
        }
        
        return summary