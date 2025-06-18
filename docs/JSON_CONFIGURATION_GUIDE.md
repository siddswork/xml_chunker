# JSON Configuration Guide for Dummies 🚀

*A Complete Beginner's Guide to Creating Powerful XML Configurations*

## Table of Contents
1. [🌟 Getting Started - Your First 5 Minutes](#getting-started)
2. [🔍 Understanding the Basics](#understanding-the-basics)
3. [📝 Step-by-Step Tutorial](#step-by-step-tutorial)
4. [🏗️ Configuration Structure Deep Dive](#configuration-structure)
5. [📊 Data Contexts - Your Data Library](#data-contexts)
6. [🔗 Smart Relationships - Making Elements Work Together](#smart-relationships)
7. [⚙️ Element Configurations - Fine-Tuning Individual Elements](#element-configurations)
8. [🎛️ Generation Settings - Global Controls](#generation-settings)
9. [🛠️ Advanced Features](#advanced-features)
10. [📋 Common Patterns & Recipes](#common-patterns)
11. [🎯 Real-World Examples](#real-world-examples)
12. [🚨 Troubleshooting & Common Errors](#troubleshooting)
13. [✅ Testing & Validation](#testing-and-validation)
14. [📚 Reference Guide](#reference-guide)

## 🌟 Getting Started

**Never used JSON configuration before? Don't worry!** This guide will take you from zero to hero in creating powerful XML configurations.

### What is JSON Configuration?

Think of JSON configuration as a **recipe book** for generating XML. Instead of getting random or generic data in your XML, you can specify exactly what data you want and how it should behave.

**Simple analogy:** 
- Without config: Like ordering "any sandwich" and getting something random
- With config: Like specifying "turkey sandwich with Swiss cheese, no mayo, extra lettuce"

### Your First Configuration (2 minutes)

Let's start with the simplest possible configuration:

```json
{
  "metadata": {
    "name": "My First Config",
    "schema_name": "your_schema.xsd"
  },
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]
    }
  }
}
```

**What this does:**
- Tells the system to use "AA", "UA", or "DL" for any `airline_code` element
- That's it! Simple as that.

### Before We Continue - What You Need to Know

1. **JSON Basics**: If you can read a recipe, you can read JSON
2. **Your XSD Schema**: Know which elements you want to customize
3. **Your Goal**: What kind of data do you want in your XML?

---

## 🔍 Understanding the Basics

### How XML Generation Works

```
XSD Schema → JSON Config → XML Chunker → Generated XML
```

1. **XSD Schema**: Defines the structure (what elements are allowed)
2. **JSON Config**: Your instructions (what data to put in those elements)
3. **XML Chunker**: The engine that follows your instructions
4. **Generated XML**: Your custom XML with the data you specified

### Key Concepts (The Big 4)

#### 1. **Element Configurations** 📝
*"What should go in this specific XML element?"*

```json
"airline_code": {
  "custom_values": ["AA", "UA", "DL"]
}
```

#### 2. **Data Contexts** 📚
*"My library of reusable data"*

```json
"data_contexts": {
  "airlines": ["AA", "UA", "DL", "WN"],
  "airports": ["NYC", "LAX", "CHI"]
}
```

#### 3. **Selection Strategies** 🎲
*"How should I pick from my data?"*

- `sequential`: AA, then UA, then DL, then repeat
- `random`: Random pick each time
- `seeded`: "Random" but predictable (for testing)

#### 4. **Smart Relationships** 🔗
*"These elements should work together logically"*

```json
"departure_city": "NYC",
"arrival_city": "LAX"  // Automatically different from departure
```

---

## 📝 Step-by-Step Tutorial

### Step 1: Create Your First Real Configuration

**Scenario**: You have an airline booking XSD and want realistic data.

#### The Minimal Configuration

```json
{
  "metadata": {
    "name": "Airline Booking Config",
    "schema_name": "airline_booking.xsd"
  },
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]
    },
    "passenger_count": {
      "custom_values": ["1", "2", "3", "4"]
    }
  }
}
```

**Save this as:** `my_first_config.json`

**What happens when you use this:**
- Every `airline_code` in your XML will be AA, UA, or DL
- Every `passenger_count` will be 1, 2, 3, or 4
- Everything else gets default values

### Step 2: Add Sequential Selection

```json
{
  "metadata": {
    "name": "Airline Booking Config v2",
    "schema_name": "airline_booking.xsd"
  },
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],
      "selection_strategy": "sequential"
    },
    "passenger_count": {
      "custom_values": ["1", "2", "3"],
      "selection_strategy": "sequential"
    }
  }
}
```

**What's different:**
- First XML: airline=AA, passengers=1
- Second XML: airline=UA, passengers=2  
- Third XML: airline=DL, passengers=3
- Fourth XML: airline=AA, passengers=1 (starts over)

### Step 3: Organize Your Data

Instead of putting values directly in element configs, let's create a data library:

```json
{
  "metadata": {
    "name": "Airline Booking Config v3",
    "schema_name": "airline_booking.xsd"
  },
  "data_contexts": {
    "airlines": ["AA", "UA", "DL", "WN", "B6"],
    "cities": ["NYC", "LAX", "CHI", "MIA", "SEA"],
    "cabin_classes": ["Economy", "Business", "First"]
  },
  "element_configs": {
    "airline_code": {
      "data_context": "airlines",
      "selection_strategy": "sequential"
    },
    "departure_city": {
      "data_context": "cities",
      "selection_strategy": "sequential"
    },
    "cabin_class": {
      "data_context": "cabin_classes",
      "selection_strategy": "random"
    }
  }
}
```

**Benefits:**
- ✅ Cleaner organization
- ✅ Reuse data across multiple elements
- ✅ Easy to maintain and update

### Step 4: Add Smart Relationships

Problem: departure_city="NYC" and arrival_city="NYC" doesn't make sense!

Solution: Smart relationships

```json
{
  "metadata": {
    "name": "Airline Booking Config v4",
    "schema_name": "airline_booking.xsd"
  },
  "data_contexts": {
    "cities": ["NYC", "LAX", "CHI", "MIA", "SEA"]
  },
  "smart_relationships": {
    "flight_routing": {
      "fields": ["departure_city", "arrival_city"],
      "strategy": "dependent_values",
      "constraints": ["departure_city != arrival_city"]
    }
  },
  "element_configs": {
    "departure_city": {
      "data_context": "cities",
      "selection_strategy": "sequential"
    },
    "arrival_city": {
      "relationship": "flight_routing",
      "data_context": "cities"
    }
  }
}
```

**What this does:**
- Picks departure_city sequentially: NYC, LAX, CHI...
- Automatically picks arrival_city that's different from departure
- No more "NYC to NYC" flights!

---

## 🏗️ Configuration Structure Deep Dive

### The Complete Structure Map

```json
{
  "metadata": {
    // Basic info about your config
  },
  "generation_settings": {
    // How the entire generation should behave
  },
  "data_contexts": {
    // Your reusable data library
  },
  "smart_relationships": {
    // Rules for how elements work together
  },
  "element_configs": {
    // Instructions for specific elements
  },
  "global_overrides": {
    // System-wide settings
  }
}
```

### When to Use Each Section

| Section | Use When | Example |
|---------|----------|---------|
| `metadata` | Always (required) | Basic config info |
| `element_configs` | You want specific data in elements | Custom airline codes |
| `data_contexts` | You have reusable data | List of cities used in multiple places |
| `smart_relationships` | Elements should be logically connected | Departure ≠ Arrival |
| `generation_settings` | You want to control overall behavior | Generate 3 passengers per booking |
| `global_overrides` | System-wide changes | Use realistic data everywhere |

---

## 📊 Data Contexts - Your Data Library

### Think of Data Contexts as...

**A library where you store all your data for reuse.**

Instead of writing the same airline codes in 10 different places, write them once in a data context and reference them everywhere.

### Basic Data Context

```json
{
  "data_contexts": {
    "airlines": ["AA", "UA", "DL"],
    "cities": ["NYC", "LAX", "CHI"],
    "classes": ["Y", "C", "F"]
  }
}
```

**Using the data:**
```json
{
  "element_configs": {
    "airline_code": {
      "data_context": "airlines"
    },
    "departure_city": {
      "data_context": "cities"
    }
  }
}
```

### Organized Data (Nested Structure)

```json
{
  "data_contexts": {
    "airlines": {
      "major": ["AA", "UA", "DL"],
      "budget": ["WN", "B6", "NK"],
      "international": ["LH", "BA", "AF"]
    },
    "locations": {
      "usa": {
        "east_coast": ["NYC", "BOS", "MIA"],
        "west_coast": ["LAX", "SFO", "SEA"],
        "central": ["CHI", "DFW", "DEN"]
      },
      "europe": ["LHR", "CDG", "FRA"]
    }
  }
}
```

**Using nested data with dot notation:**
```json
{
  "element_configs": {
    "airline_code": {
      "data_context": "airlines.major"
    },
    "departure_airport": {
      "data_context": "locations.usa.east_coast"
    }
  }
}
```

### Data Context Inheritance

**Problem**: You have basic data and premium data that's mostly the same.

**Solution**: Inheritance

```json
{
  "data_contexts": {
    "basic_airlines": {
      "carriers": ["AA", "UA"],
      "classes": ["Y", "C"]
    },
    "premium_airlines": {
      "inherits": ["basic_airlines"],
      "carriers": ["AA", "UA", "DL", "LH"],  // Overrides basic
      "classes": ["Y", "C", "F"],            // Overrides basic
      "services": ["lounge", "priority"]     // Adds new data
    }
  }
}
```

**Result**: `premium_airlines` gets everything from `basic_airlines` plus its own additions/overrides.

### Real-World Data Context Examples

#### Passenger Templates
```json
{
  "data_contexts": {
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
  }
}
```

#### Booking Scenarios
```json
{
  "data_contexts": {
    "booking_scenarios": {
      "business_travel": {
        "cabin_classes": ["C", "F"],
        "booking_types": ["one_way", "round_trip"],
        "advance_booking_days": ["1", "2", "7"]
      },
      "leisure_travel": {
        "cabin_classes": ["Y"],
        "booking_types": ["round_trip"],
        "advance_booking_days": ["30", "60", "90"]
      }
    }
  }
}
```

---

## 🔗 Smart Relationships - Making Elements Work Together

### Why Do You Need Smart Relationships?

**Without relationships:**
```xml
<flight>
  <departure_city>NYC</departure_city>
  <arrival_city>NYC</arrival_city>  <!-- Doesn't make sense! -->
  <departure_date>2024-06-20</departure_date>
  <return_date>2024-06-15</return_date>  <!-- Return before departure! -->
</flight>
```

**With relationships:**
```xml
<flight>
  <departure_city>NYC</departure_city>
  <arrival_city>LAX</arrival_city>  <!-- Automatically different -->
  <departure_date>2024-06-20</departure_date>
  <return_date>2024-06-25</return_date>  <!-- Automatically after departure -->
</flight>
```

### The 3 Types of Smart Relationships

#### 1. **Consistent Persona** 
*"These fields should belong to the same person/entity"*

```json
{
  "smart_relationships": {
    "passenger_info": {
      "fields": ["first_name", "last_name", "email", "phone"],
      "strategy": "consistent_persona"
    }
  }
}
```

**Result**: If first_name="John", then last_name, email, and phone will all belong to the same template person.

#### 2. **Dependent Values**
*"This field depends on that field"*

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

**Result**: Pick departure_city first, then pick arrival_city that's different.

#### 3. **Constraint-Based**
*"These fields must follow business rules"*

```json
{
  "smart_relationships": {
    "date_logic": {
      "fields": ["departure_date", "return_date"],
      "strategy": "constraint_based",
      "constraints": [
        "return_date > departure_date",
        "date_diff(return_date, departure_date) <= 30"
      ]
    }
  }
}
```

**Result**: Return date is always after departure date, and within 30 days.

### Step-by-Step: Creating Your First Relationship

**Scenario**: You want realistic passenger data where first_name and email match.

#### Step 1: Define Your Templates
```json
{
  "data_contexts": {
    "passenger_templates": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com"
      },
      {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com"
      }
    ]
  }
}
```

#### Step 2: Create the Relationship
```json
{
  "smart_relationships": {
    "passenger_data": {
      "fields": ["first_name", "last_name", "email"],
      "strategy": "consistent_persona"
    }
  }
}
```

#### Step 3: Configure Elements to Use the Relationship
```json
{
  "element_configs": {
    "first_name": {
      "template_source": "passenger_templates",
      "relationship": "passenger_data"
    },
    "last_name": {
      "template_source": "passenger_templates", 
      "relationship": "passenger_data"
    },
    "email": {
      "template_source": "passenger_templates",
      "relationship": "passenger_data"
    }
  }
}
```

#### Step 4: Result
```xml
<passenger>
  <first_name>John</first_name>
  <last_name>Doe</last_name>
  <email>john.doe@email.com</email>  <!-- All match! -->
</passenger>
```

---

## ⚙️ Element Configurations - Fine-Tuning Individual Elements

### The Element Configuration Toolbox

Every element can be configured with these tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `custom_values` | Specific values to use | `["AA", "UA", "DL"]` |
| `data_context` | Reference to data library | `"airlines.major"` |
| `selection_strategy` | How to pick values | `"sequential"`, `"random"` |
| `relationship` | Connect to other elements | `"passenger_data"` |
| `repeat_count` | How many times to repeat | `3` (for 3 passengers) |
| `template_source` | Use template data | `"passenger_templates"` |

### Selection Strategies Explained

#### Sequential Selection
*"Go through the list in order"*

```json
{
  "airline_code": {
    "custom_values": ["AA", "UA", "DL"],
    "selection_strategy": "sequential"
  }
}
```

**Behavior:**
- 1st XML: "AA"
- 2nd XML: "UA" 
- 3rd XML: "DL"
- 4th XML: "AA" (starts over)

**When to use**: When you want predictable, ordered data.

#### Random Selection
*"Pick randomly each time"*

```json
{
  "airline_code": {
    "custom_values": ["AA", "UA", "DL"],
    "selection_strategy": "random"
  }
}
```

**Behavior:**
- 1st XML: "DL" (random)
- 2nd XML: "AA" (random)
- 3rd XML: "DL" (random, could repeat)

**When to use**: When you want realistic variation.

#### Seeded Random Selection
*"Random, but predictable (for testing)"*

```json
{
  "generation_settings": {
    "deterministic_seed": 12345
  },
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],
      "selection_strategy": "seeded"
    }
  }
}
```

**Behavior:**
- Always produces the same "random" sequence
- Great for testing and demos

**When to use**: When you want "random" data that's reproducible.

### Element Configuration Patterns

#### Pattern 1: Simple Custom Values
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]
    }
  }
}
```

#### Pattern 2: Reference Data Context
```json
{
  "data_contexts": {
    "airlines": ["AA", "UA", "DL", "WN"]
  },
  "element_configs": {
    "airline_code": {
      "data_context": "airlines",
      "selection_strategy": "sequential"
    }
  }
}
```

#### Pattern 3: Repeating Elements
```json
{
  "element_configs": {
    "passenger": {
      "repeat_count": 3  // Generate 3 passengers
    },
    "first_name": {
      "custom_values": ["John", "Jane", "Bob"]
    }
  }
}
```

#### Pattern 4: Template-Based
```json
{
  "data_contexts": {
    "passenger_templates": [
      {"first_name": "John", "last_name": "Doe"},
      {"first_name": "Jane", "last_name": "Smith"}
    ]
  },
  "element_configs": {
    "first_name": {
      "template_source": "passenger_templates",
      "selection_strategy": "template"
    }
  }
}
```

---

## 🎛️ Generation Settings - Global Controls

### What Are Generation Settings?

Think of generation settings as the **master controls** for your entire XML generation process.

```json
{
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 2,
    "max_depth": 8,
    "include_comments": true,
    "deterministic_seed": 12345
  }
}
```

### Generation Modes Explained

#### Complete Mode (Default)
*"Generate everything possible"*

```json
{
  "generation_settings": {
    "mode": "Complete"
  }
}
```

**What it does:**
- ✅ Generates all optional elements
- ✅ Fills in all possible data
- ✅ Creates rich, comprehensive XML
- ❌ Can create large files

**When to use**: When you want full, realistic XML with all details.

#### Minimalistic Mode
*"Generate only required elements"*

```json
{
  "generation_settings": {
    "mode": "Minimalistic"
  }
}
```

**What it does:**
- ✅ Only required elements (minOccurs > 0)
- ✅ Smaller, simpler XML
- ❌ Missing optional details

**When to use**: When you want simple, lean XML for testing basic validation.

#### Custom Mode
*"You control exactly what gets generated"*

```json
{
  "generation_settings": {
    "mode": "Custom"
  }
}
```

**What it does:**
- ✅ Only generates what you specifically configure
- ✅ Maximum control
- ❌ Requires more configuration work

**When to use**: When you need precise control over every element.

### Other Important Settings

#### Global Repeat Count
*"How many times should unbounded elements repeat by default?"*

```json
{
  "generation_settings": {
    "global_repeat_count": 3  // Generate 3 of each unbounded element
  }
}
```

**Example**: If your schema allows multiple passengers, this generates 3 passengers by default.

#### Max Depth
*"How deep should nested elements go?"*

```json
{
  "generation_settings": {
    "max_depth": 5  // Stop nesting after 5 levels
  }
}
```

**Why important**: Prevents infinite recursion and overly complex XML.

#### Include Comments
*"Add helpful comments to the XML?"*

```json
{
  "generation_settings": {
    "include_comments": true
  }
}
```

**Result:**
```xml
<!-- minOccurs: 1, maxOccurs: 1 -->
<airline_code>AA</airline_code>
```

#### Deterministic Seed
*"Make random generation predictable"*

```json
{
  "generation_settings": {
    "deterministic_seed": 12345
  }
}
```

**When to use**: For testing, demos, or when you need reproducible results.

---

## 🛠️ Advanced Features

### Template Processing

Templates allow you to create **complete, consistent entities** like passengers, bookings, or flights.

#### Creating Templates

```json
{
  "data_contexts": {
    "passenger_templates": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "phone": "+1234567890",
        "loyalty_number": "AA123456789",
        "loyalty_tier": "Gold"
      },
      {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com",
        "phone": "+1987654321", 
        "loyalty_number": "UA987654321",
        "loyalty_tier": "Silver"
      }
    ]
  }
}
```

#### Using Templates

```json
{
  "smart_relationships": {
    "passenger_consistency": {
      "fields": ["first_name", "last_name", "email", "phone", "loyalty_number", "loyalty_tier"],
      "strategy": "consistent_persona"
    }
  },
  "element_configs": {
    "first_name": {
      "template_source": "passenger_templates",
      "relationship": "passenger_consistency"
    },
    "last_name": {
      "template_source": "passenger_templates",
      "relationship": "passenger_consistency"
    }
    // ... configure all related fields
  }
}
```

#### Result: Consistent Passenger Data

```xml
<passenger>
  <first_name>John</first_name>
  <last_name>Doe</last_name>
  <email>john.doe@email.com</email>
  <phone>+1234567890</phone>
  <loyalty_number>AA123456789</loyalty_number>
  <loyalty_tier>Gold</loyalty_tier>
</passenger>
```

### Complex Constraints

#### Date Logic
```json
{
  "smart_relationships": {
    "booking_dates": {
      "fields": ["booking_date", "departure_date", "return_date"],
      "strategy": "constraint_based",
      "constraints": [
        "departure_date > booking_date",
        "return_date > departure_date",
        "date_diff(departure_date, booking_date) >= 1",
        "date_diff(return_date, departure_date) <= 30"
      ]
    }
  }
}
```

#### Business Rules
```json
{
  "smart_relationships": {
    "pricing_logic": {
      "fields": ["cabin_class", "price_category"],
      "strategy": "dependent_values",
      "rules": {
        "if": "cabin_class == 'F'",
        "then": "price_category in ['premium', 'luxury']"
      }
    }
  }
}
```

### Global Overrides

System-wide settings that affect everything:

```json
{
  "global_overrides": {
    "use_realistic_data": true,           // Use realistic defaults
    "preserve_structure": true,           // Keep XSD structure intact
    "default_string_length": 50,          // Default length for strings
    "namespace_prefixes": {               // Custom namespace prefixes
      "cns": "http://www.iata.org/IATA/2015/00/2019.2/IATA_CommonTypes",
      "ama": "http://xml.amadeus.com/2010/06/Types_v2"
    },
    "enforce_constraints": true,          // Strict constraint checking
    "fallback_strategy": "realistic"      // What to do when no config exists
  }
}
```

---

## 📋 Common Patterns & Recipes

### Recipe 1: Simple Airline Data

**Use case**: You just want custom airline codes and cities.

```json
{
  "metadata": {
    "name": "Simple Airline Config",
    "schema_name": "airline.xsd"
  },
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],
      "selection_strategy": "sequential"
    },
    "departure_city": {
      "custom_values": ["NYC", "LAX", "CHI"],
      "selection_strategy": "sequential"
    },
    "arrival_city": {
      "custom_values": ["MIA", "SEA", "DFW"],
      "selection_strategy": "sequential"
    }
  }
}
```

### Recipe 2: Realistic Passenger Booking

**Use case**: Generate realistic passenger data with consistent information.

```json
{
  "metadata": {
    "name": "Realistic Passenger Booking",
    "schema_name": "booking.xsd"
  },
  "data_contexts": {
    "passenger_templates": [
      {
        "first_name": "John", "last_name": "Doe",
        "email": "john.doe@email.com", "phone": "+1234567890"
      },
      {
        "first_name": "Jane", "last_name": "Smith", 
        "email": "jane.smith@email.com", "phone": "+1987654321"
      }
    ],
    "travel_data": {
      "airlines": ["AA", "UA", "DL"],
      "cities": ["NYC", "LAX", "CHI", "MIA", "SEA"],
      "cabin_classes": ["Economy", "Business", "First"]
    }
  },
  "smart_relationships": {
    "passenger_info": {
      "fields": ["first_name", "last_name", "email", "phone"],
      "strategy": "consistent_persona"
    },
    "flight_routing": {
      "fields": ["departure_city", "arrival_city"],
      "strategy": "dependent_values",
      "constraints": ["departure_city != arrival_city"]
    }
  },
  "element_configs": {
    "passenger": {
      "repeat_count": 2
    },
    "first_name": {
      "template_source": "passenger_templates",
      "relationship": "passenger_info"
    },
    "last_name": {
      "template_source": "passenger_templates",
      "relationship": "passenger_info"
    },
    "email": {
      "template_source": "passenger_templates",
      "relationship": "passenger_info"
    },
    "airline_code": {
      "data_context": "travel_data.airlines",
      "selection_strategy": "sequential"
    },
    "departure_city": {
      "data_context": "travel_data.cities",
      "relationship": "flight_routing"
    },
    "arrival_city": {
      "relationship": "flight_routing"
    }
  }
}
```

### Recipe 3: Multi-Scenario Testing

**Use case**: Generate different types of bookings for comprehensive testing.

```json
{
  "metadata": {
    "name": "Multi-Scenario Testing",
    "schema_name": "booking.xsd"
  },
  "data_contexts": {
    "scenarios": {
      "business_travel": {
        "cabin_classes": ["Business", "First"],
        "booking_types": ["one_way", "round_trip"],
        "advance_days": [1, 2, 7]
      },
      "leisure_travel": {
        "cabin_classes": ["Economy"],
        "booking_types": ["round_trip"],
        "advance_days": [30, 60, 90]
      }
    }
  },
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 1
  },
  "element_configs": {
    "booking_type": {
      "data_context": "scenarios.business_travel.booking_types",
      "selection_strategy": "sequential"
    },
    "cabin_class": {
      "data_context": "scenarios.business_travel.cabin_classes",
      "selection_strategy": "random"
    }
  }
}
```

### Recipe 4: Error Testing Configuration

**Use case**: Generate XML that tests edge cases and error conditions.

```json
{
  "metadata": {
    "name": "Edge Case Testing",
    "schema_name": "booking.xsd"
  },
  "data_contexts": {
    "edge_cases": {
      "empty_values": ["", " ", "  "],
      "special_chars": ["<test>", "&amp;", "quotes\"test"],
      "long_strings": ["A" * 255, "B" * 500],
      "boundary_numbers": ["0", "1", "-1", "999999"]
    }
  },
  "element_configs": {
    "test_field": {
      "data_context": "edge_cases.special_chars",
      "selection_strategy": "sequential"
    }
  }
}
```

---

## 🎯 Real-World Examples

### Example 1: IATA NDC Order Create Request

**Scenario**: Generate realistic airline booking requests for IATA NDC schema.

```json
{
  "metadata": {
    "name": "IATA NDC OrderCreateRQ Configuration",
    "description": "Realistic booking requests for airline reservations",
    "schema_name": "OrderCreateRQ.xsd",
    "version": "2.0"
  },
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 2,
    "deterministic_seed": 42,
    "include_comments": true
  },
  "data_contexts": {
    "airlines": {
      "major_us": ["AA", "UA", "DL"],
      "budget_us": ["WN", "B6", "NK"],
      "international": ["LH", "BA", "AF", "KL"]
    },
    "airports": {
      "usa": {
        "hubs": ["JFK", "LAX", "ORD", "DFW", "ATL"],
        "secondary": ["BOS", "MIA", "SEA", "DEN", "PHX"]
      },
      "europe": ["LHR", "CDG", "FRA", "AMS", "FCO"]
    },
    "passenger_profiles": [
      {
        "title": "Mr", "first_name": "John", "last_name": "Doe",
        "email": "john.doe@business.com", "phone": "+1-555-0123",
        "loyalty_program": "AA", "loyalty_number": "AA123456789",
        "traveler_type": "business"
      },
      {
        "title": "Ms", "first_name": "Jane", "last_name": "Smith",
        "email": "jane.smith@email.com", "phone": "+1-555-0456", 
        "loyalty_program": "UA", "loyalty_number": "UA987654321",
        "traveler_type": "leisure"
      }
    ],
    "booking_scenarios": {
      "business": {
        "cabin_preferences": ["J", "C", "D"],
        "advance_booking": [1, 2, 7, 14],
        "trip_types": ["OW", "RT"]
      },
      "leisure": {
        "cabin_preferences": ["Y", "S", "B"],
        "advance_booking": [21, 30, 45, 60],
        "trip_types": ["RT"]
      }
    }
  },
  "smart_relationships": {
    "passenger_consistency": {
      "fields": ["title", "first_name", "last_name", "email", "phone", "loyalty_program", "loyalty_number"],
      "strategy": "consistent_persona",
      "ensure_unique": true
    },
    "flight_routing": {
      "fields": ["origin_airport", "destination_airport"],
      "strategy": "dependent_values",
      "constraints": ["origin_airport != destination_airport"]
    },
    "travel_dates": {
      "fields": ["departure_date", "return_date"],
      "strategy": "constraint_based",
      "constraints": [
        "return_date > departure_date",
        "date_diff(return_date, departure_date) <= 30"
      ]
    }
  },
  "element_configs": {
    "MessageDoc": {
      "repeat_count": 1
    },
    "Party": {
      "repeat_count": 2
    },
    "title": {
      "template_source": "passenger_profiles",
      "relationship": "passenger_consistency"
    },
    "first_name": {
      "template_source": "passenger_profiles", 
      "relationship": "passenger_consistency"
    },
    "last_name": {
      "template_source": "passenger_profiles",
      "relationship": "passenger_consistency"
    },
    "email": {
      "template_source": "passenger_profiles",
      "relationship": "passenger_consistency"
    },
    "airline_designator": {
      "data_context": "airlines.major_us",
      "selection_strategy": "sequential"
    },
    "origin_airport": {
      "data_context": "airports.usa.hubs",
      "relationship": "flight_routing",
      "selection_strategy": "sequential"
    },
    "destination_airport": {
      "data_context": "airports.usa.hubs",
      "relationship": "flight_routing"
    },
    "cabin_type": {
      "data_context": "booking_scenarios.business.cabin_preferences",
      "selection_strategy": "random"
    },
    "trip_type": {
      "data_context": "booking_scenarios.business.trip_types",
      "selection_strategy": "sequential"
    }
  },
  "global_overrides": {
    "use_realistic_data": true,
    "namespace_prefixes": {
      "cns": "http://www.iata.org/IATA/2015/00/2019.2/IATA_CommonTypes"
    },
    "enforce_constraints": true
  }
}
```

### Example 2: E-commerce Order System

**Scenario**: Generate product orders for an e-commerce system.

```json
{
  "metadata": {
    "name": "E-commerce Order Configuration",
    "description": "Realistic product orders with customers and shipping",
    "schema_name": "ecommerce_order.xsd"
  },
  "data_contexts": {
    "customers": [
      {
        "customer_id": "CUST001", "first_name": "Alice", "last_name": "Johnson",
        "email": "alice@email.com", "phone": "555-0101",
        "address": "123 Main St", "city": "New York", "state": "NY", "zip": "10001"
      },
      {
        "customer_id": "CUST002", "first_name": "Bob", "last_name": "Wilson", 
        "email": "bob@email.com", "phone": "555-0202",
        "address": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "zip": "90210"
      }
    ],
    "products": {
      "electronics": [
        {"sku": "ELEC001", "name": "Smartphone", "price": "599.99", "category": "Electronics"},
        {"sku": "ELEC002", "name": "Laptop", "price": "1299.99", "category": "Electronics"},
        {"sku": "ELEC003", "name": "Tablet", "price": "399.99", "category": "Electronics"}
      ],
      "clothing": [
        {"sku": "CLTH001", "name": "T-Shirt", "price": "19.99", "category": "Clothing"},
        {"sku": "CLTH002", "name": "Jeans", "price": "59.99", "category": "Clothing"}
      ]
    },
    "shipping": {
      "methods": ["standard", "express", "overnight"],
      "carriers": ["UPS", "FedEx", "USPS"]
    }
  },
  "smart_relationships": {
    "customer_consistency": {
      "fields": ["customer_id", "first_name", "last_name", "email", "phone", "address", "city", "state", "zip"],
      "strategy": "consistent_persona"
    },
    "order_logic": {
      "fields": ["product_category", "shipping_method"],
      "strategy": "dependent_values",
      "rules": {
        "if": "product_category == 'Electronics'",
        "then": "shipping_method in ['express', 'overnight']"
      }
    }
  },
  "element_configs": {
    "order": {
      "repeat_count": 1
    },
    "line_item": {
      "repeat_count": 3
    },
    "customer_id": {
      "template_source": "customers",
      "relationship": "customer_consistency"
    },
    "first_name": {
      "template_source": "customers",
      "relationship": "customer_consistency" 
    },
    "product_sku": {
      "data_context": "products.electronics",
      "field": "sku",
      "selection_strategy": "sequential"
    },
    "product_name": {
      "data_context": "products.electronics",
      "field": "name",
      "selection_strategy": "sequential"
    },
    "shipping_method": {
      "data_context": "shipping.methods",
      "relationship": "order_logic"
    }
  }
}
```

---

## 🚨 Troubleshooting & Common Errors

### JSON Syntax Errors

#### Error: "Unexpected token"
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"],  // ❌ Extra comma
    }
  }
}
```

**Fix**: Remove the trailing comma
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]  // ✅ No trailing comma
    }
  }
}
```

#### Error: "Missing quotes"
```json
{
  element_configs: {  // ❌ Missing quotes around key
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]
    }
  }
}
```

**Fix**: Add quotes around all keys
```json
{
  "element_configs": {  // ✅ Quoted key
    "airline_code": {
      "custom_values": ["AA", "UA", "DL"]
    }
  }
}
```

### Configuration Logic Errors

#### Error: "Data context not found"
```json
{
  "element_configs": {
    "airline_code": {
      "data_context": "airlines"  // ❌ 'airlines' doesn't exist
    }
  }
}
```

**Fix**: Define the data context first
```json
{
  "data_contexts": {
    "airlines": ["AA", "UA", "DL"]  // ✅ Define it first
  },
  "element_configs": {
    "airline_code": {
      "data_context": "airlines"  // ✅ Now it exists
    }
  }
}
```

#### Error: "Relationship not found"
```json
{
  "element_configs": {
    "first_name": {
      "relationship": "passenger_data"  // ❌ Relationship doesn't exist
    }
  }
}
```

**Fix**: Define the relationship first
```json
{
  "smart_relationships": {
    "passenger_data": {  // ✅ Define it first
      "fields": ["first_name", "last_name"],
      "strategy": "consistent_persona"
    }
  },
  "element_configs": {
    "first_name": {
      "relationship": "passenger_data"  // ✅ Now it exists
    }
  }
}
```

### Data Type Errors

#### Error: "Invalid selection strategy"
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA"],
      "selection_strategy": "alphabetical"  // ❌ Invalid strategy
    }
  }
}
```

