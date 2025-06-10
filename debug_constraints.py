#!/usr/bin/env python3
"""
Debug constraint extraction to see why length limits aren't being applied.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def debug_constraints():
    """Debug constraint extraction for string elements."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Debugging Constraint Extraction")
        print("=" * 50)
        
        # Find types with length constraints
        for type_name, type_obj in generator.schema.types.items():
            if hasattr(type_obj, 'facets') and type_obj.facets:
                for facet_name, facet in type_obj.facets.items():
                    if facet_name in ['maxLength', 'minLength', 'length']:
                        print(f"\nType: {type_name}")
                        print(f"Facet: {facet_name} = {facet.value}")
                        
                        # Test constraint extraction
                        constraints = generator._extract_type_constraints(type_obj)
                        print(f"Extracted constraints: {constraints}")
                        
                        # Test generator
                        type_gen = generator.type_factory.create_generator(type_obj, constraints)
                        print(f"Generator: {type(type_gen).__name__}")
                        
                        # Test generation
                        if 'suffix' in type_name.lower():
                            value = type_gen.generate("SuffixName", constraints)
                            print(f"Generated value: '{value}' (length: {len(value)})")
                            break
        
        # Also test for any element that might generate "Sample SuffixName"
        print(f"\n🔍 Testing SuffixName Generation")
        print("=" * 30)
        
        # Find any element with 'suffix' in the name
        for elem_name, element in generator.schema.elements.items():
            if 'suffix' in elem_name.lower():
                print(f"Found element: {elem_name}")
                if hasattr(element, 'type') and element.type:
                    constraints = generator._extract_type_constraints(element.type)
                    print(f"Element constraints: {constraints}")
                    type_gen = generator.type_factory.create_generator(element.type, constraints)
                    value = type_gen.generate(elem_name, constraints)
                    print(f"Generated: '{value}' (length: {len(value)})")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_constraints()