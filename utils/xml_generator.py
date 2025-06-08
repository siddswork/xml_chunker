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


class XMLGenerator:
    """Universal class for generating dummy XML files from any XSD schema with deep recursive parsing."""
    
    def __init__(self, xsd_path: str):
        """
        Initialize the universal XML generator.
        
        Args:
            xsd_path: Path to the XSD schema file
        """
        self.xsd_path = xsd_path
        self.schema = None
        self.processed_types = set()  # Track processed types to prevent infinite recursion
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
            
            # Create locations mapping for common IATA imports
            locations = {}
            for xsd_file in xsd_files:
                try:
                    filename = os.path.basename(xsd_file)
                    if "CommonTypes" in filename:
                        # Map common namespace patterns
                        locations["http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes"] = [xsd_file]
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
    
    def _generate_deterministic_string(self, element_name: str = "", context: str = "") -> str:
        """Generate a deterministic string based on element name and context."""
        if not element_name:
            return "SampleText"
        
        name_lower = element_name.lower()
        if 'code' in name_lower:
            return "ABC123"
        elif 'id' in name_lower:
            return f"{element_name}123456"
        elif 'name' in name_lower:
            return f"Sample{element_name}"
        elif 'text' in name_lower or 'desc' in name_lower:
            return f"Sample {element_name} description"
        elif 'uri' in name_lower or 'url' in name_lower:
            return "https://example.com/sample"
        elif 'email' in name_lower:
            return "sample@example.com"
        elif 'currency' in name_lower:
            return "USD"
        elif 'lang' in name_lower:
            return "EN"
        elif 'version' in name_lower:
            return "1.0"
        elif 'type' in name_lower:
            return "Standard"
        else:
            return f"Sample{element_name}"
    
    def _generate_deterministic_number(self, element_name: str = "") -> int:
        """Generate a deterministic number based on element name."""
        name_lower = element_name.lower() if element_name else ""
        if 'count' in name_lower or 'number' in name_lower:
            return 5
        elif 'amount' in name_lower or 'price' in name_lower:
            return 100
        elif 'version' in name_lower:
            return 1
        elif 'sequence' in name_lower:
            return 1
        else:
            return 123
    
    def _generate_deterministic_decimal(self, element_name: str = "") -> float:
        """Generate a deterministic decimal based on element name."""
        name_lower = element_name.lower() if element_name else ""
        if 'amount' in name_lower or 'price' in name_lower:
            return 99.99
        elif 'rate' in name_lower:
            return 0.15
        elif 'percentage' in name_lower:
            return 10.5
        else:
            return 123.45
    
    def _generate_deterministic_date(self, element_name: str = "") -> str:
        """Generate a deterministic date in ISO format."""
        return "2024-01-15"
    
    def _generate_deterministic_datetime(self, element_name: str = "") -> str:
        """Generate a deterministic datetime in ISO format."""
        return "2024-01-15T10:30:00"
    
    def _generate_deterministic_time(self, element_name: str = "") -> str:
        """Generate a deterministic time."""
        return "10:30:00"
    
    def _generate_deterministic_boolean(self, element_name: str = "") -> bool:
        """Generate a deterministic boolean value."""
        return True
    
    def _generate_value_for_type(self, type_name: str, element_name: str = "") -> Any:
        """Generate a deterministic value based on the XSD type."""
        type_str = str(type_name).lower()
        
        if 'string' in type_str or 'token' in type_str or 'normalizedstring' in type_str:
            return self._generate_deterministic_string(element_name)
        elif any(t in type_str for t in ['int', 'long', 'short', 'positiveinteger', 'nonpositiveinteger']):
            return self._generate_deterministic_number(element_name)
        elif any(t in type_str for t in ['decimal', 'float', 'double']):
            return self._generate_deterministic_decimal(element_name)
        elif 'boolean' in type_str:
            return self._generate_deterministic_boolean(element_name)
        elif 'datetime' in type_str:
            return self._generate_deterministic_datetime(element_name)
        elif 'date' in type_str:
            return self._generate_deterministic_date(element_name)
        elif 'time' in type_str:
            return self._generate_deterministic_time(element_name)
        elif 'anyuri' in type_str:
            return "https://example.com/sample"
        else:
            return self._generate_deterministic_string(element_name)
    
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
    
    def _get_element_count(self, element_name: str, element: xmlschema.validators.XsdElement) -> int:
        """Get the count for repeating elements."""
        if element is None or not element_name:
            return 1
            
        # Check user preferences first
        if hasattr(self, 'user_unbounded_counts') and self.user_unbounded_counts:
            possible_paths = [
                element_name,
                f"root.{element_name}",
                element_name.split(':')[-1] if ':' in element_name else element_name
            ]
            
            for path in possible_paths:
                if path in self.user_unbounded_counts:
                    return max(1, self.user_unbounded_counts[path])  # Ensure at least 1
        
        # Default: deterministic count of 2
        return 2
    
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
                    # For IATA schemas, Error and Response are typically mutually exclusive
                    # Check if we have both Error and Response elements
                    all_elements = list(element.type.content.iter_elements())
                    element_names = [e.local_name for e in all_elements]
                    if 'Error' in element_names and 'Response' in element_names:
                        # These are mutually exclusive choices in IATA schemas
                        for elem in all_elements:
                            if elem.local_name in ['Error', 'Response']:
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
                user_path = choice_data.get('path')
                # Check for exact match or if the parent_path ends with the user_path
                if (user_path == parent_path or 
                    parent_path.endswith(f".{user_path}") or
                    parent_path.endswith(user_path)):
                    selected_name = choice_data.get('selected_element')
                    for elem in choice_elements:
                        if elem.local_name == selected_name:
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
        # Prevent infinite recursion
        if depth > 15:
            return {"_recursion_limit": "Maximum depth reached"}
        
        # Track processed types to prevent circular references
        type_key = f"{element.local_name}_{str(element.type)}"
        if type_key in self.processed_types and depth > 5:
            return {"_circular_ref": f"Circular reference detected for {element.local_name}"}
        
        self.processed_types.add(type_key)
        
        try:
            result = {}
            current_path = f"{path}.{element.local_name}" if path else element.local_name
            
            # Handle null type
            if element.type is None:
                return self._generate_deterministic_string(element.local_name)
            
            # Process simple types
            if element.type.is_simple():
                return self._generate_value_for_type(str(element.type), element.local_name)
            
            # Process complex types
            if element.type.is_complex():
                # Process attributes
                if hasattr(element.type, 'attributes') and element.type.attributes:
                    for attr_name, attr in element.type.attributes.items():
                        if attr.type is not None:
                            result[f'@{attr_name}'] = self._generate_value_for_type(str(attr.type), attr_name)
                
                # Process content
                if hasattr(element.type, 'content') and element.type.content is not None:
                    # Handle choice constructs
                    choice_elements = self._get_choice_elements(element)
                    if choice_elements and len(choice_elements) > 1:
                        # This is a choice construct - select one element
                        selected_element = self._select_choice_element(choice_elements, current_path)
                        if selected_element:
                            child_name = self._format_element_name(selected_element)
                            is_optional, occurrence_info = self._get_element_occurrence_info(selected_element)
                            
                            result[f"_comment_{child_name}"] = f"{occurrence_info} (selected choice)"
                            
                            if selected_element.max_occurs is None or selected_element.max_occurs > 1:
                                count = self._get_element_count(child_name, selected_element)
                                result[child_name] = [self._create_element_dict(selected_element, f"{current_path}.{child_name}", depth + 1) for _ in range(count)]
                            else:
                                result[child_name] = self._create_element_dict(selected_element, f"{current_path}.{child_name}", depth + 1)
                        
                        # Process non-choice elements (sequence elements after the choice)
                        try:
                            for child in element.type.content.iter_elements():
                                if child not in choice_elements:
                                    child_name = self._format_element_name(child)
                                    is_optional, occurrence_info = self._get_element_occurrence_info(child)
                                    
                                    result[f"_comment_{child_name}"] = occurrence_info
                                    
                                    if child.max_occurs is None or child.max_occurs > 1:
                                        count = self._get_element_count(child_name, child)
                                        result[child_name] = [self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1) for _ in range(count)]
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
                                is_optional, occurrence_info = self._get_element_occurrence_info(child)
                                
                                result[f"_comment_{child_name}"] = occurrence_info
                                
                                if child.max_occurs is None or child.max_occurs > 1:
                                    count = self._get_element_count(child_name, child)
                                    result[child_name] = [self._create_element_dict(child, f"{current_path}.{child_name}", depth + 1) for _ in range(count)]
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
                    # Add comment if exists
                    comment_key = f"_comment_{k}"
                    if comment_key in data:
                        comment = etree.Comment(f" {data[comment_key]} ")
                        parent_element.append(comment)
                    
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
                    comment_key = f"_comment_{k}"
                    if comment_key in data:
                        children.append(f'<!-- {data[comment_key]} -->')
                    
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