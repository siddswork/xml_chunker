#!/usr/bin/env python3
"""
Debug empty elements that might be created through complex type processing.
"""

from utils.xml_generator import XMLGenerator

# Monkey patch to debug complex type processing for empty elements
original_create_element_dict = XMLGenerator._create_element_dict

def debug_create_element_dict(self, element, path="", depth=0):
    """Debug wrapper for _create_element_dict to catch empty enumeration creation."""
    
    # Call original method
    result = original_create_element_dict(self, element, path, depth)
    
    # Check if this element might be an enumeration that came out empty
    if hasattr(element, 'local_name'):
        element_name = element.local_name
        if any(pattern in element_name.lower() for pattern in 
               ['iata_locationcode', 'airlinedesigcode', 'cabintypecode', 'cabintypename']):
            
            # Check the result
            if result == "" or result is None or (isinstance(result, dict) and not result):
                print(f"\n🚨 EMPTY ENUMERATION ELEMENT CREATED")
                print(f"Element: {element_name}")
                print(f"Path: {path}")
                print(f"Depth: {depth}")
                print(f"Result: {result} (type: {type(result)})")
                print(f"Element type: {element.type}")
                print(f"Element type class: {type(element.type)}")
                print(f"Is simple: {element.type.is_simple() if element.type else 'No type'}")
                print(f"Is complex: {element.type.is_complex() if element.type else 'No type'}")
                
                if element.type:
                    constraints = self._extract_type_constraints(element.type)
                    print(f"Constraints: {constraints}")
                    
                    if 'enum_values' in constraints:
                        print(f"✅ Has enumeration: {constraints['enum_values']}")
                    else:
                        print(f"❌ No enumeration found")
                
                print("--- END EMPTY ELEMENT DEBUG ---\n")
    
    return result

# Apply monkey patch
XMLGenerator._create_element_dict = debug_create_element_dict

def debug_complex_empty_elements():
    """Debug empty enumeration elements through complex type processing."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Empty Enumeration Elements in Complex Type Processing")
    print("=" * 70)
    
    # Generate XML with debugging
    print("Generating XML with complex type debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"\nGenerated XML size: {len(xml_data)} characters")

if __name__ == "__main__":
    debug_complex_empty_elements()