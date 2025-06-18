#!/usr/bin/env python3
"""
Test script for the new generation modes functionality.
"""

import os
import sys
from utils.xml_generator import XMLGenerator

def test_generation_modes():
    """Test the different generation modes with a sample XSD."""
    
    # Use a sample XSD file from the resource directory
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    if not os.path.exists(xsd_path):
        print("❌ Sample XSD file not found. Please run this from the project root.")
        assert False, "Sample XSD file not found"
    
    try:
        print("🧪 Testing Generation Modes...")
        print("=" * 50)
        print("📋 Note: This tests the XML generator logic directly.")
        
        # Test 1: Minimalistic mode (current behavior)
        print("\n1️⃣ Testing Minimalistic Mode:")
        generator = XMLGenerator(xsd_path)
        xml_minimal = generator.generate_dummy_xml_with_options(
            generation_mode="Minimalistic"
        )
        print(f"   📊 Size: {len(xml_minimal)} characters")
        print(f"   📄 Lines: {xml_minimal.count(chr(10))}")
        
        # Test 2: Complete mode
        print("\n2️⃣ Testing Complete Mode:")
        generator = XMLGenerator(xsd_path)
        xml_complete = generator.generate_dummy_xml_with_options(
            generation_mode="Complete"
        )
        print(f"   📊 Size: {len(xml_complete)} characters")
        print(f"   📄 Lines: {xml_complete.count(chr(10))}")
        
        # Test 3: Custom mode with selections
        print("\n3️⃣ Testing Custom Mode:")
        generator = XMLGenerator(xsd_path)
        # Simulate some optional element selections
        optional_selections = ["DataLists", "Metadata", "PaymentFunctions"]
        xml_custom = generator.generate_dummy_xml_with_options(
            generation_mode="Custom",
            optional_selections=optional_selections
        )
        print(f"   📊 Size: {len(xml_custom)} characters")
        print(f"   📄 Lines: {xml_custom.count(chr(10))}")
        print(f"   ✅ Selected elements: {optional_selections}")
        
        # Compare results
        print("\n📈 Comparison:")
        print(f"   Minimalistic: {len(xml_minimal):,} chars")
        print(f"   Complete:     {len(xml_complete):,} chars (+{((len(xml_complete)/len(xml_minimal))-1)*100:.1f}%)")
        print(f"   Custom:       {len(xml_custom):,} chars (+{((len(xml_custom)/len(xml_minimal))-1)*100:.1f}%)")
        
        # Check if XMLs are valid (basic check)
        valid_minimal = xml_minimal.startswith('<?xml') and not '<error>' in xml_minimal
        valid_complete = xml_complete.startswith('<?xml') and not '<error>' in xml_complete
        valid_custom = xml_custom.startswith('<?xml') and not '<error>' in xml_custom
        
        print(f"\n✅ Generation Status:")
        print(f"   Minimalistic: {'✅ Valid' if valid_minimal else '❌ Error'}")
        print(f"   Complete:     {'✅ Valid' if valid_complete else '❌ Error'}")
        print(f"   Custom:       {'✅ Valid' if valid_custom else '❌ Error'}")
        
        # Assert all generations are valid
        assert valid_minimal, "Minimalistic generation failed"
        assert valid_complete, "Complete generation failed"  
        assert valid_custom, "Custom generation failed"
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed with error: {e}"

if __name__ == "__main__":
    test_generation_modes()
    print("\n🎉 All tests passed!")
    print("\n💡 Next steps:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload an XSD file")
    print("   3. Try the new generation modes")
    print("   4. In Custom mode, select optional elements in the tree")