"""
Agent Communication Bus

Handles message passing and coordination between agents.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4


@dataclass
class Message:
    """Inter-agent message."""
    message_id: str = field(default_factory=lambda: str(uuid4()))
    sender_id: str = ""
    target_id: str = ""
    message_type: str = "data"
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1=low, 5=high
    requires_response: bool = False
    correlation_id: Optional[str] = None


@dataclass
class MessageHandler:
    """Message handler registration."""
    agent_id: str
    message_types: List[str]
    handler_func: Callable
    is_async: bool = True


class AgentCommunicationBus:
    """
    Communication bus for inter-agent message passing.
    
    Provides:
    - Asynchronous message delivery
    - Message queuing and prioritization
    - Broadcast capabilities
    - Response correlation
    - Message history and monitoring
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._handlers: Dict[str, List[MessageHandler]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._message_history: List[Message] = []
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the message processing loop."""
        if not self._running:
            self._running = True
            self._processor_task = asyncio.create_task(self._process_messages())
            self.logger.info("Communication bus started")
    
    async def stop(self):
        """Stop the message processing loop."""
        if self._running:
            self._running = False
            if self._processor_task:
                self._processor_task.cancel()
                try:
                    await self._processor_task
                except asyncio.CancelledError:
                    pass
            self.logger.info("Communication bus stopped")
    
    def register_handler(
        self,
        agent_id: str,
        message_types: List[str],
        handler_func: Callable,
        is_async: bool = True
    ):
        """
        Register a message handler for an agent.
        
        Args:
            agent_id: ID of the agent registering the handler
            message_types: List of message types to handle
            handler_func: Function to call when message is received
            is_async: Whether the handler function is async
        """
        if agent_id not in self._handlers:
            self._handlers[agent_id] = []
        
        handler = MessageHandler(
            agent_id=agent_id,
            message_types=message_types,
            handler_func=handler_func,
            is_async=is_async
        )
        
        self._handlers[agent_id].append(handler)
        self.logger.info(f"Registered handler for {agent_id}: {message_types}")
    
    async def send_message(
        self,
        sender_id: str,
        target_id: str,
        message: Dict[str, Any],
        message_type: str = "data",
        priority: int = 1,
        requires_response: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message to another agent.
        
        Args:
            sender_id: ID of sending agent
            target_id: ID of target agent
            message: Message content
            message_type: Type of message
            priority: Message priority (1-5)
            requires_response: Whether response is expected
            
        Returns:
            Response data if requires_response=True, else delivery confirmation
        """
        msg = Message(
            sender_id=sender_id,
            target_id=target_id,
            message_type=message_type,
            content=message,
            priority=priority,
            requires_response=requires_response
        )
        
        # Add to queue with priority
        await self._message_queue.put((priority, msg))
        self._message_history.append(msg)
        
        self.logger.debug(f"Message queued: {sender_id} -> {target_id} ({message_type})")
        
        if requires_response:
            # Wait for response (simplified - would need proper correlation in production)
            return await self._wait_for_response(msg.message_id)
        else:
            return {"status": "queued", "message_id": msg.message_id}
    
    async def broadcast_message(
        self,
        sender_id: str,
        message: Dict[str, Any],
        message_type: str = "broadcast",
        target_agents: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Broadcast a message to multiple agents.
        
        Args:
            sender_id: ID of sending agent
            message: Message content
            message_type: Type of message
            target_agents: Specific agents to target (None = all)
            
        Returns:
            List of agent IDs that received the message
        """
        targets = target_agents or list(self._handlers.keys())
        delivered_to = []
        
        for target_id in targets:
            if target_id != sender_id:  # Don't send to self
                await self.send_message(
                    sender_id=sender_id,
                    target_id=target_id,
                    message=message,
                    message_type=message_type
                )
                delivered_to.append(target_id)
        
        self.logger.info(f"Broadcast from {sender_id} to {len(delivered_to)} agents")
        return {"delivered_to": delivered_to}
    
    async def _process_messages(self):
        """Main message processing loop."""
        while self._running:
            try:
                # Get message with priority (higher priority first)
                priority, message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=1.0
                )
                
                await self._deliver_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, message: Message):
        """Deliver a message to the target agent."""
        target_handlers = self._handlers.get(message.target_id, [])
        
        if not target_handlers:
            self.logger.warning(f"No handlers found for agent {message.target_id}")
            return
        
        # Find appropriate handler for message type
        handler = None
        for h in target_handlers:
            if message.message_type in h.message_types or "*" in h.message_types:
                handler = h
                break
        
        if not handler:
            self.logger.warning(
                f"No handler for message type {message.message_type} on agent {message.target_id}"
            )
            return
        
        try:
            # Call the handler
            if handler.is_async:
                result = await handler.handler_func(message)
            else:
                result = handler.handler_func(message)
            
            self.logger.debug(f"Message delivered: {message.sender_id} -> {message.target_id}")
            
        except Exception as e:
            self.logger.error(f"Error in message handler: {e}")
    
    async def _wait_for_response(self, message_id: str, timeout: float = 30.0) -> Dict[str, Any]:
        """Wait for a response to a specific message."""
        # Simplified implementation - would need proper correlation tracking
        await asyncio.sleep(0.1)  # Simulate processing time
        return {"status": "response_placeholder", "original_message_id": message_id}
    
    def get_message_history(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get message history, optionally filtered by agent."""
        messages = self._message_history
        
        if agent_id:
            messages = [
                msg for msg in messages 
                if msg.sender_id == agent_id or msg.target_id == agent_id
            ]
        
        return [
            {
                "message_id": msg.message_id,
                "sender_id": msg.sender_id,
                "target_id": msg.target_id,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp.isoformat(),
                "priority": msg.priority
            }
            for msg in messages
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication bus statistics."""
        total_messages = len(self._message_history)
        agent_stats = {}
        
        for msg in self._message_history:
            # Sender stats
            if msg.sender_id not in agent_stats:
                agent_stats[msg.sender_id] = {"sent": 0, "received": 0}
            agent_stats[msg.sender_id]["sent"] += 1
            
            # Receiver stats
            if msg.target_id not in agent_stats:
                agent_stats[msg.target_id] = {"sent": 0, "received": 0}
            agent_stats[msg.target_id]["received"] += 1
        
        return {
            "total_messages": total_messages,
            "registered_agents": len(self._handlers),
            "queue_size": self._message_queue.qsize(),
            "is_running": self._running,
            "agent_statistics": agent_stats
        }