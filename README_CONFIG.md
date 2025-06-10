# Configuration System

XML Chunker now uses a centralized configuration system to replace hardcoded values and make the application more flexible and generic.

## Configuration Files

### config.py
The main configuration module containing all configurable settings organized into logical sections:

- **RecursionLimits**: Depth limits for XML generation and tree processing
- **ElementCounts**: Default counts for elements and arrays
- **DataGeneration**: Patterns for generating sample data
- **SchemaPatterns**: Schema-specific patterns and namespace mappings
- **PerformanceSettings**: Performance-related configurations
- **UISettings**: User interface configurations

### config.example.json
Example configuration file showing all available settings. Copy this to `config.json` to customize settings.

## Usage

### Environment Variables
You can override configuration using environment variables:

```bash
export XML_MAX_TREE_DEPTH=6
export XML_DEFAULT_ELEMENT_COUNT=3
export XML_ENABLE_CACHING=false
export XML_SHOW_DEBUG=true
```

### Configuration File
Create a `config.json` file in the root directory:

```json
{
  "recursion": {
    "max_tree_depth": 6,
    "max_element_depth": 10
  },
  "elements": {
    "default_element_count": 3,
    "max_unbounded_count": 15
  },
  "data_generation": {
    "string_patterns": {
      "code": "XYZ789",
      "id": "Custom{element_name}ID"
    }
  }
}
```

### Programmatic Usage
```python
from config import get_config, load_config

# Use global config
config = get_config()

# Load from file
config = load_config('my_config.json')

# Access settings
max_depth = config.recursion.max_tree_depth
element_count = config.elements.default_element_count
resource_dir = config.get_resource_dir('iata')
```

## Configuration Sections

### Recursion Limits
Controls depth limits to prevent infinite recursion and stack overflow:
- `max_tree_depth`: Maximum depth for tree display (default: 5)
- `max_element_depth`: Maximum depth for XML element processing (default: 8)
- `max_type_processing_depth`: Depth limit for type processing (default: 3)
- `circular_reference_depth`: Depth for circular reference detection (default: 2)

### Element Counts
Controls how many elements are generated:
- `default_element_count`: Default number of elements to generate (default: 2)
- `max_unbounded_count`: Maximum count for unbounded elements (default: 10)
- `min_element_count`: Minimum count for elements (default: 1)
- `max_array_display`: Maximum elements shown in arrays (default: 10)

### Data Generation
Patterns for generating sample data based on element names:
- `string_patterns`: Mapping of element name patterns to string values
- `numeric_patterns`: Mapping of element name patterns to numeric values
- `date_patterns`: Mapping of element name patterns to date/time values
- `boolean_default`: Default boolean value (default: true)

### Schema Patterns
Schema-specific configurations:
- `choice_patterns`: Choice element detection patterns for different schema types
- `namespace_mappings`: Namespace URIs and prefixes for different schema types
- `resource_directories`: Directory names for different schema types
- `dependency_patterns`: File patterns for dependency resolution

### Performance Settings
Performance-related configurations:
- `enable_caching`: Enable caching for better performance (default: true)
- `max_cache_size`: Maximum cache entries (default: 100)
- `enable_metrics`: Enable performance metrics collection (default: false)
- `timeout_seconds`: Operation timeout in seconds (default: 30)
- `max_file_size_mb`: Maximum file size in MB (default: 50)

### UI Settings
User interface configurations:
- `default_page_title`: Application title (default: "XML Chunker")
- `max_file_upload_mb`: Maximum upload size in MB (default: 10)
- `default_tree_depth`: Default tree expansion depth (default: 4)
- `show_debug_info`: Show debug information (default: false)
- `enable_download`: Enable file downloads (default: true)

## Migration from Hardcoded Values

The following previously hardcoded values are now configurable:

| Old Hardcoded Value | New Configuration Path |
|---------------------|------------------------|
| `depth > 5` | `config.recursion.max_tree_depth` |
| `depth > 8` | `config.recursion.max_element_depth` |
| `value=2` | `config.elements.default_element_count` |
| `max_value=10` | `config.elements.max_unbounded_count` |
| `"ABC123"` | `config.data_generation.string_patterns["code"]` |
| `return 100` | `config.data_generation.numeric_patterns["amount"]` |
| `"Error", "Response"` | `config.get_choice_patterns("iata")` |
| `'21_3_5_distribution_schemas'` | `config.get_resource_dir("iata")` |
| IATA namespace URIs | `config.get_namespace_mapping("iata")` |

## Adding New Schema Types

To support a new schema type (e.g., "hl7"):

1. Add configuration in `config.json`:
```json
{
  "schema_patterns": {
    "choice_patterns": {
      "hl7": ["Error", "Success", "Warning"]
    },
    "namespace_mappings": {
      "hl7": {
        "default_namespace": "urn:hl7-org:v3",
        "prefix": "hl7"
      }
    },
    "resource_directories": {
      "hl7": "hl7_schemas"
    }
  }
}
```

2. Use in code:
```python
# Get HL7-specific settings
resource_dir = config.get_resource_dir("hl7")
choice_patterns = config.get_choice_patterns("hl7")
namespace_mapping = config.get_namespace_mapping("hl7")
```

This makes the application truly generic and extensible for any XML schema type!