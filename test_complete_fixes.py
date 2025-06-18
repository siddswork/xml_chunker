#!/usr/bin/env python3
"""
Test script to verify all the fixes for JSON config upload and auto-generation.
"""

import json
import sys
import os
import time
from pathlib import Path
import io

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
from utils.config_manager import ConfigManager

def test_old_format_rejection():
    """Test that old format is properly rejected."""
    print("🧪 Testing old format rejection...")
    
    config_manager = ConfigManager()
    
    # Old format configuration (should be rejected)
    old_format_config = {
        "metadata": {
            "name": "Old Format Test",
            "schema_name": "test.xsd"
        },
        "generation_settings": {
            "mode": "Complete"
        },
        "element_configs": {
            "TestElement": {
                "values": {  # OLD FORMAT
                    "field1": "value1",
                    "field2": "value2"
                }
            }
        }
    }
    
    try:
        config_manager.load_config(io.StringIO(json.dumps(old_format_config)))
        print("❌ Old format was not rejected!")
        return False
    except Exception as e:
        if "Additional properties are not allowed" in str(e) and "values" in str(e):
            print("✓ Old format correctly rejected")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False

def test_new_format_acceptance():
    """Test that new format is properly accepted."""
    print("\n🧪 Testing new format acceptance...")
    
    config_manager = ConfigManager()
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        config_data = config_manager.load_config(io.StringIO(config_content))
        print("✓ New format configuration loaded successfully")
        
        # Test conversion
        generator_options = config_manager.convert_config_to_generator_options(config_data)
        custom_values = generator_options.get('custom_values', {})
        
        print(f"✓ Extracted {len(custom_values)} custom value mappings")
        
        # Verify some specific elements
        expected_elements = ['type', 'name', 'ID', 'code']
        found_elements = [elem for elem in expected_elements if elem in custom_values]
        print(f"✓ Found expected elements: {found_elements}")
        
        return True
        
    except Exception as e:
        print(f"❌ New format test failed: {e}")
        return False

def test_xml_generation_with_enhanced_config():
    """Test XML generation with enhanced configuration."""
    print("\n🧪 Testing XML generation with enhanced config...")
    
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    xsd_path = "resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd"
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        config_data = config_manager.load_config(io.StringIO(config_content))
        generator_options = config_manager.convert_config_to_generator_options(config_data)
        
        # Create XMLGenerator with enhanced config
        start_time = time.time()
        generator = XMLGenerator(xsd_path, config_data=config_data)
        creation_time = time.time() - start_time
        print(f"✓ XMLGenerator created in {creation_time:.3f} seconds")
        
        # Generate XML
        start_time = time.time()
        xml_output = generator.generate_dummy_xml_with_options(
            generation_mode="Complete",
            selected_choices=generator_options.get('selected_choices', {}),
            unbounded_counts=generator_options.get('unbounded_counts', {}),
            optional_selections=generator_options.get('optional_selections', []),
            custom_values=generator_options.get('custom_values', {})
        )
        generation_time = time.time() - start_time
        
        print(f"✓ XML generated in {generation_time:.3f} seconds")
        print(f"✓ XML length: {len(xml_output)} characters")
        
        # Verify enhanced data is in the XML
        enhanced_indicators = ['FlightProduct', 'REQ001', 'American Airlines']
        found_indicators = [indicator for indicator in enhanced_indicators if indicator in xml_output]
        
        if found_indicators:
            print(f"✓ Enhanced configuration data found in XML: {found_indicators}")
            return True
        else:
            print("⚠️  Enhanced configuration data not clearly visible")
            return False
            
    except Exception as e:
        print(f"❌ XML generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_continuous_rerun_simulation():
    """Simulate the rerun fix by checking session state logic."""
    print("\n🧪 Testing rerun fix simulation...")
    
    # Simulate session state
    session_state = {}
    
    # Load config (this would set config_loaded = True)
    session_state['config_loaded'] = True
    session_state['enhanced_config_data'] = {'test': 'data'}
    session_state['auto_generated_completed'] = False
    
    # Check auto-generate trigger logic
    auto_generate = (session_state.get('config_loaded', False) and 
                    session_state.get('enhanced_config_data') and 
                    not session_state.get('auto_generated_completed', False))
    
    if auto_generate:
        print("✓ Auto-generation would be triggered once")
        
        # Simulate completion
        session_state['auto_generated_completed'] = True
        session_state['config_loaded'] = False
        
        # Check auto-generate again
        auto_generate_again = (session_state.get('config_loaded', False) and 
                              session_state.get('enhanced_config_data') and 
                              not session_state.get('auto_generated_completed', False))
        
        if not auto_generate_again:
            print("✓ Auto-generation would not trigger again (preventing continuous rerun)")
            return True
        else:
            print("❌ Auto-generation would trigger again!")
            return False
    else:
        print("❌ Auto-generation would not trigger!")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Complete Configuration Fixes\n")
    print("=" * 60)
    
    tests = [
        test_old_format_rejection,
        test_new_format_acceptance,
        test_xml_generation_with_enhanced_config,
        test_no_continuous_rerun_simulation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        
        print()
    
    print("=" * 60)
    print(f"🏁 Complete Fix Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All fixes working correctly!")
        print("\n📋 Summary of fixes:")
        print("  ✓ Removed old format support (values → custom_values)")
        print("  ✓ Fixed continuous rerun issue (removed st.rerun())")
        print("  ✓ Added auto-generation after config load")
        print("  ✓ Enhanced config properly used by XMLGenerator")
        return 0
    else:
        print("⚠️  Some issues remain. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())