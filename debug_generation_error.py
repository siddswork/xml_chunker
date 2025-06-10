#!/usr/bin/env python3
"""
Debug the generation error to find where bool.get() is being called.
"""

from utils.xml_generator import XMLGenerator
import traceback
import sys

def debug_generation():
    """Debug the XML generation error."""
    try:
        generator = XMLGenerator("resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd")
        
        # Try to generate just a small structure first
        print("Testing basic generation...")
        
        # Get root elements
        root_elements = list(generator.schema.elements.keys())
        print(f"Root elements: {root_elements[:3]}")
        
        # Test just element creation
        first_element = list(generator.schema.elements.values())[0]
        print(f"Testing element: {first_element.local_name}")
        
        # Try creating element dict
        try:
            result = generator._create_element_dict(first_element, "", 0)
            print(f"Element dict type: {type(result)}")
            print(f"Element dict content: {str(result)[:200]}...")
        except Exception as e:
            print(f"Error in _create_element_dict: {e}")
            traceback.print_exc()
            
            # Check if it's the boolean issue
            if "bool" in str(e) and "get" in str(e):
                print("\n🔍 Found the boolean.get() issue!")
                print("This happens when a boolean value is returned but dict.get() is expected")
                return
    
    except Exception as e:
        print(f"Setup error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_generation()