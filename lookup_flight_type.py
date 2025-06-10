#!/usr/bin/env python3
"""
Proper lookup for FlightNumberTextType using qualified names.
"""

from utils.xml_generator import XMLGenerator

def lookup_flight_number_type():
    """Proper lookup for FlightNumberTextType."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("=== Qualified Name Lookup ===")
    print(f"Schema namespaces: {generator.schema.namespaces}")
    
    # Try to find types in the common namespace  
    cns_namespace = 'http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes'
    
    # Check maps properly
    maps = generator.schema.maps
    print(f"Total types in maps: {len(maps.types)}")
    
    # Look for FlightNumberTextType with different qualified names
    possible_qnames = [
        'FlightNumberTextType',
        '{' + cns_namespace + '}FlightNumberTextType',
        'cns:FlightNumberTextType'
    ]
    
    for qname in possible_qnames:
        try:
            if qname in maps.types:
                flight_type = maps.types[qname]
                print(f"Found FlightNumberTextType with qname '{qname}': {flight_type}")
                
                # Extract constraints
                constraints = generator._extract_type_constraints(flight_type)
                print(f"Constraints: {constraints}")
                
                # Test generation
                if 'pattern' in constraints:
                    from utils.type_generators import StringTypeGenerator
                    string_gen = StringTypeGenerator()
                    value = string_gen.generate_pattern_value(constraints['pattern'])
                    print(f"Generated value: {value}")
                
                break
            else:
                print(f"QName '{qname}' not found in types")
        except Exception as e:
            print(f"Error with qname '{qname}': {e}")
    
    # List some actual types to see the pattern
    print(f"\n=== Sample types from schema ===")
    type_names = list(maps.types.keys())[:20]
    for name in type_names:
        if 'common' in str(name).lower() or 'flight' in str(name).lower() or 'cns' in str(name).lower():
            print(f"  {name}")
    
    # Try searching in elements instead  
    print(f"\n=== Elements containing 'flight' ===")
    for name, element in maps.elements.items():
        if 'flight' in str(name).lower():
            print(f"Element: {name}")
            print(f"  Type: {element.type}")
            if hasattr(element.type, 'name'):
                print(f"  Type name: {element.type.name}")
    
    # Direct search in types for anything containing 'flight' or 'Flight'
    print(f"\n=== Direct search in all types ===")
    for name, type_obj in maps.types.items():
        if 'flight' in str(name).lower() or 'Flight' in str(name):
            print(f"Type found: {name} -> {type_obj}")

if __name__ == "__main__":
    lookup_flight_number_type()