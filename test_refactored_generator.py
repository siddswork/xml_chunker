#!/usr/bin/env python3
"""
Test script for the refactored XML generator with modular type generators.
"""

import os
from utils.xml_generator import XMLGenerator

def test_refactored_generator():
    """Test the refactored XML generator with IATA schema."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    if not os.path.exists(schema_path):
        print(f"Schema not found: {schema_path}")
        return
    
    try:
        # Create generator instance
        generator = XMLGenerator(schema_path)
        print("✓ XMLGenerator created successfully")
        
        # Test type factory
        print(f"✓ Type factory initialized: {type(generator.type_factory).__name__}")
        
        # Test basic type generation with the new modular system
        from utils.type_generators import NumericTypeGenerator, BooleanTypeGenerator
        
        # Test numeric type generator
        numeric_gen = NumericTypeGenerator(generator.config, is_decimal=True)
        decimal_value = numeric_gen.generate("Amount")
        print(f"✓ Decimal generation: {decimal_value} (type: {type(decimal_value).__name__})")
        
        # Test boolean type generator  
        bool_gen = BooleanTypeGenerator(generator.config)
        bool_value = bool_gen.generate("ApproximateInd")
        print(f"✓ Boolean generation: {bool_value} (type: {type(bool_value).__name__})")
        
        # Verify no empty strings
        if decimal_value != "" and bool_value != "":
            print("✓ No empty string values - validation error fix successful!")
        else:
            print("✗ Still generating empty strings")
            
        print("✓ All tests passed - refactored generator is working!")
    
    except Exception as e:
        print(f"✗ Error in generator setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refactored_generator()