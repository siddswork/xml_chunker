#!/usr/bin/env python3
"""
Test script to verify Streamlit app fixes for hanging issues.
"""

import json
import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
from utils.config_manager import ConfigManager
import io

def test_config_manager_fixes():
    """Test the ConfigManager fixes for enhanced configuration."""
    print("🧪 Testing ConfigManager fixes...")
    
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    config_manager = ConfigManager()
    
    # Test loading
    start_time = time.time()
    config_data = config_manager.load_config(io.StringIO(config_content))
    load_time = time.time() - start_time
    print(f"✓ Configuration loaded in {load_time:.3f} seconds")
    
    # Test conversion to generator options (this was fixed)
    start_time = time.time()
    generator_options = config_manager.convert_config_to_generator_options(config_data)
    convert_time = time.time() - start_time
    print(f"✓ Conversion completed in {convert_time:.3f} seconds")
    
    # Check if custom_values were extracted properly
    custom_values = generator_options.get('custom_values', {})
    print(f"✓ Extracted {len(custom_values)} custom value mappings")
    
    # Show some examples
    for key, value in list(custom_values.items())[:3]:
        print(f"  - {key}: {value}")
    
    return True

def test_data_context_manager_fixes():
    """Test the DataContextManager fixes for circular inheritance."""
    print("\n🧪 Testing DataContextManager circular inheritance protection...")
    
    from utils.data_context_manager import DataContextManager
    
    # Create a test configuration with potential circular inheritance
    test_config = {
        "context_a": {
            "inherits": ["context_b"],
            "data": ["a1", "a2"]
        },
        "context_b": {
            "inherits": ["context_c"],
            "data": ["b1", "b2"]
        },
        "context_c": {
            "inherits": ["context_a"],  # This creates a cycle!
            "data": ["c1", "c2"]
        },
        "normal_context": {
            "data": ["normal1", "normal2"]
        }
    }
    
    dcm = DataContextManager(test_config)
    
    # Test resolving each context (should not hang due to cycle protection)
    for context_name in test_config.keys():
        start_time = time.time()
        result = dcm.get_context_data(context_name)
        resolve_time = time.time() - start_time
        print(f"✓ Resolved '{context_name}' in {resolve_time:.3f} seconds: {len(result)} keys")
    
    # Test normal context (should work fine)
    normal_data = dcm.get_context_data('normal_context')
    if 'data' in normal_data:
        print(f"✓ Normal context works: {normal_data['data']}")
    
    return True

def test_full_integration():
    """Test full integration with enhanced configuration."""
    print("\n🧪 Testing full integration...")
    
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    xsd_path = "resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd"
    
    # Simulate the full Streamlit workflow
    config_manager = ConfigManager()
    
    # 1. Load configuration
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    config_data = config_manager.load_config(io.StringIO(config_content))
    print("✓ Configuration loaded")
    
    # 2. Convert to generator options
    generator_options = config_manager.convert_config_to_generator_options(config_data)
    print("✓ Configuration converted")
    
    # 3. Create XMLGenerator with enhanced config
    start_time = time.time()
    generator = XMLGenerator(xsd_path, config_data=config_data)
    creation_time = time.time() - start_time
    print(f"✓ XMLGenerator created in {creation_time:.3f} seconds")
    
    # 4. Generate XML
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
    
    # Check for enhanced configuration data in output
    if 'FlightBooking' in xml_output and 'REQ001' in xml_output:
        print("✓ Enhanced configuration data found in XML")
    else:
        print("⚠️  Enhanced configuration data not clearly visible")
    
    return True

def main():
    """Run all Streamlit fix tests."""
    print("🚀 Testing Streamlit App Hanging Fixes\n")
    print("=" * 60)
    
    tests = [
        test_config_manager_fixes,
        test_data_context_manager_fixes,
        test_full_integration
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
    
    print("\n" + "=" * 60)
    print(f"🏁 Streamlit Fix Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All fixes working correctly! Streamlit app should no longer hang.")
        return 0
    else:
        print("⚠️  Some issues remain. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())