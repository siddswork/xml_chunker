#!/usr/bin/env python3
"""
Debug complex types with simple content detection.
"""

import xmlschema

def debug_complex_simple_content():
    """Debug why complex types with simple content aren't being detected."""
    
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OffersAndOrdersCommonTypes.xsd'
    
    try:
        schema = xmlschema.XMLSchema(schema_path)
        
        # Find MeasureType specifically
        if 'MeasureType' in schema.types:
            measure_type = schema.types['MeasureType']
            print(f"Found MeasureType: {measure_type}")
            print(f"Is complex: {measure_type.is_complex()}")
            print(f"Has content_type: {hasattr(measure_type, 'content_type')}")
            
            if hasattr(measure_type, 'content_type'):
                print(f"Content type: {measure_type.content_type}")
                
            if hasattr(measure_type, 'content'):
                print(f"Content: {measure_type.content}")
                print(f"Content type: {type(measure_type.content)}")
                
            print(f"Attributes: {getattr(measure_type, 'attributes', {})}")
            
            # Check for simple content extension
            if hasattr(measure_type, 'content') and measure_type.content:
                print(f"Content has base_type: {hasattr(measure_type.content, 'base_type')}")
                if hasattr(measure_type.content, 'base_type'):
                    print(f"Base type: {measure_type.content.base_type}")
        else:
            print("MeasureType not found in types")
            print(f"Available types: {list(schema.types.keys())[:10]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_complex_simple_content()