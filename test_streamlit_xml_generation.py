#!/usr/bin/env python3
"""
Test XML generation as it would be called from Streamlit app to identify issues.
"""

from utils.xml_generator import XMLGenerator
import traceback

def test_streamlit_xml_generation():
    """Test XML generation exactly as Streamlit app would call it."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        print("🔍 Testing Streamlit XML Generation Flow")
        print("=" * 60)
        
        # Test 1: Basic generator creation (as Streamlit would)
        print("1. Creating XMLGenerator...")
        generator = XMLGenerator(schema_path)
        print("   ✅ Generator created successfully")
        
        # Test 2: Choice-based generation (typical Streamlit scenario)
        print("\n2. Testing choice-based generation...")
        selected_choices = {"Response": True}
        unbounded_counts = {}
        
        try:
            xml_content = generator.generate_dummy_xml_with_choices(
                selected_choices=selected_choices,
                unbounded_counts=unbounded_counts
            )
            
            print(f"   ✅ XML generated: {len(xml_content)} characters")
            
            # Check for error XML
            if xml_content.startswith('<?xml') and '<error>' in xml_content:
                print("   ❌ ERROR XML GENERATED!")
                print(f"   Error content: {xml_content[:300]}...")
                assert False, "Error XML was generated instead of valid content"
            elif not xml_content.startswith('<?xml'):
                print("   ❌ INVALID XML FORMAT!")
                print(f"   Content preview: {xml_content[:200]}...")
                assert False, f"Invalid XML format: {xml_content[:200] if xml_content else 'No content'}"
            else:
                print("   ✅ Valid XML format detected")
                
        except Exception as gen_error:
            print(f"   ❌ Generation failed: {gen_error}")
            traceback.print_exc()
            assert False, f"Generation failed: {gen_error}"
        
        # Test 3: Check XML structure (what Streamlit would display)
        print("\n3. Testing XML structure...")
        
        # Check for proper root element
        if '<IATA_OrderViewRS' in xml_content:
            print("   ✅ Proper IATA root element found")
        else:
            print("   ❌ Missing IATA root element")
            
        # Check for namespace declarations
        if 'xmlns:cns=' in xml_content:
            print("   ✅ Namespace declarations present")
        else:
            print("   ❌ Missing namespace declarations")
            
        # Check for Response choice content
        if '<Response>' in xml_content or 'Response' in xml_content:
            print("   ✅ Response choice content present")
        else:
            print("   ❌ Missing Response choice content")
            
        # Test 4: Streamlit display simulation
        print("\n4. Simulating Streamlit display...")
        
        # This is what Streamlit typically does - encode and display
        try:
            # Test encoding (Streamlit uses UTF-8)
            encoded = xml_content.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            if len(decoded) == len(xml_content):
                print("   ✅ Encoding/decoding works correctly")
            else:
                print("   ❌ Encoding/decoding issue detected")
                
        except Exception as encoding_error:
            print(f"   ❌ Encoding error: {encoding_error}")
            
        # Test 5: Check for any invisible characters or issues
        print("\n5. Checking for display issues...")
        
        # Check for null characters or other problematic content
        if '\x00' in xml_content:
            print("   ❌ Null characters found (could break display)")
        else:
            print("   ✅ No null characters")
            
        # Check for extremely long lines (could break display)
        lines = xml_content.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        if max_line_length > 10000:
            print(f"   ⚠ Very long lines detected (max: {max_line_length} chars)")
        else:
            print(f"   ✅ Reasonable line lengths (max: {max_line_length} chars)")
            
        # Test 6: Return status for Streamlit
        print(f"\n6. Final validation...")
        
        if (xml_content and 
            xml_content.startswith('<?xml') and 
            '<IATA_OrderViewRS' in xml_content and
            not '<error>' in xml_content):
            print("   ✅ XML should display correctly in Streamlit")
            assert True  # Test passed
        else:
            print("   ❌ XML may not display correctly in Streamlit")
            assert False, "XML may not display correctly in Streamlit"
            
    except Exception as e:
        print(f"❌ Major error in XML generation: {e}")
        traceback.print_exc()
        assert False, f"Major error in XML generation: {e}"

if __name__ == "__main__":
    try:
        test_streamlit_xml_generation()
        print("\n🎉 XML generation should work in Streamlit!")
    except AssertionError as e:
        print(f"\n💥 XML generation has issues that may affect Streamlit display! {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")