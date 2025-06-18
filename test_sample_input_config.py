#!/usr/bin/env python3
"""
Test the fixed sample_input_config.json to see if it generates the target XML.
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
from utils.config_manager import ConfigManager
import io

def test_sample_input_config():
    """Test the fixed sample_input_config.json."""
    print("🧪 Testing fixed sample_input_config.json...")
    
    # Load the fixed configuration
    config_path = "resource/orderCreate/test_data_config/sample_input_config.json"
    xsd_path = "resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    if not os.path.exists(xsd_path):
        print(f"❌ XSD file not found: {xsd_path}")
        return False
    
    try:
        # Load and validate configuration
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        config_manager = ConfigManager()
        config_data = config_manager.load_config(io.StringIO(config_content))
        
        print("✓ Enhanced configuration loaded successfully")
        print(f"✓ Configuration name: {config_data['metadata']['name']}")
        print(f"✓ Data contexts: {list(config_data.get('data_contexts', {}).keys())}")
        
        # Create XMLGenerator with enhanced configuration
        generator = XMLGenerator(xsd_path, config_data=config_data)
        print("✓ XMLGenerator created with enhanced configuration")
        
        # Generate XML
        xml_output = generator.generate_dummy_xml_with_options(
            generation_mode="Complete",
            selected_choices={},
            unbounded_counts={},
            optional_selections=[],
            custom_values={}
        )
        
        print("✓ XML generated successfully")
        print(f"✓ XML length: {len(xml_output)} characters")
        
        # Save generated XML
        output_path = "test_generated_sample_input.xml"
        with open(output_path, 'w') as f:
            f.write(xml_output)
        print(f"✓ Generated XML saved to {output_path}")
        
        # Check for key elements from target XML
        checks = {
            "FlightBooking": "target element",
            "REQ001": "request ID",
            "Create": "action element",
            "passenger_count": "property key",
            "departure_city": "property key",
            "arrival_city": "property key", 
            "AA": "airline code",
            "1234": "flight number",
            "2024-01-15": "date",
            "08:00": "departure time",
            "11:30": "arrival time",
            "John": "first name",
            "Doe": "last name",
            "jane.smith@email.com": "email",
            "+1234567890": "phone"
        }
        
        found_elements = []
        missing_elements = []
        
        for element, description in checks.items():
            if element in xml_output:
                found_elements.append(f"✓ {description}: {element}")
            else:
                missing_elements.append(f"❌ {description}: {element}")
        
        print(f"\n📊 Element Check Results:")
        print(f"✓ Found: {len(found_elements)}")
        print(f"❌ Missing: {len(missing_elements)}")
        
        for element in found_elements:
            print(element)
        
        if missing_elements:
            print(f"\n⚠️  Missing elements:")
            for element in missing_elements:
                print(element)
        
        # Load target XML for comparison
        target_path = "resource/orderCreate/test_data/sample_input.xml"
        if os.path.exists(target_path):
            with open(target_path, 'r') as f:
                target_xml = f.read()
            
            print(f"\n📋 Comparison with target XML:")
            print(f"✓ Target XML length: {len(target_xml)} characters")
            print(f"✓ Generated XML length: {len(xml_output)} characters")
            
            # Compare key structural elements
            target_lines = [line.strip() for line in target_xml.split('\n') if line.strip() and not line.strip().startswith('<?') and not line.strip().startswith('<AMA_ConnectivityLayerRQ')]
            generated_lines = [line.strip() for line in xml_output.split('\n') if line.strip() and not line.strip().startswith('<?') and not line.strip().startswith('<AMA_ConnectivityLayerRQ')]
            
            print(f"✓ Target XML lines: {len(target_lines)}")
            print(f"✓ Generated XML lines: {len(generated_lines)}")
            
        success_rate = len(found_elements) / len(checks) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 70  # Consider 70%+ success as good
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🚀 Testing Fixed sample_input_config.json\n")
    print("=" * 60)
    
    if test_sample_input_config():
        print("\n🎉 Test passed! Configuration is working well.")
        return 0
    else:
        print("\n⚠️  Test had issues. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())