**Fix**: Use valid strategies
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA", "UA"],
      "selection_strategy": "sequential"  // ✅ Valid: sequential, random, seeded
    }
  }
}
```

#### Error: "Empty custom_values array"
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": []  // ❌ Empty array
    }
  }
}
```

**Fix**: Provide at least one value
```json
{
  "element_configs": {
    "airline_code": {
      "custom_values": ["AA"]  // ✅ At least one value
    }
  }
}
```

### Common Logical Mistakes

#### Mistake: Circular Dependencies
```json
{
  "smart_relationships": {
    "circular": {
      "fields": ["field_a", "field_b"],
      "strategy": "dependent_values",
      "depends_on": ["field_b"]  // ❌ field_b depends on field_a, but field_a depends on field_b
    }
  }
}
```

**Fix**: Clear dependency direction
```json
{
  "smart_relationships": {
    "clear_dependency": {
      "fields": ["field_a", "field_b"],
      "strategy": "dependent_values", 
      "depends_on": ["field_a"]  // ✅ Clear: field_b depends on field_a
    }
  }
}
```

#### Mistake: Mismatched Template Fields
```json
{
  "data_contexts": {
    "templates": [
      {"first_name": "John", "last_name": "Doe"}
    ]
  },
  "element_configs": {
    "email": {
      "template_source": "templates"  // ❌ Template has no 'email' field
    }
  }
}
```

