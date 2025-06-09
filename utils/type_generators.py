"""
Type-specific generators for XML schema validation compliance.

This module provides specialized generators for different XSD types to ensure
validation-compliant XML generation and systematic error resolution.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from datetime import datetime
import re


class BaseTypeGenerator(ABC):
    """Abstract base class for type-specific value generators."""
    
    def __init__(self, config_instance=None):
        """Initialize with configuration instance."""
        self.config = config_instance
    
    @abstractmethod
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> Any:
        """Generate a value for the specific type with optional constraints."""
        pass
    
    def _get_default_value(self, element_name: str) -> Any:
        """Get default value from config or fallback."""
        if self.config:
            return self.config.get_data_pattern(element_name, self.get_type_name())
        return self.get_fallback_value()
    
    @abstractmethod
    def get_type_name(self) -> str:
        """Return the type name for config lookups."""
        pass
    
    @abstractmethod
    def get_fallback_value(self) -> Any:
        """Return a safe fallback value."""
        pass
    
    def validate_constraints(self, value: Any, constraints: Optional[Dict] = None) -> Any:
        """Validate and adjust value based on constraints."""
        return value


class NumericTypeGenerator(BaseTypeGenerator):
    """Generator for numeric types (decimal, integer, float, double)."""
    
    def __init__(self, config_instance=None, is_decimal: bool = True):
        super().__init__(config_instance)
        self.is_decimal = is_decimal
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> Any:
        """Generate numeric value ensuring no empty strings."""
        # Get base value from config or default
        if self.config and element_name:
            base_value = self.config.get_data_pattern(element_name, 'int')
        else:
            base_value = 100 if self.is_decimal else 100
        
        # Handle amount-specific elements with realistic values
        if element_name and any(term in element_name.lower() for term in ['amount', 'price', 'cost', 'fee']):
            base_value = 99.99 if self.is_decimal else 100
        
        # Apply constraints
        value = self.validate_constraints(base_value, constraints)
        
        # Ensure proper type conversion and no empty values
        if self.is_decimal:
            return float(value) if value is not None else 0.0
        else:
            return int(value) if value is not None else 0
    
    def get_type_name(self) -> str:
        return 'decimal' if self.is_decimal else 'int'
    
    def get_fallback_value(self) -> Any:
        return 0.0 if self.is_decimal else 0
    
    def validate_constraints(self, value: Any, constraints: Optional[Dict] = None) -> Any:
        """Apply numeric constraints like min/max values."""
        if not constraints:
            return value
        
        numeric_value = float(value) if self.is_decimal else int(value)
        
        # Apply min/max constraints
        if 'min_value' in constraints:
            numeric_value = max(numeric_value, constraints['min_value'])
        if 'max_value' in constraints:
            numeric_value = min(numeric_value, constraints['max_value'])
        
        return numeric_value


class BooleanTypeGenerator(BaseTypeGenerator):
    """Generator for boolean types ensuring valid XML Schema boolean values."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid boolean value - never empty string."""
        # Use config default or fallback
        if self.config and hasattr(self.config, 'data_generation'):
            default_bool = getattr(self.config.data_generation, 'boolean_default', 'true')
        else:
            default_bool = 'true'
        
        # Ensure we return valid XML Schema boolean values
        if default_bool not in ['true', 'false', '1', '0']:
            default_bool = 'true'
        
        return default_bool
    
    def get_type_name(self) -> str:
        return 'boolean'
    
    def get_fallback_value(self) -> str:
        return 'true'


