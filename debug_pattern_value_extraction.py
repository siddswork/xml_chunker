#!/usr/bin/env python3
"""
Debug why pattern values are coming through as None in the constraint extraction.
"""

import xmlschema

def debug_pattern_value_extraction():
    """Debug pattern value extraction in detail."""
    
    print("🔍 Debug Pattern Value Extraction")
    print("=" * 60)
    
    common_types_path = 'resource/21_3_5_distribution_schemas/IATA_OffersAndOrdersCommonTypes.xsd'
    
    try:
        schema = xmlschema.XMLSchema(common_types_path)
    except Exception as e:
        print(f"Failed to load schema: {e}")
        return
    
    print(f"1. Finding pattern types and examining facet objects in detail:")
    print("-" * 60)
    
    pattern_types = []
    for type_name, type_obj in schema.types.items():
        if hasattr(type_obj, 'facets') and type_obj.facets:
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                if local_name == 'pattern':
                    pattern_types.append((type_name, type_obj, facet_name, facet))
    
    print(f"Found {len(pattern_types)} pattern types")
    
    if pattern_types:
        for i, (type_name, type_obj, facet_name, facet) in enumerate(pattern_types[:5]):
            print(f"\n   Pattern type {i+1}: {type_name}")
            print(f"   Facet name: {repr(facet_name)} (type: {type(facet_name)})")
            print(f"   Facet object: {repr(facet)} (type: {type(facet)})")
            print(f"   Facet dir: {[attr for attr in dir(facet) if not attr.startswith('_')]}")
            
            # Try different ways to get the value
            if hasattr(facet, 'value'):
                print(f"   facet.value: {repr(facet.value)}")
            if hasattr(facet, 'pattern'):
                print(f"   facet.pattern: {repr(facet.pattern)}")
            if hasattr(facet, 'patterns'):
                print(f"   facet.patterns: {repr(facet.patterns)}")
            if hasattr(facet, 'regexps'):
                print(f"   facet.regexps: {repr(facet.regexps)}")
            if hasattr(facet, '_value'):
                print(f"   facet._value: {repr(facet._value)}")
            
            # Try to convert to string
            try:
                str_value = str(facet)
                print(f"   str(facet): {repr(str_value)}")
            except:
                print(f"   str(facet): Failed")
            
            # Check if this is a collection of patterns
            if hasattr(facet, '__iter__') and not isinstance(facet, str):
                try:
                    items = list(facet)
                    print(f"   facet items: {items}")
                    for j, item in enumerate(items[:3]):
                        print(f"     item {j}: {repr(item)} (type: {type(item)})")
                        if hasattr(item, 'value'):
                            print(f"       item.value: {repr(item.value)}")
                except:
                    print(f"   facet iteration: Failed")
    
    print(f"\n2. Testing our constraint extraction logic on these pattern types:")
    print("-" * 60)
    
    from utils.xml_generator import XMLGenerator
    
    # Create a dummy generator to use the extraction method
    main_schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    gen = XMLGenerator(main_schema_path)
    
    for i, (type_name, type_obj, facet_name, facet) in enumerate(pattern_types[:3]):
        print(f"\n   Testing constraint extraction for: {type_name}")
        
        # Manually step through our extraction logic
        constraints = {}
        print(f"   Starting constraints: {constraints}")
        
        if hasattr(type_obj, 'facets') and type_obj.facets:
            print(f"   Type has facets: {len(type_obj.facets)}")
            
            for fn, f in type_obj.facets.items():
                if fn is None:
                    print(f"     Skipping None facet name")
                    continue
                
                local_name = fn.split('}')[-1] if '}' in str(fn) else str(fn)
                print(f"     Processing facet: {fn} -> {local_name}")
                
                if local_name == 'pattern':
                    print(f"       This is a pattern facet!")
                    print(f"       Facet object: {f}")
                    print(f"       Facet.value: {getattr(f, 'value', 'NO VALUE ATTR')}")
                    
                    if hasattr(f, 'value'):
                        constraints['pattern'] = f.value
                        print(f"       Set pattern to: {repr(f.value)}")
                    else:
                        print(f"       No value attribute, trying alternatives...")
                        # Try other attributes
                        if hasattr(f, 'pattern'):
                            constraints['pattern'] = f.pattern
                            print(f"       Set pattern from .pattern: {repr(f.pattern)}")
                        elif hasattr(f, 'patterns'):
                            patterns = f.patterns
                            if patterns:
                                constraints['pattern'] = patterns[0] if isinstance(patterns, list) else patterns
                                print(f"       Set pattern from .patterns: {repr(constraints['pattern'])}")
                        else:
                            print(f"       No pattern value found!")
        
        print(f"   Final constraints: {constraints}")
        
        # Compare with our method
        our_constraints = gen._extract_type_constraints(type_obj)
        print(f"   Our method result: {our_constraints}")
    
    print(f"\n3. Direct XSD file examination:")
    print("-" * 60)
    
    # Look at the raw XSD to see how patterns are defined
    from lxml import etree
    
    try:
        with open(common_types_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        root = etree.fromstring(content.encode('utf-8'))
        
        # Find pattern elements
        patterns = root.xpath('//xs:pattern', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        print(f"   Found {len(patterns)} <xs:pattern> elements in XSD")
        
        for i, pattern in enumerate(patterns[:5]):
            value = pattern.get('value')
            parent = pattern.getparent()
            grandparent = parent.getparent() if parent is not None else None
            type_name = grandparent.get('name') if grandparent is not None else 'Unknown'
            
            print(f"   Pattern {i+1}: {repr(value)} (in type: {type_name})")
            
    except Exception as e:
        print(f"   Error reading XSD file: {e}")

if __name__ == "__main__":
    debug_pattern_value_extraction()