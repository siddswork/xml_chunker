#!/usr/bin/env python3
"""
Analyze structural errors in generated XML to identify patterns and solutions.
"""

import xmlschema
import re
from collections import defaultdict

def analyze_structural_errors():
    """Comprehensive analysis of structural validation errors."""
    
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    xml_file = 'generated_xml_for_structural_analysis.xml'
    
    print("🔍 Analyzing Structural Errors")
    print("=" * 50)
    
    try:
        # Load schema and XML
        schema = xmlschema.XMLSchema(schema_path)
        with open(xml_file, 'r') as f:
            xml_content = f.read()
        
        # Get all validation errors
        validation_errors = list(schema.iter_errors(xml_content))
        print(f"Total validation errors: {len(validation_errors)}")
        
        # Categorize errors
        error_categories = defaultdict(list)
        pattern_errors = []
        empty_decimal_errors = []
        duration_errors = []
        type_mismatch_errors = []
        
        for error in validation_errors:
            error_msg = str(error)
            
            # Pattern validation errors
            if "doesn't match any pattern" in error_msg:
                pattern_match = re.search(r"pattern.*?\['([^']+)'\]", error_msg)
                if pattern_match:
                    pattern = pattern_match.group(1)
                    element_match = re.search(r"Path: ([^\n]+)", error_msg)
                    element_path = element_match.group(1) if element_match else "Unknown"
                    pattern_errors.append({
                        'pattern': pattern,
                        'path': element_path,
                        'error': error_msg[:200] + "..."
                    })
            
            # Empty decimal errors
            elif "invalid value '' for xs:decimal" in error_msg:
                element_match = re.search(r"Path: ([^\n]+)", error_msg)
                element_path = element_match.group(1) if element_match else "Unknown"
                empty_decimal_errors.append({
                    'path': element_path,
                    'error': error_msg[:200] + "..."
                })
            
            # Duration format errors
            elif "is not an xs:duration value" in error_msg:
                element_match = re.search(r"Path: ([^\n]+)", error_msg)
                element_path = element_match.group(1) if element_match else "Unknown"
                duration_errors.append({
                    'path': element_path,
                    'error': error_msg[:200] + "..."
                })
            
            # Other type mismatches
            else:
                type_mismatch_errors.append(error_msg[:150] + "...")
        
        # Report findings
        print(f"\n📊 Error Breakdown:")
        print(f"Pattern validation errors: {len(pattern_errors)}")
        print(f"Empty decimal errors: {len(empty_decimal_errors)}")
        print(f"Duration format errors: {len(duration_errors)}")
        print(f"Other type mismatches: {len(type_mismatch_errors)}")
        
        print(f"\n🎯 Pattern Error Analysis:")
        pattern_stats = defaultdict(int)
        for error in pattern_errors:
            pattern_stats[error['pattern']] += 1
        
        for pattern, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  Pattern '{pattern}': {count} errors")
            # Show example
            example = next((e for e in pattern_errors if e['pattern'] == pattern), None)
            if example:
                print(f"    Example path: {example['path']}")
        
        print(f"\n💰 Empty Decimal Error Analysis:")
        decimal_paths = set()
        for error in empty_decimal_errors:
            # Extract element name from path
            element_name = error['path'].split('/')[-1]
            decimal_paths.add(element_name)
        
        print(f"  Affected elements: {len(decimal_paths)}")
        for path in list(decimal_paths)[:10]:
            print(f"    {path}")
        
        print(f"\n⏱️ Duration Error Analysis:")
        duration_paths = set()
        for error in duration_errors:
            element_name = error['path'].split('/')[-1]
            duration_paths.add(element_name)
        
        print(f"  Affected elements: {len(duration_paths)}")
        for path in list(duration_paths)[:10]:
            print(f"    {path}")
        
        print(f"\n✅ Recommendations:")
        print("1. Fix pattern validation by generating values that match specific patterns")
        print("2. Provide proper decimal values for empty decimal elements")
        print("3. Generate valid XML duration format (e.g., PT1H30M)")
        print("4. Improve type-specific value generation in type generators")
        
        # Return detailed analysis for programmatic use
        return {
            'total_errors': len(validation_errors),
            'pattern_errors': pattern_errors,
            'empty_decimal_errors': empty_decimal_errors,
            'duration_errors': duration_errors,
            'pattern_stats': dict(pattern_stats),
            'decimal_elements': list(decimal_paths),
            'duration_elements': list(duration_paths)
        }
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

if __name__ == "__main__":
    analysis = analyze_structural_errors()
    if analysis:
        print(f"\n🎉 Analysis complete! Found {analysis['total_errors']} total errors")