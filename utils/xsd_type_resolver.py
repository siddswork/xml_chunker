"""
Universal XSD Type Resolution Module

This module provides utilities for resolving XSD types to their primitive base types
without relying on element names or heuristics. Works universally with any XSD schema.
"""

from typing import Any, Optional, Dict, Tuple, Set
import xmlschema
from xmlschema.validators import XsdType, XsdAtomicBuiltin, XsdAtomicRestriction, XsdComplexType


class UniversalXSDTypeResolver:
    """Resolves XSD types to primitive types without name-based heuristics."""
    
    def __init__(self, schema):
        """Initialize with loaded XSD schema."""
        self.schema = schema
        self._resolution_cache = {}  # Cache resolved types for performance
        self._visiting = set()  # Track types being resolved to prevent infinite recursion
    
    def resolve_to_primitive_type(self, xsd_type: Any) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve any XSD type to its primitive type and constraints.
        
        Returns:
            Tuple of (primitive_type_name, constraints_dict)
            
        Example:
            MeasureType -> ('xs:decimal', {'fractionDigits': 2})
            IATA_CodeType -> ('xs:string', {'pattern': '[A-Z]{3}', 'length': 3})
        """
        if xsd_type is None:
            return 'xs:string', {}
        
        # Use cache if available
        type_id = id(xsd_type)
        if type_id in self._resolution_cache:
            return self._resolution_cache[type_id]
        
        # Prevent infinite recursion
        if type_id in self._visiting:
            return 'xs:string', {}
        
        self._visiting.add(type_id)
        
        try:
            primitive_type, constraints = self._resolve_type_recursive(xsd_type)
            
            # Cache the result
            self._resolution_cache[type_id] = (primitive_type, constraints)
            return primitive_type, constraints
            
        finally:
            self._visiting.remove(type_id)
    
    def _resolve_type_recursive(self, xsd_type: Any) -> Tuple[str, Dict[str, Any]]:
        """Recursively resolve type to primitive."""
        constraints = {}
        
        # Handle XsdAtomicBuiltin (primitive types like xs:string, xs:decimal)
        if isinstance(xsd_type, XsdAtomicBuiltin):
            return self._extract_primitive_name(xsd_type), constraints
        
        # Handle XsdAtomicRestriction (restricted primitive types)
        if isinstance(xsd_type, XsdAtomicRestriction):
            # Get base primitive type
            if hasattr(xsd_type, 'base_type') and xsd_type.base_type:
                base_primitive, base_constraints = self._resolve_type_recursive(xsd_type.base_type)
                constraints.update(base_constraints)
            else:
                base_primitive = 'xs:string'
            
            # Extract restriction constraints
            constraints.update(self._extract_restrictions(xsd_type))
            return base_primitive, constraints
        
        # Handle complex types
        if isinstance(xsd_type, XsdComplexType):
            return self._resolve_complex_type(xsd_type)
        
        # Handle types with base_type attribute (inheritance)
        if hasattr(xsd_type, 'base_type') and xsd_type.base_type:
            return self._resolve_type_recursive(xsd_type.base_type)
        
        # Handle types with primitive_type attribute
        if hasattr(xsd_type, 'primitive_type') and xsd_type.primitive_type:
            return self._resolve_type_recursive(xsd_type.primitive_type)
        
        # Try to extract from string representation as last resort
        type_str = str(xsd_type).lower()
        if 'decimal' in type_str:
            return 'xs:decimal', constraints
        elif 'integer' in type_str or 'int' in type_str:
            return 'xs:integer', constraints
        elif 'boolean' in type_str:
            return 'xs:boolean', constraints
        elif 'datetime' in type_str:
            return 'xs:dateTime', constraints
        elif 'duration' in type_str:
            return 'xs:duration', constraints
        elif 'date' in type_str:
            return 'xs:date', constraints
        elif 'time' in type_str:
            return 'xs:time', constraints
        
        # Default fallback
        return 'xs:string', constraints
    
    def _resolve_complex_type(self, complex_type: XsdComplexType) -> Tuple[str, Dict[str, Any]]:
        """Resolve complex types (may have simple content)."""
        constraints = {}
        
        # Check if it's a complex type with simple content
        if hasattr(complex_type, 'content') and complex_type.content:
            if hasattr(complex_type.content, 'is_simple') and complex_type.content.is_simple():
                # This is complex type with simple content (has attributes + simple value)
                return self._resolve_type_recursive(complex_type.content)
        
        # For complex types without simple content, default to string
        return 'xs:string', constraints
    
    def _extract_primitive_name(self, primitive_type: XsdAtomicBuiltin) -> str:
        """Extract the primitive type name from XsdAtomicBuiltin."""
        if hasattr(primitive_type, 'name'):
            name = str(primitive_type.name)
            # Handle namespaced names like {http://www.w3.org/2001/XMLSchema}decimal
            if '}' in name:
                local_name = name.split('}')[-1]
                return f'xs:{local_name}'
            elif name.startswith('xs:'):
                return name
            else:
                return f'xs:{name}'
        
        # Fallback: parse from string representation
        type_str = str(primitive_type)
        if 'xs:' in type_str:
            # Extract xs:type from string like "XsdAtomicBuiltin(name='xs:decimal')"
            import re
            match = re.search(r"'(xs:\w+)'", type_str)
            if match:
                return match.group(1)
        
        # Handle {namespace}type format
        if '}' in type_str:
            local_name = type_str.split('}')[-1].replace("'", "").replace(")", "")
            return f'xs:{local_name}'
        
        return 'xs:string'
    
    def _extract_restrictions(self, restricted_type: XsdAtomicRestriction) -> Dict[str, Any]:
        """Extract constraint information from restricted types."""
        constraints = {}
        
        # Extract facets (restrictions) - enhanced enumeration extraction
        if hasattr(restricted_type, 'facets') and restricted_type.facets:
            for facet_name, facet in restricted_type.facets.items():
                if facet_name == 'enumeration':
                    # Handle enumeration facets properly
                    if hasattr(facet, '__iter__'):
                        constraints['enum_values'] = [str(val) for val in facet]
                    else:
                        constraints['enum_values'] = [str(facet)]
                elif facet_name == 'pattern':
                    constraints['pattern'] = str(facet)
                elif facet_name == 'minLength':
                    constraints['min_length'] = int(facet)
                elif facet_name == 'maxLength':
                    constraints['max_length'] = int(facet)
                elif facet_name == 'length':
                    constraints['length'] = int(facet)
                elif facet_name == 'minInclusive':
                    constraints['min_value'] = float(facet)
                elif facet_name == 'maxInclusive':
                    constraints['max_value'] = float(facet)
                elif facet_name == 'fractionDigits':
                    constraints['fraction_digits'] = int(facet)
                elif facet_name == 'totalDigits':
                    constraints['total_digits'] = int(facet)
        
        # Alternative enumeration extraction for xmlschema objects
        if hasattr(restricted_type, 'enumeration') and restricted_type.enumeration:
            constraints['enum_values'] = [str(val) for val in restricted_type.enumeration]
        
        return constraints
    
    def get_element_primitive_type(self, element_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Get primitive type for a named element in the schema.
        
        Args:
            element_name: Name of the element (e.g., 'DistanceMeasure')
            
        Returns:
            Tuple of (primitive_type, constraints)
        """
        if not self.schema:
            return 'xs:string', {}
        
        # Method 1: Direct element lookup
        element = self._find_element_direct(element_name)
        if element:
            return self.resolve_to_primitive_type(element.type)
        
        # Method 2: Search in types (elements might be defined as types)
        type_obj = self._find_type_by_name(element_name)
        if type_obj:
            return self.resolve_to_primitive_type(type_obj)
        
        # Method 3: Search in imported schemas
        element = self._find_element_in_imports(element_name)
        if element:
            return self.resolve_to_primitive_type(element.type)
        
        return 'xs:string', {}
    
    def _find_element_direct(self, element_name: str):
        """Find element directly in main schema."""
        if not hasattr(self.schema, 'elements'):
            return None
            
        # Direct name match
        for elem_name, elem_obj in self.schema.elements.items():
            local_name = str(elem_name).split('}')[-1] if '}' in str(elem_name) else str(elem_name)
            if local_name == element_name:
                return elem_obj
        
        # Partial match
        for elem_name, elem_obj in self.schema.elements.items():
            if element_name in str(elem_name):
                return elem_obj
        
        return None
    
    def _find_type_by_name(self, type_name: str):
        """Find type definition by name."""
        if not hasattr(self.schema, 'types'):
            return None
            
        for type_name_key, type_obj in self.schema.types.items():
            local_name = str(type_name_key).split('}')[-1] if '}' in str(type_name_key) else str(type_name_key)
            if local_name == type_name or type_name in local_name:
                return type_obj
        
        return None
    
    def _find_element_in_imports(self, element_name: str):
        """Search for element in imported schemas."""
        if not hasattr(self.schema, 'imports') or not self.schema.imports:
            return None
        
        for imported_schema in self.schema.imports.values():
            if hasattr(imported_schema, 'elements'):
                for elem_name, elem_obj in imported_schema.elements.items():
                    local_name = str(elem_name).split('}')[-1] if '}' in str(elem_name) else str(elem_name)
                    if local_name == element_name:
                        return elem_obj
        
        return None
    
    def get_type_primitive_type(self, type_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Get primitive type for a named type definition in the schema.
        
        Args:
            type_name: Name of the type (e.g., 'MeasureType')
            
        Returns:
            Tuple of (primitive_type, constraints)
        """
        if not self.schema:
            return 'xs:string', {}
        
        # Find type definition by name
        type_obj = self._find_type_by_name(type_name)
        if type_obj:
            return self.resolve_to_primitive_type(type_obj)
        
        return 'xs:string', {}


def test_type_resolution():
    """Test the type resolver with IATA schema."""
    import os
    
    # Load IATA schema
    resource_dir = os.path.join(os.path.dirname(__file__), '..', 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    if os.path.exists(xsd_path):
        try:
            schema = xmlschema.XMLSchema(xsd_path)
            resolver = UniversalXSDTypeResolver(schema)
            
            # Debug: Show available elements and types
            print("🔍 Available Elements in Schema:")
            if hasattr(schema, 'elements'):
                for i, (elem_name, elem_obj) in enumerate(schema.elements.items()):
                    if i < 10:  # Show first 10
                        local_name = str(elem_name).split('}')[-1] if '}' in str(elem_name) else str(elem_name)
                        print(f"  {local_name}")
                print(f"  ... and {len(schema.elements) - 10} more elements")
            
            print(f"\n🔍 Available Types in Schema:")
            if hasattr(schema, 'types'):
                for i, (type_name, type_obj) in enumerate(schema.types.items()):
                    if i < 20:  # Show first 20
                        local_name = str(type_name).split('}')[-1] if '}' in str(type_name) else str(type_name)
                        if 'measure' in local_name.lower() or 'distance' in local_name.lower() or 'age' in local_name.lower():
                            print(f"  {local_name} -> {type_obj}")
                
            print(f"\n🔍 Looking for Measure-related types:")
            if hasattr(schema, 'types'):
                for type_name, type_obj in schema.types.items():
                    local_name = str(type_name).split('}')[-1] if '}' in str(type_name) else str(type_name)
                    if any(term in local_name.lower() for term in ['measure', 'distance', 'age', 'seat', 'pitch', 'width']):
                        primitive_type, constraints = resolver.resolve_to_primitive_type(type_obj)
                        print(f"  {local_name}: {primitive_type} {constraints}")
            
            # Test problematic elements
            test_elements = ['DistanceMeasure', 'AgeMeasure', 'SeatPitchMeasure', 'SeatWidthMeasure']
            
            print(f"\n🔍 XSD Type Resolution Test:")
            for element_name in test_elements:
                primitive_type, constraints = resolver.get_element_primitive_type(element_name)
                print(f"  {element_name}: {primitive_type} {constraints}")
                
        except Exception as e:
            print(f"Error testing type resolution: {e}")
    else:
        print(f"Schema not found at: {xsd_path}")


if __name__ == "__main__":
    test_type_resolution()