#!/usr/bin/env python3
"""
Test recursive vs iterative approaches to see if order is preserved.
"""

import os
from utils.xml_generator import XMLGenerator
import xml.etree.ElementTree as ET

def test_both_approaches():
    """Test both recursive and iterative approaches."""
    
    # Load schema
    # Get the project root directory (parent of test directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    resource_dir = os.path.join(project_root, 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    generator = XMLGenerator(xsd_path)
    
    # Configure for Response choice
    user_choices = {
        'choice_0': {
            'path': 'IATA_OrderViewRS',
            'selected_element': 'Response'
        }
    }
    
    generator.user_choices = user_choices
    
    print("🔄 Testing Recursive Approach:")
    print("=" * 40)
    
    # Force recursive approach
    original_setting = generator.config.iterative.enable_iterative_processing
    generator.config.iterative.enable_iterative_processing = False
    
    try:
        xml_recursive = generator.generate_dummy_xml()
        root_recursive = ET.fromstring(xml_recursive)
        recursive_order = [child.tag.split('}')[-1] for child in root_recursive]
        print(f"Recursive order: {recursive_order}")
    except Exception as e:
        print(f"Recursive approach failed: {e}")
        recursive_order = ["FAILED"]
    
    print(f"\n🔄 Testing Iterative Approach:")
    print("=" * 40)
    
    # Force iterative approach
    generator.config.iterative.enable_iterative_processing = True
    
    try:
        xml_iterative = generator.generate_dummy_xml()
        root_iterative = ET.fromstring(xml_iterative)
        iterative_order = [child.tag.split('}')[-1] for child in root_iterative]
        print(f"Iterative order: {iterative_order}")
    except Exception as e:
        print(f"Iterative approach failed: {e}")
        iterative_order = ["FAILED"]
    
    # Restore original setting
    generator.config.iterative.enable_iterative_processing = original_setting
    
    print(f"\n📊 Comparison:")
    print(f"Expected order: ['Response', 'AugmentationPoint', 'DistributionChain', 'PayloadAttributes', 'PaymentFunctions']")
    print(f"Recursive:      {recursive_order}")
    print(f"Iterative:      {iterative_order}")
    
    if recursive_order == iterative_order:
        print("❓ Same order - issue is in both approaches")
    elif recursive_order[0] != "FAILED" and recursive_order != iterative_order:
        print("✅ Different orders - iterative approach is causing the issue")
    else:
        print("❌ Cannot determine - one approach failed")

if __name__ == "__main__":
    test_both_approaches()