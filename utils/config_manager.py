"""
Configuration Manager for XML Wizard.

Handles loading, validation, and processing of JSON configuration files
that define XML generation parameters, element values, choices, and repeat counts.
"""

import json
import os
import io
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import jsonschema
from config import get_config


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigManager:
    """Manages configuration files for XML generation."""
    
    def __init__(self, config_instance=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_instance: Configuration instance (uses global config if None)
        """
        self.config = config_instance or get_config()
        self.schema = self._get_config_schema()
    
    def _get_config_schema(self) -> Dict[str, Any]:
        """Define JSON schema for configuration validation."""
        return {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "schema_name": {"type": "string"},
                        "created": {"type": "string", "format": "date-time"},
                        "version": {"type": "string"}
                    },
                    "required": ["name", "schema_name"]
                },
                "generation_settings": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": ["Minimalistic", "Complete", "Custom"]
                        },
                        "global_repeat_count": {"type": "integer", "minimum": 1, "maximum": 50},
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 10},
                        "include_comments": {"type": "boolean"},
                        "deterministic_seed": {"type": "integer"},
                        "ensure_unique_combinations": {"type": "boolean"}
                    },
                    "additionalProperties": False
                },
                "element_configs": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                            "type": "object",
                            "properties": {
                                "choices": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^[a-zA-Z][a-zA-Z0-9_]*$": {"type": "string"}
                                    }
                                },
                                "repeat_count": {"type": "integer", "minimum": 1, "maximum": 50},
                                "include_optional": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "custom_values": {
                                    "type": "array",
                                    "items": {"type": ["string", "number", "boolean"]}
                                },
                                "selection_strategy": {
                                    "type": "string",
                                    "enum": ["random", "sequential", "seeded", "template"]
                                },
                                "data_context": {"type": "string"},
                                "template_source": {"type": "string"},
                                "relationship": {"type": "string"},
                                "constraints": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "ensure_unique": {"type": "boolean"}
                            },
                            "additionalProperties": False
                        }
                    }
                },
                "global_overrides": {
                    "type": "object",
                    "properties": {
                        "default_string_length": {"type": "integer", "minimum": 1, "maximum": 1000},
                        "use_realistic_data": {"type": "boolean"},
                        "preserve_structure": {"type": "boolean"},
                        "namespace_prefixes": {
                            "type": "object",
                            "patternProperties": {
                                "^[a-zA-Z][a-zA-Z0-9]*$": {"type": "string", "format": "uri"}
                            }
                        }
                    },
                    "additionalProperties": False
                },
                "data_contexts": {
                    "type": "object",
                    "additionalProperties": True
                },
                "smart_relationships": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                            "type": "object",
                            "properties": {
                                "fields": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "strategy": {
                                    "type": "string",
                                    "enum": ["consistent_persona", "dependent_values", "constraint_based"]
                                },
                                "ensure_unique": {"type": "boolean"},
                                "constraints": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "depends_on": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "additionalProperties": False
                        }
                    }
                }
            },
            "required": ["metadata", "generation_settings"],
            "additionalProperties": False
        }
    
    def load_config(self, config_path: Union[str, Path, io.StringIO]) -> Dict[str, Any]:
        """
        Load and validate a configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ConfigurationError: If the file cannot be loaded or is invalid
        """
        try:
            if isinstance(config_path, io.StringIO):
                # Handle StringIO object (from file upload)
                config_data = json.load(config_path)
            else:
                # Handle file path
                config_path = Path(config_path)
                
                if not config_path.exists():
                    raise ConfigurationError(f"Configuration file not found: {config_path}")
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error reading configuration file: {e}")
        
        # Validate against schema
        try:
            jsonschema.validate(config_data, self.schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(f"Configuration validation error: {e.message}")
        
        return config_data
    
    def save_config(self, config_data: Dict[str, Any], config_path: Union[str, Path]) -> None:
        """
        Save configuration data to file.
        
        Args:
            config_data: Configuration dictionary to save
            config_path: Path where to save the configuration
            
        Raises:
            ConfigurationError: If the configuration cannot be saved
        """
        config_path = Path(config_path)
        
        # Validate before saving
        try:
            jsonschema.validate(config_data, self.schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(f"Configuration validation error: {e.message}")
        
        # Ensure metadata has creation timestamp
        if 'metadata' in config_data:
            if 'created' not in config_data['metadata']:
                config_data['metadata']['created'] = datetime.now().isoformat()
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration file: {e}")
    
    def create_config_from_ui_state(self, 
                                   schema_name: str,
                                   generation_mode: str,
                                   selected_choices: Dict[str, Any],
                                   unbounded_counts: Dict[str, int],
                                   optional_selections: List[str],
                                   config_name: str = None,
                                   config_description: str = None) -> Dict[str, Any]:
        """
        Create a configuration dictionary from current UI state.
        
        Args:
            schema_name: Name of the XSD schema file
            generation_mode: Selected generation mode
            selected_choices: Dictionary of choice selections
            unbounded_counts: Dictionary of element repeat counts
            optional_selections: List of selected optional elements
            config_name: Name for the configuration
            config_description: Description for the configuration
            
        Returns:
            Configuration dictionary ready for saving
        """
        config = {
            "metadata": {
                "name": config_name or f"Configuration for {schema_name}",
                "description": config_description or f"Auto-generated configuration for {schema_name}",
                "schema_name": schema_name,
                "created": datetime.now().isoformat(),
                "version": "1.0"
            },
            "generation_settings": {
                "mode": generation_mode,
                "global_repeat_count": self.config.elements.default_element_count,
                "max_depth": self.config.ui.default_tree_depth,
                "include_comments": True
            },
            "element_configs": {},
            "global_overrides": {
                "use_realistic_data": True
            }
        }
        
        # Process choices into element configs
        if selected_choices:
            for choice_key, choice_data in selected_choices.items():
                path = choice_data.get('path', '')
                element_name = path.split('.')[-1] if '.' in path else path
                selected_element = choice_data.get('selected_element', '')
                
                if element_name not in config["element_configs"]:
                    config["element_configs"][element_name] = {}
                
                if "choices" not in config["element_configs"][element_name]:
                    config["element_configs"][element_name]["choices"] = {}
                
                # Use the path as the choice key for more specificity
                choice_context = path.split('.')[-2] if '.' in path and len(path.split('.')) > 1 else 'root'
                config["element_configs"][element_name]["choices"][choice_context] = selected_element
        
        # Process unbounded counts
        if unbounded_counts:
            for element_path, count in unbounded_counts.items():
                element_name = element_path.split('.')[-1] if '.' in element_path else element_path
                
                if element_name not in config["element_configs"]:
                    config["element_configs"][element_name] = {}
                
                config["element_configs"][element_name]["repeat_count"] = count
        
        # Process optional selections
        if optional_selections and generation_mode == "Custom":
            # Group optional selections by element
            element_optionals = {}
            for selection in optional_selections:
                # Clean up the selection string
                clean_selection = selection.split('_')[0] if '_' in selection else selection
                parts = clean_selection.split('.')
                if len(parts) > 1:
                    element_name = parts[0]
                    optional_element = '.'.join(parts[1:])
                    
                    if element_name not in element_optionals:
                        element_optionals[element_name] = []
                    element_optionals[element_name].append(optional_element)
            
            # Add to element configs
            for element_name, optionals in element_optionals.items():
                if element_name not in config["element_configs"]:
                    config["element_configs"][element_name] = {}
                
                config["element_configs"][element_name]["include_optional"] = optionals
        
        return config
    
    def convert_config_to_generator_options(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert configuration data to XMLGenerator options format.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Dictionary compatible with XMLGenerator.generate_dummy_xml_with_options()
        """
        generator_options = {
            "generation_mode": config_data.get("generation_settings", {}).get("mode", "Minimalistic"),
            "selected_choices": {},
            "unbounded_counts": {},
            "optional_selections": [],
            "custom_values": {}
        }
        
        element_configs = config_data.get("element_configs", {})
        
        for element_name, element_config in element_configs.items():
            # Extract choices
            if "choices" in element_config:
                for choice_context, selected_element in element_config["choices"].items():
                    # Create a choice key similar to UI format
                    choice_key = f"{element_name}_{choice_context}_choice"
                    generator_options["selected_choices"][choice_key] = {
                        "path": f"{element_name}.{choice_context}" if choice_context != 'root' else element_name,
                        "selected_element": selected_element,
                        "choice_data": {
                            "path": f"{element_name}.{choice_context}" if choice_context != 'root' else element_name
                        }
                    }
            
            # Extract repeat counts
            if "repeat_count" in element_config:
                generator_options["unbounded_counts"][element_name] = element_config["repeat_count"]
            
            # Extract optional selections
            if "include_optional" in element_config:
                for optional in element_config["include_optional"]:
                    generator_options["optional_selections"].append(f"{element_name}.{optional}")
            
            # Extract custom values (new format only)
            if "custom_values" in element_config:
                generator_options["custom_values"][element_name] = element_config["custom_values"]
        
        return generator_options
    
    def get_example_config(self, schema_name: str = "example_schema.xsd") -> Dict[str, Any]:
        """
        Generate an example configuration file.
        
        Args:
            schema_name: Name of the schema file for the example
            
        Returns:
            Example configuration dictionary
        """
        return {
            "metadata": {
                "name": "Example XML Generation Configuration",
                "description": "Example configuration showing all available options",
                "schema_name": schema_name,
                "created": datetime.now().isoformat(),
                "version": "1.0"
            },
            "generation_settings": {
                "mode": "Custom",
                "global_repeat_count": 2,
                "max_depth": 5,
                "include_comments": True
            },
            "element_configs": {
                "OrderCreateRQ": {
                    "choices": {
                        "PaymentMethod": "CreditCard"
                    },
                    "repeat_count": 1,
                    "include_optional": ["Metadata", "Extensions"]
                },
                "Version": {
                    "custom_values": ["21.3", "21.2", "21.1"],
                    "selection_strategy": "sequential"
                },
                "EchoToken": {
                    "custom_values": ["test-token-12345", "test-token-67890"],
                    "selection_strategy": "sequential"
                },
                "Traveler": {
                    "repeat_count": 3
                },
                "GivenName": {
                    "custom_values": ["John", "Jane", "Michael"],
                    "selection_strategy": "sequential"
                },
                "Surname": {
                    "custom_values": ["Doe", "Smith", "Johnson"],
                    "selection_strategy": "sequential"
                }
            },
            "global_overrides": {
                "default_string_length": 20,
                "use_realistic_data": True
            }
        }
    
    def validate_config_compatibility(self, config_data: Dict[str, Any], schema_name: str) -> List[str]:
        """
        Validate that configuration is compatible with the given schema.
        
        Args:
            config_data: Configuration dictionary
            schema_name: Name of the XSD schema
            
        Returns:
            List of validation warnings (empty if all compatible)
        """
        warnings = []
        
        # Check if schema names match
        config_schema = config_data.get("metadata", {}).get("schema_name", "")
        if config_schema and config_schema != schema_name:
            warnings.append(
                f"Configuration was created for '{config_schema}' but current schema is '{schema_name}'"
            )
        
        # Additional validation logic can be added here
        # e.g., checking if element names exist in the schema
        
        return warnings