**Fix**: Ensure template has the required fields
```json
{
  "data_contexts": {
    "templates": [
      {"first_name": "John", "last_name": "Doe", "email": "john@email.com"}  // ✅ Added email
    ]
  },
  "element_configs": {
    "email": {
      "template_source": "templates"  // ✅ Template has 'email' field
    }
  }
}
```

### Performance Issues

#### Issue: Configuration too complex
**Symptoms**: XML generation is very slow

**Common causes:**
- Too many relationships
- Very large data contexts  
- Deep nesting (high max_depth)
- Too many repeated elements

**Solutions:**
```json
{
  "generation_settings": {
    "max_depth": 5,           // ✅ Limit depth
    "global_repeat_count": 2  // ✅ Limit repetitions
  }
}
```

#### Issue: Memory usage too high
**Symptoms**: Out of memory errors

**Solutions:**
- Reduce data context size
- Use streaming for large datasets
- Limit repeat counts

---

## ✅ Testing & Validation

### Step 1: Validate Your JSON

Before using your configuration, make sure it's valid JSON:

#### Online JSON Validators
- jsonlint.com
- jsonformatter.curiousconcept.com

#### Command Line Validation
```bash
# Using Python
python -m json.tool my_config.json

# Using jq (if installed)
jq . my_config.json
```

