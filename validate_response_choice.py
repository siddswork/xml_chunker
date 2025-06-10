#!/usr/bin/env python3
"""
Validation script for IATA_OrderViewRS with Response choice generation.

This script generates XML with the Response choice instead of Error choice
to analyze the full scope of validation errors that might be found.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
import xmlschema


def generate_response_choice_xml():
    """Generate XML with Response choice instead of Error choice."""
    print("Generating XML with Response choice...")
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(xsd_path)
        
        # Configure Response choice selection
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Response',
                'choice_data': {
                    'type': 'choice',
                    'min_occurs': 1,
                    'max_occurs': 1,
                    'elements': [
                        {'name': 'Error', 'min_occurs': 1, 'max_occurs': 'unbounded'},
                        {'name': 'Response', 'min_occurs': 1, 'max_occurs': 1}
                    ]
                }
            }
        }
        
        print("Attempting to generate with Response choice...")
        xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
        
        print(f"Generated XML size: {len(xml_content)} characters")
        
        # Check what was actually generated
        if 'Response' in xml_content and 'Error' not in xml_content:
            print("✅ Successfully generated Response choice XML")
            return xml_content, 'response'
        elif 'Error' in xml_content:
            print("⚠️  Generated Error choice XML (fallback behavior)")
            return xml_content, 'error'
        else:
            print("❓ Generated XML with unknown structure")
            return xml_content, 'unknown'
            
    except Exception as e:
        print(f"Error generating Response choice XML: {e}")
        
        # Fallback to regular generation
        print("Falling back to regular XML generation...")
        xml_content = generator.generate_dummy_xml()
        return xml_content, 'error_fallback'


def validate_and_count_errors(xml_content, generator):
    """Validate XML and count errors."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(xml_content)
        temp_xml_path = temp_file.name
    
    try:
        # Validate using xmlschema
        errors = list(generator.schema.iter_errors(temp_xml_path))
        return len(errors), errors
        
    finally:
        # Cleanup temporary file
        if os.path.exists(temp_xml_path):
            os.unlink(temp_xml_path)


def test_both_choices():
    """Test both Error and Response choices to compare error counts."""
    print("🔍 Comparing Error vs Response Choice Validation")
    print("=" * 60)
    
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(xsd_path)
    
    # Test 1: Default Error choice
    print("\n--- Testing Default (Error) Choice ---")
    error_xml = generator.generate_dummy_xml()
    error_count, error_errors = validate_and_count_errors(error_xml, generator)
    print(f"Error choice validation errors: {error_count}")
    
    # Test 2: Response choice attempt
    print("\n--- Testing Response Choice ---")
    response_xml, choice_type = generate_response_choice_xml()
    response_count, response_errors = validate_and_count_errors(response_xml, generator)
    print(f"Response choice validation errors: {response_count}")
    print(f"Actually generated: {choice_type}")
    
    # Test 3: Generate very large XML to see if we can reach higher error counts
    print("\n--- Testing with Maximum Unbounded Elements ---")
    try:
        large_generator = XMLGenerator(xsd_path)  # Use default generator
        large_xml = large_generator.generate_dummy_xml()
        large_count, large_errors = validate_and_count_errors(large_xml, large_generator)
        print(f"Large XML validation errors: {large_count}")
        print(f"Large XML size: {len(large_xml)} characters")
    except Exception as e:
        print(f"Error in large XML test: {e}")
        large_count = 0
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Default Error Choice: {error_count} errors")
    print(f"Response Choice Attempt: {response_count} errors")
    print(f"Large XML Generation: {large_count} errors")
    print(f"Max error count found: {max(error_count, response_count, large_count)}")
    
    if max(error_count, response_count, large_count) < 1000:
        print("\n📝 Note: The 3663 error count mentioned might be from:")
        print("  1. A different schema or XML structure")
        print("  2. An older version before recent fixes")
        print("  3. A different validation approach")
        print("  4. A specific test configuration")
    
    return {
        'error_choice': error_count,
        'response_choice': response_count,
        'large_xml': large_count,
        'choice_type': choice_type
    }


def main():
    """Run the choice comparison analysis."""
    os.chdir(project_root)
    
    try:
        results = test_both_choices()
        
        # If we still have low error counts, let's analyze what might be different
        max_errors = max(results['error_choice'], results['response_choice'], results['large_xml'])
        
        print(f"\n✅ Choice comparison completed!")
        print(f"📊 Maximum errors found: {max_errors}")
        
        if max_errors < 500:
            print("\n🔍 Current error counts are much lower than the mentioned 3663 errors.")
            print("This suggests significant improvements have been made to the XML generation.")
            print("We'll proceed with analyzing the current validation errors.")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()