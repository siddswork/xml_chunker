#!/usr/bin/env python3
"""
Analyze current validation errors to understand what needs to be fixed next.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re

def analyze_current_errors():
    """Analyze current validation errors after type detection improvements."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Generate XML with Response choice
        print("Generating XML...")
        try:
            xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
            print(f"XML data preview: {xml_data[:200]}...")
        except Exception as gen_error:
            print(f"Generation error: {gen_error}")
            import traceback
            traceback.print_exc()
            return
        
        if not xml_data:
            print("Failed to generate XML")
            return
        
        print(f"Generated XML: {len(xml_data)} bytes")
        
        # Validate and categorize errors
        try:
            generator.schema.validate(xml_data)
            print("✅ XML is valid!")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Count different error types
            boolean_errors = error_text.count("failed decoding ''") + error_text.count("boolean")
            numeric_errors = error_text.count("decimal") + error_text.count("integer")
            enum_errors = error_text.count("not in enumeration")
            pattern_errors = error_text.count("does not match pattern")
            structural_errors = error_text.count("failed validating") - boolean_errors - numeric_errors
            
            total_errors = error_text.count("failed")
            
            print(f"\n📊 Current Error Analysis (Total: {total_errors})")
            print("=" * 50)
            print(f"Boolean errors: {boolean_errors}")
            print(f"Numeric errors: {numeric_errors}")
            print(f"Enumeration errors: {enum_errors}")
            print(f"Pattern errors: {pattern_errors}")
            print(f"Structural errors: {structural_errors}")
            
            # Sample specific errors
            print(f"\n🔍 Sample Error Details:")
            print("=" * 50)
            error_lines = error_text.split('\n')[:15]
            for i, line in enumerate(error_lines):
                if line.strip() and ('failed' in line.lower() or 'reason:' in line.lower()):
                    print(f"{i+1:2d}. {line.strip()[:100]}...")
                    if i >= 5:  # Show first 5 detailed errors
                        break
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_current_errors()