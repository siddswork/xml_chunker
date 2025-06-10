#!/usr/bin/env python3
"""
Debug script to understand why type detection is failing and causing more validation errors.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def debug_type_detection():
    """Debug type detection issues in the refactored generator."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Get some elements to test type detection
        root_elements = list(generator.schema.elements.values())[:5]
        
        print("🔍 Type Detection Analysis")
        print("=" * 50)
        
        for element in root_elements:
            if hasattr(element, 'type') and element.type:
                type_obj = element.type
                element_name = element.local_name
                
                print(f"\nElement: {element_name}")
                print(f"Type object: {type_obj}")
                print(f"Type string: {str(type_obj).lower()}")
                
                # Test constraint extraction
                constraints = generator._extract_type_constraints(type_obj)
                print(f"Constraints: {constraints}")
                
                # Test type factory detection
                type_generator = generator.type_factory.create_generator(type_obj, constraints)
                print(f"Generator chosen: {type(type_generator).__name__}")
                
                # Test value generation
                try:
                    value = type_generator.generate(element_name, constraints)
                    print(f"Generated value: {repr(value)} (type: {type(value).__name__})")
                except Exception as e:
                    print(f"Generation error: {e}")
                
                print("-" * 30)
        
        # Test specific problematic types
        print("\n🔍 Testing Boolean Type Detection")
        print("=" * 50)
        
        # Look for boolean-like elements
        for elem_name, element in generator.schema.elements.items():
            if 'ind' in str(elem_name).lower() or 'flag' in str(elem_name).lower():
                print(f"Boolean candidate: {elem_name}")
                if hasattr(element, 'type') and element.type:
                    type_str = str(element.type).lower()
                    print(f"  Type: {type_str}")
                    
                    # Check if it's being detected as boolean
                    constraints = generator._extract_type_constraints(element.type)
                    type_gen = generator.type_factory.create_generator(element.type, constraints)
                    print(f"  Generator: {type(type_gen).__name__}")
                    break
                    
    except Exception as e:
        print(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_type_detection()