#!/usr/bin/env python3
"""
Debug by calling _create_element_dict directly to get the real traceback.
"""

from utils.xml_generator import XMLGenerator
import traceback

def debug_direct_creation():
    """Debug by calling the element creation directly."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        generator.user_choices = {"Response": True}
        generator.user_unbounded_counts = {}
        
        print("🔍 Direct Element Dictionary Creation Debug")
        print("=" * 60)
        
        # Get the root element
        root_name = "IATA_OrderViewRS" 
        root_element = generator.schema.elements.get(root_name)
        
        if root_element is None:
            print(f"❌ Root element '{root_name}' not found")
            return
        
        print(f"✅ Found root element: {root_element}")
        
        # Reset processed types
        generator.processed_types = set()
        
        # Call _create_element_dict directly to get real traceback
        print("Calling _create_element_dict directly...")
        xml_dict = generator._create_element_dict(root_element, root_name)
        
        print(f"✅ Success! Generated dictionary with {len(xml_dict)} keys")
        print(f"Keys: {list(xml_dict.keys())}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_direct_creation()