#!/usr/bin/env python3
"""
Test constraint extraction and generation for SupplementNameType.
"""

from utils.xml_generator import XMLGenerator

def test_supplement_name():
    """Test constraint extraction for SupplementNameType."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Find SupplementNameType
        supplement_type = generator.schema.types.get('SupplementNameType')
        if supplement_type:
            print(f"Found SupplementNameType: {supplement_type}")
            print(f"Facets: {supplement_type.facets}")
            
            # Test constraint extraction
            constraints = generator._extract_type_constraints(supplement_type)
            print(f"Extracted constraints: {constraints}")
            
            # Test generator selection
            type_gen = generator.type_factory.create_generator(supplement_type, constraints)
            print(f"Generator: {type(type_gen).__name__}")
            
            # Test value generation
            value = type_gen.generate("SuffixName", constraints)
            print(f"Generated: '{value}' (length: {len(value)})")
            
            # Test with different element names
            for name in ["SuffixName", "TitleName"]:
                value = type_gen.generate(name, constraints)
                print(f"Generated for {name}: '{value}' (length: {len(value)})")
                
        else:
            print("SupplementNameType not found in schema types")
            # List some types to debug
            print("Available types:", list(generator.schema.types.keys())[:10])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supplement_name()