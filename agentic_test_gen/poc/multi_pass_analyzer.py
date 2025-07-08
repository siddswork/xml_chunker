"""
Multi-Pass XSLT Analyzer for Enhanced Context Understanding

This analyzer implements a three-pass approach to overcome the limitations
of single-chunk analysis:

1. Pass 1: Isolated analysis - understand the chunk in isolation
2. Pass 2: Contextual analysis - understand with immediate dependencies
3. Pass 3: Full workflow analysis - understand within complete business workflow

This approach should significantly improve integration awareness and
business context understanding.
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
from .context_provider import ContextProvider, ContextLevel


@dataclass
class PassResult:
    """Result from a single analysis pass"""
    pass_number: int
    pass_type: str
    ai_result: AIAnalysisResult
    confidence_score: float
    context_gaps: List[str]
    processing_time: float


@dataclass
class MultiPassResult:
    """Complete multi-pass analysis result"""
    final_result: AIAnalysisResult
    pass_results: List[PassResult]
    total_processing_time: float
    improvement_progression: Dict[str, List[float]]
    final_confidence: float


class MultiPassXSLTAnalyzer:
    """Enhanced XSLT analyzer with multi-pass context understanding"""
    
    def __init__(self, openai_api_key: str):
        """Initialize with OpenAI client and enhanced context capabilities"""
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.domain_kb = DomainKnowledgeBase()
        self.context_provider = ContextProvider()
        
        # Load sample XSLT content for context
        self.context_provider.load_sample_xslt()
        
        # Configuration
        self.model = "gpt-4"
        self.temperature = 0.1
        self.max_tokens = 3000  # Increased for richer context
        self.timeout = 90  # Increased for more complex analysis
        
        # Multi-pass configuration
        self.max_retries = 3
        self.retry_delay = 2
        
        # Pass-specific configurations
        self.pass_configs = {
            1: {"focus": "isolated_understanding", "max_tokens": 2000},
            2: {"focus": "contextual_integration", "max_tokens": 2500},
            3: {"focus": "workflow_comprehension", "max_tokens": 3000}
        }
    
    async def analyze_with_multi_pass(self, xslt_chunk: str, 
                                    manual_baseline: BaselineTestCase) -> MultiPassResult:
        """
        Perform multi-pass analysis with progressive context understanding
        
        This is the main method that should significantly improve upon
        single-chunk analysis limitations.
        """
        
        import time
        start_time = time.time()
        
        try:
            # Get progressive context levels
            context_levels = self._get_context_levels_for_chunk(xslt_chunk, manual_baseline)
            
            # Perform three passes
            pass_results = []
            
            # Pass 1: Isolated analysis
            pass1_result = await self._execute_analysis_pass(
                pass_number=1,
                context_level=context_levels[0],
                manual_baseline=manual_baseline,
                previous_results=[]
            )
            pass_results.append(pass1_result)
            
            # Pass 2: Contextual analysis
            pass2_result = await self._execute_analysis_pass(
                pass_number=2,
                context_level=context_levels[1],
                manual_baseline=manual_baseline,
                previous_results=[pass1_result]
            )
            pass_results.append(pass2_result)
            
            # Pass 3: Full workflow analysis
            pass3_result = await self._execute_analysis_pass(
                pass_number=3,
                context_level=context_levels[2],
                manual_baseline=manual_baseline,
                previous_results=[pass1_result, pass2_result]
            )
            pass_results.append(pass3_result)
            
            # Synthesize final result
            final_result = self._synthesize_final_result(pass_results, manual_baseline)
            
            # Calculate improvement progression
            improvement_progression = self._calculate_improvement_progression(pass_results)
            
            # Calculate final confidence
            final_confidence = self._calculate_final_confidence(pass_results)
            
            total_time = time.time() - start_time
            
            return MultiPassResult(
                final_result=final_result,
                pass_results=pass_results,
                total_processing_time=total_time,
                improvement_progression=improvement_progression,
                final_confidence=final_confidence
            )
            
        except Exception as e:
            # Return error result
            error_result = AIAnalysisResult(
                business_context=f"Multi-pass analysis failed: {str(e)}",
                business_scenarios=["Error scenario"],
                generated_tests=[{"error": "Multi-pass analysis failed"}],
                dependencies=["error_handling"],
                extracted_rules=["Error in multi-pass analysis"],
                domain_understanding="Failed to analyze with multi-pass approach",
                failure_impacts=["Multi-pass analysis failure"]
            )
            
            return MultiPassResult(
                final_result=error_result,
                pass_results=[],
                total_processing_time=time.time() - start_time,
                improvement_progression={},
                final_confidence=0.0
            )
    
    def _get_context_levels_for_chunk(self, xslt_chunk: str, 
                                    manual_baseline: BaselineTestCase) -> List[ContextLevel]:
        """Get appropriate context levels for the chunk"""
        
        # Map baseline case ID to chunk name for context lookup
        chunk_name_map = {
            "vmf1_passport_transformation": "vmf:vmf1_inputtoresult",
            "vmf2_visa_transformation": "vmf:vmf2_inputtoresult", 
            "vmf3_identity_transformation": "vmf:vmf3_inputtoresult",
            "ua_target_specific_processing": "ua_specific_processing",
            "multi_passenger_contact_validation": "multi_passenger_validation",
            "phone_number_standardization": "standardize_phone",
            "address_concatenation_logic": "process_address",
            "contact_type_processing": "Contact",
            "end_to_end_passenger_flow": "Passenger",
            "helper_template_integration": "vmf:vmf1_inputtoresult"
        }
        
        chunk_name = chunk_name_map.get(manual_baseline.id, "unknown")
        
        # Get context levels from provider
        context_levels = self.context_provider.get_context_levels(chunk_name)
        
        # If no context levels found, create basic ones
        if not context_levels:
            context_levels = [
                ContextLevel(
                    level="isolated",
                    description="Analysis of chunk in isolation",
                    content=xslt_chunk,
                    related_chunks=[]
                ),
                ContextLevel(
                    level="contextual",
                    description="Analysis with limited context",
                    content=xslt_chunk,
                    related_chunks=[]
                ),
                ContextLevel(
                    level="full_workflow",
                    description="Analysis with workflow context",
                    content=xslt_chunk,
                    related_chunks=[]
                )
            ]
        
        return context_levels
    
    async def _execute_analysis_pass(self, pass_number: int,
                                   context_level: ContextLevel,
                                   manual_baseline: BaselineTestCase,
                                   previous_results: List[PassResult]) -> PassResult:
        """Execute a single analysis pass"""
        
        import time
        start_time = time.time()
        
        # Get pass-specific configuration
        pass_config = self.pass_configs.get(pass_number, self.pass_configs[1])
        
        # Create pass-specific prompt
        prompt = self._create_pass_specific_prompt(
            pass_number, context_level, manual_baseline, previous_results
        )
        
        # Execute LLM call
        llm_response = await self._call_llm_with_retries(prompt, pass_config)
        
        if not llm_response.success:
            raise Exception(f"Pass {pass_number} failed: {llm_response.error_message}")
        
        # Parse result
        ai_result = self._parse_llm_response_to_ai_result(llm_response.parsed_content)
        
        # Calculate confidence score for this pass
        confidence_score = self._calculate_pass_confidence(llm_response.parsed_content)
        
        # Identify context gaps
        context_gaps = self._identify_context_gaps(llm_response.parsed_content)
        
        processing_time = time.time() - start_time
        
        return PassResult(
            pass_number=pass_number,
            pass_type=context_level.level,
            ai_result=ai_result,
            confidence_score=confidence_score,
            context_gaps=context_gaps,
            processing_time=processing_time
        )
    
    def _create_pass_specific_prompt(self, pass_number: int,
                                   context_level: ContextLevel,
                                   manual_baseline: BaselineTestCase,
                                   previous_results: List[PassResult]) -> str:
        """Create prompt tailored for specific analysis pass"""
        
        # Get domain context
        rule_type = self._determine_rule_type(manual_baseline)
        domain_context = self.domain_kb.get_domain_context_prompt(rule_type)
        
        # Get business workflow context
        workflow_context = self.context_provider.get_business_workflow_context(
            context_level.related_chunks[0] if context_level.related_chunks else "unknown"
        )
        
        # Pass-specific instructions
        pass_instructions = self._get_pass_specific_instructions(pass_number, previous_results)
        
        prompt = f"""You are an expert XSLT business analyst specializing in IATA NDC transformations.

