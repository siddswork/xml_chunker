#!/usr/bin/env python3
"""
Debug why some elements are generating as empty.
"""

from utils.xml_generator import XMLGenerator
import logging

# Set up logging to capture debug info
logging.basicConfig(level=logging.DEBUG)

def debug_empty_element_generation():
    """Debug why some decimal elements are empty."""
    
    print("🔍 Debugging Empty Element Generation")
    print("=" * 50)
    
    # Monkey patch the _create_element_dict method to add logging
    generator = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    original_method = generator._create_element_dict
    
    def debug_create_element_dict(element, path="", depth=0):
        element_name = getattr(element, 'local_name', 'Unknown')
        
        # Only log elements we're interested in
        if any(name in element_name for name in ['Amount', 'Rate', 'Measure']):
            print(f"{'  ' * depth}Processing {element_name} at {path}")
            print(f"{'  ' * depth}  Type: {element.type}")
            print(f"{'  ' * depth}  Is simple: {element.type.is_simple() if element.type else 'No type'}")
            print(f"{'  ' * depth}  Is complex: {element.type.is_complex() if element.type else 'No type'}")
            
            if element.type and element.type.is_complex():
                has_attrs = bool(getattr(element.type, 'attributes', None))
                print(f"{'  ' * depth}  Has attributes: {has_attrs}")
                
                content = getattr(element.type, 'content', None)
                print(f"{'  ' * depth}  Content: {content}")
                
                if content:
                    is_simple_content = hasattr(content, 'is_simple') and content.is_simple()
                    print(f"{'  ' * depth}  Content is simple: {is_simple_content}")
        
        result = original_method(element, path, depth)
        
        # Log the result for our target elements
        if any(name in element_name for name in ['Amount', 'Rate', 'Measure']):
            print(f"{'  ' * depth}  Result: {result}")
            print(f"{'  ' * depth}  Result type: {type(result)}")
            if isinstance(result, dict) and not result:
                print(f"{'  ' * depth}  ⚠️  EMPTY DICT GENERATED!")
        
        return result
    
    # Replace the method
    generator._create_element_dict = debug_create_element_dict
    
    # Generate a small test XML focusing on a problematic area
    print("Generating test XML...")
    xml_content = generator.generate_dummy_xml_with_choices({'Response': True}, {})
    
    print(f"Generated {len(xml_content)} characters")
    
    # Check for empty Amount elements in result
    import re
    empty_amounts = re.findall(r'<[^>]*Amount[^>]*/>', xml_content)
    print(f"Found {len(empty_amounts)} empty Amount elements")
    
    if empty_amounts:
        print("Examples:")
        for elem in empty_amounts[:5]:
            print(f"  {elem}")

if __name__ == "__main__":
    debug_empty_element_generation()