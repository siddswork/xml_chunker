#!/usr/bin/env python3
"""
Debug the 'NoneType is not iterable' error in XML generation.
"""

from utils.xml_generator import XMLGenerator
import traceback

def debug_none_error():
    """Debug the None type iteration error."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Debugging None Type Error")
        print("=" * 50)
        
        # Try to generate XML and catch the specific error
        print("Attempting XML generation...")
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        if xml_data and "error" in xml_data.lower():
            print(f"❌ Error XML generated: {xml_data[:500]}...")
        else:
            print(f"✅ Success! Generated {len(xml_data)} characters")
            print(f"Preview: {xml_data[:200]}...")
            
    except Exception as e:
        print(f"❌ Exception caught: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        # Check if it's the specific NoneType error
        if "NoneType" in str(e) and "iterable" in str(e):
            print("\n🎯 This is the NoneType iteration error!")
            print("This usually happens when:")
            print("1. A variable is None but code tries to iterate over it")
            print("2. A dictionary/list lookup returns None")
            print("3. An XSD element/type attribute is unexpectedly None")

if __name__ == "__main__":
    debug_none_error()