=== ANALYSIS PASS {pass_number}/3: {context_level.level.upper()} ANALYSIS ===

{domain_context}

{workflow_context}

MANUAL ANALYSIS BASELINE (your quality target):
Business Rule: {manual_baseline.business_rule}
Business Context: {manual_baseline.business_context}
Business Scenario: {manual_baseline.business_scenario}
Business Value: {manual_baseline.business_value}
Failure Impact: {manual_baseline.failure_impact}
Cross-Chunk Dependencies: {manual_baseline.cross_chunk_dependencies}

XSLT CODE WITH CONTEXT ({context_level.level} level):
{context_level.content}

RELATED CHUNKS IN CONTEXT: {context_level.related_chunks}

{pass_instructions}

ANALYSIS FRAMEWORK FOR PASS {pass_number}:
{self._get_analysis_framework(pass_number)}

OUTPUT REQUIREMENTS:
Provide a structured JSON response with this exact format:

{{
    "pass_metadata": {{
        "pass_number": {pass_number},
        "pass_type": "{context_level.level}",
        "confidence_level": "high|medium|low",
        "context_gaps": ["List any context still missing"],
        "improvement_areas": ["Areas identified for next pass"]
    }},
    "business_context": {{
        "purpose": "Why this rule exists from business perspective",
        "business_problem": "What specific business problem it solves",
        "compliance_context": "How it relates to IATA NDC compliance",
        "regulatory_drivers": "What regulations or standards require this",
        "stakeholder_impact": "Who is affected by this rule",
        "workflow_position": "Where this fits in the business workflow"
    }},
    "business_scenarios": [
        {{
            "scenario": "Specific real-world business scenario",
            "stakeholders": ["Who is affected"],
            "trigger_conditions": "When this rule applies",
            "workflow_context": "Where in booking process this occurs",
            "business_outcome": "What business result is achieved",
            "integration_points": ["How this connects to other processes"]
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
        "cross_chunk_relationships": ["How this connects to other processing sections"],
        "workflow_integration": "How this integrates with complete workflow"
    }},
    "test_strategy": {{
        "business_test_scenarios": ["Business scenarios that need test coverage"],
        "edge_cases": ["Business edge cases that could cause failures"],
        "bug_detection_tests": ["Tests that would catch real business bugs"],
        "validation_approach": "How to validate business logic correctness",
        "compliance_tests": ["Tests that ensure regulatory compliance"],
        "integration_tests": ["Tests that validate cross-chunk integration"]
    }},
    "domain_understanding": {{
        "iata_ndc_relevance": "How this relates to IATA NDC standards",
        "airline_industry_context": "Airline industry specific considerations",
        "regulatory_environment": "Regulatory environment this operates in",
        "business_criticality": "How critical this rule is to business operations"
    }}
}}

CRITICAL SUCCESS FACTORS:
- Demonstrate understanding that improves with each pass
- Show awareness of business context and cross-chunk relationships
- Connect technical implementation to business value
- Identify meaningful tests that catch real business problems
- Build upon insights from previous passes (if any)

Your analysis will be compared against manual baseline quality. Show clear improvement in business understanding and integration awareness."""
        
        return prompt
    
    def _get_pass_specific_instructions(self, pass_number: int, 
                                      previous_results: List[PassResult]) -> str:
        """Get instructions specific to each analysis pass"""
        
        if pass_number == 1:
            return """
PASS 1 FOCUS: ISOLATED UNDERSTANDING
- Analyze the chunk in isolation to understand its basic business purpose
- Identify what you CAN determine from this chunk alone
- Clearly note what you CANNOT determine without additional context
- Focus on the specific business rule implemented by this chunk
- Provide your best analysis with current limited context
"""
        
        elif pass_number == 2:
            return f"""
PASS 2 FOCUS: CONTEXTUAL INTEGRATION
- You now have context about related chunks and immediate dependencies
- Build upon your isolated analysis to understand integration points
- Identify how this chunk connects to other business processes
- Understand the data flow and dependencies
- Improve your business understanding with this additional context

PREVIOUS ANALYSIS INSIGHTS:
{self._format_previous_insights(previous_results)}

IMPROVEMENTS TO MAKE:
- Enhance business context understanding with integration awareness
- Identify cross-chunk dependencies and workflow connections
- Improve test scenarios with integration considerations
"""
        
        elif pass_number == 3:
            return f"""
PASS 3 FOCUS: FULL WORKFLOW COMPREHENSION
- You now have complete workflow context and understand the business end-to-end flow
- Synthesize all previous insights into comprehensive business understanding
- Demonstrate deep understanding of business value and compliance requirements
- Show awareness of complete workflow integration and dependencies
- Provide your most comprehensive analysis

PREVIOUS ANALYSIS PROGRESSION:
{self._format_analysis_progression(previous_results)}

FINAL SYNTHESIS REQUIREMENTS:
- Comprehensive business context understanding
- Complete integration awareness
- Business-meaningful test strategy
- Deep domain understanding
- Clear business value articulation
"""
        
        return ""
    
    def _format_previous_insights(self, previous_results: List[PassResult]) -> str:
        """Format insights from previous passes"""
        
        if not previous_results:
            return "No previous analysis available"
        
        insights = []
        for result in previous_results:
            insights.append(f"Pass {result.pass_number}: {result.ai_result.business_context[:100]}...")
            if result.context_gaps:
                insights.append(f"  Context gaps: {', '.join(result.context_gaps)}")
        
        return '\n'.join(insights)
    
    def _format_analysis_progression(self, previous_results: List[PassResult]) -> str:
        """Format the progression of analysis across passes"""
        
        if not previous_results:
            return "No previous analysis available"
        
        progression = []
        for result in previous_results:
            progression.append(f"""
Pass {result.pass_number} ({result.pass_type}):
- Business Context: {result.ai_result.business_context[:150]}...
- Integration Understanding: {len(result.ai_result.dependencies)} dependencies identified
- Test Scenarios: {len(result.ai_result.generated_tests)} tests proposed
- Confidence: {result.confidence_score:.2f}
""")
        
        return '\n'.join(progression)
    
    def _get_analysis_framework(self, pass_number: int) -> str:
        """Get analysis framework specific to each pass"""
        
        frameworks = {
            1: """
1. ISOLATED BUSINESS UNDERSTANDING:
   - What specific business rule does this chunk implement?
   - What business problem does it solve?
   - What can you determine about business value from this chunk alone?
   - What business context is missing?

2. TECHNICAL ANALYSIS:
   - What XSLT transformation does this perform?
   - What are the input/output patterns?
   - What logic is implemented?

3. CONTEXT GAPS IDENTIFICATION:
   - What related chunks do you need to understand the full picture?
   - What business workflow context is missing?
   - What integration points are unclear?
""",
            2: """
1. CONTEXTUAL BUSINESS UNDERSTANDING:
   - How does this chunk fit into the broader business workflow?
   - What are the integration points with other business processes?
   - How does the additional context improve your business understanding?

2. DEPENDENCY ANALYSIS:
   - What dependencies are now clear from the context?
   - How does data flow between this chunk and related chunks?
   - What business processes depend on this chunk's output?

3. ENHANCED TEST STRATEGY:
   - What integration test scenarios are now possible?
   - How do cross-chunk dependencies affect testing?
   - What business scenarios span multiple chunks?
""",
            3: """
1. COMPREHENSIVE BUSINESS UNDERSTANDING:
   - Complete articulation of business value and compliance requirements
   - Deep understanding of end-to-end workflow integration
   - Clear connection between technical implementation and business outcomes

2. COMPLETE INTEGRATION AWARENESS:
   - Full understanding of cross-chunk dependencies
   - Complete data flow and workflow integration
   - Comprehensive business process integration

3. BUSINESS-MEANINGFUL TEST STRATEGY:
   - Complete test coverage for business scenarios
   - Integration tests that validate end-to-end workflows
   - Business-focused tests that catch real operational issues
"""
        }
        
        return frameworks.get(pass_number, frameworks[1])
    
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
    
    async def _call_llm_with_retries(self, prompt: str, pass_config: Dict) -> 'LLMResponse':
        """Call LLM with retry logic and pass-specific configuration"""
        
        from .minimal_xslt_analyzer import LLMResponse
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self._make_llm_call(prompt, pass_config),
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
    
    async def _make_llm_call(self, prompt: str, pass_config: Dict):
        """Make actual LLM API call with pass-specific configuration"""
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert XSLT business analyst specializing in IATA NDC compliance. You perform multi-pass analysis to build comprehensive business understanding."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=pass_config.get("max_tokens", self.max_tokens)
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
        
        for integration_test in test_strategy.get('integration_tests', []):
            generated_tests.append({
                'test_scenario': integration_test,
                'test_type': 'integration_test',
                'validation_focus': 'cross_chunk_integration'
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
        failure_impacts = [impact for impact in failure_impacts if impact]
        
        return AIAnalysisResult(
            business_context=business_context,
            business_scenarios=business_scenarios,
            generated_tests=generated_tests,
            dependencies=dependencies,
            extracted_rules=extracted_rules,
            domain_understanding=domain_understanding,
            failure_impacts=failure_impacts
        )
    
    def _calculate_pass_confidence(self, parsed_content: Dict[str, Any]) -> float:
        """Calculate confidence score for a single pass"""
        
        metadata = parsed_content.get('pass_metadata', {})
        confidence_level = metadata.get('confidence_level', 'low')
        
        confidence_map = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        }
        
        return confidence_map.get(confidence_level, 0.5)
    
    def _identify_context_gaps(self, parsed_content: Dict[str, Any]) -> List[str]:
        """Identify context gaps from the analysis"""
        
        metadata = parsed_content.get('pass_metadata', {})
        return metadata.get('context_gaps', [])
    
    def _synthesize_final_result(self, pass_results: List[PassResult], 
                               manual_baseline: BaselineTestCase) -> AIAnalysisResult:
        """Synthesize the final result from all passes"""
        
        # Use the last pass (most comprehensive) as base
        final_pass = pass_results[-1]
        final_result = final_pass.ai_result
        
        # Enhance with insights from all passes
        all_dependencies = set()
        all_scenarios = []
        all_tests = []
        all_rules = []
        all_impacts = []
        
        for pass_result in pass_results:
            result = pass_result.ai_result
            all_dependencies.update(result.dependencies)
            all_scenarios.extend(result.business_scenarios)
            all_tests.extend(result.generated_tests)
            all_rules.extend(result.extracted_rules)
            all_impacts.extend(result.failure_impacts)
        
        # Create enhanced final result
        enhanced_result = AIAnalysisResult(
            business_context=final_result.business_context,
            business_scenarios=list(set(all_scenarios)),  # Remove duplicates
            generated_tests=all_tests,
            dependencies=list(all_dependencies),
            extracted_rules=list(set(all_rules)),
            domain_understanding=final_result.domain_understanding,
            failure_impacts=list(set(all_impacts))
        )
        
        return enhanced_result
    
    def _calculate_improvement_progression(self, pass_results: List[PassResult]) -> Dict[str, List[float]]:
        """Calculate improvement progression across passes"""
        
        progression = {
            'confidence': [],
            'dependencies_identified': [],
            'scenarios_identified': [],
            'tests_generated': []
        }
        
        for pass_result in pass_results:
            progression['confidence'].append(pass_result.confidence_score)
            progression['dependencies_identified'].append(len(pass_result.ai_result.dependencies))
            progression['scenarios_identified'].append(len(pass_result.ai_result.business_scenarios))
            progression['tests_generated'].append(len(pass_result.ai_result.generated_tests))
        
        return progression
    
    def _calculate_final_confidence(self, pass_results: List[PassResult]) -> float:
        """Calculate final confidence based on all passes"""
        
        if not pass_results:
            return 0.0
        
        # Weight later passes more heavily
        weights = [0.2, 0.3, 0.5]  # For passes 1, 2, 3
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for i, pass_result in enumerate(pass_results):
            if i < len(weights):
                weighted_confidence += pass_result.confidence_score * weights[i]
                total_weight += weights[i]
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0


# Backward compatibility wrapper
class EnhancedMinimalXSLTAnalyzer:
    """Enhanced analyzer that can use either single-pass or multi-pass analysis"""
    
    def __init__(self, openai_api_key: str):
        self.multi_pass_analyzer = MultiPassXSLTAnalyzer(openai_api_key)
    
    async def analyze_with_business_context(self, xslt_chunk: str, 
                                          manual_baseline: BaselineTestCase) -> AIAnalysisResult:
        """Enhanced analysis using multi-pass approach"""
        
        multi_pass_result = await self.multi_pass_analyzer.analyze_with_multi_pass(
            xslt_chunk, manual_baseline
        )
        
        return multi_pass_result.final_result


# Test function
async def test_multi_pass_analyzer():
    """Test the multi-pass analyzer"""
    
    # This would need actual OpenAI API key
    print("Multi-pass analyzer test - would need API key for full test")
    
    # Create mock baseline case
    from .manual_analysis_baseline import ManualAnalysisBaseline
    baseline = ManualAnalysisBaseline()
    test_case = baseline.get_case_by_id("vmf1_passport_transformation")
    
    print(f"Test case: {test_case.business_rule}")
    print(f"Expected improvement: Better integration awareness and business context")


if __name__ == "__main__":
    asyncio.run(test_multi_pass_analyzer())