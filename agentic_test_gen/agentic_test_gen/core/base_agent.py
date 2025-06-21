"""
Base Agent Framework

Provides the foundational classes and interfaces for all agents in the system.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class ModelType(Enum):
    """Available model types."""
    O4_MINI = "o4-mini"
    GPT_41 = "gpt-4.1"


@dataclass
class AgentCapability:
    """Defines what an agent can do."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    model_requirements: ModelType


@dataclass
class ExecutionContext:
    """Context for agent execution."""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    model_type: ModelType = ModelType.O4_MINI
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AgentResult:
    """Result from agent execution."""
    task_id: str
    agent_id: str
    status: AgentStatus
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    model_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all agents in the agentic system.
    
    Provides common functionality for model integration, communication,
    error handling, and result processing.
    """
    
    def __init__(
        self,
        agent_id: str,
        model_type: ModelType,
        capabilities: List[AgentCapability],
        logger: Optional[logging.Logger] = None
    ):
        self.agent_id = agent_id
        self.model_type = model_type
        self.capabilities = capabilities
        self.logger = logger or logging.getLogger(f"agent.{agent_id}")
        self.status = AgentStatus.IDLE
        self._communication_bus = None
        self._knowledge_base = None
        
    def set_communication_bus(self, bus):
        """Set the communication bus for inter-agent communication."""
        self._communication_bus = bus
        
    def set_knowledge_base(self, kb):
        """Set the shared knowledge base."""
        self._knowledge_base = kb
    
    async def execute(self, context: ExecutionContext, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: Execution context with task details
            input_data: Input data for processing
            
        Returns:
            AgentResult containing the execution results
        """
        start_time = time.time()
        self.status = AgentStatus.PROCESSING
        context.started_at = datetime.now()
        
        try:
            self.logger.info(f"Starting execution for task {context.task_id}")
            
            # Validate input
            await self._validate_input(input_data)
            
            # Execute main processing
            result_data = await self._process(context, input_data)
            
            # Validate output
            await self._validate_output(result_data)
            
            execution_time = time.time() - start_time
            context.completed_at = datetime.now()
            self.status = AgentStatus.COMPLETED
            
            result = AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data=result_data,
                execution_time_seconds=execution_time,
                metadata=context.metadata
            )
            
            self.logger.info(f"Completed task {context.task_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.status = AgentStatus.ERROR
            
            error_result = AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                data={},
                error_message=str(e),
                execution_time_seconds=execution_time,
                metadata=context.metadata
            )
            
            self.logger.error(f"Task {context.task_id} failed: {e}", exc_info=True)
            return error_result
    
    @abstractmethod
    async def _process(self, context: ExecutionContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing logic to be implemented by each agent.
        
        Args:
            context: Execution context
            input_data: Input data for processing
            
        Returns:
            Processed result data
        """
        pass
    
    async def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data format and content."""
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")
    
    async def _validate_output(self, output_data: Dict[str, Any]) -> None:
        """Validate output data format and content."""
        if not isinstance(output_data, dict):
            raise ValueError("Output data must be a dictionary")
    
    async def communicate(self, target_agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to another agent."""
        if self._communication_bus:
            return await self._communication_bus.send_message(
                sender_id=self.agent_id,
                target_id=target_agent_id,
                message=message
            )
        else:
            self.logger.warning("No communication bus available")
            return {}
    
    async def store_knowledge(self, key: str, data: Dict[str, Any]) -> None:
        """Store data in shared knowledge base."""
        if self._knowledge_base:
            await self._knowledge_base.store(
                key=f"{self.agent_id}:{key}",
                data=data,
                agent_id=self.agent_id
            )
    
    async def retrieve_knowledge(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from shared knowledge base."""
        if self._knowledge_base:
            return await self._knowledge_base.retrieve(key)
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "model_type": self.model_type.value,
            "capabilities": [cap.name for cap in self.capabilities]
        }


class ModelIntegratedAgent(BaseAgent):
    """
    Base class for agents that integrate with OpenAI models.
    
    Provides model-specific functionality for o4-mini and GPT-4.1.
    """
    
    def __init__(
        self,
        agent_id: str,
        model_type: ModelType,
        capabilities: List[AgentCapability],
        api_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(agent_id, model_type, capabilities, logger)
        self.api_key = api_key
        self._client = None
    
    async def _initialize_client(self):
        """Initialize OpenAI client."""
        if not self._client:
            try:
                import openai
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    async def _execute_with_model(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Execute prompt with the configured model.
        
        Args:
            prompt: Main prompt for the model
            system_message: Optional system message
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Model response and usage information
        """
        await self._initialize_client()
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        model_name = self._get_model_name()
        
        try:
            response = await self._client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model_name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            self.logger.error(f"Model execution failed: {e}")
            raise
    
    def _get_model_name(self) -> str:
        """Get the actual model name for API calls."""
        if self.model_type == ModelType.O4_MINI:
            return "o1-mini"  # Using actual available model
        elif self.model_type == ModelType.GPT_41:
            return "gpt-4-turbo-preview"  # Using actual available model
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    async def _execute_with_reasoning(self, prompt: str, reasoning_steps: List[str]) -> Dict[str, Any]:
        """
        Execute with step-by-step reasoning (optimized for o4-mini).
        
        Args:
            prompt: Main analysis prompt
            reasoning_steps: List of reasoning steps to follow
            
        Returns:
            Model response with reasoning trace
        """
        system_message = f"""
        You are a systematic analysis agent. Follow these reasoning steps exactly:
        
        {chr(10).join(f"{i+1}. {step}" for i, step in enumerate(reasoning_steps))}
        
        For each step, document your findings before proceeding to the next step.
        """
        
        return await self._execute_with_model(
            prompt=prompt,
            system_message=system_message,
            temperature=0.1
        )
    
    async def _execute_with_creativity(self, prompt: str, context: str) -> Dict[str, Any]:
        """
        Execute with creative problem-solving (optimized for GPT-4.1).
        
        Args:
            prompt: Main creative prompt
            context: Business context and domain knowledge
            
        Returns:
            Model response with creative insights
        """
        system_message = f"""
        You are a creative business logic expert with deep domain knowledge.
        
        Context: {context}
        
        Use your advanced reasoning capabilities to:
        1. Understand implicit business rules and patterns
        2. Generate creative and comprehensive solutions
        3. Consider edge cases and complex scenarios
        4. Provide detailed explanations and rationale
        """
        
        return await self._execute_with_model(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3,
            max_tokens=6000
        )