### Step 2: Start Small and Build Up

#### Test with Minimal Configuration
```json
{
  "metadata": {
    "name": "Test Config",
    "schema_name": "your_schema.xsd"
  },
  "element_configs": {
    "one_element": {
      "custom_values": ["test_value"]
    }
  }
}
```

#### Gradually Add Complexity
1. ✅ Test basic element configs
2. ✅ Add data contexts
3. ✅ Add selection strategies  
4. ✅ Add relationships
5. ✅ Add advanced features

### Step 3: Verify Generated XML

#### Check Key Elements
```bash
# Count specific elements
grep -c "<airline_code>" generated.xml

# Check for empty elements
grep "<.*></.*>" generated.xml

# Verify values are from your config
grep "airline_code" generated.xml
```

#### Validate Against Schema
```bash
# Using xmllint (if available)
xmllint --schema your_schema.xsd generated.xml
```

### Step 4: Test Different Scenarios

#### Create Test Configurations

**Test 1: Sequential Selection**
```json
{
  "element_configs": {
    "test_element": {
      "custom_values": ["A", "B", "C"],
      "selection_strategy": "sequential"
    }
  }
}
```

Generate 5 XMLs and verify you get: A, B, C, A, B

**Test 2: Random with Seed**
```json
{
  "generation_settings": {
    "deterministic_seed": 123
  },
  "element_configs": {
    "test_element": {
      "custom_values": ["A", "B", "C"],
      "selection_strategy": "seeded"
    }
  }
}
```

