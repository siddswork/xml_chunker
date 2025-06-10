#!/usr/bin/env python3
"""
Debug XML serialization to find where empty decimal elements are created.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re

def debug_xml_serialization():
    """Debug the XML serialization process."""
    
    print("🔍 Debugging XML Serialization")
    print("=" * 60)
    
    # Generate XML
    gen = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    xml = gen.generate_dummy_xml_with_choices({'Response': True}, {})
    
    print(f"Generated XML: {len(xml)} characters")
    
    # Look for empty decimal elements in the actual XML
    print("\n1. Searching for empty decimal elements in XML...")
    
    # Look for self-closing tags and empty tags
    empty_tag_patterns = [
        r'<([^>]*Amount[^>]*)/>',  # Self-closing amount tags
        r'<([^>]*Amount[^>]*)></[^>]*>',  # Empty amount tags
        r'<([^>]*Rate[^>]*)/>',  # Self-closing rate tags  
        r'<([^>]*Rate[^>]*)></[^>]*>',  # Empty rate tags
        r'<([^>]*Measure[^>]*)/>',  # Self-closing measure tags
        r'<([^>]*Measure[^>]*)></[^>]*>',  # Empty measure tags
        r'<([^>]*Price[^>]*)/>',  # Self-closing price tags
        r'<([^>]*Price[^>]*)></[^>]*>',  # Empty price tags
    ]
    
    found_empty = []
    for pattern in empty_tag_patterns:
        matches = re.findall(pattern, xml, re.IGNORECASE)
        for match in matches:
            found_empty.append(match)
            
    print(f"Found {len(found_empty)} potentially empty decimal elements:")
    for i, elem in enumerate(found_empty[:10]):  # Show first 10
        print(f"   {i+1}. {elem}")
    
    # Look for any completely empty elements (just to be sure)
    print("\n2. Looking for completely empty elements...")
    empty_elements = re.findall(r'<([^>]+)></[^>]*>', xml)
    print(f"Found {len(empty_elements)} completely empty elements:")
    for i, elem in enumerate(empty_elements[:10]):
        print(f"   {i+1}. {elem}")
    
    # Check specific validation errors
    print("\n3. Validating and checking specific errors...")
    schema = xmlschema.XMLSchema('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    errors = list(schema.iter_errors(xml))
    
    # Get empty decimal errors with paths
    empty_decimal_errors = []
    for error in errors:
        if "invalid value ''" in str(error) and 'xs:decimal' in str(error):
            # Try to extract the path
            error_str = str(error)
            path_match = re.search(r'Path: ([^\n]+)', error_str)
            if path_match:
                path = path_match.group(1)
                empty_decimal_errors.append(path)
    
    print(f"Empty decimal error paths: {len(empty_decimal_errors)}")
    for i, path in enumerate(empty_decimal_errors[:10]):
        print(f"   {i+1}. {path}")
    
    # Let's check what's actually in the XML at these paths
    if empty_decimal_errors:
        print("\n4. Examining XML content at error paths...")
        
        # Take the first error path and look for it in XML
        first_error_path = empty_decimal_errors[0]
        path_parts = first_error_path.split('/')
        element_name = path_parts[-1]
        
        print(f"Looking for element: {element_name}")
        
        # Find this element in the XML
        element_pattern = rf'<[^>]*{re.escape(element_name)}[^>]*>(.*?)</[^>]*{re.escape(element_name)}[^>]*>'
        matches = re.findall(element_pattern, xml, re.DOTALL)
        
        print(f"Found {len(matches)} instances of {element_name}:")
        for i, content in enumerate(matches[:5]):
            print(f"   {i+1}. Content: '{content}'")

if __name__ == "__main__":
    debug_xml_serialization()