#!/usr/bin/env python3
"""
Quick validation test to check if refactored type generators reduced validation errors.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import io

def test_validation_improvements():
    """Test if the modular type generators reduced validation errors."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        # Generate XML with Response choice using refactored generators
        generator = XMLGenerator(schema_path)
        
        # Set unbounded counts to small values for quick test
        generator.user_unbounded_counts = {}
        
        # Generate XML with Response choice (the problematic one)
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        if not xml_data:
            print("✗ Failed to generate XML")
            return
        
        print(f"✓ Generated XML: {len(xml_data)} bytes")
        
        # Validate against schema  
        try:
            generator.schema.validate(xml_data)
            print("✓ XML is valid - all errors fixed!")
        except xmlschema.XMLSchemaException as e:
            # Count validation errors
            error_count = str(e).count("failed")
            print(f"⚠ XML has validation issues: ~{error_count} errors detected")
            
            # Sample first few errors to see types
            error_lines = str(e).split('\n')[:5]
            print("Sample errors:")
            for line in error_lines:
                if line.strip():
                    print(f"  - {line.strip()}")
            
            # Check for empty string errors specifically
            if "failed decoding ''" in str(e):
                print("✗ Still have empty string errors - need more fixes")
            else:
                print("✓ No empty string errors detected - major improvement!")
                
    except Exception as e:
        print(f"✗ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validation_improvements()