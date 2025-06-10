#!/usr/bin/env python3
"""
Explore the schema structure to understand where the types are defined.
"""

from utils.xml_generator import XMLGenerator

def explore_schema():
    """Explore the schema structure to find where types are defined."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Schema Structure Exploration")
        print("=" * 50)
        
        # Check main schema
        print(f"Main schema: {generator.schema}")
        print(f"Target namespace: {generator.schema.target_namespace}")
        print(f"Namespaces: {generator.schema.namespaces}")
        
        # Check for maps that might contain types
        if hasattr(generator.schema, 'maps'):
            print(f"\nSchema maps: {generator.schema.maps}")
            
        # Check if there are imported schemas
        if hasattr(generator.schema, 'imports'):
            print(f"\nImports: {generator.schema.imports}")
            
        # Look for cns:SuffixName specifically
        print(f"\n🔍 Looking for SuffixName Element")
        print("=" * 40)
        
        # Check all elements
        for elem_name, element in generator.schema.elements.items():
            if 'SuffixName' in str(elem_name):
                print(f"Found: {elem_name} -> {element}")
                print(f"Element type: {element.type}")
                if hasattr(element.type, 'facets'):
                    print(f"Type facets: {element.type.facets}")
                    
                # Test constraint extraction on this element's type
                constraints = generator._extract_type_constraints(element.type)
                print(f"Constraints: {constraints}")
                break
        
        # Look for any cns prefixed elements
        print(f"\n🔍 CNS Prefixed Elements (sample)")
        print("=" * 40)
        count = 0
        for elem_name, element in generator.schema.elements.items():
            if 'cns:' in str(elem_name) or hasattr(element, 'qname'):
                print(f"  {elem_name}: {element}")
                count += 1
                if count >= 5:  # Show first 5
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_schema()