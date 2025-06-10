#!/usr/bin/env python3
"""
Debug enumeration constraint extraction to find why empty strings are being generated.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import EnumerationTypeGenerator

def debug_enumeration_extraction():
    """Debug enumeration constraint extraction."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Debugging Enumeration Constraint Extraction")
    print("=" * 50)
    
    # Find types that have enumeration facets
    enumeration_types = []
    
    for name, xsd_type in generator.schema.maps.types.items():
        constraints = generator._extract_type_constraints(xsd_type)
        if 'enum_values' in constraints and constraints['enum_values']:
            enumeration_types.append((name, xsd_type, constraints['enum_values']))
    
    print(f"Found {len(enumeration_types)} types with enumeration constraints")
    
    # Test the first few enumeration types
    for i, (type_name, xsd_type, enum_values) in enumerate(enumeration_types[:10]):
        print(f"\n--- Type {i+1}: {type_name} ---")
        print(f"Enumeration values: {enum_values}")
        
        # Test EnumerationTypeGenerator with these values
        constraints = {'enum_values': enum_values}
        enum_gen = EnumerationTypeGenerator()
        
        # Generate multiple values to test
        test_element_name = f"Test{type_name.split('}')[-1] if '}' in str(type_name) else type_name}"
        
        for j in range(3):
            generated_value = enum_gen.generate(test_element_name, constraints)
            print(f"  Generated value {j+1}: '{generated_value}'")
            
            # Check if it's in the valid enum list
            if generated_value in enum_values:
                print(f"    ✅ Valid")
            else:
                print(f"    ❌ Invalid - not in {enum_values}")
    
    # Also test with the factory
    print(f"\n--- Testing TypeGeneratorFactory ---")
    
    for i, (type_name, xsd_type, enum_values) in enumerate(enumeration_types[:3]):
        print(f"\nType: {type_name}")
        constraints = {'enum_values': enum_values}
        
        # Use the factory to create generator (same as in XML generation)
        type_gen = generator.type_factory.create_generator(xsd_type, constraints)
        print(f"Factory created: {type(type_gen)}")
        
        generated_value = type_gen.generate(f"TestElement{i}", constraints)
        print(f"Factory generated: '{generated_value}'")
        
        if generated_value in enum_values:
            print(f"✅ Valid factory generation")
        else:
            print(f"❌ Invalid factory generation - not in {enum_values}")

def test_specific_enumerations():
    """Test the specific enumerations mentioned in the error analysis."""
    
    print(f"\n🎯 Testing Specific Problematic Enumerations")
    print("=" * 50)
    
    test_cases = [
        (['Applied', 'Exempt'], 'AppliedExemptType'),
        (['Exclude', 'Preferred', 'Required'], 'ExcludePreferredRequiredType'),
    ]
    
    for enum_values, type_name in test_cases:
        print(f"\nTesting {type_name}: {enum_values}")
        
        # Test with empty constraints (simulating the error condition)
        enum_gen = EnumerationTypeGenerator()
        
        # Test with empty enum values (this might be the issue)
        empty_result = enum_gen.generate(type_name, {'enum_values': []})
        print(f"Empty enum list result: '{empty_result}'")
        
        # Test with None enum values
        none_result = enum_gen.generate(type_name, {'enum_values': [None, '', 'None']})
        print(f"None enum list result: '{none_result}'")
        
        # Test with valid enum values
        valid_result = enum_gen.generate(type_name, {'enum_values': enum_values})
        print(f"Valid enum list result: '{valid_result}'")
        
        # Test with no constraints at all
        no_constraints_result = enum_gen.generate(type_name, {})
        print(f"No constraints result: '{no_constraints_result}'")
        
        # Test what happens with None constraints
        none_constraints_result = enum_gen.generate(type_name, None)
        print(f"None constraints result: '{none_constraints_result}'")

if __name__ == "__main__":
    debug_enumeration_extraction()
    test_specific_enumerations()