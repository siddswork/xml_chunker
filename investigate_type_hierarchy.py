#!/usr/bin/env python3
"""
Investigate the type hierarchy to understand why some enum types are not working.
"""

from utils.xml_generator import XMLGenerator

def investigate_type_hierarchy():
    """Investigate the relationship between ContentType and Type definitions."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Investigating Type Hierarchy for Enum Elements")
        print("=" * 60)
        
        # Look for the relationship between different type patterns
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                
                # Find pairs like TaxTypeCodeContentType and TaxTypeCodeType
                type_pairs = {}
                for type_name in imported_schema.types.keys():
                    if type_name.endswith('ContentType'):
                        base_name = type_name[:-11]  # Remove 'ContentType'
                        corresponding_type = base_name + 'Type'
                        if corresponding_type in imported_schema.types:
                            type_pairs[base_name] = {
                                'content_type': type_name,
                                'type': corresponding_type
                            }
                
                print(f"Found {len(type_pairs)} type pairs:")
                
                for base_name, pair in list(type_pairs.items())[:5]:  # Show first 5
                    print(f"\n🔍 Analyzing: {base_name}")
                    
                    content_type = imported_schema.types[pair['content_type']]
                    regular_type = imported_schema.types[pair['type']]
                    
                    print(f"   {pair['content_type']}: {content_type}")
                    print(f"   {pair['type']}: {regular_type}")
                    
                    # Check which one has enumeration facets
                    content_constraints = generator._extract_type_constraints(content_type)
                    regular_constraints = generator._extract_type_constraints(regular_type)
                    
                    print(f"   Content type constraints: {content_constraints}")
                    print(f"   Regular type constraints: {regular_constraints}")
                    
                    # Test generation for both
                    content_gen = generator.type_factory.create_generator(content_type, content_constraints)
                    regular_gen = generator.type_factory.create_generator(regular_type, regular_constraints)
                    
                    content_value = content_gen.generate(pair['content_type'], content_constraints)
                    regular_value = regular_gen.generate(pair['type'], regular_constraints)
                    
                    print(f"   Content type generates: '{content_value}' ({type(content_gen).__name__})")
                    print(f"   Regular type generates: '{regular_value}' ({type(regular_gen).__name__})")
                    
                    if content_constraints.get('enum_values') and not regular_constraints.get('enum_values'):
                        print(f"   ⚠ ContentType has enums but Type doesn't!")
                        
                        # Check if regular type is based on content type
                        if hasattr(regular_type, 'base_type'):
                            print(f"   Regular type base: {regular_type.base_type}")
                        if hasattr(regular_type, 'content_type'):
                            print(f"   Regular type content: {regular_type.content_type}")
                
                # Now check which types are actually used by elements
                print(f"\n🔍 Checking Element Usage")
                print("=" * 40)
                
                element_type_usage = {}
                for elem_name, element in imported_schema.elements.items():
                    if hasattr(element.type, 'name') and element.type.name:
                        type_name = element.type.name
                        if 'TaxTypeCode' in type_name or 'JourneyStageCode' in type_name:
                            element_type_usage[elem_name] = type_name
                
                print("Elements and their types:")
                for elem_name, type_name in element_type_usage.items():
                    print(f"   {elem_name} -> {type_name}")
                    
                    # Test generation for this specific element
                    if type_name in imported_schema.types:
                        type_obj = imported_schema.types[type_name]
                        constraints = generator._extract_type_constraints(type_obj)
                        type_gen = generator.type_factory.create_generator(type_obj, constraints)
                        value = type_gen.generate(elem_name, constraints)
                        
                        if value == "" or value == "ABC123":
                            print(f"      ❌ Problematic generation: '{value}'")
                        else:
                            print(f"      ✅ Good generation: '{value}'")
                            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_type_hierarchy()