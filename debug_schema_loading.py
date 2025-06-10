#!/usr/bin/env python3
"""
Debug schema loading to understand why we're not seeing types or constraints.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import os

def debug_schema_loading():
    """Debug schema loading and structure."""
    
    print("🔍 Debug Schema Loading")
    print("=" * 60)
    
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    
    print(f"1. Basic file checks:")
    print(f"   File exists: {os.path.exists(schema_path)}")
    print(f"   File size: {os.path.getsize(schema_path) if os.path.exists(schema_path) else 'N/A'} bytes")
    
    print(f"\n2. Direct xmlschema loading:")
    try:
        direct_schema = xmlschema.XMLSchema(schema_path)
        print(f"   Direct load successful: {direct_schema is not None}")
        print(f"   Target namespace: {direct_schema.target_namespace}")
        print(f"   Elements count: {len(direct_schema.elements) if direct_schema.elements else 0}")
        print(f"   Types count: {len(direct_schema.types) if direct_schema.types else 0}")
        print(f"   Groups count: {len(direct_schema.groups) if direct_schema.groups else 0}")
        
        if direct_schema.elements:
            print(f"   Element names: {list(direct_schema.elements.keys())[:5]}")
        
        if direct_schema.types:
            print(f"   Type names: {list(direct_schema.types.keys())[:10]}")
    except Exception as e:
        print(f"   Direct load failed: {e}")
    
    print(f"\n3. XMLGenerator loading:")
    try:
        gen = XMLGenerator(schema_path)
        print(f"   XMLGenerator load successful: {gen.schema is not None}")
        
        if gen.schema:
            print(f"   Target namespace: {gen.schema.target_namespace}")
            print(f"   Elements count: {len(gen.schema.elements) if gen.schema.elements else 0}")
            print(f"   Types count: {len(gen.schema.types) if gen.schema.types else 0}")
            
            if gen.schema.elements:
                print(f"   Element names: {list(gen.schema.elements.keys())}")
                
                # Look at the first element in detail
                first_element_name = list(gen.schema.elements.keys())[0]
                first_element = gen.schema.elements[first_element_name]
                print(f"\n   First element details:")
                print(f"     Name: {first_element_name}")
                print(f"     Element: {first_element}")
                print(f"     Type: {first_element.type}")
                print(f"     Type name: {getattr(first_element.type, 'name', 'No name')}")
                print(f"     Is complex: {first_element.type.is_complex() if first_element.type else 'N/A'}")
                
                if first_element.type and first_element.type.is_complex():
                    print(f"     Content: {getattr(first_element.type, 'content', 'No content')}")
                    if hasattr(first_element.type, 'content') and first_element.type.content:
                        try:
                            child_elements = list(first_element.type.content.iter_elements())
                            print(f"     Child elements count: {len(child_elements)}")
                            for i, child in enumerate(child_elements[:5]):
                                print(f"       Child {i}: {child.local_name} (type: {child.type})")
                        except Exception as e:
                            print(f"     Error iterating children: {e}")
            
            if gen.schema.types:
                print(f"\n   Sample types:")
                for i, (type_name, type_obj) in enumerate(gen.schema.types.items()):
                    if i >= 5:
                        break
                    print(f"     {type_name}: {type_obj}")
                    if hasattr(type_obj, 'facets') and type_obj.facets:
                        print(f"       Facets: {type_obj.facets}")
    except Exception as e:
        print(f"   XMLGenerator load failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n4. Looking at imported schemas:")
    try:
        # Look at the actual XSD file structure
        from lxml import etree
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse with lxml to see imports
        root = etree.fromstring(content.encode('utf-8'))
        
        # Find imports
        imports = root.xpath('//xs:import', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(imports)} imports:")
        for imp in imports:
            schema_location = imp.get('schemaLocation')
            namespace = imp.get('namespace')
            print(f"     Import: {schema_location} (namespace: {namespace})")
        
        # Find includes
        includes = root.xpath('//xs:include', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(includes)} includes:")
        for inc in includes:
            schema_location = inc.get('schemaLocation')
            print(f"     Include: {schema_location}")
        
        # Find complex types in this file
        complex_types = root.xpath('//xs:complexType', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(complex_types)} complex types in this file")
        
        # Find simple types in this file
        simple_types = root.xpath('//xs:simpleType', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(simple_types)} simple types in this file")
        
        # Find elements in this file
        elements = root.xpath('//xs:element', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(elements)} elements in this file")
        
    except Exception as e:
        print(f"   Error parsing XSD file: {e}")
    
    print(f"\n5. Check imported schema files:")
    base_dir = os.path.dirname(schema_path)
    try:
        common_types_path = os.path.join(base_dir, 'IATA_OffersAndOrdersCommonTypes.xsd')
        if os.path.exists(common_types_path):
            print(f"   Common types file exists: {common_types_path}")
            
            # Load common types directly
            common_schema = xmlschema.XMLSchema(common_types_path)
            print(f"   Common types count: {len(common_schema.types) if common_schema.types else 0}")
            
            if common_schema.types:
                print(f"   Sample common types:")
                for i, (type_name, type_obj) in enumerate(common_schema.types.items()):
                    if i >= 5:
                        break
                    print(f"     {type_name}: {type_obj}")
                    if hasattr(type_obj, 'facets') and type_obj.facets:
                        print(f"       Facets: {type_obj.facets}")
        else:
            print(f"   Common types file not found: {common_types_path}")
    except Exception as e:
        print(f"   Error checking common types: {e}")

if __name__ == "__main__":
    debug_schema_loading()