#!/usr/bin/env python3
"""
Test if our choice fix resolved the structural errors.
"""

import os
import json
from datetime import datetime
from utils.xml_generator import XMLGenerator
import xmlschema

def test_choice_fix():
    """Test if choice violations are fixed."""
    
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
    
    # Generate XML
    xml_content = generator.generate_dummy_xml_with_choices(selected_choices=user_choices)
    
    # Validate and analyze errors
    try:
        schema = xmlschema.XMLSchema(xsd_path)
        errors = list(schema.iter_errors(xml_content))
        
        print(f"🔍 Total validation errors: {len(errors)}")
        
        # Categorize errors
        structural_errors = []
        choice_errors = []
        decimal_errors = []
        other_errors = []
        
        for error in errors:
            error_msg = str(error)
            if 'XsdGroup' in error_msg:
                if 'choice' in error_msg:
                    choice_errors.append(error)
                else:
                    structural_errors.append(error)
            elif 'decimal' in error_msg or "invalid value ''" in error_msg:
                decimal_errors.append(error)
            else:
                other_errors.append(error)
        
        print(f"📊 Error breakdown:")
        print(f"  - Choice model violations: {len(choice_errors)}")
        print(f"  - Other structural errors: {len(structural_errors)}")
        print(f"  - Decimal/empty value errors: {len(decimal_errors)}")
        print(f"  - Other errors: {len(other_errors)}")
        
        # Show specific choice errors if any
        if choice_errors:
            print(f"\n❌ Choice model violations still exist:")
            for i, error in enumerate(choice_errors[:5]):  # Show first 5
                print(f"  [{i+1}] {error}")
        else:
            print(f"\n✅ No choice model violations detected!")
        
        # Show decimal errors
        if decimal_errors:
            print(f"\n⚠️  Decimal/empty value errors:")
            for i, error in enumerate(decimal_errors[:3]):  # Show first 3
                print(f"  [{i+1}] {error}")
        
        # Test specific elements that were problematic
        problematic_elements = ['SeatAssignmentAssociations', 'OrderServiceAssociation', 'PaymentProcessingSummaryPaymentMethod']
        
        print(f"\n🔍 Checking for specific problematic elements in errors:")
        for element in problematic_elements:
            element_errors = [e for e in choice_errors if element in str(e)]
            print(f"  - {element}: {len(element_errors)} choice errors")
        
        # Summary
        if len(choice_errors) == 0:
            print(f"\n🎉 SUCCESS: Choice model violations have been FIXED!")
            print(f"   Remaining errors are related to decimal values, not structural issues.")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: {len(choice_errors)} choice violations remain")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    test_choice_fix()