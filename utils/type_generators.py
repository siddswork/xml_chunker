"""
Type-specific generators for XML schema validation compliance.

This module provides specialized generators for different XSD types to ensure
validation-compliant XML generation and systematic error resolution.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from datetime import datetime
import re
import random
import base64
import uuid


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
    
    def __init__(self, config_instance=None, is_decimal: bool = True, is_integer: bool = False):
        super().__init__(config_instance)
        self.is_decimal = is_decimal
        self.is_integer = is_integer
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> Any:
        """Generate numeric value ensuring no empty strings and proper integer format."""
        # Get base value from config or default
        if self.config and element_name:
            base_value = self.config.get_data_pattern(element_name, 'int')
        else:
            base_value = 100 if self.is_decimal else 100
        
        # Handle amount-specific elements with realistic values
        if element_name and any(term in element_name.lower() for term in ['amount', 'price', 'cost', 'fee']):
            base_value = 99.99 if self.is_decimal else 100
        
        # Handle ordinal and count elements with integers
        if element_name and any(term in element_name.lower() for term in ['ordinal', 'count', 'number', 'sequence']):
            base_value = 1
            self.is_integer = True
            self.is_decimal = False
        
        # Apply constraints
        value = self.validate_constraints(base_value, constraints)
        
        # Ensure proper type conversion and no empty values
        if self.is_integer or (not self.is_decimal):
            # Force integer return for integer types to prevent "123.0" format
            return int(float(value)) if value is not None else 0
        else:
            return float(value) if value is not None else 0.0
    
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
            return 'PT1H30M'  # 1 hour 30 minutes
        else:  # datetime
            return now.strftime('%Y-%m-%dT%H:%M:%S')
    
    def get_type_name(self) -> str:
        return self.date_type
    
    def get_fallback_value(self) -> str:
        return '2024-06-08T12:00:00'


class IDTypeGenerator(BaseTypeGenerator):
    """Generator for xs:ID type ensuring valid XML ID format."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid XML ID - starts with letter/underscore, valid for XML."""
        # XML IDs must start with letter or underscore, contain only valid characters
        base_name = element_name if element_name else "ID"
        
        # Clean element name to make it ID-compliant
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        
        # Ensure it starts with letter or underscore
        if clean_name and clean_name[0].isdigit():
            clean_name = 'ID_' + clean_name
        elif not clean_name or clean_name[0] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
            clean_name = 'ID_' + clean_name
        
        # Add unique suffix to ensure uniqueness
        unique_suffix = random.randint(1000, 9999)
        return f"{clean_name}_{unique_suffix}"
    
    def get_type_name(self) -> str:
        return 'ID'
    
    def get_fallback_value(self) -> str:
        return 'ID_DefaultValue_1234'


