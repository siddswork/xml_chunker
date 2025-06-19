"""XSD Schema Analyzer Agent using CrewAI."""

from crewai import Agent
from xslt_test_generator.config.settings import settings
from xslt_test_generator.tools.llm_client import llm_client
from xslt_test_generator.tools.xml_tools import XSDAnalyzer

class XSDAnalyzerAgent:
    """Agent specialized in analyzing XSD schemas."""
    
    def __init__(self):
        """Initialize XSD Analyzer Agent."""
        agent_config = settings.agents.get('xsd_analyzer')
        
        self.agent = Agent(
            role=agent_config.role,
            goal=agent_config.goal,
            backstory="""You are an expert XML Schema analyst with comprehensive knowledge of:
            - XML Schema Definition (XSD) syntax and semantics
            - Complex type definitions and inheritance
            - Element cardinalities and constraints
            - Choice elements and substitution groups
            - Data type restrictions and patterns
            - Namespace handling and imports
            
            Your expertise helps understand input data structures and validation requirements.""",
            verbose=agent_config.verbose,
            max_retries=agent_config.max_retries,
            allow_delegation=False
        )
    
    def analyze_xsd_file(self, xsd_content: str) -> dict:
        """
        Analyze XSD file and extract comprehensive schema information.
        
        Args:
            xsd_content: The XSD file content as string
            
        Returns:
            dict: Comprehensive analysis including structure, constraints, and test scenarios
        """
        
        # First, do structural analysis using XML parsing
        try:
            xsd_analyzer = XSDAnalyzer(xsd_content)
            structural_analysis = {
                'root_elements': xsd_analyzer.extract_root_elements(),
                'complex_types': xsd_analyzer.extract_complex_types(),
                'choice_elements': xsd_analyzer.extract_choice_elements()
            }
        except Exception as e:
            structural_analysis = {'error': f'Structural analysis failed: {str(e)}'}
        
        # Then, do LLM-based semantic analysis
        try:
            semantic_analysis = llm_client.analyze_xsd(xsd_content)
        except Exception as e:
            semantic_analysis = f'Semantic analysis failed: {str(e)}'
        
        return {
            'structural_analysis': structural_analysis,
            'semantic_analysis': semantic_analysis,
            'summary': self._generate_analysis_summary(structural_analysis, semantic_analysis)
        }
    
    def _generate_analysis_summary(self, structural: dict, semantic: str) -> dict:
        """Generate a summary of the XSD analysis."""
        root_elements = structural.get('root_elements', [])
        complex_types = structural.get('complex_types', [])
        choice_elements = structural.get('choice_elements', [])
        
        summary = {
            'total_root_elements': len(root_elements),
            'total_complex_types': len(complex_types),
            'total_choice_elements': len(choice_elements),
            'schema_characteristics': {
                'has_optional_elements': any(elem.get('min_occurs') == '0' for elem in root_elements),
                'has_unbounded_elements': any(elem.get('max_occurs') == 'unbounded' for elem in root_elements),
                'has_choice_constructs': len(choice_elements) > 0,
                'has_complex_nesting': any(len(ct.get('elements', [])) > 5 for ct in complex_types)
            },
            'validation_points': self._identify_validation_points(structural),
            'test_data_requirements': self._identify_test_data_requirements(structural)
        }
        
        return summary
    
    def _identify_validation_points(self, structural: dict) -> list:
        """Identify key validation points in the schema."""
        validation_points = []
        
        # Check for required elements
        for elem in structural.get('root_elements', []):
            if elem.get('min_occurs') != '0':
                validation_points.append(f"Required element: {elem.get('name')}")
        
        # Check for choice elements
        for choice in structural.get('choice_elements', []):
            validation_points.append(f"Choice validation: {len(choice.get('options', []))} options")
        
        # Check for complex types with many elements
        for ct in structural.get('complex_types', []):
            if len(ct.get('elements', [])) > 3:
                validation_points.append(f"Complex type validation: {ct.get('name')}")
        
        return validation_points
    
    def _identify_test_data_requirements(self, structural: dict) -> list:
        """Identify test data requirements based on schema."""
        requirements = []
        
        # Identify cardinality variations
        for elem in structural.get('root_elements', []):
            min_occurs = elem.get('min_occurs', '1')
            max_occurs = elem.get('max_occurs', '1')
            
            if min_occurs == '0':
                requirements.append(f"Optional element test: {elem.get('name')}")
            if max_occurs == 'unbounded':
                requirements.append(f"Multiple occurrence test: {elem.get('name')}")
        
        # Identify choice element variations
        for choice in structural.get('choice_elements', []):
            requirements.append(f"Choice variation tests: {len(choice.get('options', []))} scenarios")
        
        return requirements