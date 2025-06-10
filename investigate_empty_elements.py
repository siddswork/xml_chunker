#!/usr/bin/env python3
"""
Investigate why specific elements are still empty despite enumeration fixes.
"""

from utils.xml_generator import XMLGenerator
import xml.etree.ElementTree as ET
import xmlschema

def investigate_empty_elements():
    """Investigate why specific elements are showing empty values."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Investigating Empty Elements")
    print("=" * 35)
    
    # Target elements to investigate
    target_elements = [
        'TaxTypeCode',
        'PrefLevelCode'
    ]
    
    # Generate XML
    print("1. Generating XML...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    print(f"   Generated XML: {len(xml_data)} characters")
    
    # Parse and analyze the XML
    print("\n2. Parsing XML and searching for target elements...")
    
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return
    
    # Find all instances of target elements
    empty_elements = []
    non_empty_elements = []
    
    def search_elements(element, path=""):
        """Recursively search for target elements."""
        current_path = f"{path}/{element.tag.split('}')[-1] if '}' in element.tag else element.tag}"
        
        # Check if this is a target element
        local_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        if local_name in target_elements:
            element_text = element.text if element.text else ""
            
            element_info = {
                'name': local_name,
                'path': current_path,
                'value': element_text,
                'is_empty': element_text == "",
                'has_children': len(list(element)) > 0
            }
            
            if element_text == "":
                empty_elements.append(element_info)
            else:
                non_empty_elements.append(element_info)
        
        # Recursively search children
        for child in element:
            search_elements(child, current_path)
    
    search_elements(root)
    
    print(f"   Found {len(empty_elements)} empty target elements")
    print(f"   Found {len(non_empty_elements)} non-empty target elements")
    
    # Show empty elements
    if empty_elements:
        print(f"\n3. Empty target elements:")
        for i, elem in enumerate(empty_elements[:10]):  # Show first 10
            print(f"   {i+1}. {elem['name']} at {elem['path']}")
            print(f"      Value: '{elem['value']}'")
            print(f"      Has children: {elem['has_children']}")
        
        if len(empty_elements) > 10:
            print(f"   ... and {len(empty_elements) - 10} more")
    
    # Show non-empty elements for comparison
    if non_empty_elements:
        print(f"\n4. Non-empty target elements (for comparison):")
        for i, elem in enumerate(non_empty_elements[:5]):  # Show first 5
            print(f"   {i+1}. {elem['name']} at {elem['path']}")
            print(f"      Value: '{elem['value']}'")
    
    # Investigate the specific paths mentioned in the question
    specific_paths = [
        "/IATA_OrderViewRS/Response/cns:Order[1]/cns:OrderItem[1]/cns:FareDetail[1]/cns:FareComponent/cns:Price/cns:TaxSummary/cns:Tax/cns:TaxTypeCode",
        "/IATA_OrderViewRS/Response/cns:Order[1]/cns:OrderItem[1]/cns:FareDetail[1]/cns:FarePriceType/cns:Price/cns:TaxSummary/cns:Tax/cns:TaxTypeCode",
        "/IATA_OrderViewRS/Response/cns:Order[1]/cns:OrderItem[1]/cns:FareDetail[1]/cns:Price/cns:Discount/cns:DiscountContext/cns:PrefLevel/cns:PrefLevelCode"
    ]
    
    print(f"\n5. Checking specific paths mentioned:")
    
    for path in specific_paths:
        print(f"\n   Path: {path}")
        
        # Check if this path exists in our found elements
        matching_elements = [elem for elem in empty_elements + non_empty_elements 
                           if path.replace('cns:', '').replace('[1]', '') in elem['path']]
        
        if matching_elements:
            for elem in matching_elements:
                print(f"   Found: {elem['name']} = '{elem['value']}' at {elem['path']}")
        else:
            print(f"   ❌ Path not found in generated XML")
    
    # Check schema for these element types
    print(f"\n6. Checking schema for element type information...")
    
    for element_name in target_elements:
        print(f"\n   Element: {element_name}")
        
        # Find this element in schema
        found_elements = []
        for name, element in generator.schema.maps.elements.items():
            if element_name in str(name):
                found_elements.append((name, element))
        
        if found_elements:
            for name, element in found_elements[:3]:  # Show first 3
                print(f"   Schema element: {name}")
                print(f"   Type: {element.type}")
                
                # Check constraints
                constraints = generator._extract_type_constraints(element.type)
                print(f"   Constraints: {constraints}")
                
                if 'enum_values' in constraints:
                    print(f"   ✅ Has enumeration: {constraints['enum_values']}")
                else:
                    print(f"   ❌ No enumeration constraints found")
        else:
            print(f"   ❌ Element {element_name} not found in schema")
    
    return empty_elements

if __name__ == "__main__":
    empty_elements = investigate_empty_elements()
    
    if empty_elements:
        print(f"\n🎯 Summary: Found {len(empty_elements)} empty target elements")
        print("This suggests our enumeration fixes may not be covering all code paths.")
    else:
        print(f"\n🎉 All target elements have non-empty values!")