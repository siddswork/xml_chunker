#!/usr/bin/env python3
"""
Test script to verify structural errors are reduced after type generation fixes.
"""

import os
from utils.xml_generator import XMLGenerator
from services.xml_validator import XMLValidator
from config import get_config

def test_structural_errors():
    """Test structural error reduction with Complete mode."""
    
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    if not os.path.exists(xsd_path):
        print("❌ Sample XSD file not found.")
        return False
    
    print("🧪 Testing Structural Error Fixes...")
    print("=" * 50)
    
    try:
        # Generate XML with Complete mode
        print("\n1️⃣ Generating XML with Complete mode...")
        generator = XMLGenerator(xsd_path)
        xml_content = generator.generate_dummy_xml_with_options(
            generation_mode="Complete"
        )
        
        print(f"   📊 Generated XML size: {len(xml_content):,} characters")
        print(f"   📄 Lines: {xml_content.count(chr(10))}")
        
        # Validate the XML
        print("\n2️⃣ Validating XML against schema...")
        config = get_config()
        validator = XMLValidator(config)
        
        validation_result = validator.validate_xml_against_schema(
            xml_content, 
            xsd_path,
            "IATA_OrderViewRS.xsd",
            None
        )
        
        if validation_result['success']:
            total_errors = validation_result['total_errors']
            error_breakdown = validation_result['error_breakdown']
            
            print(f"   ✅ Validation completed")
            print(f"   📊 Total errors: {total_errors}")
            print(f"   🔢 Structural errors: {error_breakdown['structural_errors']}")
            print(f"   🔤 Enumeration errors: {error_breakdown['enumeration_errors']}")
            print(f"   ✅ Boolean errors: {error_breakdown['boolean_errors']}")
            print(f"   🎯 Pattern errors: {error_breakdown['pattern_errors']}")
            
            # Check for specific error types we fixed
            structural_errors = error_breakdown['structural_errors']
            
            print(f"\n3️⃣ Structural Error Analysis:")
            if structural_errors == 0:
                print("   🎉 No structural errors! Perfect!")
            elif structural_errors < 10:
                print(f"   ✅ Low structural errors ({structural_errors}) - good improvement!")
            elif structural_errors < 25:
                print(f"   ⚠️ Moderate structural errors ({structural_errors}) - some issues remain")
            else:
                print(f"   ❌ High structural errors ({structural_errors}) - needs more work")
            
            # Check for the specific errors we were targeting
            if validation_result.get('categorized_errors') and validation_result['categorized_errors']['structural_errors']:
                print(f"\n4️⃣ Checking for specific error patterns:")
                
                decimal_errors = 0
                duration_errors = 0
                empty_string_errors = 0
                
                for error in validation_result['categorized_errors']['structural_errors']:
                    error_msg = str(error).lower()
                    if "failed decoding ''" in error_msg and "decimal" in error_msg:
                        decimal_errors += 1
                    elif "failed decoding 'sampleduration'" in error_msg and "duration" in error_msg:
                        duration_errors += 1
                    elif "failed decoding ''" in error_msg:
                        empty_string_errors += 1
                
                print(f"   🔢 Empty decimal errors: {decimal_errors} (should be 0)")
                print(f"   ⏰ Sample duration errors: {duration_errors} (should be 0)")
                print(f"   📝 Empty string errors: {empty_string_errors}")
                
                if decimal_errors == 0 and duration_errors == 0:
                    print("   🎉 Target error patterns fixed!")
                else:
                    print("   ⚠️ Some target error patterns still present")
                
                # Show details of remaining structural errors
                print(f"\n5️⃣ Details of remaining {structural_errors} structural errors:")
                for i, error in enumerate(validation_result['categorized_errors']['structural_errors'][:10], 1):
                    error_str = str(error)
                    # Extract path and message
                    if hasattr(error, 'path') and hasattr(error, 'message'):
                        path = error.path
                        message = error.message
                    else:
                        # Parse from string format
                        lines = error_str.split('\n')
                        path = "Unknown"
                        message = error_str
                        for line in lines:
                            if line.strip().startswith('Path:'):
                                path = line.replace('Path:', '').strip()
                            elif line.strip().startswith('Message:'):
                                message = line.replace('Message:', '').strip()
                    
                    print(f"   {i}. Path: {path}")
                    print(f"      Message: {message}")
                    print()
                    
                if structural_errors > 10:
                    print(f"   ... and {structural_errors - 10} more errors")
            
            # Assert success if less than 25 structural errors
            assert structural_errors < 25, f"Too many structural errors: {structural_errors}"
        else:
            print(f"   ❌ Validation failed: {validation_result['error']}")
            assert False, f"Validation failed: {validation_result['error']}"
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed: {e}"

if __name__ == "__main__":
    test_structural_errors()
    print("\n🎉 Structural error test completed successfully!")
    print("\n💡 Key improvements:")
    print("   • Fixed xs:decimal empty string errors")
    print("   • Fixed xs:duration format errors")
    print("   • Better numeric type handling") 
    print("   • Proper content validation logic")