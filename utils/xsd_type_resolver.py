"""
Universal XSD Type Resolution Module

This module provides utilities for resolving XSD types to their primitive base types
without relying on element names or heuristics. Works universally with any XSD schema.
"""

from typing import Any, Optional, Dict, Tuple, Set, List
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
        """Extract comprehensive constraint information from restricted types."""
        constraints = {}
        
        # Extract facets (restrictions) - comprehensive facet extraction
        if hasattr(restricted_type, 'facets') and restricted_type.facets:
            for facet_name, facet in restricted_type.facets.items():
                try:
                    if facet_name == 'enumeration':
                        # Handle enumeration facets with multiple extraction strategies
                        constraints['enum_values'] = self._extract_enumeration_values(facet)
                    elif facet_name == 'pattern':
                        # Extract pattern constraints with validation
                        constraints['pattern'] = self._extract_pattern_constraint(facet)
                    elif facet_name == 'minLength':
                        constraints['min_length'] = int(facet)
                    elif facet_name == 'maxLength':
                        constraints['max_length'] = int(facet)
                    elif facet_name == 'length':
                        constraints['exact_length'] = int(facet)  # Use exact_length for precise control
                    elif facet_name == 'minInclusive':
                        constraints['min_value'] = self._safe_numeric_conversion(facet)
                    elif facet_name == 'maxInclusive':
                        constraints['max_value'] = self._safe_numeric_conversion(facet)
                    elif facet_name == 'minExclusive':
                        constraints['min_value_exclusive'] = self._safe_numeric_conversion(facet)
                    elif facet_name == 'maxExclusive':
                        constraints['max_value_exclusive'] = self._safe_numeric_conversion(facet)
                    elif facet_name == 'fractionDigits':
                        constraints['fraction_digits'] = int(facet)
                    elif facet_name == 'totalDigits':
                        constraints['total_digits'] = int(facet)
                    elif facet_name == 'whiteSpace':
                        constraints['whitespace'] = str(facet)  # 'preserve', 'replace', 'collapse'
                    # Handle additional XSD facets dynamically
                    else:
                        # Handle namespaced facet names
                        local_facet_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                        
                        if local_facet_name == 'pattern':
                            # Handle pattern facet that wasn't caught above
                            pattern = self._extract_pattern_constraint(facet)
                            if pattern:
                                constraints['pattern'] = pattern
                        else:
                            # Store unrecognized facets for potential future use
                            constraints[f'facet_{local_facet_name}'] = str(facet)
                except (ValueError, TypeError) as e:
                    # Log but don't fail on individual facet extraction errors
                    print(f"Warning: Failed to extract facet {facet_name}: {e}")
                    continue
        
        # Alternative enumeration extraction methods for robust enum handling
        if not constraints.get('enum_values'):
            if hasattr(restricted_type, 'enumeration') and restricted_type.enumeration:
                constraints['enum_values'] = self._extract_enumeration_values(restricted_type.enumeration)
        
        # Extract additional constraints from xmlschema object properties
        constraints.update(self._extract_additional_constraints(restricted_type))
        
        return constraints
    
    def _extract_enumeration_values(self, enum_facet) -> List[str]:
        """Extract enumeration values using multiple strategies."""
        enum_values = []
        
        try:
            # Strategy 1: Direct iteration
            if hasattr(enum_facet, '__iter__') and not isinstance(enum_facet, str):
                for val in enum_facet:
                    if val is not None and str(val).strip():
                        enum_values.append(str(val).strip())
            # Strategy 2: Single value
            elif enum_facet is not None:
                val_str = str(enum_facet).strip()
                if val_str and val_str != 'None':
                    enum_values.append(val_str)
            
            # Strategy 3: Check for value attribute
            if not enum_values and hasattr(enum_facet, 'value'):
                if hasattr(enum_facet.value, '__iter__') and not isinstance(enum_facet.value, str):
                    enum_values = [str(val).strip() for val in enum_facet.value if val is not None and str(val).strip()]
                else:
                    val_str = str(enum_facet.value).strip()
                    if val_str and val_str != 'None':
                        enum_values = [val_str]
        
        except Exception as e:
            print(f"Warning: Error extracting enumeration values: {e}")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(enum_values)) if enum_values else []
    
    def _extract_pattern_constraint(self, pattern_facet) -> Optional[str]:
        """Extract pattern constraint with validation and XsdPatternFacets handling."""
        try:
            if pattern_facet is None:
                return None
            
            # Handle XsdPatternFacets objects (they are list-like and contain patterns)
            if hasattr(pattern_facet, '__class__') and 'XsdPatternFacets' in str(pattern_facet.__class__):
                # Method 1: Use regexps attribute directly (most reliable)
                if hasattr(pattern_facet, 'regexps') and pattern_facet.regexps:
                    for pattern_str in pattern_facet.regexps:
                        if pattern_str and pattern_str.strip():
                            return self._validate_and_clean_pattern(pattern_str.strip())
                
                # Method 2: Iterate over Elements and extract from attrib
                for pattern_element in pattern_facet:
                    if pattern_element is not None:
                        # Handle XML Element objects with 'value' attribute
                        if hasattr(pattern_element, 'attrib') and 'value' in pattern_element.attrib:
                            pattern_str = pattern_element.attrib['value']
                            if pattern_str and pattern_str.strip():
                                return self._validate_and_clean_pattern(pattern_str.strip())
                        elif hasattr(pattern_element, 'get'):
                            pattern_str = pattern_element.get('value')
                            if pattern_str and pattern_str.strip():
                                return self._validate_and_clean_pattern(pattern_str.strip())
            
            # Handle xmlschema Element objects (lxml elements)
            if hasattr(pattern_facet, 'get') and hasattr(pattern_facet, 'text'):
                # This is an XML Element - extract the value attribute or text content
                if hasattr(pattern_facet, 'attrib') and 'value' in pattern_facet.attrib:
                    pattern_str = pattern_facet.attrib['value']
                    return self._validate_and_clean_pattern(pattern_str)
                elif pattern_facet.text:
                    pattern_str = pattern_facet.text
                    return self._validate_and_clean_pattern(pattern_str)
            
            # Handle xmlschema facet objects with value attribute
            if hasattr(pattern_facet, 'value') and pattern_facet.value is not None:
                pattern_str = str(pattern_facet.value)
                return self._validate_and_clean_pattern(pattern_str)
            
            # Handle other iterable objects
            if hasattr(pattern_facet, '__iter__') and not isinstance(pattern_facet, str):
                # This is likely a collection of patterns
                for pattern in pattern_facet:
                    if pattern is not None:
                        # Recursively extract from each pattern in collection
                        extracted = self._extract_pattern_constraint(pattern)
                        if extracted:
                            return extracted
            
            # Handle direct string representation
            pattern_str = str(pattern_facet).strip()
            if not pattern_str or pattern_str == 'None':
                return None
            
            # Handle XsdPatternFacets string representation like "XsdPatternFacets(['[0-9A-Z]{3}'])"
            if 'XsdPatternFacets' in pattern_str:
                import re
                # Extract pattern from XsdPatternFacets(['pattern']) format
                pattern_match = re.search(r"XsdPatternFacets\(\['([^']+)'\]", pattern_str)
                if pattern_match:
                    pattern_str = pattern_match.group(1)
                    return self._validate_and_clean_pattern(pattern_str)
                else:
                    # Try alternate format: XsdPatternFacets([pattern])
                    pattern_match = re.search(r"XsdPatternFacets\(\[([^\]]+)\]", pattern_str)
                    if pattern_match:
                        pattern_str = pattern_match.group(1).strip("'\"")
                        return self._validate_and_clean_pattern(pattern_str)
            
            # Skip XML Element object representations
            if '<Element ' in pattern_str and ' at 0x' in pattern_str:
                return None  # This is just the object representation, not useful
            
            return self._validate_and_clean_pattern(pattern_str)
                
        except Exception as e:
            print(f"Warning: Error extracting pattern constraint: {e}")
            return None
    
    def _validate_and_clean_pattern(self, pattern_str: str) -> Optional[str]:
        """Validate and clean a pattern string."""
        if not pattern_str or pattern_str == 'None':
            return None
        
        # Clean up the pattern string
        pattern_str = pattern_str.strip()
        
        # Validate pattern by attempting to compile it
        import re
        try:
            re.compile(pattern_str)
            return pattern_str
        except re.error:
            print(f"Warning: Invalid regex pattern detected: {pattern_str}")
            return pattern_str  # Return it anyway, might be usable
    
    def _safe_numeric_conversion(self, value) -> float:
        """Safely convert value to numeric type."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                return float(value.strip())
            else:
                return float(str(value))
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_additional_constraints(self, restricted_type) -> Dict[str, Any]:
        """Extract additional constraints from xmlschema object properties."""
        additional_constraints = {}
        
        try:
            # Check for validators or restrictions attribute
            if hasattr(restricted_type, 'validators'):
                for validator in restricted_type.validators:
                    validator_type = type(validator).__name__
                    if 'Pattern' in validator_type:
                        if hasattr(validator, 'pattern'):
                            pattern = self._extract_pattern_constraint(validator.pattern)
                            if pattern:
                                additional_constraints['pattern'] = pattern
                    elif 'Length' in validator_type:
                        if hasattr(validator, 'value'):
                            if 'MinLength' in validator_type:
                                additional_constraints['min_length'] = int(validator.value)
                            elif 'MaxLength' in validator_type:
                                additional_constraints['max_length'] = int(validator.value)
                            elif validator_type == 'XsdLengthFacet':
                                additional_constraints['exact_length'] = int(validator.value)
                    elif 'Digits' in validator_type:
                        if hasattr(validator, 'value'):
                            if 'Fraction' in validator_type:
                                additional_constraints['fraction_digits'] = int(validator.value)
                            elif 'Total' in validator_type:
                                additional_constraints['total_digits'] = int(validator.value)
                    elif 'Inclusive' in validator_type or 'Exclusive' in validator_type:
                        if hasattr(validator, 'value'):
                            numeric_value = self._safe_numeric_conversion(validator.value)
                            if 'MinInclusive' in validator_type:
                                additional_constraints['min_value'] = numeric_value
                            elif 'MaxInclusive' in validator_type:
                                additional_constraints['max_value'] = numeric_value
                            elif 'MinExclusive' in validator_type:
                                additional_constraints['min_value_exclusive'] = numeric_value
                            elif 'MaxExclusive' in validator_type:
                                additional_constraints['max_value_exclusive'] = numeric_value
            
            # Check for direct attributes on the restricted type
            for attr_name in ['min_length', 'max_length', 'length', 'pattern']:
                if hasattr(restricted_type, attr_name):
                    attr_value = getattr(restricted_type, attr_name)
                    if attr_value is not None:
                        if attr_name == 'length':
                            additional_constraints['exact_length'] = int(attr_value)
                        elif attr_name == 'pattern':
                            pattern = self._extract_pattern_constraint(attr_value)
                            if pattern:
                                additional_constraints['pattern'] = pattern
                        else:
                            additional_constraints[attr_name] = int(attr_value)
                            
        except Exception as e:
            print(f"Warning: Error extracting additional constraints: {e}")
        
        return additional_constraints
    
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
        
        return 'xs:string', {}
    
    def _find_element_direct(self, element_name: str):
        """Find element directly in main schema and all imported schemas."""
        # Search in main schema first
        element = self._search_elements_in_schema(self.schema, element_name)
        if element:
            return element
        
        # Search in all imported schemas
        if hasattr(self.schema, 'imports') and self.schema.imports:
            for imported_schema in self.schema.imports.values():
                element = self._search_elements_in_schema(imported_schema, element_name)
                if element:
                    return element
        
        return None
    
    def _search_elements_in_schema(self, schema, element_name: str):
        """Search for element in a specific schema."""
        if not hasattr(schema, 'elements'):
            return None
            
        # Direct name match
        for elem_name, elem_obj in schema.elements.items():
            local_name = str(elem_name).split('}')[-1] if '}' in str(elem_name) else str(elem_name)
            if local_name == element_name:
                return elem_obj
        
        # Partial match
        for elem_name, elem_obj in schema.elements.items():
            if element_name in str(elem_name):
                return elem_obj
        
        return None
    
    def _find_type_by_name(self, type_name: str):
        """Find type definition by name in main schema and all imported schemas."""
        # Search in main schema first
        type_obj = self._search_types_in_schema(self.schema, type_name)
        if type_obj:
            return type_obj
        
        # Search in all imported schemas
        if hasattr(self.schema, 'imports') and self.schema.imports:
            for imported_schema in self.schema.imports.values():
                type_obj = self._search_types_in_schema(imported_schema, type_name)
                if type_obj:
                    return type_obj
        
        return None
    
    def _search_types_in_schema(self, schema, type_name: str):
        """Search for type definition in a specific schema."""
        if not hasattr(schema, 'types'):
            return None
            
        for type_name_key, type_obj in schema.types.items():
            local_name = str(type_name_key).split('}')[-1] if '}' in str(type_name_key) else str(type_name_key)
            if local_name == type_name or type_name in local_name:
                return type_obj
        
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