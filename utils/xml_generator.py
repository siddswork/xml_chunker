"""
Universal XML Generator module for XML Chunker.

This module provides utilities for generating dummy XML files from ANY XSD schema
with deep recursive parsing, proper choice handling, and deterministic values.
No hardcoding for specific schemas - works universally.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Union, List, Tuple, Set
from datetime import datetime
import xmlschema
from lxml import etree
from config import get_config
from .type_generators import TypeGeneratorFactory


class XMLGenerator:
    """Universal class for generating dummy XML files from any XSD schema with deep recursive parsing."""
    
    def __init__(self, xsd_path: str, config_instance=None):
        """
        Initialize the universal XML generator.
        
        Args:
            xsd_path: Path to the XSD schema file
            config_instance: Configuration instance (uses global config if None)
        """
        self.xsd_path = xsd_path
        self.schema = None
        self.processed_types = set()  # Track processed types to prevent infinite recursion
        self.config = config_instance or get_config()
        self.type_factory = TypeGeneratorFactory(self.config)  # Initialize type generator factory
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the XSD schema from the file with dependency resolution."""
        if not self.xsd_path:
            raise ValueError("XSD path cannot be empty")
            
        if not os.path.exists(self.xsd_path):
            raise ValueError(f"XSD file not found: {self.xsd_path}")
            
        if not os.path.isfile(self.xsd_path):
            raise ValueError(f"XSD path is not a file: {self.xsd_path}")
            
        try:
            base_dir = os.path.dirname(os.path.abspath(self.xsd_path))
            print(f"Loading XSD schema from: {self.xsd_path}")
            print(f"Base directory for schema: {base_dir}")
            
            # Find all XSD files in the same directory for import resolution
            xsd_files = []
            try:
                for filename in os.listdir(base_dir):
                    if filename.endswith('.xsd'):
                        file_path = os.path.join(base_dir, filename)
                        if os.path.isfile(file_path):
                            xsd_files.append(file_path)
            except OSError as e:
                print(f"Warning: Could not list directory {base_dir}: {e}")
            
            # Create locations mapping for schema-specific imports
            locations = {}
            namespace_mappings = self.config.get_namespace_mapping('iata')
            
            for xsd_file in xsd_files:
                try:
                    filename = os.path.basename(xsd_file)
                    if "CommonTypes" in filename:
                        # Map namespace patterns from config
                        common_types_ns = namespace_mappings.get('common_types')
                        if common_types_ns:
                            locations[common_types_ns] = [xsd_file]
                except Exception as e:
                    print(f"Warning: Could not process XSD file {xsd_file}: {e}")
            
            self.schema = xmlschema.XMLSchema(
                os.path.abspath(self.xsd_path),
                base_url=base_dir,
                build=True,
                locations=locations
            )
            
            if self.schema is None:
                raise ValueError("Schema loaded but is None")
                
        except xmlschema.XMLSchemaException as e:
            raise ValueError(f"Invalid XSD schema: {e}")
        except FileNotFoundError as e:
            raise ValueError(f"XSD file or dependency not found: {e}")
        except PermissionError as e:
            raise ValueError(f"Permission denied accessing XSD file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load XSD schema: {e}")
    
    
    
    
    
    
    
    
    def _generate_value_for_type(self, type_name, element_name: str = "") -> Any:
        """Generate validation-compliant value using modular type generators."""
        # Extract constraints from the type
        constraints = self._extract_type_constraints(type_name)
        
        # Check for enumeration constraints first
        if hasattr(type_name, 'enumeration') and type_name.enumeration:
            constraints['enum_values'] = [str(value) for value in type_name.enumeration]
        
        # Create appropriate type generator and generate value
        generator = self.type_factory.create_generator(type_name, constraints)
        return generator.generate(element_name, constraints)
    
    def _extract_type_constraints(self, type_name) -> Dict[str, Any]:
        """Extract validation constraints from XSD type definition."""
        constraints = {}
        
        # Extract facets (length, pattern, min/max values)
        if hasattr(type_name, 'facets') and type_name.facets:
            for facet_name, facet in type_name.facets.items():
                # Skip None facet names
                if facet_name is None:
                    continue
                    
                # Handle both namespaced and simple facet names
                local_name = facet_name.split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                
                if local_name == 'maxLength':
                    constraints['max_length'] = facet.value
                elif local_name == 'minLength':
                    constraints['min_length'] = facet.value
                elif local_name == 'length':
                    constraints['exact_length'] = facet.value
                elif local_name == 'pattern':
                    constraints['pattern'] = facet.value
                elif local_name == 'minInclusive':
                    constraints['min_value'] = facet.value
                elif local_name == 'maxInclusive':
                    constraints['max_value'] = facet.value
                elif local_name == 'enumeration':
                    if 'enum_values' not in constraints:
                        constraints['enum_values'] = []
                    
                    # Handle XsdEnumerationFacets objects (multiple enum values)
                    if hasattr(facet, 'enumeration') and facet.enumeration:
                        constraints['enum_values'].extend([str(val) for val in facet.enumeration])
                    # Handle single enumeration facets
                    elif hasattr(facet, 'value') and facet.value is not None:
                        constraints['enum_values'].append(str(facet.value))
        
        # If no constraints found, check base_type for inherited constraints (like Type -> ContentType)
        if not constraints and hasattr(type_name, 'base_type') and type_name.base_type:
            base_constraints = self._extract_type_constraints(type_name.base_type)
            constraints.update(base_constraints)
        
        return constraints
    
    def _get_element_occurrence_info(self, element: xmlschema.validators.XsdElement) -> Tuple[bool, str]:
        """Get information about element occurrence constraints."""
        if element is None:
            return True, "Unknown element"
            
        # Safely get min_occurs with default
        min_occurs = getattr(element, 'min_occurs', 1) or 0
        max_occurs = getattr(element, 'max_occurs', 1)
        
        is_optional = min_occurs == 0
        
        if max_occurs is None or (max_occurs is not None and max_occurs > 1):
            if is_optional:
                max_occurs_str = "unbounded" if max_occurs is None else str(max_occurs)
                occurrence_info = f"Optional element with max occurrence: {max_occurs_str}"
            else:
                max_occurs_str = "unbounded" if max_occurs is None else str(max_occurs)
                occurrence_info = f"Mandatory element with max occurrence: {max_occurs_str}"
        else:
            occurrence_info = "Optional element" if is_optional else "Mandatory element"
                
        return is_optional, occurrence_info
    
    def _get_element_count(self, element_name: str, element: xmlschema.validators.XsdElement, depth: int = 0) -> int:
        """Get the count for repeating elements with depth-aware limits."""
        if element is None or not element_name:
            return 1
            
        # Check user preferences first
        if hasattr(self, 'user_unbounded_counts') and self.user_unbounded_counts:
            # Check multiple possible path formats
            possible_paths = [
                element_name,
                f"root.{element_name}",
                element_name.split(':')[-1] if ':' in element_name else element_name
            ]
            
            # Add schema-specific paths (check all keys for patterns like "SchemaName.ElementName")
            for key in self.user_unbounded_counts.keys():
                if '.' in key and key.endswith(f".{element_name}"):
                    possible_paths.append(key)
            
            for path in possible_paths:
                if path in self.user_unbounded_counts:
                    user_count = max(1, self.user_unbounded_counts[path])
                    # Limit based on depth to prevent exponential growth
                    if depth > self.config.recursion.max_element_depth:
                        return min(user_count, 1)  # Force single element at deep levels
                    elif depth > self.config.recursion.max_tree_depth:
                        return min(user_count, 2)  # Limit to 2 at moderate depth
                    return user_count
        
        # Depth-aware default count to prevent exponential growth
        if depth > self.config.recursion.max_element_depth:
            return 1  # Only 1 element at very deep levels
        elif depth > self.config.recursion.max_tree_depth:
            return 1  # Reduce to 1 at moderate depth
        else:
            return self.config.elements.default_element_count  # Default from config
    
    def _get_namespace_prefix(self, namespace: str) -> Optional[str]:
        """Get the prefix for a given namespace."""
        if not namespace:
            return None
        for prefix, ns in self.schema.namespaces.items():
            if ns == namespace and prefix:
                return prefix
        return None
    
    def _format_element_name(self, element: xmlschema.validators.XsdElement) -> str:
        """Format element name with appropriate namespace prefix."""
        if element is None:
            return "UnknownElement"
            
        local_name = getattr(element, 'local_name', 'UnknownElement')
        target_namespace = getattr(element, 'target_namespace', None)
        
        if (target_namespace and 
            self.schema and 
            target_namespace != getattr(self.schema, 'target_namespace', None)):
            prefix = self._get_namespace_prefix(target_namespace)
            if prefix:
                return f"{prefix}:{local_name}"
        return local_name
    
    def _is_choice_element(self, element: xmlschema.validators.XsdElement) -> bool:
        """Check if an element is part of a choice construct."""
        if not element.type.is_complex():
            return False
        
        if hasattr(element.type, 'content') and element.type.content:
            # Check if the content model has choice elements
            return hasattr(element.type.content, 'model') and 'choice' in str(element.type.content.model).lower()
        return False
    
    def _get_choice_elements(self, element: xmlschema.validators.XsdElement) -> List[xmlschema.validators.XsdElement]:
        """Get all choice elements from a choice construct."""
        choice_elements = []
        if element.type.is_complex() and hasattr(element.type, 'content') and element.type.content:
            try:
                # Look for actual choice constructs in the content model
                if hasattr(element.type.content, 'model') and str(element.type.content.model) == 'choice':
                    for child in element.type.content.iter_elements():
                        choice_elements.append(child)
                elif hasattr(element.type.content, '_group'):
                    # Check for nested choice groups
                    for group in element.type.content._group:
                        if hasattr(group, 'model') and str(group.model) == 'choice':
                            for child in group.iter_elements():
                                choice_elements.append(child)
                else:
                    # For schema-specific patterns, check for configured choice patterns
                    all_elements = list(element.type.content.iter_elements())
                    element_names = [e.local_name for e in all_elements]
                    choice_patterns = self.config.get_choice_patterns('iata')
                    
                    if choice_patterns and all(pattern in element_names for pattern in choice_patterns):
                        # These are mutually exclusive choices based on config
                        for elem in all_elements:
                            if elem.local_name in choice_patterns:
                                choice_elements.append(elem)
            except:
                pass
        return choice_elements
    
    def _select_choice_element(self, choice_elements: List[xmlschema.validators.XsdElement], parent_path: str) -> Optional[xmlschema.validators.XsdElement]:
        """Select which choice element to generate based on user preferences."""
        if not choice_elements:
            return None
            
        # Check user preferences
        if hasattr(self, 'user_choices') and self.user_choices:
            for choice_key, choice_data in self.user_choices.items():
                # Handle multiple formats:
                # 1. Simple format: {"Response": True}
                # 2. Complex format: {"key": {"path": ..., "selected_element": ...}}
                # 3. Streamlit format: {"choice_0": {"path": ..., "selected_element": ...}}
                
                if isinstance(choice_data, bool):
                    # Simple format: look for element with matching name
                    if choice_data:  # If True, select this choice
                        for elem in choice_elements:
                            if elem.local_name == choice_key:
                                return elem
                elif isinstance(choice_data, dict):
                    # Complex/Streamlit format: with path and selected_element
                    user_path = choice_data.get('path')
                    selected_element_name = choice_data.get('selected_element')
                    
                    # Check path matching (for specific choice locations)
                    path_matches = (user_path == parent_path or 
                                  parent_path.endswith(f".{user_path}") or
                                  parent_path.endswith(user_path)) if user_path else False
                    
                    # For Streamlit format, also check if any element name matches selected_element
                    if selected_element_name:
                        for elem in choice_elements:
                            if elem.local_name == selected_element_name:
                                # If path matches or we don't have specific path info, use this selection
                                if path_matches or not user_path:
                                    return elem
                    
                    # Legacy path-based matching
                    if path_matches and selected_element_name:
                        for elem in choice_elements:
                            if elem.local_name == selected_element_name:
                                return elem
        
        # Default: select first element
        return choice_elements[0]
    
    def _create_element_dict(self, element: xmlschema.validators.XsdElement, path: str = "", depth: int = 0) -> Dict[str, Any]:
        """
        Universally create a dictionary representation of any XSD element with deep recursive parsing.
        
        Args:
            element: XSD element to process
            path: Current path in the schema hierarchy
            depth: Current recursion depth
            
        Returns:
            Dictionary with element structure and appropriate values
        """
        # CRITICAL: Prevent infinite recursion with much lower limit
        if depth > self.config.recursion.max_element_depth:
            return {"_recursion_limit": "Maximum depth reached"}
        
        # CRITICAL: Aggressive circular reference protection
        type_key = f"{element.local_name}_{str(element.type)}"
        if type_key in self.processed_types and depth > self.config.recursion.circular_reference_depth:
            return {"_circular_ref": f"Circular reference detected for {element.local_name}"}
        
        # CRITICAL: Prevent processing same type multiple times at any depth > configured limit
        if depth > self.config.recursion.max_type_processing_depth and type_key in self.processed_types:
            return {"_type_reuse": f"Type {element.local_name} already processed"}
        
        self.processed_types.add(type_key)
        
        try:
            result = {}
            current_path = f"{path}.{element.local_name}" if path else element.local_name
            
            # Handle null type
            if element.type is None:
                # Use string generator for unknown types
                string_gen = self.type_factory.create_generator("string", {})
                return string_gen.generate(element.local_name, {})
            
            # Process simple types
            if element.type.is_simple():
                return self._generate_value_for_type(element.type, element.local_name)
            
            # Process complex types
            if element.type.is_complex():
                # Process attributes
                if hasattr(element.type, 'attributes') and element.type.attributes:
                    for attr_name, attr in element.type.attributes.items():
                        if attr.type is not None:
                            result[f'@{attr_name}'] = self._generate_value_for_type(attr.type, attr_name)
                
                # Process content
                if hasattr(element.type, 'content') and element.type.content is not None:
                    # Handle choice constructs
                    choice_elements = self._get_choice_elements(element)
                    if choice_elements and len(choice_elements) > 1:
                        # This is a choice construct - select one element
                        selected_element = self._select_choice_element(choice_elements, current_path)
                        if selected_element:
                            child_name = self._format_element_name(selected_element)
                            
                            if selected_element.max_occurs is None or selected_element.max_occurs > 1:
                                count = self._get_element_count(child_name, selected_element, depth)
                                # CRITICAL: Limit count based on depth to prevent memory explosion
                                safe_count = min(count, max(1, self.config.recursion.max_tree_depth - depth))  # Reduce count based on config
                                result[child_name] = [self._create_element_dict(selected_element, f"{current_path}.{child_name}", depth + 1) for _ in range(safe_count)]
                            else:
                                result[child_name] = self._create_element_dict(selected_element, f"{current_path}.{child_name}", depth + 1)
                        
                        # Process non-choice elements (sequence elements after the choice)
                        try:
                            for child in element.type.content.iter_elements():
                                if child not in choice_elements:
                                    child_name = self._format_element_name(child)
                                    
                                    if child.max_occurs is None or child.max_occurs > 1:
                                        count = self._get_element_count(child_name, child, depth)
                                        # CRITICAL: Limit count based on depth to prevent memory explosion
                                        safe_count = min(count, max(1, 5 - depth))  # Exponentially reduce count
                                        result[child_name] = [self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1) for _ in range(safe_count)]
                                    else:
                                        result[child_name] = self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1)
                        except AttributeError:
                            # Handle cases where content doesn't have iter_elements (simple types)
                            pass
                    else:
                        # No choice construct - process all elements normally
                        try:
                            for child in element.type.content.iter_elements():
                                child_name = self._format_element_name(child)
                                
                                if child.max_occurs is None or child.max_occurs > 1:
                                    count = self._get_element_count(child_name, child, depth)
                                    # CRITICAL: Limit count based on depth to prevent memory explosion
                                    safe_count = min(count, max(1, 5 - depth))  # Exponentially reduce count
                                    result[child_name] = [self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1) for _ in range(safe_count)]
                                else:
                                    result[child_name] = self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1)
                        except AttributeError:
                            # Handle cases where content doesn't have iter_elements (simple types)
                            pass
            
            return result
            
        finally:
            # Remove from processed types when done
            self.processed_types.discard(type_key)
    
    def generate_dummy_xml_with_choices(self, selected_choices=None, unbounded_counts=None, output_path=None) -> str:
        """Generate XML with user-selected choices and unbounded counts."""
        if not self.schema:
            return '<?xml version="1.0" encoding="UTF-8"?><error>Failed to load schema</error>'
        
        # Store user preferences
        self.user_choices = selected_choices or {}
        self.user_unbounded_counts = unbounded_counts or {}
        
        return self.generate_dummy_xml(output_path)
    
    def generate_dummy_xml(self, output_path: Optional[str] = None) -> str:
        """Generate a dummy XML file based on the XSD schema."""
        if not self.schema:
            return self._create_error_xml("Schema not loaded or is None")
        
        # Add performance monitoring
        import time
        start_time = time.time()
        print(f"Starting XML generation at {start_time}")
        
        try:
            # Validate schema has elements
            if not hasattr(self.schema, 'elements') or not self.schema.elements:
                return self._create_error_xml("Schema has no elements defined")
                
            root_elements = list(self.schema.elements.keys())
            if not root_elements:
                return self._create_error_xml("No root elements found in schema")
            
            root_name = root_elements[0]
            root_element = self.schema.elements.get(root_name)
            
            if root_element is None:
                return self._create_error_xml(f"Root element '{root_name}' is None")
            
            # Reset processed types for each generation
            self.processed_types = set()
            
            try:
                # Create a dictionary representation of the XML
                xml_dict = self._create_element_dict(root_element, root_name)
                
                if not xml_dict:
                    return self._create_error_xml("Generated XML dictionary is empty")
                    
            except RecursionError:
                return self._create_error_xml("Maximum recursion depth exceeded during XML generation")
            except Exception as e:
                return self._create_error_xml(f"Error creating element dictionary: {str(e)}")
            
            # Build namespace map safely
            nsmap = {}
            try:
                if hasattr(self.schema, 'namespaces') and self.schema.namespaces:
                    for prefix, uri in self.schema.namespaces.items():
                        if prefix and uri and prefix != 'xml':
                            nsmap[prefix] = uri
                
                if hasattr(self.schema, 'target_namespace') and self.schema.target_namespace:
                    nsmap[None] = self.schema.target_namespace
            except Exception as e:
                print(f"Warning: Error building namespace map: {e}")
            
            # Build XML tree with fallback
            xml_string = ""
            try:
                if self.schema.target_namespace:
                    root = etree.Element(etree.QName(self.schema.target_namespace, root_name), nsmap=nsmap)
                else:
                    root = etree.Element(root_name, nsmap=nsmap)
                    
                self._build_xml_tree(root, xml_dict)
                xml_string = etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=False).decode('utf-8')
                
            except Exception as tree_error:
                print(f"Warning: XML tree building failed: {tree_error}")
                try:
                    # Fallback to simple XML building
                    namespace = getattr(self.schema, 'target_namespace', '')
                    namespace_prefix = f'xmlns="{namespace}"' if namespace else ''
                    xml_string = self._dict_to_xml(root_name, xml_dict, namespace_prefix)
                except Exception as fallback_error:
                    return self._create_error_xml(f"Both XML tree building and fallback failed: {fallback_error}")
            
            if not xml_string:
                return self._create_error_xml("Generated XML string is empty")
            
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'
            
            # Performance monitoring
            end_time = time.time()
            generation_time = end_time - start_time
            print(f"XML generation completed in {generation_time:.2f} seconds")
            print(f"Generated XML size: {len(xml_content)} characters")
            print(f"Processed types count: {len(self.processed_types)}")
            
            # Save to file if requested
            if output_path:
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(xml_content)
                except Exception as save_error:
                    print(f"Warning: Could not save XML to {output_path}: {save_error}")
            
            return xml_content
            
        except Exception as e:
            return self._create_error_xml(f"Unexpected error during XML generation: {str(e)}")
    
    def _create_error_xml(self, message: str) -> str:
        """Create a standardized error XML response."""
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<error>\n'
            f'  <message>{message}</message>\n'
            f'  <timestamp>{datetime.now().isoformat()}</timestamp>\n'
            f'</error>'
        )
    
    def _build_xml_tree(self, parent_element: etree.Element, data: Union[Dict[str, Any], str, int, float, bool, None]) -> None:
        """Recursively build an XML tree from a dictionary."""
        if data is None:
            return
            
        if isinstance(data, dict):
            # Process attributes first
            for k, v in data.items():
                if isinstance(k, str) and k.startswith('@'):
                    attr_name = k[1:]
                    if v is not None:
                        parent_element.set(attr_name, str(v))
            
            # Process elements
            for k, v in data.items():
                if isinstance(k, str) and not k.startswith('@') and not k.startswith('_'):
                    
                    # Determine qualified name
                    if ':' in k:
                        ns_prefix, local_name = k.split(':', 1)
                        ns_uri = self.schema.namespaces.get(ns_prefix)
                        qname = etree.QName(ns_uri, local_name) if ns_uri else k
                    else:
                        ns_uri = self.schema.target_namespace
                        qname = etree.QName(ns_uri, k) if ns_uri else k
                    
                    # Create elements
                    if isinstance(v, list):
                        for item in v:
                            child_element = etree.SubElement(parent_element, qname)
                            if isinstance(item, dict):
                                self._build_xml_tree(child_element, item)
                            else:
                                child_element.text = str(item)
                    else:
                        child_element = etree.SubElement(parent_element, qname)
                        if isinstance(v, dict):
                            self._build_xml_tree(child_element, v)
                        else:
                            child_element.text = str(v)
        else:
            parent_element.text = str(data)
    
    def _dict_to_xml(self, element_name: str, data: Union[Dict[str, Any], str, int, float, bool, None], namespace_prefix: str = '') -> str:
        """Convert a dictionary to XML string (fallback method)."""
        if data is None:
            return f'<{element_name}></{element_name}>'
            
        if isinstance(data, dict):
            # Build attributes
            attrs = []
            for k, v in data.items():
                if isinstance(k, str) and k.startswith('@') and v is not None:
                    attrs.append(f'{k[1:]}="{v}"')
            
            attrs_str = ' '.join(attrs)
            if namespace_prefix and attrs_str:
                attrs_str = f'{namespace_prefix} {attrs_str}'
            elif namespace_prefix:
                attrs_str = namespace_prefix
            
            # Build child elements
            children = []
            for k, v in data.items():
                if isinstance(k, str) and not k.startswith('@') and not k.startswith('_'):
                    
                    if isinstance(v, list):
                        for item in v:
                            children.append(self._dict_to_xml(k, item))
                    else:
                        children.append(self._dict_to_xml(k, v))
            
            if not children:
                return f'<{element_name}{" " + attrs_str if attrs_str else ""}></{element_name}>'
            
            children_str = ''.join(children)
            return f'<{element_name}{" " + attrs_str if attrs_str else ""}>{children_str}</{element_name}>'
        else:
            return f'<{element_name}>{data}</{element_name}>'