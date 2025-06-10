#!/usr/bin/env python3
"""
Find the exact element causing the SuffixName length validation error.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def find_error_element():
    """Find the element causing the string length error."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Generate XML
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        # Validate and get detailed error
        try:
            generator.schema.validate(xml_data)
            print("XML is valid!")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Look for the SuffixName error specifically
            if "SuffixName" in error_text:
                print("🔍 Found SuffixName Error Details:")
                print("=" * 40)
                
                # Split error into lines and find relevant ones
                lines = error_text.split('\n')
                for i, line in enumerate(lines):
                    if 'SuffixName' in line or 'maxLength' in line:
                        print(f"Line {i}: {line}")
                        # Print context around the error
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if j != i:
                                print(f"  {j}: {lines[j]}")
                        break
                
                # Also search in generated XML for SuffixName
                print(f"\n🔍 Searching XML for SuffixName:")
                print("=" * 40)
                xml_lines = xml_data.split('\n')
                for i, line in enumerate(xml_lines):
                    if 'SuffixName' in line:
                        print(f"XML Line {i}: {line.strip()}")
                        break
                        
        print(f"\nXML size: {len(xml_data)} characters")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_error_element()