"""
Smart Relationships Engine for handling element dependencies and constraints.

This module provides utilities for managing relationships between XML elements,
ensuring consistency, uniqueness, and applying business logic constraints.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
import random
import re
from collections import defaultdict
from .data_context_manager import DataContextManager


class SmartRelationshipsEngine:
    """Manages smart relationships between XML elements with constraint enforcement."""
    
    def __init__(self, relationships: Dict[str, Any] = None, data_context_manager: DataContextManager = None):
        """
        Initialize SmartRelationshipsEngine.
        
        Args:
            relationships: Dictionary of relationship definitions
            data_context_manager: DataContextManager instance for data resolution
        """
        self.relationships = relationships or {}
        self.data_context_manager = data_context_manager or DataContextManager()
        self.generated_values = defaultdict(list)  # Track generated values per element
        self.relationship_groups = {}  # Track related element groups
        self.constraint_violations = []
        
    def apply_relationship(self, element_name: str, instance_index: int = 0, 
                          context_values: Dict[str, Any] = None) -> Optional[Any]:
        """
        Apply relationship logic to generate value for an element.
        
        Args:
            element_name: Name of the element
            instance_index: Index of the current instance
            context_values: Current context values from related elements
            
        Returns:
            Generated value following relationship rules
        """
        context_values = context_values or {}
        
        # Find relationship that applies to this element
        for relationship_name, relationship_config in self.relationships.items():
            if element_name in relationship_config.get('fields', []):
                return self._apply_relationship_strategy(
                    relationship_name, element_name, instance_index, context_values
                )
        
        return None
    
    def _apply_relationship_strategy(self, relationship_name: str, element_name: str, 
                                   instance_index: int, context_values: Dict[str, Any]) -> Any:
        """Apply specific relationship strategy."""
        relationship = self.relationships[relationship_name]
        strategy = relationship.get('strategy', 'consistent_persona')
        
        if strategy == 'consistent_persona':
            return self._apply_consistent_persona(relationship_name, element_name, instance_index)
        elif strategy == 'dependent_values':
            return self._apply_dependent_values(relationship_name, element_name, context_values)
        elif strategy == 'constraint_based':
            return self._apply_constraint_based(relationship_name, element_name, context_values)
        
        return None
    
    def _apply_consistent_persona(self, relationship_name: str, element_name: str, instance_index: int) -> Any:
        """
        Apply consistent persona strategy - keeps related fields consistent.
        
        This ensures that elements belonging to the same persona (like passenger details)
        maintain consistency across all fields.
        """
        relationship = self.relationships[relationship_name]
        
        # Check if we have a persona template for this instance
        group_key = f"{relationship_name}_{instance_index}"
        
        if group_key not in self.relationship_groups:
            # Create new persona group
            self.relationship_groups[group_key] = self._create_persona_group(relationship, instance_index)
        
        persona_data = self.relationship_groups[group_key]
        return persona_data.get(element_name)
    
    def _create_persona_group(self, relationship: Dict[str, Any], instance_index: int) -> Dict[str, Any]:
        """Create a consistent persona group for related elements."""
        fields = relationship.get('fields', [])
        persona_data = {}
        
        # Check if relationship has predefined persona templates
        if 'persona_templates' in relationship:
            templates = relationship['persona_templates']
            if templates and instance_index < len(templates):
                return templates[instance_index].copy()
            elif templates:
                # Cycle through templates
                return templates[instance_index % len(templates)].copy()
        
        # Try to get passenger templates from data context manager
        passenger_templates = self.data_context_manager.resolve_data_reference('passenger_templates')
        if passenger_templates and isinstance(passenger_templates, list):
            if instance_index < len(passenger_templates):
                template_data = passenger_templates[instance_index].copy()
                # Filter to only include relevant fields
                filtered_data = {k: v for k, v in template_data.items() if k in fields}
                if filtered_data:
                    return filtered_data
            elif passenger_templates:
                # Cycle through templates
                template_data = passenger_templates[instance_index % len(passenger_templates)].copy()
                filtered_data = {k: v for k, v in template_data.items() if k in fields}
                if filtered_data:
                    return filtered_data
        
        # Generate consistent persona using data contexts
        for field in fields:
            # Try to get field-specific data from contexts
            field_data = self._get_field_data_for_persona(field, instance_index)
            if field_data:
                persona_data[field] = field_data
        
        return persona_data
    
    def _get_field_data_for_persona(self, field_name: str, instance_index: int) -> Any:
        """Get appropriate data for a field in a persona context."""
        # Common persona mappings
        persona_mappings = {
            'title': ['Mr', 'Ms', 'Mrs', 'Dr', 'Prof'],
            'first_name': ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa'],
            'last_name': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson'],
            'email': lambda fn, ln: f"{fn.lower()}.{ln.lower()}@email.com",
            'phone': ['+1234567890', '+1987654321', '+1555123456', '+1444999777', '+1333666999']
        }
        
        if field_name in persona_mappings:
            mapping = persona_mappings[field_name]
            if callable(mapping):
                # Handle computed fields like email
                return None  # Will be computed after other fields are set
            else:
                return mapping[instance_index % len(mapping)]
        
        return None
    
    def _apply_dependent_values(self, relationship_name: str, element_name: str, context_values: Dict[str, Any]) -> Any:
        """
        Apply dependent values strategy - element value depends on other elements.
        """
        relationship = self.relationships[relationship_name]
        depends_on = relationship.get('depends_on', [])
        
        # Check if all dependencies are available
        for dependency in depends_on:
            if dependency not in context_values:
                return None
        
        # Apply dependency logic
        if element_name == 'arrival_city' and 'departure_city' in context_values:
            # Ensure arrival is different from departure
            departure = context_values['departure_city']
            available_cities = self.data_context_manager.resolve_data_reference('global.airports') or []
            available_cities = [city for city in available_cities if city != departure]
            if available_cities:
                return random.choice(available_cities)
        
        return None
    
    def _apply_constraint_based(self, relationship_name: str, element_name: str, context_values: Dict[str, Any]) -> Any:
        """
        Apply constraint-based strategy - enforce business rules and constraints.
        """
        relationship = self.relationships[relationship_name]
        constraints = relationship.get('constraints', [])
        
        for constraint in constraints:
            if not self._evaluate_constraint(constraint, element_name, context_values):
                # Constraint violation - need to find valid value
                return self._find_constraint_compliant_value(constraint, element_name, context_values)
        
        return None
    
    def _evaluate_constraint(self, constraint: str, element_name: str, context_values: Dict[str, Any]) -> bool:
        """
        Evaluate a constraint expression.
        
        Args:
            constraint: Constraint expression like "departure_city != arrival_city"
            element_name: Current element being evaluated
            context_values: Available context values
            
        Returns:
            True if constraint is satisfied
        """
        # Simple constraint evaluation (can be extended for complex expressions)
        if '!=' in constraint:
            left, right = constraint.split('!=')
            left_val = context_values.get(left.strip())
            right_val = context_values.get(right.strip())
            return left_val != right_val
        elif '==' in constraint:
            left, right = constraint.split('==')
            left_val = context_values.get(left.strip())
            right_val = context_values.get(right.strip())
            return left_val == right_val
        elif '>' in constraint:
            left, right = constraint.split('>')
            left_val = context_values.get(left.strip())
            right_val = context_values.get(right.strip())
            if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                return left_val > right_val
        
        return True
    
    def _find_constraint_compliant_value(self, constraint: str, element_name: str, context_values: Dict[str, Any]) -> Any:
        """Find a value that satisfies the given constraint."""
        # This is a simplified implementation - can be enhanced for complex constraints
        if element_name in constraint and '!=' in constraint:
            # Find values that are different from the constraint value
            parts = constraint.split('!=')
            other_element = parts[0].strip() if parts[1].strip() == element_name else parts[1].strip()
            avoid_value = context_values.get(other_element)
            
            # Get possible values for this element
            possible_values = self._get_possible_values_for_element(element_name)
            valid_values = [v for v in possible_values if v != avoid_value]
            
            if valid_values:
                return random.choice(valid_values)
        
        return None
    
    def _get_possible_values_for_element(self, element_name: str) -> List[Any]:
        """Get possible values for an element from data contexts."""
        # Common element value mappings
        element_mappings = {
            'departure_city': 'global.airports',
            'arrival_city': 'global.airports',
            'airline': 'global.airlines',
            'cabin_class': 'global.cabin_classes'
        }
        
        if element_name in element_mappings:
            data_ref = element_mappings[element_name]
            values = self.data_context_manager.resolve_data_reference(data_ref)
            if isinstance(values, list):
                return values
            elif isinstance(values, dict):
                # Flatten dictionary values
                all_values = []
                for v in values.values():
                    if isinstance(v, list):
                        all_values.extend(v)
                    else:
                        all_values.append(v)
                return all_values
        
        return []
    
    def ensure_uniqueness(self, element_name: str, proposed_value: Any, instance_index: int) -> Any:
        """
        Ensure uniqueness for elements that require unique values.
        
        Args:
            element_name: Name of the element
            proposed_value: Proposed value to check
            instance_index: Current instance index
            
        Returns:
            Unique value (modified if necessary)
        """
        if proposed_value in self.generated_values[element_name]:
            # Value already used, need to find alternative
            possible_values = self._get_possible_values_for_element(element_name)
            unused_values = [v for v in possible_values if v not in self.generated_values[element_name]]
            
            if unused_values:
                unique_value = random.choice(unused_values)
            else:
                # All values used, append instance index to make unique
                unique_value = f"{proposed_value}_{instance_index}"
            
            self.generated_values[element_name].append(unique_value)
            return unique_value
        
        self.generated_values[element_name].append(proposed_value)
        return proposed_value
    
    def finalize_persona_group(self, relationship_name: str, instance_index: int) -> Dict[str, Any]:
        """
        Finalize persona group by computing dependent fields.
        
        Args:
            relationship_name: Name of the relationship
            instance_index: Instance index
            
        Returns:
            Complete persona data with all computed fields
        """
        group_key = f"{relationship_name}_{instance_index}"
        
        if group_key not in self.relationship_groups:
            return {}
        
        persona_data = self.relationship_groups[group_key]
        
        # Compute dependent fields like email
        if 'first_name' in persona_data and 'last_name' in persona_data and 'email' not in persona_data:
            first_name = persona_data['first_name']
            last_name = persona_data['last_name']
            persona_data['email'] = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        return persona_data
    
    def get_relationship_summary(self) -> Dict[str, Any]:
        """Get summary of all relationships and their current state."""
        summary = {
            'relationships': list(self.relationships.keys()),
            'active_groups': len(self.relationship_groups),
            'generated_values_count': {k: len(v) for k, v in self.generated_values.items()},
            'constraint_violations': len(self.constraint_violations)
        }
        return summary
    
    def reset_state(self) -> None:
        """Reset the engine state for new generation cycle."""
        self.generated_values.clear()
        self.relationship_groups.clear()
        self.constraint_violations.clear()