#!/usr/bin/env python3
"""
Debug script to specifically test FlightNumberTextType pattern extraction.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import StringTypeGenerator

def debug_flight_number_type():
    """Debug FlightNumberTextType pattern extraction."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("=== Debugging FlightNumberTextType ===")
    
    # Look for FlightNumberTextType in the schema
    flight_number_type = None
    for name, type_obj in generator.schema.types.items():
        if 'FlightNumberTextType' in str(name):
            flight_number_type = type_obj
            print(f"Found type: {name}")
            print(f"Type object: {type_obj}")
            break
    
    if not flight_number_type:
        print("FlightNumberTextType not found, checking all types containing 'flight':")
        for name, type_obj in generator.schema.types.items():
            if 'flight' in str(name).lower():
                print(f"  {name}: {type_obj}")
        return
    
    # Extract constraints
    print(f"\n--- Extracting constraints for {flight_number_type} ---")
    constraints = generator._extract_type_constraints(flight_number_type)
    print(f"Extracted constraints: {constraints}")
    
    # Check the type structure
    print(f"\nType attributes:")
    for attr in dir(flight_number_type):
        if not attr.startswith('_'):
            try:
                value = getattr(flight_number_type, attr)
                print(f"  {attr}: {value}")
            except:
                print(f"  {attr}: <error accessing>")
    
    # Check facets specifically
    if hasattr(flight_number_type, 'facets'):
        print(f"\nFacets: {flight_number_type.facets}")
        if flight_number_type.facets:
            for facet_name, facet in flight_number_type.facets.items():
                print(f"  Facet {facet_name}: {facet}")
                print(f"    Type: {type(facet)}")
                if hasattr(facet, 'regexps'):
                    print(f"    Regexps: {facet.regexps}")
                if hasattr(facet, 'value'):
                    print(f"    Value: {facet.value}")
    
    # Test generating value with correct pattern
    if 'pattern' in constraints:
        pattern = constraints['pattern']
        print(f"\n--- Testing pattern generation for: {pattern} ---")
        
        string_gen = StringTypeGenerator()
        test_value = string_gen.generate_pattern_value(pattern)
        print(f"Generated value: {test_value}")
        
        is_compliant = string_gen.test_pattern_compliance(test_value, pattern)
        print(f"Pattern compliant: {is_compliant}")
        
        # Test the complete flow
        type_gen = generator.type_factory.create_generator(flight_number_type, constraints)
        complete_value = type_gen.generate("MarketingCarrierFlightNumberText", constraints)
        print(f"Complete generator value: {complete_value}")
        
    else:
        print("No pattern constraint found - this is the issue!")
        
        # Manual test with known pattern
        print("\n--- Manual test with [0-9]{1,4} pattern ---")
        manual_constraints = {'pattern': '[0-9]{1,4}'}
        string_gen = StringTypeGenerator()
        manual_value = string_gen.validate_constraints("SampleText", manual_constraints)
        print(f"Manual generation result: {manual_value}")

if __name__ == "__main__":
    debug_flight_number_type()