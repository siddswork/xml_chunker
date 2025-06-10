#!/usr/bin/env python3
"""
Find enumeration types with multiple values and test enumeration error generation.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def find_real_enums():
    """Find enumeration types with multiple actual values."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Finding Real Enumeration Types")
        print("=" * 50)
        
        # Check imported schemas (Common Types) for multi-value enums
        multi_value_enums = []
        
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for type_name, type_obj in imported_schema.types.items():
                    if hasattr(type_obj, 'facets') and type_obj.facets:
                        enum_values = []
                        for facet_name, facet in type_obj.facets.items():
                            if facet_name and 'enumeration' in str(facet_name).lower():
                                enum_values.append(str(facet.value))
                        
                        # Only include types with multiple real enum values (not just 'None')
                        if len(enum_values) > 1 or (len(enum_values) == 1 and enum_values[0] != 'None'):
                            multi_value_enums.append((type_name, type_obj, enum_values))
        
        print(f"Found {len(multi_value_enums)} types with real enumeration values:")
        
        for i, (type_name, type_obj, enum_values) in enumerate(multi_value_enums[:15]):
            print(f"\n{i+1}. {type_name}:")
            print(f"   Values: {enum_values}")
            
            # Test current generation
            constraints = generator._extract_type_constraints(type_obj)
            type_gen = generator.type_factory.create_generator(type_obj, constraints)
            generated_value = type_gen.generate(type_name, constraints)
            
            print(f"   Generated: '{generated_value}'")
            
            # Check if generated value is in enum list
            if generated_value in enum_values:
                print(f"   ✅ Generated value is valid")
            else:
                print(f"   ❌ Generated value NOT in enum list!")
                print(f"   Should be one of: {enum_values}")
        
        # Test by generating XML and checking for actual enum errors
        print(f"\n🔍 Testing for Actual Enumeration Errors")
        print("=" * 50)
        
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        try:
            generator.schema.validate(xml_data)
            print("✅ No validation errors found")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Look for specific enumeration error patterns
            enum_error_count = 0
            lines = error_text.split('\n')
            
            for line in lines:
                if 'not in enumeration' in line.lower():
                    enum_error_count += 1
                    print(f"Enum error: {line[:100]}...")
                    if enum_error_count >= 5:  # Show first 5
                        break
            
            print(f"Total enumeration errors found: {enum_error_count}")
            
            # Count total errors for context
            total_errors = error_text.count('failed')
            print(f"Total validation errors: {total_errors}")
            print(f"Enumeration errors: {enum_error_count} ({enum_error_count/total_errors*100:.1f}%)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_real_enums()