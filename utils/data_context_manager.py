"""
Data Context Manager for hierarchical data organization and retrieval.

This module provides utilities for managing hierarchical data contexts,
inheritance chains, and data resolution for XML generation.
"""

from typing import Dict, Any, List, Optional, Union, Set
import random
from pathlib import Path
import json


class DataContextManager:
    """Manages hierarchical data contexts with inheritance and resolution."""
    
    def __init__(self, data_contexts: Dict[str, Any] = None):
        """
        Initialize DataContextManager with data contexts.
        
        Args:
            data_contexts: Dictionary of named data contexts
        """
        self.data_contexts = data_contexts or {}
        self._resolved_cache = {}
        
    def resolve_data_reference(self, data_ref: str) -> Any:
        """
        Resolve a data reference like 'global.airlines.major' to actual data.
        
        Args:
            data_ref: Dot-notation reference to data
            
        Returns:
            Resolved data value or None if not found
        """
        if data_ref in self._resolved_cache:
            return self._resolved_cache[data_ref]
            
        parts = data_ref.split('.')
        current_data = self.data_contexts
        
        try:
            for part in parts:
                if isinstance(current_data, dict):
                    current_data = current_data[part]
                else:
                    return None
                    
            self._resolved_cache[data_ref] = current_data
            return current_data
            
        except (KeyError, TypeError):
            return None
    
    def get_context_data(self, context_name: str, _visited: Set[str] = None) -> Dict[str, Any]:
        """
        Get all data for a specific context with inheritance resolution.
        
        Args:
            context_name: Name of the context to retrieve
            _visited: Set to track visited contexts and prevent circular inheritance
            
        Returns:
            Resolved context data with inheritance applied
        """
        if _visited is None:
            _visited = set()
        
        # Prevent circular inheritance
        if context_name in _visited:
            return {}
        
        if context_name not in self.data_contexts:
            return {}
            
        context = self.data_contexts[context_name]
        
        # Handle inheritance
        if isinstance(context, dict) and 'inherits' in context:
            resolved_data = {}
            
            # Add current context to visited set
            _visited.add(context_name)
            
            # Apply inherited contexts first
            for parent_context in context['inherits']:
                parent_data = self.get_context_data(parent_context, _visited)
                resolved_data.update(parent_data)
            
            # Remove current context from visited set
            _visited.discard(context_name)
            
            # Apply current context data (overrides inherited)
            for key, value in context.items():
                if key != 'inherits':
                    resolved_data[key] = value
                    
            return resolved_data
        
        return context if isinstance(context, dict) else {}
    
    def resolve_wildcards(self, data_ref: str) -> List[Any]:
        """
        Resolve wildcard references like 'airports.*' to all values in category.
        
        Args:
            data_ref: Reference that may contain wildcards
            
        Returns:
            List of all matching values
        """
        if '*' not in data_ref:
            result = self.resolve_data_reference(data_ref)
            return [result] if result is not None else []
        
        parts = data_ref.split('.')
        wildcard_index = None
        
        for i, part in enumerate(parts):
            if part == '*':
                wildcard_index = i
                break
        
        if wildcard_index is None:
            return []
        
        # Get data up to wildcard
        base_ref = '.'.join(parts[:wildcard_index])
        base_data = self.resolve_data_reference(base_ref)
        
        if not isinstance(base_data, dict):
            return []
        
        # Collect all values from remaining path
        results = []
        remaining_parts = parts[wildcard_index + 1:]
        
        for key, value in base_data.items():
            if remaining_parts:
                # Continue resolving path after wildcard
                current = value
                for part in remaining_parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = None
                        break
                if current is not None:
                    if isinstance(current, list):
                        results.extend(current)
                    else:
                        results.append(current)
            else:
                # No remaining path, take the value
                if isinstance(value, list):
                    results.extend(value)
                else:
                    results.append(value)
        
        return results
    
    def get_template_data(self, template_source: str, instance_index: int = 0) -> Dict[str, Any]:
        """
        Get template data for specific instance index.
        
        Args:
            template_source: Reference to template data source
            instance_index: Index of the template instance to retrieve
            
        Returns:
            Template data for the specified instance
        """
        template_data = self.resolve_data_reference(template_source)
        
        if not isinstance(template_data, list):
            return {}
        
        if instance_index < len(template_data):
            return template_data[instance_index]
        
        # Cycle through templates if index exceeds length
        return template_data[instance_index % len(template_data)]
    
    def validate_context_structure(self) -> Dict[str, List[str]]:
        """
        Validate data context structure and return any issues found.
        
        Returns:
            Dictionary with context names as keys and lists of issues as values
        """
        issues = {}
        
        for context_name, context_data in self.data_contexts.items():
            context_issues = []
            
            if not isinstance(context_data, dict):
                context_issues.append("Context must be a dictionary")
                continue
            
            # Check inheritance chains
            if 'inherits' in context_data:
                inherits = context_data['inherits']
                if not isinstance(inherits, list):
                    context_issues.append("'inherits' must be a list")
                else:
                    for parent in inherits:
                        if parent not in self.data_contexts:
                            context_issues.append(f"Parent context '{parent}' not found")
            
            if context_issues:
                issues[context_name] = context_issues
        
        return issues
    
    def add_context(self, name: str, data: Dict[str, Any]) -> None:
        """
        Add or update a data context.
        
        Args:
            name: Context name
            data: Context data
        """
        self.data_contexts[name] = data
        self._resolved_cache.clear()  # Clear cache when contexts change
    
    def remove_context(self, name: str) -> bool:
        """
        Remove a data context.
        
        Args:
            name: Context name to remove
            
        Returns:
            True if context was removed, False if not found
        """
        if name in self.data_contexts:
            del self.data_contexts[name]
            self._resolved_cache.clear()
            return True
        return False
    
    def get_all_context_names(self) -> List[str]:
        """Get list of all available context names."""
        return list(self.data_contexts.keys())
    
    def export_contexts(self, file_path: Union[str, Path]) -> None:
        """
        Export data contexts to JSON file.
        
        Args:
            file_path: Path to export file
        """
        with open(file_path, 'w') as f:
            json.dump(self.data_contexts, f, indent=2)
    
    def import_contexts(self, file_path: Union[str, Path]) -> None:
        """
        Import data contexts from JSON file.
        
        Args:
            file_path: Path to import file
        """
        with open(file_path, 'r') as f:
            imported_contexts = json.load(f)
        
        self.data_contexts.update(imported_contexts)
        self._resolved_cache.clear()