class Base64BinaryTypeGenerator(BaseTypeGenerator):
    """Generator for xs:base64Binary type ensuring valid base64 encoding."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid base64 encoded binary data."""
        # Generate sample binary data based on element name
        if element_name and 'exponent' in element_name.lower():
            # RSA exponent is typically 65537 (0x010001)
            sample_data = b'\x01\x00\x01'
        elif element_name and 'modulus' in element_name.lower():
            # Sample RSA modulus (small for testing)
            sample_data = b'Sample RSA Modulus 1024-bit key data for testing purposes only'
        elif element_name and any(keyword in element_name.lower() for keyword in ['key', 'signature', 'cert']):
            # Sample cryptographic data
            sample_data = f"Sample cryptographic data for {element_name}".encode('utf-8')
        else:
            # Generic binary data
            sample_data = f"SampleBinaryData_{element_name}".encode('utf-8')
        
        # Apply length constraint if specified
        if constraints and 'exact_length' in constraints:
            target_length = constraints['exact_length']
            # Adjust data to produce roughly target base64 length
            # Base64 encoding inflates by ~4/3, so binary should be ~3/4 of target
            binary_length = max(1, (target_length * 3) // 4)
            sample_data = sample_data[:binary_length].ljust(binary_length, b'0')
        
        # Encode to base64
        return base64.b64encode(sample_data).decode('ascii')
    
    def get_type_name(self) -> str:
        return 'base64Binary'
    
    def get_fallback_value(self) -> str:
        return base64.b64encode(b'DefaultSampleData').decode('ascii')


class StringTypeGenerator(BaseTypeGenerator):
    """Generator for string types with length and pattern constraints."""
    
    # Comprehensive pattern library based on validation error analysis
    AVIATION_PATTERNS = {
        # Service and Reference Codes (highest frequency)
        '[0-9A-Z]{1,3}': lambda: f"{random.randint(1,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}",
        '[0-9A-Z]{3}': lambda: f"{random.randint(0,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}",
        '[A-Z]{3}': lambda: ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3)),
        '[A-Z]{2}': lambda: ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2)),
        
        # Numeric Codes
        '[0-9]{1,4}': lambda: str(random.randint(1, 9999)),
        '[0-9]{1,8}': lambda: str(random.randint(1, 99999999)),
        '[0-9]{2}': lambda: f"{random.randint(10, 99)}",
        '[0-9]{3}': lambda: f"{random.randint(100, 999)}",
        '[0-9]{4}': lambda: f"{random.randint(1000, 9999)}",
        
        # Payment and Business Codes
        '(IATAC|BLTRL)[A-Za-z0-9]{2}': lambda: f"IATAC{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}",
        '([0-9]{7}[A-Za-z0-9]{8})': lambda: f"{random.randint(1000000, 9999999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}",
        
        # Mixed Alphanumeric
        '[A-Za-z0-9]{2}': lambda: f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}",
        '[A-Za-z0-9]{3}': lambda: ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3)),
        
        # Common regex variants (normalized forms)
        r'[A-Z]{3}': lambda: ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3)),
        r'[0-9]+': lambda: str(random.randint(1, 9999)),
        r'\d+': lambda: str(random.randint(1, 9999)),
        r'[0-9A-Z]+': lambda: ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    }
    
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
    
    def generate_pattern_value(self, pattern_str: str) -> str:
        """Generate value for specific pattern using comprehensive library."""
        if pattern_str in self.AVIATION_PATTERNS:
            return self.AVIATION_PATTERNS[pattern_str]()
        
        # Dynamic pattern generation for unhandled patterns
        return self.generate_dynamic_pattern_value(pattern_str)
    
    def generate_dynamic_pattern_value(self, pattern_str: str) -> str:
        """Generate value for unknown patterns using regex analysis."""
        try:
            # Analyze pattern and generate appropriate value
            if re.match(r'\[0-9\]\{(\d+),?(\d+)?\}', pattern_str):
                # Numeric range patterns like [0-9]{1,3}
                match = re.match(r'\[0-9\]\{(\d+),?(\d+)?\}', pattern_str)
                min_len = int(match.group(1))
                max_len = int(match.group(2)) if match.group(2) else min_len
                length = random.randint(min_len, max_len)
                return ''.join([str(random.randint(0, 9)) for _ in range(length)])
            
            elif re.match(r'\[A-Z\]\{(\d+),?(\d+)?\}', pattern_str):
                # Alpha range patterns like [A-Z]{2,4}
                match = re.match(r'\[A-Z\]\{(\d+),?(\d+)?\}', pattern_str)
                min_len = int(match.group(1))
                max_len = int(match.group(2)) if match.group(2) else min_len
                length = random.randint(min_len, max_len)
                return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))
            
            elif re.match(r'\[A-Za-z0-9\]\{(\d+),?(\d+)?\}', pattern_str):
                # Mixed alphanumeric patterns
                match = re.match(r'\[A-Za-z0-9\]\{(\d+),?(\d+)?\}', pattern_str)
                min_len = int(match.group(1))
                max_len = int(match.group(2)) if match.group(2) else min_len
                length = random.randint(min_len, max_len)
                return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=length))
            
            # Default fallback for complex patterns
            return "VAL123"
            
        except Exception:
            # If pattern analysis fails, return safe default
            return "DEF123"
    
    def test_pattern_compliance(self, value: str, pattern_str: str) -> bool:
        """Test if generated value matches pattern."""
        try:
            return bool(re.match(f"^{pattern_str}$", value))
        except re.error:
            return False
    
    def validate_and_regenerate_pattern(self, value: str, pattern_str: str, max_attempts: int = 5) -> str:
        """Validate pattern compliance and regenerate if needed."""
        for attempt in range(max_attempts):
            if self.test_pattern_compliance(value, pattern_str):
                return value
            
            # Regenerate value using pattern-specific generator
            value = self.generate_pattern_value(pattern_str)
        
        # If all attempts fail, return a safe default that might work
        return "123"  # Numeric fallback for most patterns
    
    def get_type_name(self) -> str:
        return 'string'
    
    def get_fallback_value(self) -> str:
        return "SampleText"
    
    def validate_constraints(self, value: str, constraints: Optional[Dict] = None) -> str:
        """Apply string constraints like length limits and patterns with enhanced validation."""
        if not constraints:
            return value
        
        # First apply length constraints
        value = self.validate_length_constraints(value, constraints)
        
        # Then apply pattern constraints with comprehensive validation
        if 'pattern' in constraints:
            pattern = constraints['pattern']
            try:
                # Ensure pattern is a string
                pattern_str = str(pattern) if pattern is not None else ""
                if pattern_str:
                    # Use enhanced pattern validation and regeneration
                    value = self.validate_and_regenerate_pattern(value, pattern_str)
            except re.error:
                # Invalid regex pattern, skip pattern validation
                pass
        
        return value
    
    def validate_length_constraints(self, value: str, constraints: Dict) -> str:
        """Comprehensive length constraint validation with smart adjustments."""
        
        # Exact length has highest priority
        if 'exact_length' in constraints:
            target_length = constraints['exact_length']
            return self.adjust_to_exact_length(value, target_length)
        
        # Apply min/max length constraints
        min_len = constraints.get('min_length', 0)
        max_len = constraints.get('max_length', float('inf'))
        
        current_length = len(value)
        
        # Truncate if too long
        if current_length > max_len:
            value = self.smart_truncate(value, max_len)
        
        # Pad if too short
        elif current_length < min_len:
            value = self.smart_pad(value, min_len)
        
        return value
    
    def adjust_to_exact_length(self, value: str, target_length: int) -> str:
        """Adjust string to exact length requirement."""
        current_length = len(value)
        
        if current_length == target_length:
            return value
        elif current_length > target_length:
            return self.smart_truncate(value, target_length)
        else:
            return self.smart_pad(value, target_length)
    
    def smart_truncate(self, value: str, max_length: int) -> str:
        """Intelligently truncate while preserving meaning."""
        if len(value) <= max_length:
            return value
        
        # Handle edge case of zero length
        if max_length == 0:
            return ''
        
        # For any positive length, just truncate the original value
        return value[:max_length]
    
    def smart_pad(self, value: str, min_length: int) -> str:
        """Intelligently pad to meet minimum length."""
        if len(value) >= min_length:
            return value
        
        padding_needed = min_length - len(value)
        
        # Use context-appropriate padding
        if value.isdigit():
            # Numeric values - pad with zeros or digits
            return value + '0' * padding_needed
        elif value.isalpha():
            # Alphabetic values - pad with letters
            return value + 'X' * padding_needed
        else:
            # Mixed content - pad with alphanumeric
            return value + ('X' * padding_needed)