class DateTimeTypeGenerator(BaseTypeGenerator):
    """Generator for date/time types ensuring valid ISO formats."""
    
    def __init__(self, config_instance=None, date_type: str = 'datetime'):
        super().__init__(config_instance)
        self.date_type = date_type  # 'datetime', 'date', 'time', 'duration'
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid ISO format date/time - never empty string."""
        if self.config:
            pattern_value = self.config.get_data_pattern(element_name or self.date_type, self.date_type)
            if pattern_value and pattern_value.strip():
                return pattern_value
        
        # Generate current timestamp as fallback
        now = datetime.now()
        
        if self.date_type == 'date':
            return now.strftime('%Y-%m-%d')
        elif self.date_type == 'time':
            return now.strftime('%H:%M:%S')
        elif self.date_type == 'duration':
            return 'PT1H30M'  # ISO 8601 duration format (1 hour 30 minutes)
        else:  # datetime
            return now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def get_type_name(self) -> str:
        return self.date_type
    
    def get_fallback_value(self) -> str:
        if self.date_type == 'date':
            return '2024-06-08'
        elif self.date_type == 'time':
            return '12:00:00'
        elif self.date_type == 'duration':
            return 'PT1H30M'
        else:
            return '2024-06-08T12:00:00Z'


class StringTypeGenerator(BaseTypeGenerator):
    """Generator for string types with length and pattern constraints."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate string value respecting length constraints."""
        # Get base value from config
        if self.config and element_name:
            base_value = str(self.config.get_data_pattern(element_name, 'string'))
        else:
            # Create shorter default based on element name to avoid length issues
            if element_name:
                # Use just the element name without "Sample" prefix if it's long
                if len(element_name) <= 10:
                    base_value = f"S{element_name}"  # Shorter prefix
                else:
                    base_value = element_name[:8]  # Just use first 8 chars of element name
            else:
                base_value = "SampleTxt"  # Shorter default
        
        # Apply constraints
        return self.validate_constraints(base_value, constraints)
    
    def get_type_name(self) -> str:
        return 'string'
    
    def get_fallback_value(self) -> str:
        return "SampleText"
    
    def validate_constraints(self, value: str, constraints: Optional[Dict] = None) -> str:
        """Apply string constraints like length limits and patterns."""
        if not constraints:
            return value
        
        # Handle exact length first (most restrictive)
        if 'exact_length' in constraints:
            exact_len = constraints['exact_length']
            if len(value) != exact_len:
                if len(value) > exact_len:
                    value = value[:exact_len]
                else:
                    value = value.ljust(exact_len, 'X')
            return value  # Return early since exact length overrides min/max
        
        # Handle max length constraint
        if 'max_length' in constraints:
            max_len = constraints['max_length']
            if len(value) > max_len:
                # Try to create a meaningful shorter value
                if max_len >= 3:
                    value = value[:max_len]
                else:
                    # For very short limits, use simple values
                    value = 'X' * max_len
        
        # Handle min length constraint
        if 'min_length' in constraints:
            min_len = constraints['min_length']
            if len(value) < min_len:
                # Pad with meaningful characters
                padding_needed = min_len - len(value)
                value = value + ('X' * padding_needed)
        
        # Handle pattern constraints
        if 'pattern' in constraints:
            pattern = constraints['pattern']
            try:
                # Ensure pattern is a string
                pattern_str = str(pattern) if pattern is not None else ""
                if pattern_str and not re.match(pattern_str, value):
                    # For common patterns, generate compliant values based on our error analysis
                    if pattern_str == '[0-9A-Z]{1,3}':  # Service codes (most common)
                        value = '1A2'
                    elif pattern_str == '[0-9]{1,4}':  # Flight numbers
                        value = '1234'
                    elif pattern_str == '[0-9A-Z]{3}':  # Aircraft codes
                        value = '320'
                    elif pattern_str == '(IATAC|BLTRL)[A-Za-z0-9]{2}':  # Payment rule codes
                        value = 'IATAC1'
                    elif pattern_str == '([0-9]{7}[A-Za-z0-9]{8})':  # Clearance IDs
                        value = '1234567AB123456'
                    elif pattern_str == '[0-9]{1,8}':  # IIN numbers
                        value = '12345678'
                    elif pattern_str == r'[A-Z]{3}':  # Country/currency codes
                        value = 'USD'
                    elif pattern_str == r'[A-Z]{2}':
                        value = 'US'
                    elif pattern_str == r'[A-Za-z]{2}':
                        value = 'EN'
                    elif pattern_str == r'\d+':  # Numeric strings
                        value = '123'
                    else:
                        # Keep original value as fallback
                        pass
            except re.error:
                # Invalid regex pattern, skip pattern validation
                pass
        
        return value


