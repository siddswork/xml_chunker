#!/usr/bin/env python3
"""
Debug specific enumeration errors that are still occurring with empty strings.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re

def debug_specific_enum_errors():
    """Debug the specific enumeration elements that are still generating empty strings."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Debugging Specific Enumeration Elements")
        print("=" * 60)
        
        # Generate XML and validate to find exact errors
        xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
        
        try:
            generator.schema.validate(xml_data)
            print("✅ XML is valid - no errors found")
        except xmlschema.XMLSchemaException as e:
            error_text = str(e)
            
            # Look for the specific enumeration errors mentioned
            problematic_elements = ['TaxTypeCode', 'JourneyStageCode']
            
            print("🔍 Searching for enumeration errors:")
            
            lines = error_text.split('\n')
            for i, line in enumerate(lines):
                if any(elem in line for elem in problematic_elements) and 'XsdEnumerationFacets' in line:
                    print(f"\n❌ Found enumeration error:")
                    print(f"   {line}")
                    
                    # Extract the enumeration values from the error
                    enum_match = re.search(r"XsdEnumerationFacets\(\[([^\]]+)\]", line)
                    if enum_match:
                        enum_values_str = enum_match.group(1)
                        enum_values = [val.strip("' \"") for val in enum_values_str.split(', ')]
                        print(f"   Expected values: {enum_values}")
                    
                    # Show context
                    if i > 0:
                        print(f"   Context: {lines[i-1]}")
        
        # Now let's find these elements in the XSD and test their type generation
        print(f"\n🔍 Analyzing Element Type Definitions")
        print("=" * 50)
        
        # Search for TaxTypeCode and JourneyStageCode in schemas
        target_elements = ['TaxTypeCode', 'JourneyStageCode']
        
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                for elem_name, element in imported_schema.elements.items():
                    if any(target in elem_name for target in target_elements):
                        print(f"\n🔍 Found element: {elem_name}")
                        print(f"   Element type: {element.type}")
                        
                        if hasattr(element.type, 'name'):
                            print(f"   Type name: {element.type.name}")
                            
                            # Find the type definition
                            type_name = element.type.name
                            if type_name in imported_schema.types:
                                type_def = imported_schema.types[type_name]
                                print(f"   Type definition: {type_def}")
                                
                                # Test constraint extraction
                                constraints = generator._extract_type_constraints(type_def)
                                print(f"   Extracted constraints: {constraints}")
                                
                                # Test type generation
                                type_gen = generator.type_factory.create_generator(type_def, constraints)
                                generated_value = type_gen.generate(elem_name, constraints)
                                print(f"   Generated value: '{generated_value}'")
                                
                                if generated_value == "" or generated_value is None:
                                    print(f"   ❌ PROBLEM: Generating empty value!")
                                elif constraints.get('enum_values') and generated_value in constraints['enum_values']:
                                    print(f"   ✅ Generated value is valid")
                                else:
                                    print(f"   ⚠ Generated value might not be in enum list")
        
        # Also search in main schema
        for elem_name, element in generator.schema.elements.items():
            if any(target in elem_name for target in target_elements):
                print(f"\n🔍 Found in main schema: {elem_name}")
                # Similar analysis...
        
        # Search for these elements in the generated XML
        print(f"\n🔍 Searching Generated XML for Problem Elements")
        print("=" * 50)
        
        for target in target_elements:
            # Find all occurrences of this element in XML
            pattern = f'<[^>]*{target}[^>]*>([^<]*)</[^>]*{target}[^>]*>'
            matches = re.findall(pattern, xml_data)
            
            if matches:
                print(f"\n{target} values in XML:")
                for i, match in enumerate(matches[:5]):  # Show first 5
                    print(f"   {i+1}. '{match}' (length: {len(match)})")
                    if match == "":
                        print(f"      ❌ EMPTY STRING FOUND!")
            else:
                print(f"\n{target}: No matches found in XML")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_enum_errors()