#!/usr/bin/env python3
"""
Debug empty value generation to find the source of empty decimal elements.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import TypeGeneratorFactory
import xmlschema

def debug_empty_value_creation():
    """Track down where empty values are being created."""
    
    print("🔍 Debugging Empty Value Creation")
    print("=" * 60)
    
    # Create generator
    gen = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    
    # Track empty values during dictionary creation
    original_create_element = gen._create_element_dict
    empty_elements = []
    
    def track_empty_elements(element, path="", depth=0):
        result = original_create_element(element, path, depth)
        
        # Check if result is None, empty string, or dict with empty values
        if result is None or result == "":
            empty_elements.append({
                'element_name': element.local_name if hasattr(element, 'local_name') else str(element),
                'path': path,
                'result': result,
                'element_type': str(element.type) if hasattr(element, 'type') else 'unknown'
            })
            print(f"🚨 Empty element: {element.local_name} at {path} -> {repr(result)}")
        
        # Check if dict has empty values
        if isinstance(result, dict):
            for k, v in result.items():
                if v is None or v == "":
                    empty_elements.append({
                        'element_name': f"{element.local_name if hasattr(element, 'local_name') else str(element)}.{k}",
                        'path': f"{path}.{k}",
                        'result': v,
                        'element_type': 'dict_value'
                    })
                    print(f"🚨 Empty dict value: {k} = {repr(v)} in {path}")
        
        return result
    
    gen._create_element_dict = track_empty_elements
    
    # Track type generation
    original_generate_value = gen._generate_value_for_type
    type_generations = []
    
    def track_type_generation(type_name, element_name=""):
        result = original_generate_value(type_name, element_name)
        
        type_generations.append({
            'type_name': str(type_name),
            'element_name': element_name,
            'result': result,
            'result_type': type(result).__name__
        })
        
        if result is None or result == "":
            print(f"🚨 Empty type generation: {element_name} ({type_name}) -> {repr(result)}")
        
        return result
    
    gen._generate_value_for_type = track_type_generation
    
    print("Generating test XML...")
    try:
        xml = gen.generate_dummy_xml_with_choices({'Response': True}, {'OrderTotalAmount': 1})
        print(f"Generated XML: {len(xml)} characters")
        print(f"Empty elements detected: {len(empty_elements)}")
        print(f"Type generations: {len(type_generations)}")
        
        # Show summary
        if empty_elements:
            print("\n📊 Empty Elements Summary:")
            for elem in empty_elements[:10]:  # Show first 10
                print(f"   {elem['element_name']} -> {repr(elem['result'])}")
        
        # Check for empty decimal type generations
        empty_decimals = [t for t in type_generations if (t['result'] is None or t['result'] == "") and 'decimal' in t['type_name'].lower()]
        print(f"\nEmpty decimal generations: {len(empty_decimals)}")
        
        if empty_decimals:
            print("📊 Empty Decimal Type Generations:")
            for elem in empty_decimals[:5]:
                print(f"   {elem['element_name']} ({elem['type_name']}) -> {repr(elem['result'])}")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_empty_value_creation()