Generate multiple times and verify you get the same sequence.

**Test 3: Relationships**
```json
{
  "data_contexts": {
    "cities": ["NYC", "LAX", "CHI"]
  },
  "smart_relationships": {
    "routing": {
      "fields": ["departure", "arrival"],
      "strategy": "dependent_values",
      "constraints": ["departure != arrival"]
    }
  },
  "element_configs": {
    "departure": {
      "data_context": "cities",
      "relationship": "routing"
    },
    "arrival": {
      "relationship": "routing"
    }
  }
}
```

Verify that departure and arrival are always different.

### Debugging Tips

#### Enable Debug Mode
```json
{
  "generation_settings": {
    "include_comments": true  // Adds helpful comments to XML
  }
}
```

#### Use Smaller Data Sets
```json
{
  "data_contexts": {
    "airlines": ["AA", "UA"]  // Use just 2 values for easier testing
  }
}
```

#### Test One Feature at a Time
Don't combine multiple new features in one test. Add them incrementally.

---

## 📚 Reference Guide

### Complete Field Reference

#### Metadata Section
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ Yes | string | Configuration name |
| `schema_name` | ✅ Yes | string | Target XSD filename |
| `description` | ❌ No | string | Configuration description |
| `created` | ❌ No | string | ISO timestamp |
| `version` | ❌ No | string | Configuration version |