class IDTypeGenerator(BaseTypeGenerator):
    """Generator for xs:ID types ensuring valid XML ID format."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid XML ID values that start with letter/underscore."""
        # XML ID must start with letter or underscore, followed by letters, digits, hyphens, dots, underscores
        import random
        import string
        
        # Create a valid ID based on element name if available
        if element_name:
            # Remove namespace prefix if present
            local_name = element_name.split(':')[-1] if ':' in element_name else element_name
            # Create ID starting with letter and element name
            base_id = f"ID_{local_name}_{random.randint(1, 9999)}"
        else:
            # Generic ID
            base_id = f"ID_{random.randint(1, 9999)}"
        
        # Ensure ID starts with letter and contains only valid characters
        valid_id = ''.join(c if c.isalnum() or c in '_-.' else '_' for c in base_id)
        if not valid_id[0].isalpha() and valid_id[0] != '_':
            valid_id = 'ID_' + valid_id
        
        return valid_id
    
    def get_type_name(self) -> str:
        return 'ID'
    
    def get_fallback_value(self) -> str:
        return "ID_123"


class Base64BinaryTypeGenerator(BaseTypeGenerator):
    """Generator for xs:base64Binary types ensuring valid base64 encoding."""
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Generate valid base64Binary values."""
        import base64
        import random
        
        # Create sample binary data based on element purpose
        if element_name and any(term in element_name.lower() for term in ['signature', 'key', 'modulus', 'exponent']):
            # For cryptographic elements, generate longer base64 data
            sample_data = f"CryptographicData_{element_name}_{random.randint(1000, 9999)}".encode('utf-8')
            # Pad to make it longer for realistic crypto data
            sample_data += b'0' * random.randint(50, 200)
        else:
            # For general binary data
            sample_data = f"BinaryData_{element_name or 'Sample'}_{random.randint(100, 999)}".encode('utf-8')
        
        # Encode as base64
        base64_value = base64.b64encode(sample_data).decode('ascii')
        
        # Apply length constraints if specified
        if constraints:
            if 'max_length' in constraints:
                max_len = constraints['max_length']
                if len(base64_value) > max_len:
                    # Truncate but ensure valid base64 (multiple of 4)
                    truncated_len = (max_len // 4) * 4
                    base64_value = base64_value[:truncated_len]
            
            if 'min_length' in constraints:
                min_len = constraints['min_length']
                while len(base64_value) < min_len:
                    # Pad with additional base64 data
                    additional_data = b'PADDING' * ((min_len - len(base64_value)) // 8 + 1)
                    additional_b64 = base64.b64encode(additional_data).decode('ascii')
                    base64_value += additional_b64
                    if len(base64_value) > min_len:
                        # Truncate to exact length (multiple of 4)
                        target_len = (min_len // 4) * 4
                        if target_len < min_len:
                            target_len += 4  # Round up to next multiple of 4
                        base64_value = base64_value[:target_len]
                        break
        
        return base64_value
    
    def get_type_name(self) -> str:
        return 'base64Binary'
    
    def get_fallback_value(self) -> str:
        import base64
        return base64.b64encode(b"SampleBinaryData").decode('ascii')


class EnumerationTypeGenerator(BaseTypeGenerator):
    """Generator for enumerated values with smart selection and value tracking."""
    
    # Class-level tracking of used enum values for diversity
    _used_values_tracker = {}
    
    def __init__(self, config_instance=None, enum_values: Optional[List[str]] = None):
        super().__init__(config_instance)
        self.enum_values = enum_values or []
    
    def generate(self, element_name: str = "", constraints: Optional[Dict] = None) -> str:
        """Enhanced enumeration generation with robust fallbacks and validation."""
        
        # Extract enum values with multiple strategies
        enum_list = []
        
        if constraints and 'enum_values' in constraints:
            enum_list = constraints['enum_values']
        elif self.enum_values:
            enum_list = self.enum_values
        
        # Filter and validate enum values - remove None/empty/invalid values
        valid_enums = [val for val in enum_list if val and val.strip() and val != 'None' and str(val) != 'None']
        
        if not valid_enums:
            # Try element-specific fallbacks first, then use general fallback
            fallback_value = self.get_element_specific_fallback(element_name)
            if fallback_value == "VALUE":  # No specific fallback found
                return self.get_fallback_value()
            return fallback_value
        
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
    
    def get_element_specific_fallback(self, element_name: str) -> str:
        """Provide element-specific enumeration fallbacks for aviation schemas."""
        fallbacks = {
            # Currency and Country Codes
            'currencycode': 'USD',
            'countrycode': 'US', 
            'languagecode': 'EN',
            'iata_locationcode': 'LAX',
            
            # Tax and Payment Codes
            'taxtypecode': 'TAX',
            'paymentmethodcode': 'CC',
            'statuscode': 'OK',
            
            # Cabin and Class Codes
            'classcode': 'Y',
            'cabincode': 'Y',
            'cabintypecode': 'Y',
            'cabintypename': 'Economy',
            
            # Baggage and Rules
            'bagrulecode': 'Y',
            'bagdisclosurerulecode': 'Y',
            
            # Measurements
            'weightunitofmeasurement': 'KGM',
            'lengthunitofmeasurement': 'CMT',
            
            # Personal Info
            'gendercode': 'M',
            'documenttypecode': 'PP',
            'passengertypecode': 'ADT',
            'name': 'Father Surname',  # For AddlNameTypeCode
            'typename': 'Father Surname',
            'addlnametype': 'Father Surname',
            
            # Seat and Service
            'seatcharacteristiccode': 'A',
            'mealcode': 'KSML',
            
            # Airline and Aircraft
            'airlinecode': 'AA',
            'airlinedesigcode': 'AA',
            'aircraftcode': '320',
            'airportcode': 'LAX',
            
            # Applied/Exempt type patterns
            'applied': 'Applied',
            'exempt': 'Exempt',
            'appliedexempt': 'Applied',
            
            # Action codes
            'actioncode': 'Add',
            'action': 'Add',
            
            # Disclosure rules
            'disclosurerule': 'D',
            'disclosure': 'D',
            
            # Common IATA patterns
            'typecode': 'Other',
            'code': 'ABC',
            'type': 'Other',
            'taxonomycode': 'ABC',
            'codeset': 'ABC',
        }
        
        # Match by element name patterns (case insensitive)
        element_lower = element_name.lower()
        for pattern, fallback in fallbacks.items():
            if pattern in element_lower:
                return fallback
        
        return "VALUE"  # Ultimate fallback
    
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
        
        # Handle special XSD types by name inspection first
        type_str = str(xsd_type_name).lower()
        
        # Check for specific XSD types that need special handling
        if "'xs:id'" in type_str or ('xsdatomicbuiltin' in type_str and "'xs:id'" in type_str):
            return IDTypeGenerator(self.config)
        elif "'xs:base64binary'" in type_str or 'base64binary' in type_str:
            return Base64BinaryTypeGenerator(self.config)
        
        # Handle xmlschema type objects with proper introspection
        if hasattr(xsd_type_name, 'primitive_type') and xsd_type_name.primitive_type:
            primitive_type = xsd_type_name.primitive_type
            if hasattr(primitive_type, 'name'):
                primitive_name = str(primitive_type.name).lower()
                
                # Check exact primitive type names for precise matching
                if 'boolean' in primitive_name:
                    return BooleanTypeGenerator(self.config)
                elif 'decimal' in primitive_name:
                    return NumericTypeGenerator(self.config, is_decimal=True, is_integer=False)
                elif 'integer' in primitive_name or 'int' in primitive_name:
                    return NumericTypeGenerator(self.config, is_decimal=False, is_integer=True)
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
                elif 'id' in primitive_name and primitive_name.endswith('id'):
                    return IDTypeGenerator(self.config)
                elif 'base64binary' in primitive_name:
                    return Base64BinaryTypeGenerator(self.config)
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
        try:
            type_str = str(xsd_type_name).lower()
        except Exception:
            # If string conversion fails, return string generator as fallback
            return StringTypeGenerator(self.config)
        
        # Enhanced string-based type detection with more specific patterns
        if 'xsdatomicbuiltin' in type_str:
            # Extract the actual type from XsdAtomicBuiltin(name='xs:type')
            if "'xs:decimal'" in type_str or "'xs:float'" in type_str or "'xs:double'" in type_str:
                return NumericTypeGenerator(self.config, is_decimal=True, is_integer=False)
            elif "'xs:integer'" in type_str or "'xs:int'" in type_str or "'xs:long'" in type_str:
                return NumericTypeGenerator(self.config, is_decimal=False, is_integer=True)
            elif "'xs:datetime'" in type_str:
                return DateTimeTypeGenerator(self.config, 'datetime')
            elif "'xs:date'" in type_str:
                return DateTimeTypeGenerator(self.config, 'date')
            elif "'xs:time'" in type_str:
                return DateTimeTypeGenerator(self.config, 'time')
            elif "'xs:duration'" in type_str:
                return DateTimeTypeGenerator(self.config, 'duration')
            elif "'xs:boolean'" in type_str:
                return BooleanTypeGenerator(self.config)
            elif "'xs:string'" in type_str or "'xs:token'" in type_str:
                return StringTypeGenerator(self.config)
        
        # Fallback string-based detection
        if any(t in type_str for t in ['decimal', 'float', 'double']):
            return NumericTypeGenerator(self.config, is_decimal=True, is_integer=False)
        elif any(t in type_str for t in ['integer', 'int', 'long', 'short']):
            return NumericTypeGenerator(self.config, is_decimal=False, is_integer=True)
        elif 'boolean' in type_str:
            return BooleanTypeGenerator(self.config)
        elif 'datetime' in type_str:
            return DateTimeTypeGenerator(self.config, 'datetime')
        elif 'duration' in type_str:
            return DateTimeTypeGenerator(self.config, 'duration')
        elif 'date' in type_str:
            return DateTimeTypeGenerator(self.config, 'date')
        elif 'time' in type_str:
            return DateTimeTypeGenerator(self.config, 'time')
        elif "'xs:id'" in type_str or 'xsdatomicbuiltin' in type_str and 'id' in type_str:
            return IDTypeGenerator(self.config)
        elif 'base64binary' in type_str:
            return Base64BinaryTypeGenerator(self.config)
        elif 'anyuri' in type_str:
            return StringTypeGenerator(self.config)  # URIs are strings
        else:
            return StringTypeGenerator(self.config)