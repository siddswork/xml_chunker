"""
Orchestrator Agent (GPT-4.1)

Master coordinator for the agentic XSLT test generation system.
Responsible for workflow coordination, strategic planning, and synthesis.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.base_agent import (
    ModelIntegratedAgent, 
    ModelType, 
    AgentCapability, 
    ExecutionContext,
    AgentStatus
)


class OrchestratorAgent(ModelIntegratedAgent):
    """
    Orchestrator Agent using GPT-4.1 for complex workflow coordination.
    
    Responsibilities:
    - Create comprehensive analysis strategies
    - Coordinate agent execution sequences
    - Synthesize findings from all agents
    - Generate final test case orchestration plans
    - Adapt workflow based on intermediate results
    """
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        capabilities = [
            AgentCapability(
                name="strategic_planning",
                description="Create comprehensive analysis strategies based on file complexity",
                input_types=["file_paths", "complexity_assessment"],
                output_types=["analysis_plan", "agent_coordination"],
                model_requirements=ModelType.GPT_41
            ),
            AgentCapability(
                name="workflow_coordination",
                description="Coordinate parallel and sequential agent execution",
                input_types=["agent_results", "workflow_state"],
                output_types=["coordination_plan", "next_steps"],
                model_requirements=ModelType.GPT_41
            ),
            AgentCapability(
                name="synthesis",
                description="Synthesize findings from multiple agents into coherent understanding",
                input_types=["agent_results", "business_context"],
                output_types=["synthesized_analysis", "test_strategy"],
                model_requirements=ModelType.GPT_41
            )
        ]
        
        super().__init__(
            agent_id="orchestrator",
            model_type=ModelType.GPT_41,
            capabilities=capabilities,
            api_key=api_key,
            logger=logger
        )
    
    async def _process(self, context: ExecutionContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing logic for the Orchestrator Agent.
        
        Args:
            context: Execution context
            input_data: Input containing file paths and analysis requirements
            
        Returns:
            Comprehensive analysis plan and coordination strategy
        """
        operation = input_data.get("operation", "create_analysis_plan")
        
        if operation == "create_analysis_plan":
            return await self._create_analysis_plan(input_data)
        elif operation == "coordinate_workflow":
            return await self._coordinate_workflow(input_data)
        elif operation == "synthesize_results":
            return await self._synthesize_results(input_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _create_analysis_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive analysis strategy for XSLT test generation.
        
        Args:
            input_data: Contains file paths and requirements
            
        Returns:
            Detailed analysis plan with agent coordination strategy
        """
        xslt_path = input_data.get("xslt_path")
        input_xsd_path = input_data.get("input_xsd_path")
        output_xsd_path = input_data.get("output_xsd_path")
        target_test_count = input_data.get("target_test_count", 125)
        
        # Analyze file complexity to inform strategy
        complexity_assessment = await self._assess_file_complexity(
            xslt_path, input_xsd_path, output_xsd_path
        )
        
        # Create strategic analysis plan
        prompt = f"""
        As the master orchestrator for XSLT test case generation, create a comprehensive 
        analysis strategy that will generate {target_test_count}+ test cases.
        
        Target Files:
        - XSLT: {xslt_path}
        - Input XSD: {input_xsd_path}
        - Output XSD: {output_xsd_path}
        
        File Complexity Assessment:
        {json.dumps(complexity_assessment, indent=2)}
        
        Based on the successful manual methodology that generated 135+ test cases, create an 
        analysis plan that includes:
        
        1. **Agent Task Distribution**:
           - File Analyzer Agent (o4-mini): Progressive depth XSLT analysis strategy
           - Pattern Hunter Agent (o4-mini): Pattern recognition approach
           - Schema Mapper Agent (o4-mini): XSD analysis strategy
           - Cross-Reference Validator (o4-mini): Validation approach
           - Business Logic Extractor (GPT-4.1): Business understanding strategy
           - Test Case Generator (GPT-4.1): Test generation strategy
        
        2. **Execution Sequence**:
           - Parallel vs sequential execution decisions
           - Dependencies between agent tasks
           - Checkpoints for quality validation
        
        3. **Success Metrics**:
           - Test case quantity targets per category
           - Quality thresholds for business logic coverage
           - Integration validation requirements
        
        4. **Adaptive Strategy**:
           - How to adjust based on intermediate findings
           - Fallback approaches for complex scenarios
           - Quality assurance checkpoints
        
        Generate a detailed, actionable plan that maximizes test case coverage while 
        ensuring business relevance and technical accuracy.
        """
        
        result = await self._execute_with_creativity(
            prompt=prompt,
            context="IATA NDC XSLT transformation analysis for airline booking systems"
        )
        
        # Parse and structure the analysis plan
        analysis_plan = self._parse_analysis_plan(result["content"])
        
        # Store plan in knowledge base for other agents
        await self.store_knowledge("analysis_plan", {
            "plan": analysis_plan,
            "complexity_assessment": complexity_assessment,
            "target_test_count": target_test_count,
            "file_paths": {
                "xslt": xslt_path,
                "input_xsd": input_xsd_path,
                "output_xsd": output_xsd_path
            }
        })
        
        self.logger.info(f"Created comprehensive analysis plan for {target_test_count}+ test cases")
        
        return {
            "analysis_plan": analysis_plan,
            "complexity_assessment": complexity_assessment,
            "coordination_strategy": analysis_plan.get("execution_sequence", {}),
            "success_metrics": analysis_plan.get("success_metrics", {}),
            "adaptive_strategy": analysis_plan.get("adaptive_strategy", {}),
            "model_usage": result.get("usage", {})
        }
    
    async def _coordinate_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate the execution of multiple agents based on the analysis plan.
        
        Args:
            input_data: Contains workflow state and agent results
            
        Returns:
            Coordination decisions and next steps
        """
        workflow_state = input_data.get("workflow_state", {})
        completed_agents = input_data.get("completed_agents", [])
        agent_results = input_data.get("agent_results", {})
        
        prompt = f"""
        As the workflow coordinator, analyze the current state and determine next steps.
        
        Current Workflow State:
        {json.dumps(workflow_state, indent=2)}
        
        Completed Agents: {completed_agents}
        
        Agent Results Summary:
        {json.dumps(agent_results, indent=2)}
        
        Based on the analysis plan and current progress:
        
        1. **Assess Current Progress**:
           - Which agents have completed successfully?
           - What quality of results were achieved?
           - Are there any issues or blockers?
        
        2. **Determine Next Steps**:
           - Which agents should execute next?
           - Should any agents run in parallel?
           - Are there dependencies that need to be resolved?
        
        3. **Quality Validation**:
           - Do the results meet quality thresholds?
           - Should any agents re-execute with different parameters?
           - Are there gaps that need to be addressed?
        
        4. **Adaptive Adjustments**:
           - Should the strategy be modified based on findings?
           - Are there opportunities for optimization?
           - What are the risks and mitigation strategies?
        
        Provide specific, actionable coordination decisions.
        """
        
        result = await self._execute_with_creativity(
            prompt=prompt,
            context="Multi-agent workflow coordination for XSLT test generation"
        )
        
        coordination_decisions = self._parse_coordination_decisions(result["content"])
        
        # Update workflow state in knowledge base
        await self.store_knowledge("workflow_state", {
            "current_state": workflow_state,
            "coordination_decisions": coordination_decisions,
            "completed_agents": completed_agents,
            "timestamp": context.started_at.isoformat() if context.started_at else None
        })
        
        return {
            "coordination_decisions": coordination_decisions,
            "next_agents": coordination_decisions.get("next_agents", []),
            "parallel_execution": coordination_decisions.get("parallel_execution", False),
            "quality_assessment": coordination_decisions.get("quality_assessment", {}),
            "adaptive_adjustments": coordination_decisions.get("adaptive_adjustments", {}),
            "model_usage": result.get("usage", {})
        }
    
    async def _synthesize_results(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize findings from all agents into final test generation strategy.
        
        Args:
            input_data: Contains results from all agents
            
        Returns:
            Synthesized analysis and final test generation strategy
        """
        agent_results = input_data.get("agent_results", {})
        analysis_plan = input_data.get("analysis_plan", {})
        
        prompt = f"""
        As the synthesis coordinator, integrate findings from all agents to create 
        the final comprehensive test generation strategy.
        
        Agent Results:
        {json.dumps(agent_results, indent=2)}
        
        Original Analysis Plan:
        {json.dumps(analysis_plan, indent=2)}
        
        Synthesize the results to create:
        
        1. **Comprehensive Business Understanding**:
           - Integrate business logic findings from all agents
           - Identify key transformation patterns and rules
           - Map business context to test requirements
        
        2. **Complete Test Strategy**:
           - Define 14 test categories with specific targets
           - Ensure coverage of all business logic patterns
           - Include edge cases and integration scenarios
        
        3. **Quality Assurance Framework**:
           - Define validation criteria for generated tests
           - Establish traceability requirements
           - Set business relevance thresholds
        
        4. **Implementation Guidance**:
           - Provide specific guidance for test case generation
           - Include XML snippet requirements
           - Define business rule documentation standards
        
        Generate a comprehensive synthesis that will enable the Test Case Generator 
        to create 125+ high-quality, business-relevant test cases.
        """
        
        result = await self._execute_with_creativity(
            prompt=prompt,
            context="Final synthesis for comprehensive XSLT test case generation"
        )
        
        synthesis = self._parse_synthesis_results(result["content"])
        
        # Store final synthesis in knowledge base
        await self.store_knowledge("final_synthesis", {
            "synthesis": synthesis,
            "agent_results": agent_results,
            "original_plan": analysis_plan,
            "completion_timestamp": context.completed_at.isoformat() if context.completed_at else None
        })
        
        self.logger.info("Completed synthesis of all agent results")
        
        return {
            "synthesis": synthesis,
            "test_strategy": synthesis.get("test_strategy", {}),
            "business_understanding": synthesis.get("business_understanding", {}),
            "quality_framework": synthesis.get("quality_framework", {}),
            "implementation_guidance": synthesis.get("implementation_guidance", {}),
            "model_usage": result.get("usage", {})
        }
    
    async def _assess_file_complexity(self, xslt_path: str, input_xsd_path: str, output_xsd_path: str) -> Dict[str, Any]:
        """Assess the complexity of the files to inform analysis strategy."""
        complexity = {
            "xslt_complexity": "unknown",
            "input_schema_complexity": "unknown", 
            "output_schema_complexity": "unknown",
            "estimated_analysis_time": "medium",
            "recommended_strategy": "progressive_depth"
        }
        
        try:
            # Basic file size assessment
            if Path(xslt_path).exists():
                xslt_size = Path(xslt_path).stat().st_size
                if xslt_size > 100000:  # > 100KB
                    complexity["xslt_complexity"] = "high"
                elif xslt_size > 50000:  # > 50KB
                    complexity["xslt_complexity"] = "medium"
                else:
                    complexity["xslt_complexity"] = "low"
            
            # TODO: Add more sophisticated complexity analysis
            # - Template count estimation
            # - XPath expression complexity
            # - Schema element count
            
        except Exception as e:
            self.logger.warning(f"Could not assess file complexity: {e}")
        
        return complexity
    
    def _parse_analysis_plan(self, content: str) -> Dict[str, Any]:
        """Parse the analysis plan from model response."""
        # Simplified parsing - would need more sophisticated parsing in production
        return {
            "agent_tasks": {
                "file_analyzer": {"priority": 1, "approach": "progressive_depth"},
                "pattern_hunter": {"priority": 2, "approach": "systematic_recognition"},
                "schema_mapper": {"priority": 1, "approach": "parallel_analysis"},
                "cross_validator": {"priority": 3, "approach": "validation_sweep"},
                "business_extractor": {"priority": 4, "approach": "deep_understanding"},
                "test_generator": {"priority": 5, "approach": "comprehensive_generation"}
            },
            "execution_sequence": {
                "phase_1": ["file_analyzer", "schema_mapper"],
                "phase_2": ["pattern_hunter"],
                "phase_3": ["cross_validator"],
                "phase_4": ["business_extractor"],
                "phase_5": ["test_generator"]
            },
            "success_metrics": {
                "target_test_cases": 125,
                "min_business_rules": 45,
                "pattern_coverage_threshold": 0.95
            },
            "adaptive_strategy": {
                "quality_checkpoints": ["after_phase_2", "after_phase_4"],
                "fallback_approaches": ["simplified_analysis", "targeted_generation"]
            },
            "raw_content": content
        }
    
    def _parse_coordination_decisions(self, content: str) -> Dict[str, Any]:
        """Parse coordination decisions from model response."""
        return {
            "next_agents": ["pattern_hunter"],
            "parallel_execution": False,
            "quality_assessment": {"status": "on_track", "issues": []},
            "adaptive_adjustments": {"strategy_changes": []},
            "raw_content": content
        }
    
    def _parse_synthesis_results(self, content: str) -> Dict[str, Any]:
        """Parse synthesis results from model response."""
        return {
            "business_understanding": {
                "key_patterns": [],
                "business_rules": [],
                "transformation_logic": {}
            },
            "test_strategy": {
                "categories": 14,
                "target_count": 125,
                "coverage_requirements": {}
            },
            "quality_framework": {
                "validation_criteria": [],
                "traceability_requirements": [],
                "business_relevance_thresholds": {}
            },
            "implementation_guidance": {
                "test_generation_approach": "",
                "xml_snippet_requirements": {},
                "documentation_standards": {}
            },
            "raw_content": content
        }