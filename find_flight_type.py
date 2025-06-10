#!/usr/bin/env python3
"""
Find FlightNumberTextType in the schema by checking all namespaces.
"""

from utils.xml_generator import XMLGenerator

def find_flight_number_type():
    """Find FlightNumberTextType in all schema namespaces."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("=== Searching for FlightNumberTextType ===")
    print(f"Schema namespaces: {generator.schema.namespaces}")
    
    # Check all types
    print(f"\nTotal types in schema: {len(generator.schema.types)}")
    
    # Look for flight-related types
    flight_types = []
    for name, type_obj in generator.schema.types.items():
        name_str = str(name)
        if 'flight' in name_str.lower() or 'FlightNumber' in name_str:
            flight_types.append((name, type_obj))
            print(f"Flight-related type found: {name}")
    
    print(f"Found {len(flight_types)} flight-related types")
    
    # Check specific elements
    print(f"\n=== Searching for MarketingCarrierFlightNumberText element ===")
    
    for name, element in generator.schema.elements.items():
        if 'MarketingCarrierFlightNumberText' in str(name):
            print(f"Found element: {name}")
            print(f"Element type: {element.type}")
            print(f"Element type name: {getattr(element.type, 'name', 'No name')}")
            
            # Try to extract constraints from this element's type
            if hasattr(element.type, 'facets'):
                print(f"Element type facets: {element.type.facets}")
                
            constraints = generator._extract_type_constraints(element.type)
            print(f"Extracted constraints: {constraints}")
            
            # Test generating a value for this element
            try:
                type_gen = generator.type_factory.create_generator(element.type, constraints)
                value = type_gen.generate(str(name), constraints)
                print(f"Generated value: {value}")
            except Exception as e:
                print(f"Error generating value: {e}")
                import traceback
                traceback.print_exc()
    
    # Check the schema map
    print(f"\n=== Schema map info ===")
    if hasattr(generator.schema, 'maps'):
        maps = generator.schema.maps
        print(f"Schema has maps: {type(maps)}")
        
        if hasattr(maps, 'types'):
            print(f"Types in maps: {len(maps.types)}")
            for name in list(maps.types.keys())[:10]:  # First 10
                print(f"  {name}")
                
        # Look specifically for flight number
        if hasattr(maps, 'lookup'):
            try:
                flight_type = maps.lookup('FlightNumberTextType')
                print(f"Found FlightNumberTextType via lookup: {flight_type}")
                
                constraints = generator._extract_type_constraints(flight_type)
                print(f"Constraints from lookup: {constraints}")
                
            except Exception as e:
                print(f"Lookup failed: {e}")

if __name__ == "__main__":
    find_flight_number_type()