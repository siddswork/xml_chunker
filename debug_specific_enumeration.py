#!/usr/bin/env python3
"""
Debug specific enumeration elements that are still empty.
"""

from utils.xml_generator import XMLGenerator

# Monkey patch to debug specific enumeration generation
original_generate_value = XMLGenerator._generate_value_for_type

def debug_specific_enumeration_generation(self, type_name, element_name: str = ""):
    """Debug wrapper for specific enumeration elements."""
    
    # Check for problematic elements
    if element_name and any(name in element_name for name in ['Name', 'IATA_LocationCode', 'AirlineDesigCode', 'CabinTypeCode']):
        print(f"\n🔍 DEBUG: Generating value for enumeration element")
        print(f"Element name: {element_name}")
        print(f"Type: {type_name}")
        print(f"Type class: {type(type_name)}")
        
        if hasattr(type_name, 'name'):
            print(f"Type name: {type_name.name}")
        
        # Extract constraints
        constraints = self._extract_type_constraints(type_name)
        print(f"Extracted constraints: {constraints}")
        
        # Check if this has enumeration
        if 'enum_values' in constraints:
            print(f"✅ Found enumeration values: {constraints['enum_values']}")
        else:
            print(f"❌ No enumeration values found")
            
            # Check what the type looks like
            if hasattr(type_name, 'enumeration'):
                print(f"Type enumeration attribute: {type_name.enumeration}")
            if hasattr(type_name, 'facets'):
                print(f"Type facets: {type_name.facets}")
                if type_name.facets:
                    for fname, facet in type_name.facets.items():
                        print(f"  Facet {fname}: {facet}")
                        if hasattr(facet, 'enumeration'):
                            print(f"    Facet enumeration: {facet.enumeration}")
        
        # Generate value
        result = original_generate_value(self, type_name, element_name)
        print(f"Generated result: '{result}'")
        print(f"Result type: {type(result)}")
        print("--- END DEBUG ---\n")
        
        return result
    
    # Call original for other elements
    return original_generate_value(self, type_name, element_name)

# Apply monkey patch
XMLGenerator._generate_value_for_type = debug_specific_enumeration_generation

def debug_specific_enumeration():
    """Debug specific enumeration generation."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Specific Enumeration Elements")
    print("=" * 50)
    
    # Generate XML with focused debugging
    print("Generating XML with enumeration debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"\nGenerated XML size: {len(xml_data)} characters")

if __name__ == "__main__":
    debug_specific_enumeration()