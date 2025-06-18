"""
Configuration module for XML Wizard application.
Contains all configurable values that were previously hardcoded.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class RecursionLimits:
    """Configuration for recursion depth limits in XML generation."""
    max_tree_depth: int = 5
    max_element_depth: int = 8
    max_type_processing_depth: int = 3
    circular_reference_depth: int = 2


@dataclass 
class IterativeProcessing:
    """Configuration for iterative XML generation (memory safe, no recursion)."""
    enable_iterative_processing: bool = False  # Use recursive approach for correct sequence order
    max_processing_depth: int = 50  # Maximum depth for iterative processing
    max_elements_per_queue: int = 10000  # Maximum elements in processing queue
    enable_constraint_caching: bool = True  # Enable constraint extraction caching
    enable_element_tracking: bool = True  # Enable element processing tracking


@dataclass
class ElementCounts:
    """Configuration for element generation counts."""
    default_element_count: int = 2
    max_unbounded_count: int = 10
    min_element_count: int = 1
    max_array_display: int = 10


@dataclass
class DataGeneration:
    """Configuration for sample data generation patterns."""
    
    # String patterns based on element name
    string_patterns: Dict[str, str] = None
    
    # Numeric values based on element name
    numeric_patterns: Dict[str, int] = None
    
    # Date/time patterns
    date_patterns: Dict[str, str] = None
    
    # Boolean defaults (XML Schema format - lowercase strings)
    boolean_default: str = "true"
    
    # Default string length
    default_string_length: int = 10
    
    def __post_init__(self):
        if self.string_patterns is None:
            self.string_patterns = {
                'code': 'ABC123',
                'id': '{element_name}123456',
                'name': 'Sample {element_name}',
                'description': 'Sample description for {element_name}',
                'type': 'SampleType',
                'currency': 'USD',
                'country': 'US',
                'language': 'en',
                'email': 'sample@example.com',
                'phone': '+1234567890',
                'url': 'https://example.com',
                'version': '1.0'
            }
        
        if self.numeric_patterns is None:
            self.numeric_patterns = {
                'count': 5,
                'number': 123,
                'amount': 100,
                'price': 100,
                'quantity': 1,
                'total': 500,
                'tax': 10,
                'fee': 25,
                'rate': 15,
                'percentage': 10,
                'age': 25,
                'year': 2024,
                'month': 6,
                'day': 15
            }
        
        if self.date_patterns is None:
            self.date_patterns = {
                'date': '2024-06-08',
                'datetime': '2024-06-08T12:00:00Z',
                'time': '12:00:00',
                'timestamp': '2024-06-08T12:00:00.000Z',
                'duration': 'PT1H30M'  # ISO 8601 duration format
            }


@dataclass
class SchemaPatterns:
    """Configuration for schema-specific patterns and detection rules."""
    
    # Choice element detection patterns
    choice_patterns: Dict[str, List[str]] = None
    
    # Namespace mappings for different schema types
    namespace_mappings: Dict[str, Dict[str, str]] = None
    
    # Schema-specific resource directories
    resource_directories: Dict[str, str] = None
    
    # File patterns for dependency resolution
    dependency_patterns: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.choice_patterns is None:
            self.choice_patterns = {
                'iata_order_view': ['Error', 'Response'],
                'iata_error_response': ['Error', 'Response'],
                'generic_choice': []  # Will be detected automatically
            }
        
        if self.namespace_mappings is None:
            self.namespace_mappings = {
                'iata': {
                    'common_types': 'http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes',
                    'default_namespace': 'http://www.iata.org/IATA/2015/EASD/00/',
                    'prefix': 'cns'
                },
                'generic': {
                    'default_namespace': '',
                    'prefix': ''
                }
            }
        
        if self.resource_directories is None:
            self.resource_directories = {
                'iata': '21_3_5_distribution_schemas',
                'default': 'schemas'
            }
        
        if self.dependency_patterns is None:
            self.dependency_patterns = {
                'iata': ['IATA_*.xsd', '*CommonTypes.xsd', 'xmldsig-*.xsd'],
                'default': ['*.xsd']
            }


@dataclass
class PerformanceSettings:
    """Configuration for performance-related settings."""
    enable_caching: bool = True
    max_cache_size: int = 100
    enable_metrics: bool = False
    timeout_seconds: int = 30
    max_file_size_mb: int = 50


@dataclass
class UISettings:
    """Configuration for UI-related settings."""
    default_page_title: str = "XML Wizard"
    max_file_upload_mb: int = 10
    default_tree_depth: int = 10  # Increased depth for Complete mode XML generation
    show_debug_info: bool = False
    enable_download: bool = True


class Config:
    """Main configuration class that holds all settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.recursion = RecursionLimits()
        self.iterative = IterativeProcessing()
        self.elements = ElementCounts()
        self.data_generation = DataGeneration()
        self.schema_patterns = SchemaPatterns()
        self.performance = PerformanceSettings()
        self.ui = UISettings()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Load from environment variables
        self.load_from_env()
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        # Recursion limits
        self.recursion.max_tree_depth = int(os.getenv('XML_MAX_TREE_DEPTH', self.recursion.max_tree_depth))
        self.recursion.max_element_depth = int(os.getenv('XML_MAX_ELEMENT_DEPTH', self.recursion.max_element_depth))
        
        # Element counts
        self.elements.default_element_count = int(os.getenv('XML_DEFAULT_ELEMENT_COUNT', self.elements.default_element_count))
        self.elements.max_unbounded_count = int(os.getenv('XML_MAX_UNBOUNDED_COUNT', self.elements.max_unbounded_count))
        
        # Performance
        self.performance.enable_caching = os.getenv('XML_ENABLE_CACHING', 'true').lower() == 'true'
        self.performance.timeout_seconds = int(os.getenv('XML_TIMEOUT_SECONDS', self.performance.timeout_seconds))
        
        # UI settings
        self.ui.show_debug_info = os.getenv('XML_SHOW_DEBUG', 'false').lower() == 'true'
        self.ui.max_file_upload_mb = int(os.getenv('XML_MAX_UPLOAD_MB', self.ui.max_file_upload_mb))
    
    def load_from_file(self, config_file: str):
        """Load configuration from a JSON or YAML file."""
        import json
        
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    config_data = json.load(f)
                else:
                    # Try YAML if available
                    try:
                        import yaml
                        config_data = yaml.safe_load(f)
                    except ImportError:
                        raise ValueError("YAML support not available. Install PyYAML or use JSON config.")
                
                # Update configuration with loaded data
                self._update_from_dict(config_data)
        
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from a dictionary."""
        for section, values in config_data.items():
            if hasattr(self, section) and isinstance(values, dict):
                section_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def get_resource_dir(self, schema_type: str = 'iata') -> str:
        """Get the resource directory for a specific schema type."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resource_subdir = self.schema_patterns.resource_directories.get(
            schema_type, 
            self.schema_patterns.resource_directories['default']
        )
        return os.path.join(base_dir, 'resource', resource_subdir)
    
    def get_choice_patterns(self, schema_type: str = 'iata') -> List[str]:
        """Get choice patterns for a specific schema type."""
        if schema_type == 'iata':
            return self.schema_patterns.choice_patterns.get('iata_order_view', [])
        return self.schema_patterns.choice_patterns.get('generic_choice', [])
    
    def get_namespace_mapping(self, schema_type: str = 'iata') -> Dict[str, str]:
        """Get namespace mapping for a specific schema type."""
        return self.schema_patterns.namespace_mappings.get(
            schema_type, 
            self.schema_patterns.namespace_mappings['generic']
        )
    
    def get_data_pattern(self, element_name: str, data_type: str = 'string') -> Any:
        """Get data generation pattern for an element."""
        element_name_lower = element_name.lower()
        
        if data_type == 'string':
            for pattern, value in self.data_generation.string_patterns.items():
                if pattern in element_name_lower:
                    return value.format(element_name=element_name)
            return f"Sample{element_name}"
        
        elif data_type in ['int', 'integer', 'number', 'decimal', 'float', 'double']:
            for pattern, value in self.data_generation.numeric_patterns.items():
                if pattern in element_name_lower:
                    # Return appropriate numeric type
                    if data_type in ['decimal', 'float', 'double']:
                        return float(value) if 'amount' in pattern or 'price' in pattern else value
                    return value
            # Return appropriate default based on type
            if data_type in ['decimal', 'float', 'double']:
                return 123.45
            return 123
        
        elif data_type in ['date', 'datetime', 'time', 'duration']:
            # Check for specific element name patterns in priority order (most specific first)
            if data_type == 'duration':
                return self.data_generation.date_patterns['duration']
            elif 'timestamp' in element_name_lower or 'datetime' in element_name_lower:
                return self.data_generation.date_patterns['datetime']
            elif data_type == 'datetime':
                return self.data_generation.date_patterns['datetime']
            elif data_type == 'time' and 'time' in element_name_lower and 'datetime' not in element_name_lower:
                return self.data_generation.date_patterns['time']
            elif data_type == 'time':
                return self.data_generation.date_patterns['time']
            elif data_type == 'date':
                return self.data_generation.date_patterns['date']
            else:
                return self.data_generation.date_patterns['date']
        
        elif data_type == 'boolean':
            return self.data_generation.boolean_default
        
        return f"Sample{element_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'recursion': {
                'max_tree_depth': self.recursion.max_tree_depth,
                'max_element_depth': self.recursion.max_element_depth,
                'max_type_processing_depth': self.recursion.max_type_processing_depth,
                'circular_reference_depth': self.recursion.circular_reference_depth
            },
            'elements': {
                'default_element_count': self.elements.default_element_count,
                'max_unbounded_count': self.elements.max_unbounded_count,
                'min_element_count': self.elements.min_element_count,
                'max_array_display': self.elements.max_array_display
            },
            'data_generation': {
                'string_patterns': self.data_generation.string_patterns,
                'numeric_patterns': self.data_generation.numeric_patterns,
                'date_patterns': self.data_generation.date_patterns,
                'boolean_default': self.data_generation.boolean_default,
                'default_string_length': self.data_generation.default_string_length
            },
            'schema_patterns': {
                'choice_patterns': self.schema_patterns.choice_patterns,
                'namespace_mappings': self.schema_patterns.namespace_mappings,
                'resource_directories': self.schema_patterns.resource_directories,
                'dependency_patterns': self.schema_patterns.dependency_patterns
            },
            'performance': {
                'enable_caching': self.performance.enable_caching,
                'max_cache_size': self.performance.max_cache_size,
                'enable_metrics': self.performance.enable_metrics,
                'timeout_seconds': self.performance.timeout_seconds,
                'max_file_size_mb': self.performance.max_file_size_mb
            },
            'ui': {
                'default_page_title': self.ui.default_page_title,
                'max_file_upload_mb': self.ui.max_file_upload_mb,
                'default_tree_depth': self.ui.default_tree_depth,
                'show_debug_info': self.ui.show_debug_info,
                'enable_download': self.ui.enable_download
            }
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def load_config(config_file: str) -> Config:
    """Load configuration from file and return new instance."""
    return Config(config_file)