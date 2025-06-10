#!/usr/bin/env python3
"""
Access the imported common types schema to find SupplementNameType constraints.
"""

from utils.xml_generator import XMLGenerator

def access_imported_types():
    """Access the imported schema to find type constraints."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Get the imported Common Types schema
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                print(f"🔍 Found Common Types Schema: {imported_schema}")
                print(f"Target namespace: {imported_schema.target_namespace}")
                
                # Look for SupplementNameType
                if 'SupplementNameType' in imported_schema.types:
                    supplement_type = imported_schema.types['SupplementNameType']
                    print(f"\n✅ Found SupplementNameType: {supplement_type}")
                    print(f"Facets: {supplement_type.facets}")
                    
                    # Test constraint extraction
                    constraints = generator._extract_type_constraints(supplement_type)
                    print(f"Extracted constraints: {constraints}")
                    
                    # Test generation
                    type_gen = generator.type_factory.create_generator(supplement_type, constraints)
                    value = type_gen.generate("SuffixName", constraints)
                    print(f"Generated value: '{value}' (length: {len(value)})")
                    
                    if len(value) <= 16:
                        print("✅ Constraint is being respected!")
                    else:
                        print("❌ Constraint is NOT being respected!")
                        
                    return
                        
                # List available types in Common Types schema
                print(f"\nAvailable types in Common Types schema:")
                type_names = list(imported_schema.types.keys())
                print(f"Total types: {len(type_names)}")
                for i, type_name in enumerate(type_names[:10]):
                    print(f"  {i+1}. {type_name}")
                if len(type_names) > 10:
                    print(f"  ... and {len(type_names) - 10} more")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    access_imported_types()