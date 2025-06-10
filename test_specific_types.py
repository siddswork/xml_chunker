#!/usr/bin/env python3
"""
Test specific type detection for boolean, numeric and other simple types.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

def test_type_detection():
    """Test type detection for specific XSD simple types."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Testing Simple Type Detection")
        print("=" * 50)
        
        # Get all types from schema to find simple types
        all_types = generator.schema.types
        
        test_types = []
        for type_name, type_obj in all_types.items():
            if hasattr(type_obj, 'is_simple') and type_obj.is_simple():
                test_types.append((type_name, type_obj))
                if len(test_types) >= 10:  # Test first 10 simple types
                    break
        
        for type_name, type_obj in test_types:
            print(f"\nType: {type_name}")
            print(f"Type object: {type_obj}")
            print(f"Type string: {str(type_obj)}")
            
            # Check primitive type
            if hasattr(type_obj, 'primitive_type'):
                print(f"Primitive type: {type_obj.primitive_type}")
            
            # Test constraint extraction
            constraints = generator._extract_type_constraints(type_obj)
            print(f"Constraints: {constraints}")
            
            # Test generator selection
            type_generator = generator.type_factory.create_generator(type_obj, constraints)
            print(f"Generator: {type(type_generator).__name__}")
            
            # Test value generation
            try:
                value = type_generator.generate(type_name, constraints)
                print(f"Generated: {repr(value)} (type: {type(value).__name__})")
            except Exception as e:
                print(f"Generation error: {e}")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_type_detection()