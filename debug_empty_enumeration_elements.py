#!/usr/bin/env python3
"""
Debug why empty strings appear in XML for enumeration elements.
"""

from utils.xml_generator import XMLGenerator
import re

# Monkey patch to debug XML building for enumeration elements
original_build_xml_tree = XMLGenerator._build_xml_tree

def debug_build_xml_tree(self, parent_element, data):
    """Debug wrapper for _build_xml_tree to catch empty enumeration values."""
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and not k.startswith('@') and not k.startswith('_'):
                # Check if this looks like an enumeration element that's getting empty value
                if v == '' or v is None:
                    element_name = k.split(':')[-1] if ':' in k else k
                    # Look for enumeration-type elements based on common IATA patterns
                    if any(keyword in element_name.lower() for keyword in 
                           ['code', 'type', 'status', 'rule', 'disclosure', 'applied', 'exempt']):
                        print(f"🚨 DEBUG: Empty value for potential enumeration element")
                        print(f"   Element: {k}")
                        print(f"   Value: '{v}'")
                        print(f"   Data type: {type(v)}")
                        print(f"   Parent context: {type(parent_element)}")
                        
                        # Try to find what type this should be
                        if hasattr(self, 'schema'):
                            element_qname = k
                            if ':' in k:
                                ns_prefix, local_name = k.split(':', 1)
                                ns_uri = self.schema.namespaces.get(ns_prefix)
                                if ns_uri:
                                    element_qname = f"{{{ns_uri}}}{local_name}"
                            
                            # Look for this element in schema
                            for name, element in self.schema.maps.elements.items():
                                if element_qname in str(name) or local_name in str(name):
                                    print(f"   Schema element: {name}")
                                    print(f"   Element type: {element.type}")
                                    
                                    # Check if this type has enumeration constraints
                                    constraints = self._extract_type_constraints(element.type)
                                    if 'enum_values' in constraints:
                                        print(f"   Expected enums: {constraints['enum_values']}")
                                        
                                        # Generate a proper value
                                        type_gen = self.type_factory.create_generator(element.type, constraints)
                                        proper_value = type_gen.generate(element_name, constraints)
                                        print(f"   Proper value would be: '{proper_value}'")
                                    break
                        print()
    
    # Call original method
    return original_build_xml_tree(self, parent_element, data)

# Apply monkey patch
XMLGenerator._build_xml_tree = debug_build_xml_tree

def debug_empty_enumeration_in_xml():
    """Debug empty enumeration values in XML generation."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Empty Enumeration Values in XML")
    print("=" * 50)
    
    # Generate XML with debugging
    print("Generating XML with enumeration debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    if xml_data:
        print(f"Generated XML size: {len(xml_data)} characters")
        
        # Search for empty elements in the XML that might be enumerations
        print("\n🔍 Searching for empty elements in generated XML...")
        
        # Find self-closing tags or empty content tags
        empty_patterns = [
            r'<([^>]+)/>',  # Self-closing tags
            r'<([^>]+)></([^>]+)>',  # Empty content tags
        ]
        
        empty_elements = []
        for pattern in empty_patterns:
            matches = re.findall(pattern, xml_data)
            for match in matches:
                if isinstance(match, tuple):
                    element_name = match[0].split()[0]  # Get tag name, ignore attributes
                else:
                    element_name = match.split()[0]  # Get tag name, ignore attributes
                
                # Filter for potential enumeration elements
                if any(keyword in element_name.lower() for keyword in 
                       ['code', 'type', 'status', 'rule', 'disclosure', 'applied', 'exempt']):
                    empty_elements.append(element_name)
        
        print(f"Found {len(empty_elements)} potentially empty enumeration elements:")
        for element in set(empty_elements[:10]):  # Show unique elements, max 10
            print(f"   {element}")
        
        if len(set(empty_elements)) > 10:
            print(f"   ... and {len(set(empty_elements)) - 10} more")
            
    else:
        print("❌ Failed to generate XML")

if __name__ == "__main__":
    debug_empty_enumeration_in_xml()