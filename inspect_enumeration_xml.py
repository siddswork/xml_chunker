#!/usr/bin/env python3
"""
Inspect the actual XML to see enumeration elements and their values.
"""

from utils.xml_generator import XMLGenerator
import re
import xml.etree.ElementTree as ET

def inspect_enumeration_xml():
    """Inspect enumeration elements in the generated XML."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Inspecting Enumeration Elements in Generated XML")
    print("=" * 55)
    
    # Generate XML
    print("1. Generating XML...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    if not xml_data:
        print("❌ Failed to generate XML")
        return
    
    print(f"   Generated XML: {len(xml_data)} characters")
    
    # Parse the XML to analyze enumeration elements
    print("\n2. Parsing XML for enumeration analysis...")
    
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return
    
    # Find enumeration types in schema first
    print("3. Finding enumeration types in schema...")
    enumeration_types = {}
    
    for name, xsd_type in generator.schema.maps.types.items():
        constraints = generator._extract_type_constraints(xsd_type)
        if 'enum_values' in constraints and constraints['enum_values']:
            type_local_name = str(name).split('}')[-1] if '}' in str(name) else str(name)
            enumeration_types[type_local_name] = constraints['enum_values']
    
    print(f"   Found {len(enumeration_types)} enumeration types")
    
    # Analyze elements in the XML
    print("\n4. Analyzing enumeration elements in XML...")
    
    enumeration_elements = []
    
    def analyze_element(element, path=""):
        """Recursively analyze XML elements."""
        current_path = f"{path}/{element.tag.split('}')[-1] if '}' in element.tag else element.tag}"
        
        # Check if this element might be an enumeration based on name patterns
        local_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Check against known enumeration types
        possible_enum = False
        expected_values = None
        
        for type_name, enum_values in enumeration_types.items():
            if type_name.lower() in local_name.lower() or local_name.lower() in type_name.lower():
                possible_enum = True
                expected_values = enum_values
                break
        
        # Also check by common enumeration patterns
        if not possible_enum:
            enum_patterns = ['code', 'type', 'status', 'rule', 'applied', 'exempt', 'disclosure']
            if any(pattern in local_name.lower() for pattern in enum_patterns):
                possible_enum = True
        
        if possible_enum:
            element_text = element.text if element.text else ""
            enumeration_elements.append({
                'path': current_path,
                'tag': local_name,
                'value': element_text,
                'expected_values': expected_values,
                'is_empty': element_text == "",
                'has_children': len(list(element)) > 0
            })
        
        # Recursively analyze children
        for child in element:
            analyze_element(child, current_path)
    
    analyze_element(root)
    
    print(f"   Found {len(enumeration_elements)} potential enumeration elements")
    
    # Analyze the enumeration elements
    print("\n5. Enumeration element analysis:")
    
    empty_count = sum(1 for elem in enumeration_elements if elem['is_empty'])
    non_empty_count = len(enumeration_elements) - empty_count
    
    print(f"   Empty enumeration elements: {empty_count}")
    print(f"   Non-empty enumeration elements: {non_empty_count}")
    
    # Show examples of empty enumeration elements
    print(f"\n6. Examples of empty enumeration elements:")
    
    empty_elements = [elem for elem in enumeration_elements if elem['is_empty']]
    for i, elem in enumerate(empty_elements[:10]):
        print(f"   {i+1}. {elem['tag']} (path: {elem['path']})")
        if elem['expected_values']:
            print(f"      Expected values: {elem['expected_values'][:5]}{'...' if len(elem['expected_values']) > 5 else ''}")
        else:
            print(f"      Expected values: Unknown")
    
    # Show examples of non-empty enumeration elements
    print(f"\n7. Examples of non-empty enumeration elements:")
    
    non_empty_elements = [elem for elem in enumeration_elements if not elem['is_empty']]
    for i, elem in enumerate(non_empty_elements[:10]):
        print(f"   {i+1}. {elem['tag']}: '{elem['value']}' (path: {elem['path']})")
        if elem['expected_values']:
            valid = elem['value'] in elem['expected_values']
            print(f"      Expected: {elem['expected_values'][:3]}{'...' if len(elem['expected_values']) > 3 else ''} - {'✅ Valid' if valid else '❌ Invalid'}")
    
    return enumeration_elements

if __name__ == "__main__":
    enumeration_elements = inspect_enumeration_xml()
    
    if enumeration_elements:
        empty_count = sum(1 for elem in enumeration_elements if elem['is_empty'])
        print(f"\n🎯 Summary:")
        print(f"   Total enumeration elements: {len(enumeration_elements)}")
        print(f"   Empty elements: {empty_count}")
        print(f"   Empty percentage: {empty_count/len(enumeration_elements)*100:.1f}%")