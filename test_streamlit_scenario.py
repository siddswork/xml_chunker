#!/usr/bin/env python3
"""
Test the XML generation in a scenario similar to Streamlit app usage.
"""

from utils.xml_generator import XMLGenerator

def test_streamlit_scenario():
    """Test XML generation as it would be called from Streamlit."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        print("🔍 Testing Streamlit-like XML Generation")
        print("=" * 50)
        
        # Create generator (as Streamlit would)
        generator = XMLGenerator(schema_path)
        
        # Generate XML with choices (as Streamlit would)
        selected_choices = {"Response": True}
        unbounded_counts = {}
        
        xml_content = generator.generate_dummy_xml_with_choices(
            selected_choices=selected_choices,
            unbounded_counts=unbounded_counts
        )
        
        if xml_content and not xml_content.startswith('<?xml'):
            print(f"❌ Error: {xml_content[:200]}...")
        elif xml_content and '<error>' in xml_content:
            print(f"❌ Error XML: {xml_content[:300]}...")
        else:
            print(f"✅ Success! Generated {len(xml_content)} characters")
            print(f"✅ Valid XML starts with: {xml_content[:100]}...")
            
            # Test if it's valid XML by checking structure
            if xml_content.startswith('<?xml') and '<IATA_OrderViewRS' in xml_content:
                print("✅ XML structure looks correct")
            else:
                print("⚠ XML structure might have issues")
        
    except Exception as e:
        print(f"❌ Exception in Streamlit scenario: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streamlit_scenario()