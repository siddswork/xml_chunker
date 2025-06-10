#!/usr/bin/env python3
"""
Test if enumeration values are actually being used in generated XML.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def test_enum_in_xml():
    """Test if enumeration values appear in generated XML and cause validation errors."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Testing Enumeration Values in Generated XML")
        print("=" * 60)
        
        # Generate XML
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        # Search for enumeration values in XML
        enum_values_to_find = ['Add', 'Delete', 'Update', 'D', 'N', 'Other', 'Y', 'Father Surname', 'Mother Surname']
        
        found_enums = []
        for enum_val in enum_values_to_find:
            if enum_val in xml_data:
                found_enums.append(enum_val)
        
        print(f"📊 Enumeration values found in XML: {found_enums}")
        
        if found_enums:
            print("✅ Enumeration values are being generated in XML!")
        else:
            print("❌ No enumeration values found in XML - might not be getting used")
        
        # Check for specific enumeration elements in XML
        enum_elements = ['ActionCode', 'BagRuleCode', 'AddlNameTypeCode']
        
        for elem in enum_elements:
            if elem in xml_data:
                # Extract value from XML (simple regex)
                import re
                pattern = f'<[^>]*{elem}[^>]*>([^<]*)</[^>]*{elem}[^>]*>'
                matches = re.findall(pattern, xml_data)
                if matches:
                    print(f"Element {elem} values in XML: {matches[:3]}...")  # Show first 3
        
        # Test validation for enumeration errors specifically
        print(f"\n🔍 Testing Validation for Enumeration Errors")
        print("=" * 50)
        
        try:
            generator.schema.validate(xml_data)
            print("✅ XML is completely valid!")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Count enumeration-specific errors
            enum_error_patterns = [
                'not in enumeration',
                'is not an element of the enumeration',
                'enumeration',
                'not in facet enumeration'
            ]
            
            enum_errors = 0
            total_errors = error_text.count('failed')
            
            for pattern in enum_error_patterns:
                enum_errors += error_text.lower().count(pattern.lower())
            
            print(f"Total validation errors: {total_errors}")
            print(f"Enumeration-related errors: {enum_errors}")
            
            if enum_errors > 0:
                print(f"\n📋 Sample enumeration errors:")
                lines = error_text.split('\n')
                enum_error_lines = []
                for line in lines:
                    if any(pattern.lower() in line.lower() for pattern in enum_error_patterns):
                        enum_error_lines.append(line.strip())
                        if len(enum_error_lines) >= 3:  # Show first 3
                            break
                
                for i, line in enumerate(enum_error_lines):
                    print(f"  {i+1}. {line[:100]}...")
            else:
                print("✅ No enumeration validation errors found!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enum_in_xml()