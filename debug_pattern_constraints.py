#!/usr/bin/env python3
"""
Debug script to check pattern constraint extraction and application.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import StringTypeGenerator
import xmlschema

def debug_pattern_constraints():
    """Debug pattern constraint extraction and application."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("=== Debugging Pattern Constraint Extraction ===")
    
    # Test specific types mentioned in the error
    test_types = [
        'FlightNumberTextType',
        'MarketingCarrierFlightNumberText',
        'SampleMarketingCarrierFlightNumberText'
    ]
    
    for type_name in test_types:
        print(f"\n--- Testing Type: {type_name} ---")
        
        try:
            # Try to find this type in the schema
            xsd_type = None
            for name, type_obj in generator.schema.types.items():
                if type_name in str(name):
                    xsd_type = type_obj
                    print(f"Found XSD type: {name}")
                    break
            
            if not xsd_type:
                print(f"Type {type_name} not found in schema")
                continue
                
            # Extract constraints for this type
            constraints = generator._extract_type_constraints(xsd_type)
            print(f"Extracted constraints: {constraints}")
            
            # Test pattern generation if pattern constraint exists
            if 'pattern' in constraints:
                pattern = constraints['pattern']
                print(f"Pattern found: {pattern}")
                
                # Test our StringTypeGenerator with this pattern
                string_gen = StringTypeGenerator()
                test_value = string_gen.generate_pattern_value(pattern)
                print(f"Generated value: {test_value}")
                
                # Test pattern compliance
                is_compliant = string_gen.test_pattern_compliance(test_value, pattern)
                print(f"Pattern compliant: {is_compliant}")
                
            else:
                print("No pattern constraint found")
                
        except Exception as e:
            print(f"Error testing {type_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Test element-specific constraint extraction
    print("\n=== Testing Element Constraint Extraction ===")
    
    # Try to find elements with flight number patterns
    flight_elements = []
    for name, element in generator.schema.elements.items():
        if 'flight' in str(name).lower() and 'number' in str(name).lower():
            flight_elements.append((name, element))
    
    print(f"Found {len(flight_elements)} flight number elements")
    
    for name, element in flight_elements[:3]:  # Test first 3
        print(f"\n--- Element: {name} ---")
        print(f"Element type: {element.type}")
        
        # Try to extract constraints from the element's type
        if hasattr(element.type, 'name'):
            type_name = element.type.name
            constraints = generator._extract_type_constraints(element.type)
            print(f"Type name: {type_name}")
            print(f"Constraints: {constraints}")
            
            # Test value generation for this element
            if constraints:
                try:
                    type_gen = generator.type_factory.create_generator(element.type, constraints)
                    value = type_gen.generate(str(name), constraints)
                    print(f"Generated value: {value}")
                except Exception as e:
                    print(f"Error generating value: {e}")

if __name__ == "__main__":
    debug_pattern_constraints()