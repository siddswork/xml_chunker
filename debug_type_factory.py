#!/usr/bin/env python3
"""
Debug type factory to see what generators are being created for decimal elements.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import TypeGeneratorFactory

def debug_type_factory():
    """Debug type factory generation for problematic elements."""
    
    print("🔍 Debugging Type Factory Generation")
    print("=" * 50)
    
    # Create generator and get schema
    gen = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    schema = gen.schema
    factory = gen.type_factory
    
    # Monkey patch the factory to log what generators are created
    original_create = factory.create_generator
    
    def debug_create_generator(xsd_type_name, constraints=None):
        # Log generation for amount/rate/measure types
        type_str = str(xsd_type_name)
        
        if any(keyword in type_str.lower() for keyword in ['amount', 'rate', 'measure', 'decimal']):
            print(f"Creating generator for: {type_str}")
            print(f"  Type: {type(xsd_type_name)}")
            print(f"  Constraints: {constraints}")
            
            if hasattr(xsd_type_name, 'primitive_type'):
                print(f"  Primitive type: {xsd_type_name.primitive_type}")
            if hasattr(xsd_type_name, 'name'):
                print(f"  Name: {xsd_type_name.name}")
            if hasattr(xsd_type_name, 'base_type'):
                print(f"  Base type: {xsd_type_name.base_type}")
        
        result = original_create(xsd_type_name, constraints)
        
        if any(keyword in type_str.lower() for keyword in ['amount', 'rate', 'measure', 'decimal']):
            print(f"  Generated: {type(result).__name__}")
            print(f"  Generator type: {result.get_type_name()}")
            
            # Test the generator
            try:
                test_value = result.generate("TestElement", constraints)
                print(f"  Test value: {test_value} (type: {type(test_value)})")
            except Exception as e:
                print(f"  Generation error: {e}")
            print()
        
        return result
    
    factory.create_generator = debug_create_generator
    
    # Generate a small test that will trigger problematic elements
    print("Generating test XML...")
    xml_content = gen.generate_dummy_xml_with_choices({'Response': True}, {})
    
    print(f"Generated {len(xml_content)} characters")

if __name__ == "__main__":
    debug_type_factory()