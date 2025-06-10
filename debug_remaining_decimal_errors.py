#!/usr/bin/env python3
"""
Debug remaining empty decimal errors to understand why some elements still don't have content.
"""

import xmlschema
import re

def debug_remaining_decimal_errors():
    """Debug the remaining 568 empty decimal errors."""
    
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    xml_file = 'generated_xml_for_structural_analysis.xml'
    
    print("🔍 Debugging Remaining Empty Decimal Errors")
    print("=" * 50)
    
    try:
        schema = xmlschema.XMLSchema(schema_path)
        with open(xml_file, 'r') as f:
            xml_content = f.read()
        
        # Get decimal-related validation errors
        validation_errors = list(schema.iter_errors(xml_content))
        empty_decimal_errors = []
        
        for error in validation_errors:
            error_msg = str(error)
            if "invalid value '' for xs:decimal" in error_msg:
                empty_decimal_errors.append(error_msg)
        
        print(f"Found {len(empty_decimal_errors)} empty decimal errors")
        
        # Extract element paths and names
        element_info = []
        for error in empty_decimal_errors[:20]:  # First 20 for analysis
            path_match = re.search(r"Path: ([^\n]+)", error)
            if path_match:
                path = path_match.group(1)
                element_name = path.split('/')[-1]
                element_info.append({
                    'path': path,
                    'element': element_name,
                    'error': error[:200] + "..."
                })
        
        print(f"\n📋 Sample Empty Decimal Elements:")
        for i, info in enumerate(element_info[:10]):
            print(f"{i+1:2d}. {info['element']}")
            print(f"    Path: {info['path']}")
            
        # Analyze patterns in element names  
        element_names = [info['element'] for info in element_info]
        name_patterns = {}
        for name in element_names:
            if 'Amount' in name:
                name_patterns['Amount'] = name_patterns.get('Amount', 0) + 1
            elif 'Measure' in name:
                name_patterns['Measure'] = name_patterns.get('Measure', 0) + 1
            elif 'Rate' in name:
                name_patterns['Rate'] = name_patterns.get('Rate', 0) + 1
            elif 'Percent' in name:
                name_patterns['Percent'] = name_patterns.get('Percent', 0) + 1
            else:
                name_patterns['Other'] = name_patterns.get('Other', 0) + 1
        
        print(f"\n📊 Element Name Patterns:")
        for pattern, count in sorted(name_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} errors")
        
        # Check actual XML content for these elements
        print(f"\n🔍 XML Content Analysis:")
        sample_elements = element_names[:5]
        for elem_name in sample_elements:
            # Find actual XML tags for this element
            pattern = rf'<{re.escape(elem_name)}[^>]*>.*?</{re.escape(elem_name)}>'
            matches = re.findall(pattern, xml_content)
            if matches:
                print(f"  {elem_name}: {matches[0][:100]}...")
            else:
                # Try self-closing version
                pattern = rf'<{re.escape(elem_name)}[^/>]*/?>'
                matches = re.findall(pattern, xml_content)
                if matches:
                    print(f"  {elem_name} (self-closing): {matches[0]}")
                else:
                    print(f"  {elem_name}: NOT FOUND in XML")
        
        # Try to understand why these specific elements are empty
        print(f"\n🤔 Investigating Element Types...")
        
        # Check if these are also complex types with simple content
        for elem_name in sample_elements[:3]:
            # Remove namespace prefix for lookup
            local_name = elem_name.split(':')[-1]
            
            # Try to find element definition in schema
            found_element = None
            for schema_elem_name, schema_elem in schema.elements.items():
                if local_name in schema_elem_name:
                    found_element = schema_elem
                    break
            
            if found_element:
                print(f"  {elem_name}:")
                print(f"    Type: {found_element.type}")
                print(f"    Is complex: {found_element.type.is_complex()}")
                if found_element.type.is_complex():
                    print(f"    Has attributes: {bool(getattr(found_element.type, 'attributes', None))}")
                    print(f"    Content: {getattr(found_element.type, 'content', None)}")
                    if hasattr(found_element.type, 'content') and found_element.type.content:
                        print(f"    Content is simple: {getattr(found_element.type.content, 'is_simple', lambda: False)()}")
            else:
                print(f"  {elem_name}: Element definition not found")
        
        return {
            'total_empty_decimals': len(empty_decimal_errors),
            'element_patterns': name_patterns,
            'sample_elements': element_names[:10]
        }
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_remaining_decimal_errors()