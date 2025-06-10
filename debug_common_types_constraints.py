#!/usr/bin/env python3
"""
Debug constraints specifically in the common types schema where the actual types are defined.
"""

import xmlschema
import os

def debug_common_types_constraints():
    """Debug constraints in the common types schema."""
    
    print("🔍 Debug Common Types Constraints")
    print("=" * 60)
    
    common_types_path = 'resource/21_3_5_distribution_schemas/IATA_OffersAndOrdersCommonTypes.xsd'
    
    print(f"1. Loading common types schema:")
    try:
        schema = xmlschema.XMLSchema(common_types_path)
        print(f"   Types count: {len(schema.types)}")
        print(f"   Target namespace: {schema.target_namespace}")
    except Exception as e:
        print(f"   Failed to load: {e}")
        return
    
    print(f"\n2. Finding types with facet constraints:")
    print("-" * 40)
    
    types_with_facets = []
    constraint_types = set()
    
    for type_name, type_obj in schema.types.items():
        if hasattr(type_obj, 'facets') and type_obj.facets:
            types_with_facets.append((type_name, type_obj))
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                constraint_types.add(local_name)
    
    print(f"   Found {len(types_with_facets)} types with facets")
    print(f"   Constraint types found: {sorted(constraint_types)}")
    
    # Show some examples
    if types_with_facets:
        print(f"\n3. Examples of types with constraints:")
        print("-" * 40)
        
        for i, (type_name, type_obj) in enumerate(types_with_facets[:10]):
            print(f"\n   Type: {type_name}")
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                facet_value = getattr(facet, 'value', facet)
                print(f"     {local_name}: {facet_value}")
    
    print(f"\n4. Looking for specific pattern constraints:")
    print("-" * 40)
    
    pattern_types = []
    for type_name, type_obj in schema.types.items():
        if hasattr(type_obj, 'facets') and type_obj.facets:
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                if local_name == 'pattern':
                    pattern_types.append((type_name, type_obj, facet))
    
    print(f"   Found {len(pattern_types)} types with pattern constraints")
    
    if pattern_types:
        print(f"\n   Pattern examples:")
        for i, (type_name, type_obj, pattern_facet) in enumerate(pattern_types[:10]):
            pattern_value = getattr(pattern_facet, 'value', pattern_facet)
            print(f"     {type_name}: {pattern_value}")
    
    print(f"\n5. Looking for enumeration constraints:")
    print("-" * 40)
    
    enum_types = []
    for type_name, type_obj in schema.types.items():
        if hasattr(type_obj, 'enumeration') and type_obj.enumeration:
            enum_types.append((type_name, type_obj))
        elif hasattr(type_obj, 'facets') and type_obj.facets:
            # Check facets for enumeration
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                if local_name == 'enumeration':
                    enum_types.append((type_name, type_obj))
                    break
    
    print(f"   Found {len(enum_types)} types with enumeration constraints")
    
    if enum_types:
        print(f"\n   Enumeration examples:")
        for i, (type_name, type_obj) in enumerate(enum_types[:5]):
            if hasattr(type_obj, 'enumeration') and type_obj.enumeration:
                enum_values = list(type_obj.enumeration)[:5]
                print(f"     {type_name}: {enum_values}...")
            else:
                print(f"     {type_name}: (has enumeration facets)")
    
    print(f"\n6. Testing constraint extraction on sample types:")
    print("-" * 40)
    
    # Import our constraint extraction method
    from utils.xml_generator import XMLGenerator
    
    # Create a dummy generator to use the extraction method
    main_schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    gen = XMLGenerator(main_schema_path)
    
    # Test on some types with constraints
    test_types = []
    if pattern_types:
        test_types.extend(pattern_types[:3])
    if enum_types:
        test_types.extend([(name, obj, None) for name, obj in enum_types[:3]])
    
    for type_name, type_obj, _ in test_types:
        print(f"\n   Testing: {type_name}")
        try:
            # Test our constraint extraction
            constraints = gen._extract_type_constraints(type_obj)
            print(f"     Extracted constraints: {constraints}")
            
            # Test value generation
            value = gen._generate_value_for_type(type_obj, type_name.split('Type')[0])
            print(f"     Generated value: {repr(value)}")
            
        except Exception as e:
            print(f"     Error: {e}")
    
    print(f"\n7. Summary:")
    print("-" * 40)
    print(f"   Total types: {len(schema.types)}")
    print(f"   Types with facets: {len(types_with_facets)}")
    print(f"   Types with patterns: {len(pattern_types)}")
    print(f"   Types with enumerations: {len(enum_types)}")
    print(f"   All constraint types: {sorted(constraint_types)}")

if __name__ == "__main__":
    debug_common_types_constraints()