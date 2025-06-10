#!/usr/bin/env python3
"""
Debug the XML tree building process to see where empty values appear.
"""

from utils.xml_generator import XMLGenerator
import xml.etree.ElementTree as ET

# Monkey patch to debug XML tree building
original_build_xml_tree = XMLGenerator._build_xml_tree

def debug_build_xml_tree(self, parent_element, data):
    """Debug wrapper for _build_xml_tree to catch empty value insertion."""
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and not k.startswith('@') and not k.startswith('_'):
                # Check for enumeration-like elements that are getting empty values
                if any(pattern in k.lower() for pattern in 
                       ['iata_locationcode', 'airlinedesigcode', 'cabintypecode', 'cabintypename']):
                    
                    if v == '' or v is None:
                        print(f"\n🚨 EMPTY VALUE IN XML BUILDING")
                        print(f"Element: {k}")
                        print(f"Value: '{v}' (type: {type(v)})")
                        print(f"Parent: {parent_element.tag if hasattr(parent_element, 'tag') else parent_element}")
                        
                        # This should trigger our fallback
                        fallback_value = self._generate_fallback_for_empty_element(k, None)
                        print(f"Fallback would be: '{fallback_value}'")
                        print("--- END XML BUILDING DEBUG ---\n")
                    
                    elif v and isinstance(v, str) and v != '':
                        print(f"✅ Non-empty value for {k}: '{v}'")
    
    # Call original method
    return original_build_xml_tree(self, parent_element, data)

# Apply monkey patch
XMLGenerator._build_xml_tree = debug_build_xml_tree

def debug_xml_tree_building():
    """Debug XML tree building process."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging XML Tree Building Process")
    print("=" * 45)
    
    # Generate XML with debugging
    print("Generating XML with tree building debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"\nGenerated XML size: {len(xml_data)} characters")

if __name__ == "__main__":
    debug_xml_tree_building()