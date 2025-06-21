"""
Main Agentic System Orchestration

Coordinates the execution of all agents to generate comprehensive XSLT test cases.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.base_agent import ExecutionContext, AgentStatus
from .core.communication_bus import AgentCommunicationBus
from .core.knowledge_base import SharedKnowledgeBase
from .agents.orchestrator import OrchestratorAgent
from .agents.file_analyzer import FileAnalyzerAgent
from .config.settings import AgenticSystemSettings, get_settings, validate_settings
from .utils.logging import setup_logging, get_logger


class AgenticXSLTTestGenerator:
    """
    Main orchestration system for agentic XSLT test case generation.
    
    Coordinates all agents to analyze XSLT transformations and generate 
    comprehensive test cases following the proven manual methodology.
    """
    
    def __init__(self, settings: Optional[AgenticSystemSettings] = None):
        self.settings = settings or get_settings()
        validate_settings(self.settings)
        
        # Initialize logging
        self.logger = setup_logging(
            log_level="DEBUG" if self.settings.debug_mode else "INFO",
            log_file="agentic_system.log" if not self.settings.debug_mode else None,
            log_dir=self.settings.logs_directory,
            verbose=self.settings.verbose_logging
        )
        
        # Initialize core components
        self.communication_bus = AgentCommunicationBus(logger=self.logger)
        self.knowledge_base = SharedKnowledgeBase(
            persist_to_disk=True,
            storage_path=Path(self.settings.knowledge_base_path),
            logger=self.logger
        )
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent(
            api_key=self.settings.openai_api_key,
            logger=get_logger("orchestrator")
        )
        self.file_analyzer = FileAnalyzerAgent(
            api_key=self.settings.openai_api_key,
            logger=get_logger("file_analyzer")
        )
        
        # TODO: Initialize remaining agents
        # self.pattern_hunter = PatternHunterAgent(...)
        # self.schema_mapper = SchemaMapperAgent(...)
        # self.cross_validator = CrossReferenceValidatorAgent(...)
        # self.business_extractor = BusinessLogicExtractorAgent(...)
        # self.test_generator = TestCaseGeneratorAgent(...)
        
        self.agents = {
            "orchestrator": self.orchestrator,
            "file_analyzer": self.file_analyzer
        }
        
        # Set up agent communication
        self._setup_agent_communication()
        
        self.logger.info("Agentic XSLT Test Generator initialized")
    
    async def generate_test_cases(
        self,
        xslt_file: str,
        input_xsd_file: str,
        output_xsd_file: str,
        target_test_count: int = 125
    ) -> Dict[str, Any]:
        """
        Generate comprehensive test cases for XSLT transformation.
        
        Args:
            xslt_file: Path to XSLT transformation file
            input_xsd_file: Path to input XSD schema
            output_xsd_file: Path to output XSD schema
            target_test_count: Target number of test cases to generate
            
        Returns:
            Generated test cases and analysis results
        """
        start_time = time.time()
        
        self.logger.info(f"Starting test case generation for {xslt_file}")
        self.logger.info(f"Target: {target_test_count} test cases")
        
        try:
            # Start communication bus
            await self.communication_bus.start()
            
            # Phase 1: Strategic Planning
            self.logger.info("Phase 1: Creating analysis strategy")
            analysis_plan = await self._create_analysis_plan(
                xslt_file, input_xsd_file, output_xsd_file, target_test_count
            )
            
            # Phase 2: File Analysis
            self.logger.info("Phase 2: Analyzing XSLT structure")
            file_analysis = await self._analyze_xslt_structure(xslt_file, analysis_plan)
            
            # TODO: Implement remaining phases
            # Phase 3: Pattern Recognition and Schema Analysis
            # Phase 4: Cross-Reference Validation
            # Phase 5: Business Logic Extraction
            # Phase 6: Test Case Generation
            
            execution_time = time.time() - start_time
            
            # Compile results
            results = {
                "status": "partial_success",  # Will be "success" when all phases complete
                "execution_time_seconds": execution_time,
                "analysis_plan": analysis_plan,
                "file_analysis": file_analysis,
                "test_cases": [],  # Will contain generated test cases
                "statistics": {
                    "phases_completed": 2,
                    "total_phases": 6,
                    "agents_executed": ["orchestrator", "file_analyzer"]
                }
            }
            
            self.logger.info(f"Test case generation completed in {execution_time:.2f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Test case generation failed: {e}", exc_info=True)
            raise
        finally:
            await self.communication_bus.stop()
    
    async def _create_analysis_plan(
        self,
        xslt_file: str,
        input_xsd_file: str,
        output_xsd_file: str,
        target_test_count: int
    ) -> Dict[str, Any]:
        """Create comprehensive analysis strategy using Orchestrator Agent."""
        
        context = ExecutionContext(
            agent_id="orchestrator",
            max_retries=self.settings.performance.max_retries,
            timeout_seconds=self.settings.performance.analysis_timeout
        )
        
        input_data = {
            "operation": "create_analysis_plan",
            "xslt_path": xslt_file,
            "input_xsd_path": input_xsd_file,
            "output_xsd_path": output_xsd_file,
            "target_test_count": target_test_count
        }
        
        result = await self.orchestrator.execute(context, input_data)
        
        if result.status != AgentStatus.COMPLETED:
            raise RuntimeError(f"Orchestrator failed: {result.error_message}")
        
        return result.data
    
    async def _analyze_xslt_structure(
        self,
        xslt_file: str,
        analysis_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze XSLT structure using File Analyzer Agent."""
        
        context = ExecutionContext(
            agent_id="file_analyzer",
            max_retries=self.settings.performance.max_retries,
            timeout_seconds=self.settings.performance.analysis_timeout
        )
        
        input_data = {
            "xslt_path": xslt_file,
            "analysis_plan": analysis_plan
        }
        
        result = await self.file_analyzer.execute(context, input_data)
        
        if result.status != AgentStatus.COMPLETED:
            raise RuntimeError(f"File Analyzer failed: {result.error_message}")
        
        return result.data
    
    def _setup_agent_communication(self):
        """Set up communication between agents."""
        
        # Set communication bus for all agents
        for agent in self.agents.values():
            agent.set_communication_bus(self.communication_bus)
            agent.set_knowledge_base(self.knowledge_base)
        
        # Register message handlers (simplified for MVP)
        # In production, would have more sophisticated message routing
        
        self.logger.debug("Agent communication setup completed")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics."""
        
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()
        
        return {
            "system_status": "running",
            "agents": agent_statuses,
            "communication_bus": self.communication_bus.get_statistics(),
            "knowledge_base": self.knowledge_base.get_statistics(),
            "settings": {
                "target_test_cases": self.settings.quality.min_test_cases,
                "debug_mode": self.settings.debug_mode
            }
        }
    
    async def cleanup(self):
        """Clean up system resources."""
        try:
            await self.communication_bus.stop()
            self.logger.info("System cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Convenience function for simple usage
async def generate_xslt_test_cases(
    xslt_file: str,
    input_xsd_file: str,
    output_xsd_file: str,
    target_test_count: int = 125,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate XSLT test cases.
    
    Args:
        xslt_file: Path to XSLT transformation file
        input_xsd_file: Path to input XSD schema
        output_xsd_file: Path to output XSD schema
        target_test_count: Target number of test cases
        api_key: OpenAI API key (optional if set in environment)
        
    Returns:
        Generated test cases and analysis results
    """
    
    settings = get_settings()
    if api_key:
        settings.openai_api_key = api_key
    
    system = AgenticXSLTTestGenerator(settings)
    
    try:
        return await system.generate_test_cases(
            xslt_file=xslt_file,
            input_xsd_file=input_xsd_file,
            output_xsd_file=output_xsd_file,
            target_test_count=target_test_count
        )
    finally:
        await system.cleanup()