#### Generation Settings
| Field | Required | Type | Default | Options |
|-------|----------|------|---------|---------|
| `mode` | ❌ No | string | "Complete" | "Complete", "Minimalistic", "Custom" |
| `global_repeat_count` | ❌ No | integer | 2 | 1-50 |
| `max_depth` | ❌ No | integer | 8 | 1-20 |
| `include_comments` | ❌ No | boolean | false | true, false |
| `deterministic_seed` | ❌ No | integer | null | Any integer |

#### Element Configurations
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `custom_values` | ❌ No | array | Specific values to use |
| `data_context` | ❌ No | string | Reference to data context |
| `selection_strategy` | ❌ No | string | How to select values |
| `relationship` | ❌ No | string | Reference to smart relationship |
| `repeat_count` | ❌ No | integer | Number of repetitions |
| `template_source` | ❌ No | string | Template data source |

#### Selection Strategies
| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `sequential` | Values in order, repeat when end reached | Predictable, ordered data |
| `random` | Random selection each time | Realistic variation |
| `seeded` | Deterministic "random" using seed | Reproducible test data |
| `template` | Use template-based generation | Complex entity data |

#### Smart Relationship Strategies
| Strategy | Purpose | Configuration |
|----------|---------|---------------|
| `consistent_persona` | Keep related fields consistent | `fields: ["name", "email"]` |
| `dependent_values` | One field depends on another | `depends_on: ["field1"]` |
| `constraint_based` | Apply business rules | `constraints: ["rule1"]` |

