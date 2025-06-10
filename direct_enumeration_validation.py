#!/usr/bin/env python3
"""
Direct validation test to count actual enumeration errors.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re

def direct_enumeration_validation():
    """Direct validation test for enumeration errors."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Direct Enumeration Validation Test")
    print("=" * 40)
    
    # Generate XML
    print("1. Generating XML...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"   Generated XML: {len(xml_data)} characters")
    
    # Validate and count enumeration errors specifically
    print("2. Validating XML and counting enumeration errors...")
    
    enumeration_error_count = 0
    total_error_count = 0
    
    try:
        generator.schema.validate(xml_data)
        print("✅ XML is completely valid!")
        return 0
    except xmlschema.XMLSchemaException as e:
        error_text = str(e)
        
        # Count total errors
        total_error_count = error_text.count('failed validating')
        
        # Count enumeration-specific errors
        enumeration_errors = re.findall(r"failed validating '[^']*' with XsdEnumerationFacets", error_text)
        enumeration_error_count = len(enumeration_errors)
        
        # Count empty string enumeration errors specifically
        empty_enum_errors = re.findall(r"failed validating '' with XsdEnumerationFacets", error_text)
        empty_enum_count = len(empty_enum_errors)
        
        print(f"   Total validation errors: {total_error_count}")
        print(f"   Enumeration errors: {enumeration_error_count}")
        print(f"   Empty string enumeration errors: {empty_enum_count}")
        
        if enumeration_error_count > 0:
            print(f"\n3. Sample enumeration errors:")
            # Extract and display first few enumeration errors
            enum_error_pattern = r"failed validating '([^']*)' with XsdEnumerationFacets\(\[([^\]]*)\]\)"
            matches = re.findall(enum_error_pattern, error_text)
            
            for i, (value, enum_list) in enumerate(matches[:5]):
                print(f"   {i+1}. Value: '{value}' | Expected: [{enum_list}]")
                
            if len(matches) > 5:
                print(f"   ... and {len(matches) - 5} more")
        
        return enumeration_error_count

if __name__ == "__main__":
    enum_errors = direct_enumeration_validation()
    
    print(f"\n🎯 Result: {enum_errors} enumeration errors found")
    
    if enum_errors == 0:
        print("🎉 SUCCESS: Zero enumeration errors achieved!")
    else:
        print(f"⚠️  Still need to fix {enum_errors} enumeration errors")