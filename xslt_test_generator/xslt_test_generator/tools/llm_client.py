"""LLM client using LiteLLM for multi-provider support."""

import litellm
from typing import Dict, Any, List, Optional
from xslt_test_generator.config.settings import settings
from xslt_test_generator.config.logging_config import LoggerMixin, get_logger

class LLMClient(LoggerMixin):
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self, provider: str = None):
        """Initialize LLM client with specified provider."""
        self.provider = provider or settings.llm.get('default_provider', 'openai')
        self.config = settings.get_llm_config(self.provider)
        
        # Set API keys
        if self.provider == 'openai' and settings.openai_api_key:
            litellm.openai_key = settings.openai_api_key
        elif self.provider == 'anthropic' and settings.anthropic_api_key:
            litellm.anthropic_key = settings.anthropic_api_key
        elif self.provider == 'google' and settings.google_api_key:
            litellm.google_key = settings.google_api_key
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         **kwargs) -> str:
        """Generate response using the configured LLM."""
        try:
            response = litellm.completion(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def analyze_xslt(self, xslt_content: str) -> str:
        """Analyze XSLT content and extract transformation patterns."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert XSLT transformation analyst. Analyze the given XSLT file and extract:

1. **Transformation Patterns**: Key mapping logic and data transformations
2. **Business Rules**: Conditional logic, value mappings, and decision points  
3. **Template Functions**: Named templates and their purposes
4. **XPath Expressions**: Complex expressions and their intent
5. **Edge Cases**: Data sanitization, error handling, default values
6. **Input-Output Mapping**: What input elements map to what output elements

Provide a structured analysis that will be used to generate comprehensive test cases."""
            },
            {
                "role": "user", 
                "content": f"Analyze this XSLT transformation:\n\n{xslt_content}"
            }
        ]
        
        return self.generate_response(messages)
    
    def analyze_xsd(self, xsd_content: str) -> str:
        """Analyze XSD schema and extract structure information."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert XML Schema analyst. Analyze the given XSD file and extract:

1. **Element Structure**: Root elements, complex types, and hierarchy
2. **Constraints**: Required vs optional elements, cardinalities (minOccurs/maxOccurs)
3. **Data Types**: Simple types, restrictions, and validation rules
4. **Choice Elements**: Alternative element options and their implications
5. **Relationships**: How elements relate to each other
6. **Test Scenarios**: What variations in input structure should be tested

Provide a structured analysis that will be used to generate test input scenarios."""
            },
            {
                "role": "user",
                "content": f"Analyze this XSD schema:\n\n{xsd_content}"
            }
        ]
        
        return self.generate_response(messages)
    
    def generate_test_cases(self, 
                           xslt_analysis: str, 
                           xsd_analysis: str) -> str:
        """Generate Gherkin test cases based on XSLT and XSD analysis."""
        messages = [
            {
                "role": "system", 
                "content": """You are an expert test case architect specializing in behavior-driven development. Based on the XSLT transformation analysis and XSD schema analysis provided, generate comprehensive Gherkin test scenarios.

Generate test cases that cover:

1. **Happy Path Scenarios**: Normal transformation flows
2. **Business Rule Testing**: Each conditional logic path
3. **Data Validation**: Required vs optional elements  
4. **Edge Cases**: Boundary conditions, special characters, data sanitization
5. **Error Scenarios**: Invalid inputs, missing required data
6. **Integration Testing**: Multiple elements working together

Format each test case using proper Gherkin syntax:
```
Feature: [Feature Name]
  Background:
    Given [setup conditions]
  
  Scenario: [Scenario Description]
    Given [preconditions]
    When [action/transformation]
    Then [expected outcome]
    And [additional validations]
```

Include scenario outlines with examples for parameterized testing where appropriate.
Focus on testing the transformation logic, not just XML structure validation."""
            },
            {
                "role": "user",
                "content": f"""Generate Gherkin test cases based on these analyses:

XSLT Analysis:
{xslt_analysis}

XSD Analysis:  
{xsd_analysis}

Generate comprehensive test scenarios covering all transformation logic and edge cases."""
            }
        ]
        
        return self.generate_response(messages)

# Global client instance
llm_client = LLMClient()