### Quick Reference Examples

#### Minimal Configuration
```json
{
  "metadata": {"name": "Test", "schema_name": "test.xsd"},
  "element_configs": {
    "element_name": {"custom_values": ["value1", "value2"]}
  }
}
```

#### Full Configuration Template
```json
{
  "metadata": {
    "name": "Configuration Name",
    "description": "What this config does",
    "schema_name": "target_schema.xsd",
    "version": "1.0"
  },
  "generation_settings": {
    "mode": "Complete",
    "global_repeat_count": 2,
    "max_depth": 8,
    "include_comments": true,
    "deterministic_seed": 12345
  },
  "data_contexts": {
    "context_name": ["value1", "value2", "value3"],
    "nested_context": {
      "subcategory": ["val1", "val2"]
    },
    "templates": [
      {"field1": "value1", "field2": "value2"}
    ]
  },
  "smart_relationships": {
    "relationship_name": {
      "fields": ["field1", "field2"],
      "strategy": "consistent_persona",
      "ensure_unique": true
    }
  },
  "element_configs": {
    "element_name": {
      "data_context": "context_name",
      "selection_strategy": "sequential",
      "relationship": "relationship_name"
    }
  },
  "global_overrides": {
    "use_realistic_data": true,
    "preserve_structure": true
  }
}
```