class EnumerationTypeGenerator(BaseTypeGenerator):
    """Generator for enumerated values with smart selection and value tracking."""
    
    # Class-level tracking of used enum values for diversity
    _used_values_tracker = {}
    
    def __init__(self, config_instance=None, enum_values: Optional[List[str]] = None):
        super().__init__(config_instance)
        self.enum_values = enum_values or []
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate value from enumeration list with smart selection and tracking."""
        # Extract enum values from constraints if provided
        if constraints and 'enum_values' in constraints:
            enum_list = constraints['enum_values']
        else:
            enum_list = self.enum_values
        
        if not enum_list:
            return self.get_fallback_value()
        
        # Filter out 'None' values which are just XSD placeholders
        valid_enums = [val for val in enum_list if val != 'None']
        if not valid_enums:
            valid_enums = enum_list  # Use all if no non-None values
        
        # Smart selection with tracking for variety
        selected_value = self._select_enum_value(element_name, valid_enums)
        
        # Track usage for future variety
        self._track_enum_usage(element_name, selected_value, valid_enums)
        
        return selected_value
    
    def _select_enum_value(self, element_name: str, enum_list: List[str]) -> str:
        """Select an enumeration value with smart rotation for variety."""
        if len(enum_list) == 1:
            return enum_list[0]
        
        # Create a key for tracking this enum type
        tracking_key = f"{element_name}_{len(enum_list)}"
        
        # If we've used this enum type before, try to use a different value
        if tracking_key in self._used_values_tracker:
            used_values = self._used_values_tracker[tracking_key]
            
            # Find unused values first
            unused_values = [val for val in enum_list if val not in used_values]
            if unused_values:
                return unused_values[0]  # Use first unused value
            
            # If all values have been used, cycle through them
            # Use least recently used value
            usage_count = {val: used_values.get(val, 0) for val in enum_list}
            return min(usage_count.keys(), key=lambda x: usage_count[x])
        
        # First time encountering this enum type - use first value
        return enum_list[0]
    
    def _track_enum_usage(self, element_name: str, selected_value: str, enum_list: List[str]) -> None:
        """Track enum value usage for future selections."""
        tracking_key = f"{element_name}_{len(enum_list)}"
        
        if tracking_key not in self._used_values_tracker:
            self._used_values_tracker[tracking_key] = {}
        
        # Increment usage count
        current_count = self._used_values_tracker[tracking_key].get(selected_value, 0)
        self._used_values_tracker[tracking_key][selected_value] = current_count + 1
    
    def get_type_name(self) -> str:
        return 'enum'
    
    def get_fallback_value(self) -> str:
        return "EnumValue"
    
    @classmethod
    def get_usage_stats(cls) -> Dict[str, Dict[str, int]]:
        """Get current enum value usage statistics."""
        return cls._used_values_tracker.copy()
    
    @classmethod
    def reset_usage_tracker(cls) -> None:
        """Reset the enum value usage tracker."""
        cls._used_values_tracker.clear()


class TypeGeneratorFactory:
    """Factory for creating appropriate type generators."""
    
    def __init__(self, config_instance=None):
        self.config = config_instance
    
    def create_generator(self, xsd_type_name, constraints: Optional[Dict] = None) -> BaseTypeGenerator:
        """Create appropriate generator based on XSD type."""
        # Handle enumeration types first
        if constraints and 'enum_values' in constraints:
            return EnumerationTypeGenerator(self.config, constraints['enum_values'])
        
        # Handle xmlschema type objects with proper introspection
        if hasattr(xsd_type_name, 'primitive_type') and xsd_type_name.primitive_type:
            primitive_type = xsd_type_name.primitive_type
            if hasattr(primitive_type, 'name'):
                primitive_name = str(primitive_type.name).lower()
                
                # Check exact primitive type names for precise matching
                if 'boolean' in primitive_name:
                    return BooleanTypeGenerator(self.config)
                elif 'decimal' in primitive_name:
                    return NumericTypeGenerator(self.config, is_decimal=True)
                elif 'integer' in primitive_name:
                    return NumericTypeGenerator(self.config, is_decimal=False)
                elif 'datetime' in primitive_name:
                    return DateTimeTypeGenerator(self.config, 'datetime')
                elif 'date' in primitive_name:
                    return DateTimeTypeGenerator(self.config, 'date')
                elif 'time' in primitive_name:
                    return DateTimeTypeGenerator(self.config, 'time')
                elif 'duration' in primitive_name:
                    return DateTimeTypeGenerator(self.config, 'duration')
                elif any(t in primitive_name for t in ['float', 'double']):
                    return NumericTypeGenerator(self.config, is_decimal=True)
                elif any(t in primitive_name for t in ['string', 'token', 'normalizedstring']):
                    return StringTypeGenerator(self.config)
        
        # Check base type for type restrictions (like IndType based on boolean)
        if hasattr(xsd_type_name, 'base_type') and xsd_type_name.base_type:
            base_str = str(xsd_type_name.base_type).lower()
            if 'boolean' in base_str:
                return BooleanTypeGenerator(self.config)
        
        # Check for boolean-related type names (IndType, FlagType, etc.)
        if hasattr(xsd_type_name, 'name') and xsd_type_name.name:
            type_name = str(xsd_type_name.name).lower()
            if 'ind' in type_name or 'flag' in type_name:
                return BooleanTypeGenerator(self.config)
        
        # String-based fallback detection
        type_str = str(xsd_type_name).lower()
        
        # Enhanced string-based type detection with more specific patterns
        if 'xsdatomicbuiltin' in type_str:
            # Extract the actual type from XsdAtomicBuiltin(name='xs:type')
            if "'xs:decimal'" in type_str or "'xs:float'" in type_str or "'xs:double'" in type_str:
                return NumericTypeGenerator(self.config, is_decimal=True)
            elif "'xs:integer'" in type_str or "'xs:int'" in type_str or "'xs:long'" in type_str:
                return NumericTypeGenerator(self.config, is_decimal=False)
            elif "'xs:datetime'" in type_str:
                return DateTimeTypeGenerator(self.config, 'datetime')
            elif "'xs:date'" in type_str:
                return DateTimeTypeGenerator(self.config, 'date')
            elif "'xs:time'" in type_str:
                return DateTimeTypeGenerator(self.config, 'time')
            elif "'xs:boolean'" in type_str:
                return BooleanTypeGenerator(self.config)
            elif "'xs:string'" in type_str or "'xs:token'" in type_str:
                return StringTypeGenerator(self.config)
        
        # Fallback string-based detection
        if any(t in type_str for t in ['decimal', 'float', 'double']):
            return NumericTypeGenerator(self.config, is_decimal=True)
        elif any(t in type_str for t in ['integer', 'int', 'long', 'short']):
            return NumericTypeGenerator(self.config, is_decimal=False)
        elif 'boolean' in type_str:
            return BooleanTypeGenerator(self.config)
        elif 'datetime' in type_str:
            return DateTimeTypeGenerator(self.config, 'datetime')
        elif 'date' in type_str:
            return DateTimeTypeGenerator(self.config, 'date')
        elif 'time' in type_str:
            return DateTimeTypeGenerator(self.config, 'time')
        elif 'anyuri' in type_str:
            return StringTypeGenerator(self.config)  # URIs are strings
        else:
            return StringTypeGenerator(self.config)