#!/usr/bin/env python3
"""
Debug the specific failing enumeration elements that still show empty strings.
"""

from utils.xml_generator import XMLGenerator

# Monkey patch to catch Applied/Exempt and Exclude/Preferred/Required elements
original_generate_value = XMLGenerator._generate_value_for_type

def debug_specific_failing_enums(self, type_name, element_name: str = ""):
    """Debug wrapper for specific failing enumeration elements."""
    
    # Check constraints first
    constraints = self._extract_type_constraints(type_name)
    
    # Look for the specific problematic enumerations
    if 'enum_values' in constraints:
        enum_values = constraints['enum_values']
        
        # Check for Applied/Exempt enumeration
        if set(enum_values) == {'Applied', 'Exempt'}:
            print(f"\n🔍 DEBUG: Applied/Exempt enumeration")
            print(f"Element: {element_name}")
            print(f"Type: {type_name}")
            print(f"Enum values: {enum_values}")
            
            result = original_generate_value(self, type_name, element_name)
            print(f"Generated result: '{result}' (type: {type(result)})")
            
            if result == '' or result is None:
                print(f"🚨 EMPTY RESULT for Applied/Exempt enum!")
            else:
                print(f"✅ Non-empty result for Applied/Exempt enum")
            print("--- END Applied/Exempt DEBUG ---\n")
            return result
            
        # Check for Exclude/Preferred/Required enumeration
        elif set(enum_values) == {'Exclude', 'Preferred', 'Required'}:
            print(f"\n🔍 DEBUG: Exclude/Preferred/Required enumeration")
            print(f"Element: {element_name}")
            print(f"Type: {type_name}")
            print(f"Enum values: {enum_values}")
            
            result = original_generate_value(self, type_name, element_name)
            print(f"Generated result: '{result}' (type: {type(result)})")
            
            if result == '' or result is None:
                print(f"🚨 EMPTY RESULT for Exclude/Preferred/Required enum!")
            else:
                print(f"✅ Non-empty result for Exclude/Preferred/Required enum")
            print("--- END Exclude/Preferred/Required DEBUG ---\n")
            return result
    
    # Call original for other elements
    return original_generate_value(self, type_name, element_name)

# Apply monkey patch
XMLGenerator._generate_value_for_type = debug_specific_failing_enums

def debug_specific_failing_enums_test():
    """Debug specific failing enumeration elements."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Specific Failing Enumeration Elements")
    print("=" * 55)
    
    # Generate XML with specific debugging
    print("Generating XML with specific enumeration debugging...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"\nGenerated XML size: {len(xml_data)} characters")

if __name__ == "__main__":
    debug_specific_failing_enums_test()