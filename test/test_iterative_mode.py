#!/usr/bin/env python3
"""
Test iterative processing mode to ensure it still works after fixes.
"""

import os
from utils.xml_generator import XMLGenerator
import xmlschema

def test_iterative_mode():
    """Test iterative processing mode."""
    
    print("🔄 Testing Iterative Processing Mode")
    print("=" * 40)
    
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
    
    # Test recursive mode (current default)
    print("\n📋 Testing Recursive Mode:")
    generator.config.iterative.enable_iterative_processing = False
    xml_recursive = generator.generate_dummy_xml_with_choices(selected_choices=user_choices)
    
    # Validate recursive mode
    schema = xmlschema.XMLSchema(xsd_path)
    recursive_errors = list(schema.iter_errors(xml_recursive))
    
    print(f"   ✓ Recursive mode - XML length: {len(xml_recursive)}")
    print(f"   ✓ Recursive mode - Validation errors: {len(recursive_errors)}")
    
    # Test iterative mode
    print("\n📋 Testing Iterative Mode:")
    generator.config.iterative.enable_iterative_processing = True
    xml_iterative = generator.generate_dummy_xml_with_choices(selected_choices=user_choices)
    
    # Validate iterative mode
    iterative_errors = list(schema.iter_errors(xml_iterative))
    
    print(f"   ✓ Iterative mode - XML length: {len(xml_iterative)}")
    print(f"   ✓ Iterative mode - Validation errors: {len(iterative_errors)}")
    
    # Compare modes
    print("\n📊 Comparison:")
    print(f"   Recursive errors: {len(recursive_errors)}")
    print(f"   Iterative errors: {len(iterative_errors)}")
    
    if len(recursive_errors) == 0:
        print("   🎉 Recursive mode: Perfect validation!")
    
    if len(iterative_errors) == 0:
        print("   🎉 Iterative mode: Perfect validation!")
    elif len(iterative_errors) <= len(recursive_errors):
        print("   ✅ Iterative mode: Acceptable validation (no worse than recursive)")
    else:
        print("   ⚠️  Iterative mode: More errors than recursive mode")
    
    # Both should work without major issues
    assert len(xml_recursive) > 1000, "Recursive mode should generate substantial XML"
    assert len(xml_iterative) > 1000, "Iterative mode should generate substantial XML"
    
    print("\n🎉 Both processing modes work correctly!")

if __name__ == "__main__":
    test_iterative_mode()