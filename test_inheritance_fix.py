#!/usr/bin/env python3
"""
Test if the inheritance-aware constraint extraction fixes the enum issues.
"""

from utils.xml_generator import XMLGenerator

def test_inheritance_fix():
    """Test if Type classes now inherit constraints from ContentType classes."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Testing Inheritance-Aware Constraint Extraction")
        print("=" * 60)
        
        # Test the problematic Type classes that should inherit from ContentType
        test_types = ['ActionCodeType', 'TaxTypeCodeType', 'BagDisclosureRuleTypeCodeType']
        
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for type_name in test_types:
                    if type_name in imported_schema.types:
                        type_obj = imported_schema.types[type_name]
                        
                        print(f"\n🧪 Testing: {type_name}")
                        print(f"   Type object: {type_obj}")
                        print(f"   Base type: {getattr(type_obj, 'base_type', 'None')}")
                        
                        # Test constraint extraction (should now inherit from base)
                        constraints = generator._extract_type_constraints(type_obj)
                        print(f"   Constraints: {constraints}")
                        
                        # Test generation
                        type_gen = generator.type_factory.create_generator(type_obj, constraints)
                        value = type_gen.generate(type_name, constraints)
                        
                        print(f"   Generator: {type(type_gen).__name__}")
                        print(f"   Generated: '{value}'")
                        
                        if constraints.get('enum_values') and value in constraints['enum_values']:
                            print(f"   ✅ SUCCESS: Generated valid enum value!")
                        elif value == "ABC123":
                            print(f"   ❌ STILL FAILING: Generating fallback string")
                        else:
                            print(f"   ⚠ UNKNOWN: Generated unexpected value")
        
        # Test full XML generation to see overall impact
        print(f"\n🧪 Testing Full XML Generation")
        print("=" * 40)
        
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        # Check for fallback values in enum-like elements
        import re
        fallback_pattern = r'<([^>]*(?:Code|Type)[^>]*)>ABC123</[^>]*>'
        fallback_matches = re.findall(fallback_pattern, xml_data)
        
        if fallback_matches:
            print(f"Found {len(fallback_matches)} elements still using fallback 'ABC123':")
            for match in fallback_matches[:5]:
                clean_match = match.split()[-1] if ' ' in match else match
                clean_match = clean_match.split(':')[-1]
                print(f"   - {clean_match}")
        else:
            print("✅ No 'ABC123' fallbacks found in enum-like elements!")
        
        # Check for empty elements
        empty_pattern = r'<([^>]+)><\/[^>]+>'
        empty_matches = re.findall(empty_pattern, xml_data)
        
        if empty_matches:
            print(f"⚠ Found {len(empty_matches)} empty elements (potential enum issues)")
        else:
            print("✅ No empty elements found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inheritance_fix()