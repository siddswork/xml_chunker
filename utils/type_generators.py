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
        self.date_type = date_type  # 'datetime', 'date', 'time'
    
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
        else:  # datetime
            return now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def get_type_name(self) -> str:
        return self.date_type
    
    def get_fallback_value(self) -> str:
        if self.date_type == 'date':
            return '2024-06-08'
        elif self.date_type == 'time':
            return '12:00:00'
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
            base_value = f"Sample{element_name}" if element_name else "SampleText"
        
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
        
        # Handle length constraints
        if 'max_length' in constraints:
            max_len = constraints['max_length']
            if len(value) > max_len:
                value = value[:max_len]
        
        if 'min_length' in constraints:
            min_len = constraints['min_length']
            if len(value) < min_len:
                value = value.ljust(min_len, 'X')
        
        if 'exact_length' in constraints:
            exact_len = constraints['exact_length']
            if len(value) != exact_len:
                if len(value) > exact_len:
                    value = value[:exact_len]
                else:
                    value = value.ljust(exact_len, 'X')
        
        # Handle pattern constraints
        if 'pattern' in constraints:
            pattern = constraints['pattern']
            if not re.match(pattern, value):
                # For common patterns, generate compliant values
                if pattern == r'[A-Z]{3}':  # Country/currency codes
                    value = 'USD'
                elif pattern == r'[A-Z]{2}':
                    value = 'US'
                else:
                    # Keep original value as fallback
                    pass
        
        return value


class EnumerationTypeGenerator(BaseTypeGenerator):
    """Generator for enumerated values ensuring valid choices."""
    
    def __init__(self, config_instance=None, enum_values: Optional[List[str]] = None):
        super().__init__(config_instance)
        self.enum_values = enum_values or []
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate value from enumeration list."""
        # Extract enum values from constraints if provided
        if constraints and 'enum_values' in constraints:
            enum_list = constraints['enum_values']
        else:
            enum_list = self.enum_values
        
        if not enum_list:
            return self.get_fallback_value()
        
        # Use first valid enumeration value
        return enum_list[0]
    
    def get_type_name(self) -> str:
        return 'enum'
    
    def get_fallback_value(self) -> str:
        return "EnumValue"


class TypeGeneratorFactory:
    """Factory for creating appropriate type generators."""
    
    def __init__(self, config_instance=None):
        self.config = config_instance
    
    def create_generator(self, xsd_type_name: str, constraints: Optional[Dict] = None) -> BaseTypeGenerator:
        """Create appropriate generator based on XSD type."""
        type_str = str(xsd_type_name).lower()
        
        # Handle enumeration types first
        if constraints and 'enum_values' in constraints:
            return EnumerationTypeGenerator(self.config, constraints['enum_values'])
        
        # Numeric types
        if any(t in type_str for t in ['decimal', 'float', 'double']):
            return NumericTypeGenerator(self.config, is_decimal=True)
        elif any(t in type_str for t in ['integer', 'int', 'long', 'short']):
            return NumericTypeGenerator(self.config, is_decimal=False)
        
        # Boolean types
        elif 'boolean' in type_str:
            return BooleanTypeGenerator(self.config)
        
        # Date/time types
        elif 'datetime' in type_str:
            return DateTimeTypeGenerator(self.config, 'datetime')
        elif 'date' in type_str:
            return DateTimeTypeGenerator(self.config, 'date')
        elif 'time' in type_str:
            return DateTimeTypeGenerator(self.config, 'time')
        
        # String types (default)
        else:
            return StringTypeGenerator(self.config)