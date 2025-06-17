# Enhanced JSON Configuration Guide

## Table of Contents
1. [Overview](#overview)
2. [Configuration Structure](#configuration-structure)
3. [Metadata Section](#metadata-section)
4. [Generation Settings](#generation-settings)
5. [Data Contexts](#data-contexts)
6. [Smart Relationships](#smart-relationships)
7. [Element Configurations](#element-configurations)
8. [Global Overrides](#global-overrides)
9. [Complete Example](#complete-example)
10. [XML Output Examples](#xml-output-examples)
11. [Best Practices](#best-practices)

## Overview

The Enhanced JSON Configuration system provides powerful control over XML generation from XSD schemas. It supports hierarchical data contexts, smart relationships between elements, and flexible value selection strategies.

### Key Features
- **Hierarchical Data Contexts**: Organize data with inheritance
- **Smart Relationships**: Ensure consistency between related elements
- **Selection Strategies**: Control how values are selected (sequential, random, seeded)
- **Template Processing**: Generate deterministic entities like passengers
- **Constraint-Based Generation**: Apply business rules and constraints

## Configuration Structure

```json
{
  "metadata": { ... },
  "generation_settings": { ... },
  "data_contexts": { ... },
  "smart_relationships": { ... },
  "element_configs": { ... },
  "global_overrides": { ... }
}
```

## Metadata Section

Defines basic information about the configuration.

```json
{
  "metadata": {
    "name": "Configuration Name",
    "description": "Detailed description of what this config generates",
    "schema_name": "target_schema.xsd",
    "created": "2025-06-17T12:00:00.000000",
    "version": "2.0"
  }
}
```

**Required Fields:**
- `name`: Human-readable configuration name
- `schema_name`: Target XSD schema filename

**Optional Fields:**
- `description`: Detailed description
- `created`: ISO timestamp
- `version`: Configuration version

## Generation Settings

Controls the overall XML generation behavior.

```json
{
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 1,
    "max_depth": 8,
    "include_comments": true,
    "deterministic_seed": 12345,
    "ensure_unique_combinations": true
  }
}
```

### Field Descriptions

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `mode` | string | `"Minimalistic"`, `"Complete"`, `"Custom"` | Generation complexity level |
| `global_repeat_count` | integer | 1-50 | Default repeat count for unbounded elements |
| `max_depth` | integer | 1-10 | Maximum nesting depth for XML structure |
| `include_comments` | boolean | `true`, `false` | Include occurrence info as XML comments |
| `deterministic_seed` | integer | Any integer | Seed for reproducible random generation |
| `ensure_unique_combinations` | boolean | `true`, `false` | Prevent duplicate value combinations |

## Data Contexts

Hierarchical data organization with inheritance support.

### Basic Data Context

```json
{
  "data_contexts": {
    "global": {
      "airlines": ["AA", "UA", "DL", "WN", "B6"],
      "airports": ["NYC", "LAX", "CHI", "MIA", "SEA"],
      "cabin_classes": ["Y", "C", "F", "W"]
    }
  }
}
```

### Data Context with Inheritance

```json
{
  "data_contexts": {
    "base_travel": {
      "airlines": ["AA", "UA", "DL"],
      "airports": ["NYC", "LAX", "CHI"]
    },
    "premium_travel": {
      "inherits": ["base_travel"],
      "cabin_classes": ["C", "F"],
      "services": ["priority_boarding", "lounge_access"]
    }
  }
}
```

### Dot-Notation References

Access nested data using dot notation:

```json
{
  "data_contexts": {
    "global": {
      "airlines": {
        "major": ["AA", "UA", "DL"],
        "budget": ["WN", "B6", "NK"]
      }
    }
  }
}
```

Reference: `"global.airlines.major"` → `["AA", "UA", "DL"]`

## Smart Relationships

Ensure consistency and apply constraints between related elements.

### Consistent Persona Strategy

```json
{
  "smart_relationships": {
    "passenger_data": {
      "fields": ["first_name", "last_name", "email", "phone"],
      "strategy": "consistent_persona",
      "ensure_unique": false
    }
  }
}
```

### Dependent Values Strategy

```json
{
  "smart_relationships": {
    "flight_routing": {
      "fields": ["departure_city", "arrival_city"],
      "strategy": "dependent_values",
      "depends_on": ["departure_city"],
      "constraints": ["departure_city != arrival_city"]
    }
  }
}
```

### Constraint-Based Strategy

```json
{
  "smart_relationships": {
    "booking_constraints": {
      "fields": ["departure_date", "return_date"],
      "strategy": "constraint_based",
      "constraints": ["return_date > departure_date"]
    }
  }
}
```

## Element Configurations

Define how individual XML elements should be generated.

### Basic Element Config

```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],
      "selection_strategy": "sequential"
    }
  }
}
```

### Advanced Element Config

```json
{
  "element_configs": {
    "passenger": {
      "repeat_count": 3,
      "relationship": "passenger_data",
      "ensure_unique": true
    },
    "first_name": {
      "data_context": "global.names.first",
      "selection_strategy": "seeded",
      "template_source": "passenger_templates"
    }
  }
}
```

### Selection Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| `sequential` | Values selected in order | 1st call: "AA", 2nd call: "UA", 3rd call: "DL" |
| `random` | Values selected randomly | Random selection from array |
| `seeded` | Deterministic random using seed | Reproducible "random" selection |
| `template` | Use template-based generation | Passenger templates with consistent data |

## Global Overrides

System-wide settings that affect all elements.

```json
{
  "global_overrides": {
    "use_realistic_data": true,
    "preserve_structure": true,
    "default_string_length": 50,
    "namespace_prefixes": {
      "cns": "http://www.iata.org/IATA/2015/00/2019.2/IATA_CommonTypes"
    }
  }
}
```

## Complete Example

Here's a comprehensive configuration for an airline booking system:

```json
{
  "metadata": {
    "name": "Airline Booking Configuration",
    "description": "Enhanced configuration for generating realistic airline booking XML",
    "schema_name": "AirlineBooking.xsd",
    "created": "2025-06-17T12:00:00.000000",
    "version": "2.0"
  },
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 2,
    "max_depth": 8,
    "include_comments": true,
    "deterministic_seed": 12345,
    "ensure_unique_combinations": true
  },
  "data_contexts": {
    "global": {
      "airlines": {
        "major": ["AA", "UA", "DL"],
        "budget": ["WN", "B6", "NK"]
      },
      "airports": ["NYC", "LAX", "CHI", "MIA", "SEA", "DFW"],
      "cabin_classes": ["Y", "C", "F"],
      "booking_types": ["round_trip", "one_way", "multi_city"]
    },
    "passenger_templates": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "phone": "+1234567890",
        "frequent_flyer": "AA123456789"
      },
      {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com",
        "phone": "+1987654321",
        "frequent_flyer": "UA987654321"
      }
    ]
  },
  "smart_relationships": {
    "passenger_data": {
      "fields": ["first_name", "last_name", "email", "phone"],
      "strategy": "consistent_persona",
      "ensure_unique": true
    },
    "flight_routing": {
      "fields": ["departure_city", "arrival_city"],
      "strategy": "dependent_values",
      "depends_on": ["departure_city"],
      "constraints": ["departure_city != arrival_city"]
    }
  },
  "element_configs": {
    "booking": {
      "repeat_count": 1
    },
    "passenger": {
      "repeat_count": 2,
      "relationship": "passenger_data"
    },
    "first_name": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    },
    "last_name": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    },
    "email": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    },
    "airline_code": {
      "data_context": "global.airlines.major",
      "selection_strategy": "sequential"
    },
    "departure_city": {
      "data_context": "global.airports",
      "selection_strategy": "sequential"
    },
    "arrival_city": {
      "relationship": "flight_routing",
      "data_context": "global.airports"
    },
    "cabin_class": {
      "data_context": "global.cabin_classes",
      "selection_strategy": "random"
    },
    "booking_type": {
      "data_context": "global.booking_types",
      "selection_strategy": "sequential"
    }
  },
  "global_overrides": {
    "use_realistic_data": true,
    "preserve_structure": true,
    "default_string_length": 50
  }
}
```

## XML Output Examples

### Example 1: Basic Configuration

**JSON Configuration:**
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],
      "selection_strategy": "sequential"
    },
    "flight_number": {
      "custom_values": ["1234", "5678", "9012"],
      "selection_strategy": "sequential"
    }
  }
}
```

**Generated XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<flight>
  <airline_code>AA</airline_code>
  <flight_number>1234</flight_number>
</flight>
```

### Example 2: Template-Based Generation

**JSON Configuration:**
```json
{
  "data_contexts": {
    "passenger_templates": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com"
      }
    ]
  },
  "element_configs": {
    "passenger": {
      "repeat_count": 2
    },
    "first_name": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    },
    "last_name": {
      "template_source": "passenger_templates", 
      "selection_strategy": "template"
    },
    "email": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    }
  }
}
```

**Generated XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<booking>
  <passenger>
    <first_name>John</first_name>
    <last_name>Doe</last_name>
    <email>john.doe@email.com</email>
  </passenger>
  <passenger>
    <first_name>John</first_name>
    <last_name>Doe</last_name>
    <email>john.doe@email.com</email>
  </passenger>
</booking>
```

### Example 3: Smart Relationships

**JSON Configuration:**
```json
{
  "data_contexts": {
    "global": {
      "airports": ["NYC", "LAX", "CHI"]
    }
  },
  "smart_relationships": {
    "flight_routing": {
      "fields": ["departure_city", "arrival_city"],
      "strategy": "dependent_values",
      "depends_on": ["departure_city"],
      "constraints": ["departure_city != arrival_city"]
    }
  },
  "element_configs": {
    "departure_city": {
      "data_context": "global.airports",
      "selection_strategy": "sequential"
    },
    "arrival_city": {
      "relationship": "flight_routing"
    }
  }
}
```

**Generated XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<flight>
  <departure_city>NYC</departure_city>
  <arrival_city>LAX</arrival_city>  <!-- Automatically different from departure -->
</flight>
```

### Example 4: Data Context Inheritance

**JSON Configuration:**
```json
{
  "data_contexts": {
    "base_airlines": {
      "carriers": ["AA", "UA"]
    },
    "premium_airlines": {
      "inherits": ["base_airlines"],
      "carriers": ["AA", "UA", "DL"],  // Overrides base
      "services": ["first_class", "business_class"]
    }
  },
  "element_configs": {
    "airline": {
      "data_context": "premium_airlines.carriers",
      "selection_strategy": "sequential"
    },
    "service": {
      "data_context": "premium_airlines.services",
      "selection_strategy": "random"
    }
  }
}
```

**Generated XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<booking>
  <airline>AA</airline>
  <service>first_class</service>
</booking>
```

## Best Practices

### 1. Data Organization
- Group related data in logical contexts
- Use inheritance to avoid duplication
- Keep data contexts focused and cohesive

### 2. Selection Strategies
- Use `sequential` for predictable, ordered data
- Use `random` for realistic variation
- Use `seeded` for reproducible test data
- Use `template` for complex entity generation

### 3. Smart Relationships
- Define relationships for logically connected fields
- Use constraints to enforce business rules
- Ensure unique values where appropriate

### 4. Performance Considerations
- Limit `max_depth` to prevent excessive nesting
- Use reasonable `repeat_count` values
- Consider memory usage with large data contexts

### 5. Maintainability
- Use descriptive names for contexts and relationships
- Document complex configurations
- Version your configurations
- Test configurations with your actual schemas

### 6. Error Prevention
- Validate your JSON syntax
- Test with small data sets first
- Use realistic data that matches XSD constraints
- Monitor generation performance

