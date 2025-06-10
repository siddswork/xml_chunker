#!/usr/bin/env python3
"""
Examine what types of constraints are actually present in the IATA schema.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def examine_schema_constraints():
    """Examine all constraint types in the schema."""
    
    print("🔍 Examining Schema Constraints")
    print("=" * 60)
    
    # Load the schema
    gen = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    schema = gen.schema
    
    print("1. All constraint types found in schema:")
    print("-" * 40)
    
    constraint_types = set()
    type_count = 0
    facet_count = 0
    
    for type_name, type_obj in schema.types.items():
        type_count += 1
        if hasattr(type_obj, 'facets') and type_obj.facets:
            print(f"\nType: {type_name}")
            for facet_name, facet in type_obj.facets.items():
                facet_count += 1
                # Handle namespaced facet names
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                constraint_types.add(local_name)
                
                print(f"  Facet: {local_name}")
                if hasattr(facet, 'value'):
                    print(f"    Value: {facet.value}")
                else:
                    print(f"    Facet object: {facet}")
    
    print(f"\n2. Summary:")
    print(f"   Total types examined: {type_count}")
    print(f"   Total facets found: {facet_count}")
    print(f"   Unique constraint types: {sorted(constraint_types)}")
    
    if not constraint_types:
        print("\n3. Alternative constraint checking - looking at elements:")
        print("-" * 40)
        
        element_count = 0
        elements_with_constraints = 0
        
        for element_name, element in schema.elements.items():
            element_count += 1
            if hasattr(element, 'type') and element.type:
                if hasattr(element.type, 'facets') and element.type.facets:
                    elements_with_constraints += 1
                    print(f"\nElement: {element_name}")
                    print(f"  Type: {element.type}")
                    for facet_name, facet in element.type.facets.items():
                        local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                        print(f"  Facet: {local_name} = {facet}")
        
        print(f"\nElement summary:")
        print(f"  Total elements: {element_count}")
        print(f"  Elements with constraints: {elements_with_constraints}")
    
    print("\n4. Looking at specific problematic types:")
    print("-" * 40)
    
    # Look for types that might cause validation issues
    problematic_patterns = ['code', 'type', 'measure', 'amount', 'rate']
    
    for pattern in problematic_patterns:
        print(f"\nTypes containing '{pattern}':")
        found_types = []
        for type_name, type_obj in schema.types.items():
            if pattern.lower() in type_name.lower():
                found_types.append((type_name, type_obj))
                if len(found_types) <= 3:  # Show first 3
                    print(f"  {type_name}")
                    if hasattr(type_obj, 'base_type') and type_obj.base_type:
                        print(f"    Base type: {type_obj.base_type}")
                    if hasattr(type_obj, 'primitive_type') and type_obj.primitive_type:
                        print(f"    Primitive type: {type_obj.primitive_type}")
                    if hasattr(type_obj, 'facets') and type_obj.facets:
                        print(f"    Facets: {type_obj.facets}")
                    else:
                        print(f"    No facets")
        
        if len(found_types) > 3:
            print(f"  ... and {len(found_types) - 3} more")
    
    print("\n5. Check for enumeration constraints:")
    print("-" * 40)
    
    enum_count = 0
    for type_name, type_obj in schema.types.items():
        if hasattr(type_obj, 'enumeration') and type_obj.enumeration:
            enum_count += 1
            if enum_count <= 5:  # Show first 5
                print(f"\nEnum type: {type_name}")
                print(f"  Values: {list(type_obj.enumeration)[:10]}...")  # First 10 values
    
    print(f"\nFound {enum_count} enumeration types")

if __name__ == "__main__":
    examine_schema_constraints()