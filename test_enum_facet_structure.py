#!/usr/bin/env python3
"""
Test the structure of XsdEnumerationFacets to understand how to extract values.
"""

from utils.xml_generator import XMLGenerator

def test_enum_facet_structure():
    """Test how to extract values from XsdEnumerationFacets."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        # Get ActionCodeContentType for testing
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                if 'ActionCodeContentType' in imported_schema.types:
                    type_obj = imported_schema.types['ActionCodeContentType']
                    
                    print("🔍 XsdEnumerationFacets Structure Analysis")
                    print("=" * 50)
                    
                    enum_facet = type_obj.facets['{http://www.w3.org/2001/XMLSchema}enumeration']
                    print(f"Facet object: {enum_facet}")
                    print(f"Facet type: {type(enum_facet).__name__}")
                    print(f"Facet dir: {[attr for attr in dir(enum_facet) if not attr.startswith('_')]}")
                    
                    # Try different ways to get the values
                    print(f"\nTrying different access methods:")
                    
                    try:
                        print(f"facet.value: {enum_facet.value}")
                    except:
                        print(f"facet.value: Failed")
                    
                    try:
                        print(f"facet.enumeration: {enum_facet.enumeration}")
                    except:
                        print(f"facet.enumeration: Failed")
                    
                    try:
                        print(f"list(facet): {list(enum_facet)}")
                    except:
                        print(f"list(facet): Failed")
                    
                    try:
                        if hasattr(enum_facet, '__iter__'):
                            values = [str(item) for item in enum_facet]
                            print(f"iterate facet: {values}")
                    except Exception as e:
                        print(f"iterate facet: Failed - {e}")
                    
                    try:
                        if hasattr(enum_facet, 'values'):
                            print(f"facet.values: {enum_facet.values}")
                    except:
                        print(f"facet.values: Failed")
                    
                    try:
                        if hasattr(enum_facet, 'items'):
                            print(f"facet.items(): {list(enum_facet.items())}")
                    except:
                        print(f"facet.items(): Failed")
                        
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enum_facet_structure()