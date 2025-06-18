"""
Schema Analysis Service for XML Wizard.

This module provides comprehensive XSD schema analysis including
choice element detection, unbounded element identification, and
element tree structure extraction.
"""

from typing import Dict, Any, Optional, List, Tuple, Set
from utils.xsd_parser import XSDParser
from config import get_config


class SchemaAnalyzer:
    """Analyzes XSD schemas to extract structural information."""
    
    def __init__(self, config_instance=None):
        """
        Initialize the schema analyzer.
        
        Args:
            config_instance: Configuration instance (uses global config if None)
        """
        self.config = config_instance or get_config()
    
    def analyze_xsd_schema(self, xsd_file_path: str) -> Dict[str, Any]:
        """
        Analyze XSD schema to extract choice elements and structure.
        
        Args:
            xsd_file_path: Path to the XSD file
            
        Returns:
            Dictionary containing schema analysis
        """
        try:
            parser = XSDParser(xsd_file_path)
            schema_info = parser.get_schema_info()
            root_elements = parser.get_root_elements()
            
            # Get detailed element structure including unbounded elements
            choices = []
            unbounded_elements = []
            element_tree = {}
            
            if parser.schema:
                for element_name, element in parser.schema.elements.items():
                    if element.type and element.type.is_complex():
                        tree_data = self.extract_element_tree(element, element_name)
                        element_tree[element_name] = tree_data
                        
                        # Enhanced choice extraction - find ALL choices including nested ones
                        element_choices = self.extract_all_choice_elements(element, element_name)
                        if element_choices:
                            choices.extend(element_choices)
                        
                        # Find unbounded elements
                        unbounded = self.find_unbounded_elements(element)
                        unbounded_elements.extend(unbounded)
            
            return {
                'schema_info': schema_info,
                'root_elements': root_elements,
                'choices': choices,
                'unbounded_elements': unbounded_elements,
                'element_tree': element_tree,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def extract_element_tree(
        self, 
        element, 
        element_name: str, 
        level: int = 0, 
        processed_types: Optional[Set] = None
    ) -> Dict[str, Any]:
        """
        Extract element tree structure for display with improved depth and None handling.
        
        Args:
            element: XSD element
            element_name: Name of the element
            level: Nesting level for indentation
            processed_types: Set to track processed types and prevent circular references
            
        Returns:
            Dictionary containing tree structure
        """
        # Initialize processed types set if not provided
        if processed_types is None:
            processed_types = set()
        
        # CRITICAL: Prevent circular references
        if element and hasattr(element, 'type') and element.type:
            type_key = f"{element_name}_{str(element.type)}"
            if type_key in processed_types:
                return {
                    'name': element_name,
                    'level': level,
                    'children': [],
                    'is_choice': False,
                    'choice_options': [],
                    'is_unbounded': False,
                    'occurs': {'min': 1, 'max': '1'},
                    '_circular_ref': f'Circular reference: {element_name}'
                }
            processed_types.add(type_key)
        
        # CRITICAL: Prevent stack overflow with enhanced depth limit for UI display
        if level > self.config.ui.default_tree_depth:
            return {
                'name': element_name,
                'level': level,
                'children': [],
                'is_choice': False,
                'choice_options': [],
                'is_unbounded': False,
                'occurs': {'min': 1, 'max': '1'},
                '_depth_limit': f'Maximum depth reached ({self.config.ui.default_tree_depth})'
            }
        
        # Safely get occurrence values with proper None handling
        # CRITICAL: Don't use 'or 1' because minOccurs=0 is valid and should be preserved
        min_occurs = getattr(element, 'min_occurs', None)
        if min_occurs is None:
            min_occurs = 1
        max_occurs = getattr(element, 'max_occurs', 1)
        
        # Format max_occurs to avoid showing None
        if max_occurs is None:
            max_display = "unbounded"
            is_unbounded = True
        elif max_occurs > 1:
            max_display = str(max_occurs)
            is_unbounded = True
        else:
            max_display = "1"
            is_unbounded = False
        
        tree_data = {
            'name': element_name,
            'level': level,
            'children': [],
            'is_choice': False,
            'choice_options': [],
            'is_unbounded': is_unbounded,
            'occurs': {'min': min_occurs, 'max': max_display}
        }
        
        try:
            # Only process complex types that have content
            if (hasattr(element, 'type') and element.type and 
                element.type.is_complex() and 
                hasattr(element.type, 'content') and element.type.content and 
                level < self.config.ui.default_tree_depth + 2):  # Allow extra depth for better tree display
                
                choice_found = False
                
                try:
                    # Check for choice constructs first
                    for item in element.type.content.iter_components():
                        if hasattr(item, 'model') and item.model == 'choice':
                            tree_data['is_choice'] = True
                            choice_found = True
                            # Safely iterate choice elements
                            try:
                                for choice_item in item.iter_elements():
                                    choice_min = getattr(choice_item, 'min_occurs', None)
                                    if choice_min is None:
                                        choice_min = 1
                                    choice_max = getattr(choice_item, 'max_occurs', 1)
                                    choice_max_display = "unbounded" if choice_max is None else str(choice_max)
                                    
                                    tree_data['choice_options'].append({
                                        'name': choice_item.local_name or 'UnknownChoice',
                                        'min_occurs': choice_min,
                                        'max_occurs': choice_max_display
                                    })
                            except AttributeError:
                                # Skip items that don't support iter_elements
                                pass
                except AttributeError:
                    # iter_components not available
                    pass
                
                try:
                    # Process regular elements safely
                    for item in element.type.content.iter_elements():
                        if (hasattr(item, 'local_name') and item.local_name and 
                            hasattr(item, 'type') and item.type):
                            child_tree = self.extract_element_tree(item, item.local_name, level + 1, processed_types)
                            if child_tree and child_tree.get('name'):  # Only add valid trees
                                tree_data['children'].append(child_tree)
                except AttributeError:
                    # iter_elements not available, try alternative approach
                    try:
                        # For some schema types, use direct iteration
                        if hasattr(element.type.content, '_group'):
                            for group_item in element.type.content._group:
                                if hasattr(group_item, 'local_name') and group_item.local_name:
                                    child_tree = self.extract_element_tree(group_item, group_item.local_name, level + 1, processed_types)
                                    if child_tree and child_tree.get('name'):
                                        tree_data['children'].append(child_tree)
                    except:
                        pass
                            
                # Special handling for schema-specific patterns - detect choice patterns
                if not choice_found and element_name:
                    child_names = [child['name'] for child in tree_data['children']]
                    choice_patterns = self.config.get_choice_patterns('iata')
                    
                    # Check if all choice patterns are present in children
                    if choice_patterns and all(pattern in child_names for pattern in choice_patterns):
                        tree_data['is_choice'] = True
                        tree_data['choice_options'] = []
                        for pattern in choice_patterns:
                            tree_data['choice_options'].append({
                                'name': pattern, 
                                'min_occurs': 1, 
                                'max_occurs': 'unbounded' if pattern == 'Error' else '1'
                            })
            
            # Handle simple types - just show type info
            elif hasattr(element, 'type') and element.type and element.type.is_simple():
                tree_data['_type_info'] = f"Simple type: {element.type.local_name or str(element.type)}"
                        
        except Exception as e:
            # More specific error handling
            error_msg = str(e)
            if "iter_elements" in error_msg:
                tree_data['_error'] = "Simple type element (no children)"
            elif "iter_components" in error_msg:
                tree_data['_error'] = "Complex type without accessible components"
            else:
                tree_data['_error'] = f"Error extracting tree: {error_msg}"
        
        return tree_data
    
    def extract_all_choice_elements(self, element, root_path: str = "root", depth: int = 0, processed_types: Optional[Set] = None) -> List[Dict[str, Any]]:
        """
        Extract ALL choice elements from XSD element tree with comprehensive deep search.
        
        Args:
            element: XSD element
            root_path: Current path in the schema
            depth: Current recursion depth
            processed_types: Set to track processed types to prevent cycles
            
        Returns:
            List of all choice information found in the element tree
        """
        # Initialize processed types set
        if processed_types is None:
            processed_types = set()
        
        # Prevent infinite recursion
        if depth > 6:  # Increased depth limit for comprehensive choice detection
            return []
        
        # Prevent circular references
        if element and hasattr(element, 'type') and element.type:
            type_key = f"{root_path}_{str(element.type)}_{depth}"
            if type_key in processed_types:
                return []
            processed_types.add(type_key)
            
        choices = []
        
        try:
            if hasattr(element, 'type') and element.type and element.type.is_complex():
                if hasattr(element.type, 'content') and element.type.content:
                    # Method 1: Check for direct choice constructs
                    try:
                        for item in element.type.content.iter_components():
                            if hasattr(item, 'model') and item.model == 'choice':
                                item_min = getattr(item, 'min_occurs', None)
                                if item_min is None:
                                    item_min = 1
                                item_max = getattr(item, 'max_occurs', None)
                                if item_max is None:
                                    item_max = 1
                                choice_info = {
                                    'type': 'choice',
                                    'min_occurs': item_min,
                                    'max_occurs': item_max,
                                    'elements': [],
                                    'path': root_path
                                }
                                
                                # Extract choice options
                                try:
                                    for choice_item in item.iter_elements():
                                        if hasattr(choice_item, 'local_name') and choice_item.local_name:
                                            choice_min = getattr(choice_item, 'min_occurs', None)
                                            if choice_min is None:
                                                choice_min = 1
                                            choice_max = getattr(choice_item, 'max_occurs', 1)
                                            choice_max_display = "unbounded" if choice_max is None else str(choice_max)
                                            
                                            choice_info['elements'].append({
                                                'name': choice_item.local_name,
                                                'type': str(choice_item.type) if choice_item.type else 'unknown',
                                                'min_occurs': choice_min,
                                                'max_occurs': choice_max_display
                                            })
                                except (AttributeError, TypeError):
                                    pass
                                
                                if choice_info['elements']:
                                    choices.append(choice_info)
                    except (AttributeError, TypeError):
                        pass
                    
                    # Method 2: Check _group for choice elements (enhanced approach)
                    try:
                        if hasattr(element.type.content, '_group'):
                            for group_item in element.type.content._group:
                                if hasattr(group_item, 'model') and str(group_item.model) == 'choice':
                                    group_min = getattr(group_item, 'min_occurs', None)
                                    if group_min is None:
                                        group_min = 1
                                    group_max = getattr(group_item, 'max_occurs', None)
                                    if group_max is None:
                                        group_max = 1
                                    choice_info = {
                                        'type': 'choice',
                                        'min_occurs': group_min,
                                        'max_occurs': group_max,
                                        'elements': [],
                                        'path': root_path
                                    }
                                    
                                    # Extract choice options from _group
                                    try:
                                        if hasattr(group_item, 'iter_elements'):
                                            for choice_item in group_item.iter_elements():
                                                if hasattr(choice_item, 'local_name') and choice_item.local_name:
                                                    choice_min = getattr(choice_item, 'min_occurs', None)
                                                    if choice_min is None:
                                                        choice_min = 1
                                                    choice_max = getattr(choice_item, 'max_occurs', 1)
                                                    choice_max_display = "unbounded" if choice_max is None else str(choice_max)
                                                    
                                                    choice_info['elements'].append({
                                                        'name': choice_item.local_name,
                                                        'type': str(choice_item.type) if choice_item.type else 'unknown',
                                                        'min_occurs': choice_min,
                                                        'max_occurs': choice_max_display
                                                    })
                                    except (AttributeError, TypeError):
                                        pass
                                    
                                    if choice_info['elements']:
                                        choices.append(choice_info)
                    except (AttributeError, TypeError):
                        pass
                    
                    # Method 3: Recursively search child elements for nested choices
                    try:
                        for item in element.type.content.iter_elements():
                            if hasattr(item, 'local_name') and item.local_name:
                                child_path = f"{root_path}.{item.local_name}"
                                nested_choices = self.extract_all_choice_elements(item, child_path, depth + 1, processed_types)
                                choices.extend(nested_choices)
                    except (AttributeError, TypeError):
                        pass
                    
                    # Method 4: Check for schema-specific choice patterns (like IATA Error/Response)
                    if not any(choice['path'] == root_path for choice in choices):
                        child_names = []
                        try:
                            for item in element.type.content.iter_elements():
                                if hasattr(item, 'local_name') and item.local_name:
                                    child_names.append(item.local_name)
                        except (AttributeError, TypeError):
                            pass
                        
                        choice_patterns = self.config.get_choice_patterns('iata')
                        if choice_patterns and all(pattern in child_names for pattern in choice_patterns):
                            choice_info = {
                                'type': 'choice',
                                'min_occurs': 1,
                                'max_occurs': 1,
                                'elements': [],
                                'path': root_path
                            }
                            
                            for pattern in choice_patterns:
                                choice_info['elements'].append({
                                    'name': pattern,
                                    'type': 'schema_pattern',
                                    'min_occurs': 1,
                                    'max_occurs': 'unbounded' if pattern == 'Error' else '1'
                                })
                            
                            choices.append(choice_info)
        
        except Exception as e:
            # Log error but continue processing
            pass
        
        # CRITICAL: Remove duplicate choices based on path and element combinations
        unique_choices = []
        seen_choices = set()
        
        for choice in choices:
            # Create a unique identifier for this choice
            element_names = tuple(sorted([elem['name'] for elem in choice['elements']]))
            choice_id = (choice['path'], element_names)
            
            if choice_id not in seen_choices:
                seen_choices.add(choice_id)
                unique_choices.append(choice)
        
        return unique_choices
    
    def extract_choice_elements(self, element, depth: int = 0) -> List[Dict[str, Any]]:
        """
        Extract choice elements from XSD element with enhanced information.
        
        Args:
            element: XSD element
            depth: Current recursion depth
            
        Returns:
            List of choice information
        """
        # Legacy method - now just calls the enhanced version
        return self.extract_all_choice_elements(element, getattr(element, 'local_name', 'root'), depth)
    
    def find_unbounded_elements(self, element, path: str = "") -> List[Dict[str, Any]]:
        """
        Find elements with maxOccurs="unbounded".
        
        Args:
            element: XSD element
            path: Current path in the schema
            
        Returns:
            List of unbounded elements
        """
        unbounded = []
        current_path = f"{path}.{element.local_name}" if path else element.local_name
        
        try:
            # Check if current element is unbounded
            if hasattr(element, 'max_occurs') and (element.max_occurs is None or element.max_occurs > 1):
                max_val = "unbounded" if element.max_occurs is None else element.max_occurs
                unbounded.append({
                    'name': element.local_name,
                    'path': current_path,
                    'max_occurs': max_val
                })
            
            # Check children
            if hasattr(element.type, 'content') and element.type.content:
                for item in element.type.content.iter_elements():
                    if hasattr(item, 'max_occurs') and (item.max_occurs is None or item.max_occurs > 1):
                        max_val = "unbounded" if item.max_occurs is None else item.max_occurs
                        unbounded.append({
                            'name': item.local_name,
                            'path': f"{current_path}.{item.local_name}",
                            'max_occurs': max_val
                        })
        except Exception:
            pass
        
        return unbounded