#!/usr/bin/env python3
"""
Full simulation of Streamlit app XML generation flow to ensure display works.
"""

from utils.xml_generator import XMLGenerator
import tempfile
import os

def simulate_streamlit_flow():
    """Simulate the exact flow that happens in Streamlit app."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        print("🔍 Full Streamlit App Flow Simulation")
        print("=" * 60)
        
        # Step 1: Schema upload simulation
        print("1. Simulating schema upload...")
        with open(schema_path, 'rb') as f:
            file_content = f.read()
        
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "IATA_OrderViewRS.xsd")
        
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)
        
        print(f"   ✅ Temp file created: {temp_file_path}")
        
        # Step 2: Schema analysis (simulated)
        print("\n2. Simulating schema analysis...")
        # This would normally be done by analyze_xsd_schema function
        print("   ✅ Schema analysis completed (simulated)")
        
        # Step 3: User selections (typical Streamlit format)
        print("\n3. Simulating user choice selections...")
        selected_choices = {
            "choice_0": {
                "path": "IATA_OrderViewRS",
                "selected_element": "Response",
                "choice_data": {"path": "IATA_OrderViewRS", "elements": []}
            }
        }
        unbounded_counts = {}
        
        print(f"   Selected choices: {selected_choices}")
        
        # Step 4: XML generation (exact Streamlit call)
        print("\n4. Generating XML (exact Streamlit method)...")
        
        # This simulates the generate_xml_from_xsd function
        generator = XMLGenerator(temp_file_path)
        
        if selected_choices or unbounded_counts:
            xml_content = generator.generate_dummy_xml_with_choices(selected_choices, unbounded_counts)
        else:
            xml_content = generator.generate_dummy_xml()
        
        print(f"   ✅ XML generated: {len(xml_content)} characters")
        
        # Step 5: Streamlit session state simulation
        print("\n5. Simulating Streamlit session state...")
        session_state = {
            'generated_xml': xml_content,
            'temp_file_path': temp_file_path,
            'uploaded_file_name': 'IATA_OrderViewRS.xsd'
        }
        
        # Step 6: Display logic simulation
        print("\n6. Simulating Streamlit display logic...")
        
        if 'generated_xml' in session_state and session_state['generated_xml']:
            xml_to_display = session_state['generated_xml']
            
            print(f"   ✅ XML ready for display: {len(xml_to_display)} chars")
            print(f"   ✅ XML starts with: {xml_to_display[:50]}...")
            
            # Check what Streamlit st.code() would receive
            if xml_to_display and xml_to_display.strip():
                print("   ✅ st.code() would receive non-empty content")
                
                # Check for problematic content
                if '<error>' in xml_to_display:
                    print("   ❌ Error XML detected - this would show errors")
                    print(f"   Error content: {xml_to_display[:200]}...")
                    return False
                elif xml_to_display.startswith('<?xml'):
                    print("   ✅ Valid XML format - should display correctly")
                    return True
                else:
                    print("   ❌ Invalid XML format detected")
                    return False
            else:
                print("   ❌ Empty or None XML content - Streamlit would show nothing")
                return False
        else:
            print("   ❌ No XML in session state - Streamlit would show nothing")
            return False
        
    except Exception as e:
        print(f"❌ Error in simulation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    success = simulate_streamlit_flow()
    if success:
        print("\n🎉 Streamlit app should display XML correctly!")
    else:
        print("\n💥 Streamlit app will have display issues!")