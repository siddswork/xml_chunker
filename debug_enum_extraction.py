#!/usr/bin/env python3
"""
Debug why enumeration constraint extraction is not finding real enum values.
"""

from utils.xml_generator import XMLGenerator

def debug_enum_extraction():
    """Debug enumeration constraint extraction for specific types."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Debugging Enumeration Constraint Extraction")
        print("=" * 60)
        
        # Test specific enumeration types we found in XSD
        test_types = ['ActionCodeContentType', 'BagRuleCodeContentType', 'AddlNameTypeCodeContentType']
        
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for type_name in test_types:
                    if type_name in imported_schema.types:
                        type_obj = imported_schema.types[type_name]
                        
                        print(f"\n🔍 Testing: {type_name}")
                        print(f"Type object: {type_obj}")
                        print(f"Has facets: {hasattr(type_obj, 'facets')}")
                        
                        if hasattr(type_obj, 'facets'):
                            print(f"Facets dict: {type_obj.facets}")
                            print(f"Facets keys: {list(type_obj.facets.keys())}")
                            
                            # Debug each facet
                            for facet_name, facet in type_obj.facets.items():
                                print(f"  Facet: {facet_name} -> {facet}")
                                print(f"  Facet value: {getattr(facet, 'value', 'NO VALUE')}")
                                
                                # Check if it's enumeration
                                if facet_name and 'enumeration' in str(facet_name).lower():
                                    print(f"  ✅ This is an enumeration facet!")
                        
                        # Test our constraint extraction
                        print(f"\n🧪 Testing constraint extraction:")
                        constraints = generator._extract_type_constraints(type_obj)
                        print(f"Extracted constraints: {constraints}")
                        
                        # Test type generation
                        print(f"\n🧪 Testing type generation:")
                        type_gen = generator.type_factory.create_generator(type_obj, constraints)
                        print(f"Generator type: {type(type_gen).__name__}")
                        
                        generated_value = type_gen.generate(type_name, constraints)
                        print(f"Generated value: '{generated_value}'")
                        
                        print("-" * 50)
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_enum_extraction()