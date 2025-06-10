#!/usr/bin/env python3
"""
Debug elements that generate empty values.
"""

from utils.xml_generator import XMLGenerator

# Monkey patch to debug empty value generation
original_generate_value = XMLGenerator._generate_value_for_type

def debug_empty_value_generation(self, type_name, element_name: str = ""):
    """Debug wrapper to catch empty value generation."""
    
    # Generate value first
    result = original_generate_value(self, type_name, element_name)
    
    # Check if result is empty or None
    if result is None or result == "":
        print(f"\n🚨 EMPTY VALUE GENERATED")
        print(f"Element name: {element_name}")
        print(f"Type: {type_name}")
        print(f"Type class: {type(type_name)}")
        print(f"Result: '{result}' (type: {type(result)})")
        
        if hasattr(type_name, 'name'):
            print(f"Type name: {type_name.name}")
        
        # Check constraints
        constraints = self._extract_type_constraints(type_name)
        print(f"Constraints: {constraints}")
        
        # Check what generator was created
        generator = self.type_factory.create_generator(type_name, constraints)
        print(f"Generator: {type(generator)}")
        
        # Try to generate again to see if it's consistent
        retry_result = generator.generate(element_name, constraints)
        print(f"Retry result: '{retry_result}'")
        print("--- END EMPTY DEBUG ---\n")
    
    return result

# Apply monkey patch
XMLGenerator._generate_value_for_type = debug_empty_value_generation

def debug_empty_generation():
    """Debug empty value generation."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Empty Value Generation")
    print("=" * 40)
    
    # Generate XML with empty value debugging
    print("Generating XML with empty value debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"\nGenerated XML size: {len(xml_data)} characters")

if __name__ == "__main__":
    debug_empty_generation()