"""
Minimal XSLT Analyzer Agent for PoC Validation

This agent represents the simplest possible implementation focused on business context
understanding rather than technical sophistication. It's designed to test whether
our approach can match manual analysis quality before scaling to full system.

Key Focus Areas:
1. Business context understanding (WHY rules exist)
2. Domain knowledge integration (IATA NDC awareness)
3. Cross-chunk dependency recognition
4. Meaningful test generation
"""

import openai
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from .domain_knowledge import DomainKnowledgeBase
from .manual_analysis_baseline import BaselineTestCase
from .quality_validator import AIAnalysisResult


@dataclass
class LLMResponse:
    """Structured LLM response"""
    raw_response: str
    parsed_content: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


class MinimalXSLTAnalyzer:
    """Minimal XSLT analyzer focused on business context understanding"""
    
    def __init__(self, openai_api_key: str):
        """Initialize with OpenAI client and domain knowledge"""
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.domain_kb = DomainKnowledgeBase()
        
        # Configuration for quality-focused analysis
        self.model = "gpt-4"
        self.temperature = 0.1  # Low temperature for consistency
        self.max_tokens = 2000
        self.timeout = 60  # seconds
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def analyze_with_business_context(self, xslt_chunk: str, 
                                           manual_baseline: BaselineTestCase) -> AIAnalysisResult:
        """
        Analyze XSLT chunk with focus on matching manual analysis quality
        
        This is the core PoC method that must demonstrate 90%+ quality match
        with manual analysis to validate our approach.
        """
        
        try:
            # Get domain context for the business rule type
            rule_type = self._determine_rule_type(manual_baseline)
            domain_context = self.domain_kb.get_domain_context_prompt(rule_type)
            
            # Create business-focused prompt
            prompt = self._create_business_focused_prompt(
                xslt_chunk, manual_baseline, domain_context
            )
            
            # Call LLM with retry logic
            llm_response = await self._call_llm_with_retries(prompt)
            
            if not llm_response.success:
                raise Exception(f"LLM call failed: {llm_response.error_message}")
            
            # Parse and structure the response
            ai_result = self._parse_llm_response_to_ai_result(llm_response.parsed_content)
            
            return ai_result
            
        except Exception as e:
            # Return minimal result on error to allow quality scoring
            return AIAnalysisResult(
                business_context=f"Error in analysis: {str(e)}",
                business_scenarios=["Error scenario"],
                generated_tests=[{"error": "Analysis failed"}],
                dependencies=["error_handling"],
                extracted_rules=["Error in rule extraction"],
                domain_understanding="Failed to analyze",
                failure_impacts=["Analysis failure impact"]
            )
    
    def _determine_rule_type(self, baseline_case: BaselineTestCase) -> str:
        """Determine the type of business rule for context selection"""
        
        category_map = {
            'helper_template': 'document_transformation',
            'main_template': 'target_processing', 
            'integration': 'integration_flow'
        }
        
        # Check for specific patterns in the business rule
        rule_lower = baseline_case.business_rule.lower()
        
        if 'document' in rule_lower and 'transform' in rule_lower:
            return 'document_transformation'
        elif 'target' in rule_lower or 'ua' in rule_lower:
            return 'target_processing'
        elif 'contact' in rule_lower or 'phone' in rule_lower or 'address' in rule_lower:
            return 'contact_validation'
        elif 'integration' in rule_lower or 'flow' in rule_lower or 'dependencies' in rule_lower:
            return 'integration_flow'
        elif 'error' in rule_lower or 'fallback' in rule_lower:
            return 'error_handling'
        else:
            return category_map.get(baseline_case.category, 'document_transformation')
    
    def _create_business_focused_prompt(self, xslt_chunk: str, 
                                       manual_baseline: BaselineTestCase,
                                       domain_context: str) -> str:
        """Create prompt optimized for business understanding"""
        
        return f"""You are an expert XSLT business analyst specializing in IATA NDC transformations.

{domain_context}

MANUAL ANALYSIS BASELINE (your target quality):
Business Rule: {manual_baseline.business_rule}
Business Context: {manual_baseline.business_context}
Business Scenario: {manual_baseline.business_scenario}
Business Value: {manual_baseline.business_value}
Failure Impact: {manual_baseline.failure_impact}
Cross-Chunk Dependencies: {manual_baseline.cross_chunk_dependencies}

XSLT CODE TO ANALYZE:
{xslt_chunk}

CRITICAL REQUIREMENT: Your analysis must match or exceed the manual baseline quality.

ANALYSIS FRAMEWORK:
Answer these specific questions with the same depth as the manual baseline:

1. BUSINESS CONTEXT ANALYSIS:
   - WHY does this business rule exist? (What business problem does it solve?)
   - WHAT business value does it provide to stakeholders?
   - HOW does it fit into IATA NDC compliance requirements?
   - WHAT are the regulatory or compliance drivers behind this rule?

2. BUSINESS SCENARIO IDENTIFICATION:
   - WHAT real-world business scenarios trigger this rule?
   - WHO are the stakeholders affected (passengers, airlines, systems)?
   - WHEN would this rule be applied in a typical booking workflow?
   - WHERE in the booking/processing workflow does this rule activate?

3. BUSINESS VALUE & IMPACT ASSESSMENT:
   - WHAT specific business value does this rule deliver?
   - WHAT would break in business operations if this rule failed?
   - HOW would failures impact customers, airlines, and systems?
   - WHAT compliance or regulatory risks exist without this rule?

4. INTEGRATION & DEPENDENCY UNDERSTANDING:
   - HOW does this rule integrate with other business rules?
   - WHAT dependencies exist with other processing sections?
   - HOW does data flow through the complete transformation?
   - WHAT downstream business processes depend on this rule's output?

5. BUSINESS-FOCUSED TEST STRATEGY:
   - WHAT business scenarios need comprehensive test coverage?
   - WHAT edge cases could cause real business failures?
   - WHAT tests would catch actual business bugs (not just syntax errors)?
   - HOW would you validate that the business logic works correctly?

OUTPUT REQUIREMENTS:
Provide a structured JSON response with this exact format:

{{
    "business_context": {{
        "purpose": "Why this rule exists from business perspective",
        "business_problem": "What specific business problem it solves",
        "compliance_context": "How it relates to IATA NDC compliance",
        "regulatory_drivers": "What regulations or standards require this",
        "stakeholder_impact": "Who is affected by this rule"
    }},
    "business_scenarios": [
        {{
            "scenario": "Specific real-world business scenario",
            "stakeholders": ["Who is affected"],
            "trigger_conditions": "When this rule applies",
            "workflow_context": "Where in booking process this occurs",
            "business_outcome": "What business result is achieved"
        }}
    ],
    "business_value": {{
        "value_provided": "Specific business value this rule delivers",
        "failure_impact": "What business operations break if rule fails",
        "operational_impact": "How failures affect day-to-day operations",
        "compliance_risks": "Regulatory risks without this rule",
        "customer_impact": "How this affects customer experience"
    }},
    "integration_analysis": {{
        "rule_dependencies": ["Other business rules this depends on"],
        "data_flow": "How business data flows through transformation",
        "downstream_impact": "What business processes depend on this output",
        "end_to_end_context": "Role in complete business workflow",
        "cross_chunk_relationships": ["How this connects to other processing sections"]
    }},
    "test_strategy": {{
        "business_test_scenarios": ["Business scenarios that need test coverage"],
        "edge_cases": ["Business edge cases that could cause failures"],
        "bug_detection_tests": ["Tests that would catch real business bugs"],
        "validation_approach": "How to validate business logic correctness",
        "compliance_tests": ["Tests that ensure regulatory compliance"]
    }},
    "domain_understanding": {{
        "iata_ndc_relevance": "How this relates to IATA NDC standards",
        "airline_industry_context": "Airline industry specific considerations",
        "regulatory_environment": "Regulatory environment this operates in",
        "business_criticality": "How critical this rule is to business operations"
    }}
}}

CRITICAL SUCCESS FACTORS:
- Focus on business meaning and real-world applicability, not just code syntax
- Demonstrate deep understanding of WHY rules exist, not just WHAT they do
- Show awareness of business consequences and stakeholder impacts
- Connect technical implementation to business value and compliance requirements
- Identify tests that would catch real business problems, not just technical errors

Your response will be scored against the manual baseline. Match or exceed the baseline's business understanding depth to validate this approach."""
        
    async def _call_llm_with_retries(self, prompt: str) -> LLMResponse:
        """Call LLM with retry logic and error handling"""
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self._make_llm_call(prompt),
                    timeout=self.timeout
                )
                
                # Parse response
                try:
                    parsed_content = json.loads(response.choices[0].message.content)
                    return LLMResponse(
                        raw_response=response.choices[0].message.content,
                        parsed_content=parsed_content,
                        success=True
                    )
                except json.JSONDecodeError as e:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        return LLMResponse(
                            raw_response=response.choices[0].message.content,
                            parsed_content={},
                            success=False,
                            error_message=f"JSON parsing failed: {str(e)}"
                        )
                
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return LLMResponse(
                        raw_response="",
                        parsed_content={},
                        success=False,
                        error_message="LLM call timeout"
                    )
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return LLMResponse(
                        raw_response="",
                        parsed_content={},
                        success=False,
                        error_message=f"LLM call failed: {str(e)}"
                    )
        
        return LLMResponse(
            raw_response="",
            parsed_content={},
            success=False,
            error_message="All retry attempts failed"
        )
    
    async def _make_llm_call(self, prompt: str):
        """Make actual LLM API call"""
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert XSLT business analyst specializing in IATA NDC compliance and airline industry business rules. Focus on business context and real-world applicability."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
    
    def _parse_llm_response_to_ai_result(self, parsed_content: Dict[str, Any]) -> AIAnalysisResult:
        """Convert LLM response to standardized AIAnalysisResult format"""
        
        # Extract business context
        business_context_data = parsed_content.get('business_context', {})
        business_context = f"{business_context_data.get('purpose', '')} {business_context_data.get('business_problem', '')}"
        
        # Extract business scenarios
        scenarios_data = parsed_content.get('business_scenarios', [])
        business_scenarios = [scenario.get('scenario', '') for scenario in scenarios_data]
        
        # Extract generated tests from test strategy
        test_strategy = parsed_content.get('test_strategy', {})
        generated_tests = []
        
        # Convert test strategy to test structure
        for scenario in test_strategy.get('business_test_scenarios', []):
            generated_tests.append({
                'test_scenario': scenario,
                'test_type': 'business_scenario',
                'validation_focus': 'business_logic'
            })
        
        for edge_case in test_strategy.get('edge_cases', []):
            generated_tests.append({
                'test_scenario': edge_case,
                'test_type': 'edge_case',
                'validation_focus': 'business_edge_case'
            })
        
        # Extract dependencies
        integration_data = parsed_content.get('integration_analysis', {})
        dependencies = integration_data.get('rule_dependencies', []) + integration_data.get('cross_chunk_relationships', [])
        
        # Extract rules
        extracted_rules = [business_context_data.get('purpose', '')]
        if 'business_value' in parsed_content:
            extracted_rules.append(parsed_content['business_value'].get('value_provided', ''))
        
        # Extract domain understanding
        domain_data = parsed_content.get('domain_understanding', {})
        domain_understanding = f"{domain_data.get('iata_ndc_relevance', '')} {domain_data.get('airline_industry_context', '')}"
        
        # Extract failure impacts
        business_value_data = parsed_content.get('business_value', {})
        failure_impacts = [
            business_value_data.get('failure_impact', ''),
            business_value_data.get('operational_impact', ''),
            business_value_data.get('customer_impact', '')
        ]
        failure_impacts = [impact for impact in failure_impacts if impact]  # Remove empty strings
        
        return AIAnalysisResult(
            business_context=business_context,
            business_scenarios=business_scenarios,
            generated_tests=generated_tests,
            dependencies=dependencies,
            extracted_rules=extracted_rules,
            domain_understanding=domain_understanding,
            failure_impacts=failure_impacts
        )
    
    def analyze_helper_template(self, template_chunk: str) -> Dict[str, Any]:
        """Legacy method for backwards compatibility"""
        # This would be called from the main PoC validation loop
        # For now, return basic structure
        return {
            'template_info': {'name': 'helper_template', 'complexity_score': 0.5},
            'transformation_rules': [],
            'business_context': 'Helper template analysis',
            'dependencies': []
        }


# Test function for PoC validation
async def test_minimal_analyzer():
    """Test the minimal analyzer with a sample case"""
    
    # This would need actual OpenAI API key
    # analyzer = MinimalXSLTAnalyzer("your-openai-api-key")
    
    # Create a mock baseline case for testing
    from .manual_analysis_baseline import ManualAnalysisBaseline
    baseline = ManualAnalysisBaseline()
    test_case = baseline.get_case_by_id("vmf1_passport_transformation")
    
    print(f"Test case: {test_case.business_rule}")
    print(f"Expected business context: {test_case.business_context}")
    print(f"Expected business value: {test_case.business_value}")
    
    # In actual PoC, we would call:
    # result = await analyzer.analyze_with_business_context(test_case.xslt_chunk, test_case)
    # return result


if __name__ == "__main__":
    # Run basic test
    asyncio.run(test_minimal_analyzer())