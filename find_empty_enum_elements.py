#!/usr/bin/env python3
"""
Find elements that might be generating empty strings instead of enum values.
"""

from utils.xml_generator import XMLGenerator
import re

def find_empty_enum_elements():
    """Find elements that should be enums but are generating empty strings."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Finding Elements That Should Be Enums But Generate Empty Strings")
        print("=" * 70)
        
        # Generate XML multiple times to catch intermittent issues
        for attempt in range(3):
            print(f"\n🧪 Attempt {attempt + 1}:")
            
            xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
            
            # Find all empty elements in XML
            empty_pattern = r'<([^>]+)><\/[^>]+>'
            empty_matches = re.findall(empty_pattern, xml_data)
            
            if empty_matches:
                print(f"   Found {len(empty_matches)} empty elements:")
                
                # Check if any of these might be enumeration types
                potential_enum_elements = []
                for match in empty_matches[:10]:  # Check first 10
                    element_name = match.split()[-1] if ' ' in match else match
                    # Clean up namespace prefixes and attributes
                    clean_name = element_name.split(':')[-1]
                    
                    # Check if this element name suggests it should be an enumeration
                    enum_indicators = ['Code', 'Type', 'Status', 'Category', 'Kind', 'Mode']
                    if any(indicator in clean_name for indicator in enum_indicators):
                        potential_enum_elements.append(clean_name)
                
                if potential_enum_elements:
                    print(f"   Potential enum elements that are empty: {potential_enum_elements}")
                else:
                    print(f"   No obvious enum elements found empty")
            else:
                print(f"   No empty elements found")
            
            # Also look for very short generic values that might indicate fallback
            generic_pattern = r'<([^>]*(?:Code|Type)[^>]*)>([^<]{1,10})</[^>]*>'
            generic_matches = re.findall(generic_pattern, xml_data)
            
            if generic_matches:
                print(f"   Elements with short generic values:")
                for element, value in generic_matches[:5]:
                    clean_element = element.split()[-1] if ' ' in element else element
                    clean_element = clean_element.split(':')[-1]
                    if value in ['ABC123', 'SampleText', 'Sample']:
                        print(f"     {clean_element}: '{value}' (likely fallback)")
        
        # Now let's specifically test the problematic elements you mentioned
        print(f"\n🎯 Testing Specific Problematic Elements")
        print("=" * 50)
        
        problematic_types = ['TaxTypeCode', 'JourneyStageCode']
        
        # Search for these types in the schema
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for type_name, type_obj in imported_schema.types.items():
                    if any(prob in type_name for prob in problematic_types):
                        print(f"\n🔍 Testing type: {type_name}")
                        
                        # Test multiple generations to catch inconsistencies
                        for i in range(5):
                            constraints = generator._extract_type_constraints(type_obj)
                            type_gen = generator.type_factory.create_generator(type_obj, constraints)
                            value = type_gen.generate(type_name, constraints)
                            
                            if value == "" or value is None:
                                print(f"   Generation {i+1}: ❌ EMPTY VALUE GENERATED!")
                                print(f"   Constraints: {constraints}")
                                print(f"   Generator: {type(type_gen).__name__}")
                            elif len(value) < 3:
                                print(f"   Generation {i+1}: ⚠ Very short value: '{value}'")
                            else:
                                print(f"   Generation {i+1}: ✅ '{value}'")
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_empty_enum_elements()