#!/usr/bin/env python3
"""
Directly inspect a failing element to understand why it's empty.
"""

import xmlschema
import xml.etree.ElementTree as ET

def inspect_failing_element():
    """Inspect a specific failing element path."""
    
    xml_file = 'generated_xml_for_structural_analysis.xml'
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    
    # Parse the XML to find a specific empty element
    with open(xml_file, 'r') as f:
        xml_content = f.read()
    
    # Parse XML to inspect structure
    root = ET.fromstring(xml_content)
    
    # Find a specific empty AirportAmount
    empty_elements = []
    for elem in root.iter():
        if 'AirportAmount' in elem.tag and not elem.text and not elem.attrib:
            empty_elements.append(elem)
    
    print(f"Found {len(empty_elements)} empty AirportAmount elements")
    
    if empty_elements:
        empty_elem = empty_elements[0]
        print(f"Empty element: {empty_elem.tag}")
        print(f"Parent: {empty_elem.getparent().tag if empty_elem.getparent() is not None else 'None'}")
        print(f"Attributes: {empty_elem.attrib}")
        print(f"Text: '{empty_elem.text}'")
        
        # Get the full path to this element
        path_parts = []
        current = empty_elem
        while current is not None:
            path_parts.insert(0, current.tag.split('}')[-1] if '}' in current.tag else current.tag)
            current = current.getparent()
        
        element_path = '/' + '/'.join(path_parts)
        print(f"Full path: {element_path}")
        
        # Now use schema to inspect this path
        schema = xmlschema.XMLSchema(schema_path)
        
        # Try to validate just this element to get the specific error
        try:
            # Create a minimal XML with just this empty element
            test_xml = f"<{empty_elem.tag}></{empty_elem.tag}>"
            print(f"Test XML: {test_xml}")
            
            # Get parent context for validation
            parent_elem = empty_elem.getparent()
            if parent_elem is not None:
                # Create a more complete test context
                parent_tag = parent_elem.tag.split('}')[-1] if '}' in parent_tag else parent_elem.tag
                test_xml = f"<root xmlns:cns='http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes'><{empty_elem.tag}></{empty_elem.tag}></root>"
                print(f"Context test XML: {test_xml}")
        
        except Exception as e:
            print(f"Error creating test XML: {e}")
    
    # Also look at a working (filled) AirportAmount for comparison
    filled_elements = []
    for elem in root.iter():
        if 'AirportAmount' in elem.tag and elem.text:
            filled_elements.append(elem)
    
    print(f"\nFound {len(filled_elements)} filled AirportAmount elements")
    
    if filled_elements:
        filled_elem = filled_elements[0]
        print(f"Filled element: {filled_elem.tag}")
        print(f"Attributes: {filled_elem.attrib}")
        print(f"Text: '{filled_elem.text}'")
        print(f"Parent: {filled_elem.getparent().tag if filled_elem.getparent() is not None else 'None'}")

if __name__ == "__main__":
    inspect_failing_element()