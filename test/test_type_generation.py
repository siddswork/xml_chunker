#!/usr/bin/env python3
"""
Test script to debug type generation issues.
"""

import os
from utils.xml_generator import XMLGenerator
from utils.type_generators import TypeGeneratorFactory

def test_type_generation():
    """Test type generation for problematic types."""
    
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    if not os.path.exists(xsd_path):
        print("❌ Sample XSD file not found.")
        return False
    
    print("🧪 Testing Type Generation for Problematic Types...")
    print("=" * 60)
    
    try:
        # Create generator and load schema
        generator = XMLGenerator(xsd_path)
        factory = TypeGeneratorFactory()
        
        # Test problematic types
        test_cases = [
            {
                'type_name': 'xs:decimal',
                'element_name': 'DistanceMeasure',
                'description': 'Decimal type causing empty strings'
            },
            {
                'type_name': 'xs:duration', 
                'element_name': 'Duration',
                'description': 'Duration type with invalid format'
            },
            {
                'type_name': 'xs:string',
                'element_name': 'TestString',
                'description': 'String type for comparison'
            }
        ]
        
        print("📋 Type Generation Results:")
        print()
        
        for i, test in enumerate(test_cases, 1):
            type_name = test['type_name']
            element_name = test['element_name']
            description = test['description']
            
            print(f"{i}. {description}:")
            print(f"   Type: {type_name}")
            print(f"   Element: {element_name}")
            
            # Create a mock type object to test factory
            class MockType:
                def __init__(self, name):
                    self.name = name
                    self.primitive_type = None
                    
                def __str__(self):
                    return f"XsdAtomicBuiltin(name='{self.name}')"
            
            mock_type = MockType(type_name)
            
            # Test factory generator selection
            type_generator = factory.create_generator(mock_type)
            print(f"   Generator: {type(type_generator).__name__}")
            
            # Test value generation
            generated_value = type_generator.generate(element_name)
            print(f"   Generated: '{generated_value}' (type: {type(generated_value).__name__})")
            print(f"   Empty?: {generated_value == '' or generated_value is None}")
            print(f"   Valid?: {generated_value and str(generated_value).strip()}")
            print()
        
        # Test completed successfully
        assert True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed: {e}"

if __name__ == "__main__":
    test_type_generation()
    print("🎉 Type generation test completed!")