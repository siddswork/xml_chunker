#!/usr/bin/env python3
"""
Debug why some decimal elements are empty - type detection issue.
"""

import xml.etree.ElementTree as ET
from utils.xml_generator import XMLGenerator

def debug_decimal_type_detection():
    """Debug decimal type detection in XML generation."""
    
    print("🔍 Debugging Decimal Type Detection")
    print("=" * 50)
    
    # Create a simple test to see what happens with different elements
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    generator = XMLGenerator(schema_path)
    
    # Get schema for inspection
    schema = generator.schema
    
    # Find elements that should be decimal
    decimal_elements = []
    
    print("Looking for decimal-related element types...")
    
    # Look for elements containing "Amount" in their name
    for elem_name, elem in schema.elements.items():
        if elem and hasattr(elem, 'type') and elem.type:
            if elem.type.is_simple():
                # Check if it's a decimal type
                if hasattr(elem.type, 'primitive_type') and elem.type.primitive_type:
                    if 'decimal' in str(elem.type.primitive_type).lower():
                        decimal_elements.append((elem_name, elem, 'simple'))
            elif elem.type.is_complex():
                # Check if it's complex with simple content
                if (hasattr(elem.type, 'content') and elem.type.content and 
                    hasattr(elem.type.content, 'is_simple') and elem.type.content.is_simple()):
                    if hasattr(elem.type.content, 'primitive_type') and elem.type.content.primitive_type:
                        if 'decimal' in str(elem.type.content.primitive_type).lower():
                            decimal_elements.append((elem_name, elem, 'complex_simple'))
    
    print(f"Found {len(decimal_elements)} decimal-related elements")
    
    # Show examples
    for name, elem, type_category in decimal_elements[:10]:
        print(f"  {name}: {type_category}")
        if type_category == 'complex_simple':
            print(f"    Attributes: {list(elem.type.attributes.keys()) if elem.type.attributes else []}")
    
    # Now test generation for a few elements
    print(f"\n🧪 Testing Element Generation...")
    
    # Test with a known problematic element
    test_elements = ['AirportAmount', 'Amount', 'ConversionRate']
    
    for elem_name in test_elements:
        # Try to find this element in the schema
        found_elements = []
        for schema_name, schema_elem in schema.elements.items():
            if elem_name in schema_name:
                found_elements.append((schema_name, schema_elem))
        
        print(f"\n  {elem_name}:")
        if found_elements:
            for schema_name, schema_elem in found_elements[:3]:
                print(f"    Schema: {schema_name}")
                print(f"    Type: {schema_elem.type}")
                print(f"    Is simple: {schema_elem.type.is_simple()}")
                print(f"    Is complex: {schema_elem.type.is_complex()}")
                
                if schema_elem.type.is_complex():
                    has_attributes = bool(getattr(schema_elem.type, 'attributes', None))
                    print(f"    Has attributes: {has_attributes}")
                    
                    content = getattr(schema_elem.type, 'content', None)
                    print(f"    Content: {content}")
                    
                    if content:
                        is_simple_content = hasattr(content, 'is_simple') and content.is_simple()
                        print(f"    Content is simple: {is_simple_content}")
        else:
            print(f"    Not found in root elements")

if __name__ == "__main__":
    debug_decimal_type_detection()