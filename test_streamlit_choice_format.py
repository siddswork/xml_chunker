#!/usr/bin/env python3
"""
Test XML generation with Streamlit-style choice format to fix display issue.
"""

from utils.xml_generator import XMLGenerator

def test_streamlit_choice_format():
    """Test XML generation with the exact format that Streamlit app uses."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        print("🔍 Testing Streamlit Choice Format")
        print("=" * 50)
        
        generator = XMLGenerator(schema_path)
        
        # Test 1: Streamlit-style complex format (what's actually sent)
        print("1. Testing Streamlit complex format...")
        streamlit_choices = {
            "choice_0": {
                "path": "IATA_OrderViewRS",
                "selected_element": "Response",
                "choice_data": {"some": "metadata"}
            }
        }
        
        xml_content = generator.generate_dummy_xml_with_choices(
            selected_choices=streamlit_choices,
            unbounded_counts={}
        )
        
        if xml_content and xml_content.startswith('<?xml'):
            print(f"   ✅ Generated XML: {len(xml_content)} chars")
            
            # Check if Response choice is being used
            if '<Response>' in xml_content:
                print("   ✅ Response choice correctly selected")
            else:
                print("   ❌ Response choice not found in XML")
                
        elif '<error>' in xml_content:
            print(f"   ❌ Error XML generated: {xml_content[:200]}...")
        else:
            print(f"   ❌ Invalid XML: {xml_content[:100]}...")
        
        # Test 2: Simple format (for comparison)
        print("\n2. Testing simple format (for comparison)...")
        simple_choices = {"Response": True}
        
        xml_content2 = generator.generate_dummy_xml_with_choices(
            selected_choices=simple_choices,
            unbounded_counts={}
        )
        
        if xml_content2 and xml_content2.startswith('<?xml'):
            print(f"   ✅ Generated XML: {len(xml_content2)} chars")
        else:
            print(f"   ❌ Failed: {xml_content2[:100]}...")
        
        # Test 3: Compare results
        print("\n3. Comparing results...")
        if xml_content == xml_content2:
            print("   ✅ Both formats produce identical XML")
        elif len(xml_content) == len(xml_content2):
            print("   ✅ Both formats produce same length XML (probably identical)")
        else:
            print(f"   ⚠ Different results: {len(xml_content)} vs {len(xml_content2)} chars")
        
        # Test 4: Empty/no choices (fallback behavior)
        print("\n4. Testing empty choices (fallback)...")
        xml_content3 = generator.generate_dummy_xml_with_choices(
            selected_choices={},
            unbounded_counts={}
        )
        
        if xml_content3 and xml_content3.startswith('<?xml'):
            print(f"   ✅ Fallback works: {len(xml_content3)} chars")
        else:
            print(f"   ❌ Fallback failed: {xml_content3[:100]}...")
            
        assert xml_content and xml_content.startswith('<?xml'), "Should generate valid XML"
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed with exception: {e}"

if __name__ == "__main__":
    try:
        test_streamlit_choice_format()
        print("\n🎉 Streamlit choice format should work!")
    except AssertionError as e:
        print(f"\n💥 Streamlit choice format still has issues! {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")