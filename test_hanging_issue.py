#!/usr/bin/env python3
"""
Test script to reproduce and debug hanging issues with enhanced configuration.
"""

import json
import sys
import os
import time
from pathlib import Path
import signal

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
from utils.config_manager import ConfigManager
import io

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_config_loading_speed():
    """Test if configuration loading itself is fast."""
    print("🧪 Testing configuration loading speed...")
    start_time = time.time()
    
    try:
        config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
        
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        config_manager = ConfigManager()
        config_data = config_manager.load_config(io.StringIO(config_content))
        
        load_time = time.time() - start_time
        print(f"✓ Configuration loaded in {load_time:.3f} seconds")
        
        # Test conversion to generator options
        start_time = time.time()
        generator_options = config_manager.convert_config_to_generator_options(config_data)
        convert_time = time.time() - start_time
        print(f"✓ Conversion completed in {convert_time:.3f} seconds")
        
        return config_data, generator_options
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return None, None

def test_xml_generation_with_timeout():
    """Test XML generation with a timeout to detect hanging."""
    print("\n🧪 Testing XML generation with timeout...")
    
    config_data, generator_options = test_config_loading_speed()
    if not config_data:
        return False
    
    xsd_path = "resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd"
    
    try:
        # Set up timeout (30 seconds)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        start_time = time.time()
        
        # Create XMLGenerator with enhanced configuration
        print("Creating XMLGenerator...")
        generator = XMLGenerator(xsd_path, config_data=config_data)
        creation_time = time.time() - start_time
        print(f"✓ XMLGenerator created in {creation_time:.3f} seconds")
        
        # Generate XML
        print("Generating XML...")
        generation_start = time.time()
        xml_output = generator.generate_dummy_xml_with_options(
            generation_mode="Complete",
            selected_choices={},
            unbounded_counts={},
            optional_selections=[],
            custom_values={}
        )
        generation_time = time.time() - generation_start
        
        # Cancel timeout
        signal.alarm(0)
        
        total_time = time.time() - start_time
        print(f"✓ XML generated successfully in {generation_time:.3f} seconds")
        print(f"✓ Total time: {total_time:.3f} seconds")
        print(f"✓ XML length: {len(xml_output)} characters")
        
        return True
        
    except TimeoutError:
        print("❌ XML generation timed out after 30 seconds - likely hanging!")
        return False
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print(f"❌ XML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_initialization_speed():
    """Test individual component initialization speed."""
    print("\n🧪 Testing component initialization speed...")
    
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    config_manager = ConfigManager()
    config_data = config_manager.load_config(io.StringIO(config_content))
    
    # Test DataContextManager
    start_time = time.time()
    from utils.data_context_manager import DataContextManager
    dcm = DataContextManager(config_data.get('data_contexts', {}))
    dcm_time = time.time() - start_time
    print(f"✓ DataContextManager initialized in {dcm_time:.3f} seconds")
    
    # Test SmartRelationshipsEngine
    start_time = time.time()
    from utils.smart_relationships_engine import SmartRelationshipsEngine
    sre = SmartRelationshipsEngine(config_data.get('smart_relationships', {}), dcm)
    sre_time = time.time() - start_time
    print(f"✓ SmartRelationshipsEngine initialized in {sre_time:.3f} seconds")
    
    # Test TemplateProcessor
    start_time = time.time()
    from utils.template_processor import TemplateProcessor
    tp = TemplateProcessor(dcm, config_data.get('generation_settings', {}).get('deterministic_seed'))
    tp_time = time.time() - start_time
    print(f"✓ TemplateProcessor initialized in {tp_time:.3f} seconds")
    
    total_component_time = dcm_time + sre_time + tp_time
    print(f"✓ Total component initialization: {total_component_time:.3f} seconds")
    
    return True

def test_data_resolution():
    """Test data resolution for potential infinite loops."""
    print("\n🧪 Testing data resolution...")
    
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    config_manager = ConfigManager()
    config_data = config_manager.load_config(io.StringIO(config_content))
    
    from utils.data_context_manager import DataContextManager
    dcm = DataContextManager(config_data.get('data_contexts', {}))
    
    # Test various data resolutions
    test_refs = [
        "global.request_targets",
        "global.airlines",
        "property_keys",
        "property_values"
    ]
    
    for ref in test_refs:
        start_time = time.time()
        result = dcm.resolve_data_reference(ref)
        resolve_time = time.time() - start_time
        print(f"✓ Resolved '{ref}' in {resolve_time:.3f} seconds: {result[:50] if isinstance(result, list) else result}")
    
    return True

def main():
    """Run all hanging issue tests."""
    print("🚀 Testing for Hanging Issues in Enhanced Configuration\n")
    print("=" * 60)
    
    tests = [
        test_config_loading_speed,
        test_component_initialization_speed,
        test_data_resolution,
        test_xml_generation_with_timeout
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🏁 Hanging Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 No hanging issues detected!")
        return 0
    else:
        print("⚠️  Potential hanging issues found. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())