### Validation Checklist

Before using your configuration:

- [ ] ✅ JSON is syntactically valid
- [ ] ✅ All required fields are present
- [ ] ✅ All referenced data contexts exist
- [ ] ✅ All referenced relationships exist  
- [ ] ✅ Selection strategies are valid
- [ ] ✅ No circular dependencies in relationships
- [ ] ✅ Template sources contain required fields
- [ ] ✅ Tested with small dataset first
- [ ] ✅ Generated XML validates against schema

### Getting Help

#### Common Issues
1. **JSON syntax errors** → Use online JSON validator
2. **Configuration not working** → Start with minimal config and build up
3. **Elements not getting values** → Check data context references
4. **Relationships not working** → Verify relationship definitions
5. **Performance issues** → Reduce repeat counts and max depth

#### Best Practices Summary
1. 🧪 **Test incrementally** - Add features one at a time
2. 📝 **Document your configs** - Add descriptions and comments  
3. 🔄 **Version your configs** - Track changes over time
4. 🎯 **Start simple** - Begin with basic configs, add complexity gradually
5. ✅ **Validate frequently** - Check JSON syntax and test outputs

---

*That's it! You now have a complete guide to creating powerful JSON configurations. Start with the simple examples and gradually work your way up to more complex scenarios. Happy configuring! 🚀*
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

