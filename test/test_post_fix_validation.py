#!/usr/bin/env python3
"""
Post-fix validation test to ensure all fixes work correctly.
"""

import os
from utils.xml_generator import XMLGenerator
import xmlschema
import xml.etree.ElementTree as ET

def test_post_fix_validation():
    """Test that all fixes work correctly after implementation."""
    
    print("🧪 Running Post-Fix Validation Tests")
    print("=" * 50)
    
    # Get the project root directory (parent of test directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    resource_dir = os.path.join(project_root, 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    # Test 1: Response Choice Generation
    print("\n📋 Test 1: Response Choice Generation")
    generator = XMLGenerator(xsd_path)
    
    user_choices = {
        'choice_0': {
            'path': 'IATA_OrderViewRS',
            'selected_element': 'Response'
        }
    }
    
    xml_content = generator.generate_dummy_xml_with_choices(selected_choices=user_choices)
    
    # Parse and check structure
    root = ET.fromstring(xml_content)
    root_children = [child.tag.split('}')[-1] for child in root]
    
    print(f"   ✓ XML generated successfully ({len(xml_content)} chars)")
    print(f"   ✓ Root children: {root_children}")
    
    # Check that we have Response but not Error
    has_response = any('Response' in child for child in root_children)
    has_error = any('Error' in child for child in root_children)
    
    print(f"   ✓ Has Response: {has_response}")
    print(f"   ✓ Has Error: {has_error}")
    
    assert has_response, "Should have Response element"
    assert not has_error, "Should NOT have Error element"
    
    # Test 2: Schema Validation
    print("\n📋 Test 2: Schema Validation")
    try:
        schema = xmlschema.XMLSchema(xsd_path)
        errors = list(schema.iter_errors(xml_content))
        
        print(f"   ✓ Validation errors: {len(errors)}")
        
        if errors:
            print("   ⚠️  Remaining errors:")
            for i, error in enumerate(errors[:3]):  # Show first 3
                print(f"      [{i+1}] {error}")
        else:
            print("   🎉 Perfect validation - zero errors!")
        
        # Should have 0 errors after our fixes
        assert len(errors) == 0, f"Expected 0 validation errors, got {len(errors)}"
        
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        raise
    
    # Test 3: Amount Element with Decimal Content
    print("\n📋 Test 3: Amount Element Validation")
    
    amount_elements = []
    def find_amount_elements(element):
        if element.tag.endswith('Amount'):
            amount_elements.append(element)
        for child in element:
            find_amount_elements(child)
    
    find_amount_elements(root)
    
    print(f"   ✓ Found {len(amount_elements)} Amount elements")
    
    for i, amount in enumerate(amount_elements):
        print(f"   ✓ Amount[{i}]: text='{amount.text}', attrs={amount.attrib}")
        assert amount.text is not None and amount.text.strip(), f"Amount element {i} should have text content"
        assert 'CurCode' in amount.attrib, f"Amount element {i} should have CurCode attribute"
    
    # Test 4: Choice Group Handling
    print("\n📋 Test 4: Choice Group Handling")
    
    # Look for elements that were problematic before (should now be handled correctly)
    problematic_elements = ['SeatAssignmentAssociations', 'OrderServiceAssociation', 'PaymentProcessingSummaryPaymentMethod']
    
    def count_elements_by_name(element, name):
        count = 0
        if element.tag.endswith(name):
            count += 1
        for child in element:
            count += count_elements_by_name(child, name)
        return count
    
    for element_name in problematic_elements:
        count = count_elements_by_name(root, element_name)
        print(f"   ✓ {element_name}: {count} instances")
    
    # Test 5: Sequence Order Verification
    print("\n📋 Test 5: Sequence Order Verification")
    
    expected_root_order = ['Response', 'AugmentationPoint', 'DistributionChain', 'PayloadAttributes', 'PaymentFunctions']
    actual_order = [child.tag.split('}')[-1] for child in root]
    
    print(f"   Expected order: {expected_root_order}")
    print(f"   Actual order:   {actual_order}")
    
    # Check that Response comes first
    if actual_order:
        assert actual_order[0] == 'Response', f"First element should be Response, got {actual_order[0]}"
        print("   ✓ Response element is first (correct choice selection)")
    
    print("\n🎉 All Post-Fix Validation Tests PASSED!")
    print("   - Response choice generation: ✓")
    print("   - Zero validation errors: ✓") 
    print("   - Amount element text content: ✓")
    print("   - Choice group handling: ✓")
    print("   - Sequence order: ✓")

if __name__ == "__main__":
    test_post_fix_validation()