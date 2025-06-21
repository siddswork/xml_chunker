"""
Shared Knowledge Base

Provides centralized storage and retrieval of analysis data across agents.
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class KnowledgeEntry:
    """Entry in the knowledge base."""
    key: str
    data: Dict[str, Any]
    agent_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    tags: Set[str] = field(default_factory=set)
    content_hash: str = ""
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate content hash for change detection."""
        content_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


class SharedKnowledgeBase:
    """
    Shared knowledge base for inter-agent data exchange.
    
    Features:
    - In-memory storage with optional persistence
    - Content-based change detection
    - Access pattern tracking
    - Tag-based organization
    - Automatic cleanup of stale data
    """
    
    def __init__(self, 
                 persist_to_disk: bool = True,
                 storage_path: Optional[Path] = None,
                 logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._storage: Dict[str, KnowledgeEntry] = {}
        self._persist_to_disk = persist_to_disk
        self._storage_path = storage_path or Path("knowledge_base.json")
        
        # Load existing data if available
        if persist_to_disk and self._storage_path.exists():
            self._load_from_disk()
    
    async def store(self,
                   key: str,
                   data: Dict[str, Any],
                   agent_id: str,
                   tags: Optional[Set[str]] = None) -> bool:
        """
        Store data in the knowledge base.
        
        Args:
            key: Unique key for the data
            data: Data to store
            agent_id: ID of the agent storing the data
            tags: Optional tags for organization
            
        Returns:
            True if data was stored/updated, False if unchanged
        """
        tags = tags or set()
        new_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        # Check if data has changed
        if key in self._storage:
            existing_entry = self._storage[key]
            if existing_entry.content_hash == new_hash:
                existing_entry.access_count += 1
                self.logger.debug(f"Data unchanged for key: {key}")
                return False
            else:
                # Update existing entry
                existing_entry.data = data
                existing_entry.updated_at = datetime.now()
                existing_entry.content_hash = new_hash
                existing_entry.tags.update(tags)
                self.logger.info(f"Updated knowledge entry: {key}")
        else:
            # Create new entry
            entry = KnowledgeEntry(
                key=key,
                data=data,
                agent_id=agent_id,
                tags=tags,
                content_hash=new_hash
            )
            self._storage[key] = entry
            self.logger.info(f"Created knowledge entry: {key}")
        
        # Persist to disk if enabled
        if self._persist_to_disk:
            await self._save_to_disk()
        
        return True
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from the knowledge base.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Stored data or None if not found
        """
        if key in self._storage:
            entry = self._storage[key]
            entry.access_count += 1
            self.logger.debug(f"Retrieved knowledge entry: {key}")
            return entry.data
        
        self.logger.debug(f"Knowledge entry not found: {key}")
        return None
    
    async def search_by_tags(self, tags: Set[str]) -> Dict[str, Dict[str, Any]]:
        """
        Search for entries by tags.
        
        Args:
            tags: Tags to search for
            
        Returns:
            Dictionary of matching entries
        """
        results = {}
        
        for key, entry in self._storage.items():
            if tags.intersection(entry.tags):
                results[key] = entry.data
                entry.access_count += 1
        
        self.logger.debug(f"Tag search for {tags} returned {len(results)} results")
        return results
    
    async def search_by_agent(self, agent_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for entries by agent ID.
        
        Args:
            agent_id: Agent ID to search for
            
        Returns:
            Dictionary of entries created by the agent
        """
        results = {}
        
        for key, entry in self._storage.items():
            if entry.agent_id == agent_id:
                results[key] = entry.data
        
        self.logger.debug(f"Agent search for {agent_id} returned {len(results)} results")
        return results
    
    async def update_tags(self, key: str, tags: Set[str]) -> bool:
        """
        Update tags for an existing entry.
        
        Args:
            key: Entry key
            tags: New tags to set
            
        Returns:
            True if updated, False if key not found
        """
        if key in self._storage:
            self._storage[key].tags = tags
            self._storage[key].updated_at = datetime.now()
            
            if self._persist_to_disk:
                await self._save_to_disk()
            
            self.logger.debug(f"Updated tags for {key}: {tags}")
            return True
        
        return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete an entry from the knowledge base.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if key not found
        """
        if key in self._storage:
            del self._storage[key]
            
            if self._persist_to_disk:
                await self._save_to_disk()
            
            self.logger.info(f"Deleted knowledge entry: {key}")
            return True
        
        return False
    
    async def cleanup_stale_data(self, max_age_hours: int = 24) -> int:
        """
        Clean up stale data entries.
        
        Args:
            max_age_hours: Maximum age in hours before data is considered stale
            
        Returns:
            Number of entries removed
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        stale_keys = []
        
        for key, entry in self._storage.items():
            if entry.updated_at < cutoff_time and entry.access_count == 0:
                stale_keys.append(key)
        
        for key in stale_keys:
            del self._storage[key]
        
        if stale_keys and self._persist_to_disk:
            await self._save_to_disk()
        
        self.logger.info(f"Cleaned up {len(stale_keys)} stale entries")
        return len(stale_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        total_entries = len(self._storage)
        agent_counts = {}
        tag_counts = {}
        total_access_count = 0
        
        for entry in self._storage.values():
            # Agent statistics
            if entry.agent_id not in agent_counts:
                agent_counts[entry.agent_id] = 0
            agent_counts[entry.agent_id] += 1
            
            # Tag statistics
            for tag in entry.tags:
                if tag not in tag_counts:
                    tag_counts[tag] = 0
                tag_counts[tag] += 1
            
            total_access_count += entry.access_count
        
        return {
            "total_entries": total_entries,
            "total_access_count": total_access_count,
            "entries_by_agent": agent_counts,
            "entries_by_tag": tag_counts,
            "storage_path": str(self._storage_path) if self._persist_to_disk else None
        }
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all keys, optionally filtered by prefix.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            List of matching keys
        """
        keys = list(self._storage.keys())
        
        if prefix:
            keys = [key for key in keys if key.startswith(prefix)]
        
        return sorted(keys)
    
    async def _save_to_disk(self):
        """Save knowledge base to disk."""
        try:
            # Convert to serializable format
            serializable_data = {}
            for key, entry in self._storage.items():
                serializable_data[key] = {
                    "data": entry.data,
                    "agent_id": entry.agent_id,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                    "access_count": entry.access_count,
                    "tags": list(entry.tags),
                    "content_hash": entry.content_hash
                }
            
            with open(self._storage_path, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            
            self.logger.debug(f"Saved knowledge base to {self._storage_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save knowledge base: {e}")
    
    def _load_from_disk(self):
        """Load knowledge base from disk."""
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to KnowledgeEntry objects
            for key, entry_data in data.items():
                entry = KnowledgeEntry(
                    key=key,
                    data=entry_data["data"],
                    agent_id=entry_data["agent_id"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                    access_count=entry_data["access_count"],
                    tags=set(entry_data["tags"]),
                    content_hash=entry_data["content_hash"]
                )
                self._storage[key] = entry
            
            self.logger.info(f"Loaded {len(self._storage)} entries from {self._storage_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            self._storage = {}