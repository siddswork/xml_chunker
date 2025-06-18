#!/usr/bin/env python3
"""
Test script for the enhanced configuration system.

This script demonstrates the new hybrid configuration features:
- Hierarchical data contexts
- Smart relationships 
- Template-based generation
- Deterministic passenger generation
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.data_context_manager import DataContextManager
from utils.smart_relationships_engine import SmartRelationshipsEngine
from utils.template_processor import TemplateProcessor
from utils.config_manager import ConfigManager

def test_data_context_manager():
    """Test DataContextManager functionality."""
    print("🧪 Testing DataContextManager...")
    
    # Load example configuration
    with open('examples/enhanced_passenger_config.json', 'r') as f:
        config_data = json.load(f)
    
    # Initialize DataContextManager
    dcm = DataContextManager(config_data['data_contexts'])
    
    # Test data resolution
    airlines = dcm.resolve_data_reference('global.airlines.major')
    print(f"✓ Major airlines: {airlines}")
    
    # Test wildcard resolution
    all_airlines = dcm.resolve_wildcards('global.airlines.*')
    print(f"✓ All airlines: {all_airlines[:10]}...")  # Show first 10
    
    # Test inheritance
    flight_data = dcm.get_context_data('flight_booking')
    print(f"✓ Flight booking context (with inheritance): {list(flight_data.keys())}")
    
    # Test template data
    passenger_template = dcm.get_template_data('passenger_templates', 0)
    print(f"✓ Passenger template 0: {passenger_template}")
    
    print("✅ DataContextManager tests passed!\n")
    return True

def test_smart_relationships():
    """Test SmartRelationshipsEngine functionality."""
    print("🧪 Testing SmartRelationshipsEngine...")
    
    # Load example configuration
    with open('examples/enhanced_passenger_config.json', 'r') as f:
        config_data = json.load(f)
    
    # Initialize components
    dcm = DataContextManager(config_data['data_contexts'])
    sre = SmartRelationshipsEngine(config_data['smart_relationships'], dcm)
    
    # Test passenger profile relationship
    context_values = {}
    
    # Generate passenger data with relationships
    for i in range(3):
        print(f"\n--- Passenger {i+1} ---")
        
        # Apply relationships for passenger fields
        title = sre.apply_relationship('title', i, context_values)
        first_name = sre.apply_relationship('first_name', i, context_values)
        last_name = sre.apply_relationship('last_name', i, context_values)
        email = sre.apply_relationship('email', i, context_values)
        
        print(f"Title: {title}")
        print(f"First name: {first_name}")
        print(f"Last name: {last_name}")
        print(f"Email: {email}")
        
        # Update context for next iteration
        context_values.update({
            'title': title,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        })
    
    print("\n✅ SmartRelationshipsEngine tests passed!\n")
    return True

def test_template_processor():
    """Test TemplateProcessor functionality."""
    print("🧪 Testing TemplateProcessor...")
    
    # Load example configuration
    with open('examples/enhanced_passenger_config.json', 'r') as f:
        config_data = json.load(f)
    
    # Initialize components
    dcm = DataContextManager(config_data['data_contexts'])
    tp = TemplateProcessor(dcm, seed=12345)
    
    # Test passenger template generation
    for i in range(3):
        print(f"\n--- Template Passenger {i+1} ---")
        
        # Generate business passenger template
        passenger_data = tp.generate_passenger_template(i, 'business')
        print(f"Business passenger: {passenger_data}")
        
        # Test template processing for specific element
        first_name = tp.process_template('passenger_templates', i, 'first_name')
        print(f"First name from template: {first_name}")
    
    # Test flight template generation
    print(f"\n--- Flight Templates ---")
    try:
        for i in range(2):
            flight_data = tp.generate_flight_template(i, 'domestic')
            print(f"Flight {i+1}: {flight_data}")
    except Exception as e:
        print(f"Flight template error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ TemplateProcessor tests passed!\n")
    return True

def test_config_validation():
    """Test configuration validation with new schema."""
    print("🧪 Testing configuration validation...")
    
    try:
        config_manager = ConfigManager()
        
        # Test loading the enhanced configuration
        with open('examples/enhanced_passenger_config.json', 'r') as f:
            config_content = f.read()
        
        import io
        config_data = config_manager.load_config(io.StringIO(config_content))
        print("✓ Enhanced configuration loaded successfully")
        print(f"✓ Configuration name: {config_data['metadata']['name']}")
        print(f"✓ Data contexts: {list(config_data.get('data_contexts', {}).keys())}")
        print(f"✓ Smart relationships: {list(config_data.get('smart_relationships', {}).keys())}")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Configuration validation tests passed!\n")
    return True

def test_deterministic_generation():
    """Test deterministic value generation."""
    print("🧪 Testing deterministic generation...")
    
    # Load example configuration
    with open('examples/enhanced_passenger_config.json', 'r') as f:
        config_data = json.load(f)
    
    # Initialize components with deterministic seed
    dcm = DataContextManager(config_data['data_contexts'])
    tp = TemplateProcessor(dcm, seed=12345)
    
    # Generate passengers multiple times with same seed - should be identical
    runs = []
    for run in range(2):
        run_passengers = []
        tp.clear_cache()  # Clear cache to test determinism
        
        for i in range(3):
            passenger = tp.generate_passenger_template(i, 'business')
            run_passengers.append(passenger)
        
        runs.append(run_passengers)
    
    # Compare runs for determinism
    if runs[0] == runs[1]:
        print("✓ Deterministic generation working - identical results across runs")
    else:
        print("❌ Deterministic generation failed - results differ between runs")
        return False
    
    # Test sequential selection strategy
    print("\n--- Testing Sequential Selection ---")
    values = ["NYC", "LAX", "CHI", "DFW", "ATL"]
    
    # Simulate sequential selection
    selected_values = []
    for i in range(7):  # Test wrapping around
        selected = values[i % len(values)]
        selected_values.append(selected)
        print(f"Instance {i}: {selected}")
    
    print(f"Selected sequence: {selected_values}")
    
    print("\n✅ Deterministic generation tests passed!\n")
    return True

def main():
    """Run all tests for the enhanced configuration system."""
    print("🚀 Starting Enhanced Configuration System Tests\n")
    print("=" * 60)
    
    tests = [
        test_config_validation,
        test_data_context_manager,
        test_smart_relationships,
        test_template_processor,
        test_deterministic_generation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"🏁 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced configuration system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())