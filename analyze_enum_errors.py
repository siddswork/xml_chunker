#!/usr/bin/env python3
"""
Analyze current enumeration errors to understand patterns and improve detection.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re

def analyze_enum_errors():
    """Analyze enumeration validation errors to understand what needs fixing."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Generate XML with Response choice
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        print(f"🔍 Enumeration Error Analysis")
        print("=" * 50)
        print(f"Generated XML: {len(xml_data)} bytes")
        
        # Validate and extract enumeration errors
        try:
            generator.schema.validate(xml_data)
            print("✅ XML is valid!")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Extract enumeration-specific errors
            enum_errors = []
            lines = error_text.split('\n')
            
            for i, line in enumerate(lines):
                if 'not in enumeration' in line.lower() or 'enumeration' in line.lower():
                    # Capture context around enumeration errors
                    context = []
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        context.append(f"  {j}: {lines[j]}")
                    enum_errors.append('\n'.join(context))
            
            print(f"\n📊 Found {len(enum_errors)} enumeration error patterns:")
            print("=" * 60)
            
            for i, error in enumerate(enum_errors[:5]):  # Show first 5
                print(f"\nEnumeration Error #{i+1}:")
                print(error)
                print("-" * 40)
        
        # Also analyze XSD types to find enumeration definitions
        print(f"\n🔍 XSD Enumeration Type Analysis")
        print("=" * 50)
        
        # Check main schema
        enum_types = []
        for type_name, type_obj in generator.schema.types.items():
            if hasattr(type_obj, 'facets') and type_obj.facets:
                for facet_name, facet in type_obj.facets.items():
                    if facet_name and 'enumeration' in str(facet_name).lower():
                        enum_types.append((type_name, type_obj))
                        break
        
        # Check imported schemas (Common Types)
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for type_name, type_obj in imported_schema.types.items():
                    if hasattr(type_obj, 'facets') and type_obj.facets:
                        for facet_name, facet in type_obj.facets.items():
                            if facet_name and 'enumeration' in str(facet_name).lower():
                                enum_types.append((f"cns:{type_name}", type_obj))
                                break
        
        print(f"Found {len(enum_types)} types with enumeration facets:")
        
        for i, (type_name, type_obj) in enumerate(enum_types[:10]):  # Show first 10
            print(f"\n{i+1}. {type_name}:")
            
            # Extract enumeration values
            enum_values = []
            if hasattr(type_obj, 'facets') and type_obj.facets:
                for facet_name, facet in type_obj.facets.items():
                    if facet_name and 'enumeration' in str(facet_name).lower():
                        enum_values.append(str(facet.value))
            
            print(f"   Enum values: {enum_values[:5]}{'...' if len(enum_values) > 5 else ''}")
            print(f"   Total values: {len(enum_values)}")
            
            # Test current constraint extraction
            constraints = generator._extract_type_constraints(type_obj)
            extracted_enums = constraints.get('enum_values', [])
            print(f"   Extracted by current code: {extracted_enums}")
            
            if enum_values and not extracted_enums:
                print(f"   ❌ Current code missing enumeration values!")
            elif enum_values and extracted_enums:
                print(f"   ✅ Current code found enumeration values")
                
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_enum_errors()