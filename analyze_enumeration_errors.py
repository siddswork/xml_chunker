#!/usr/bin/env python3
"""
Detailed analysis of enumeration validation errors in IATA_OrderViewRS.xsd.
"""

from utils.xml_generator import XMLGenerator
import xmlschema
import re
from collections import defaultdict

def analyze_enumeration_errors():
    """Analyze enumeration validation errors in detail."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("🔍 Detailed Enumeration Error Analysis")
    print("=" * 50)
    
    # Generate XML
    print("1. Generating XML...")
    generator.user_unbounded_counts = {}
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    if not xml_data:
        print("❌ Failed to generate XML")
        return
    
    print(f"   Generated XML: {len(xml_data)} characters")
    
    # Validate and capture enumeration errors
    print("2. Validating and capturing enumeration errors...")
    enumeration_errors = []
    
    try:
        generator.schema.validate(xml_data)
        print("✅ XML is valid - no enumeration errors!")
        return
    except xmlschema.XMLSchemaException as e:
        error_text = str(e)
        
        # Extract enumeration-specific errors
        error_lines = error_text.split('\n')
        current_error = {}
        
        for line in error_lines:
            line = line.strip()
            if not line:
                if current_error and 'enumeration' in current_error.get('reason', '').lower():
                    enumeration_errors.append(current_error)
                current_error = {}
                continue
                
            if line.startswith('failed validating'):
                # Extract element value and type
                value_match = re.search(r"'([^']*)'", line)
                if value_match:
                    current_error['value'] = value_match.group(1)
                    current_error['line'] = line
                    
            elif line.startswith('Reason:'):
                current_error['reason'] = line.replace('Reason:', '').strip()
                
            elif line.startswith('Path:'):
                current_error['path'] = line.replace('Path:', '').strip()
    
    print(f"   Found {len(enumeration_errors)} enumeration errors")
    
    if not enumeration_errors:
        print("ℹ️  No enumeration-specific errors found in validation output")
        # Look for any errors that might be enumeration-related
        print("\n📋 All validation errors (first 10):")
        lines = str(e).split('\n')[:20]
        for line in lines:
            if line.strip():
                print(f"   {line.strip()}")
        return
    
    # Analyze enumeration errors by type
    print("\n3. Analyzing enumeration errors by type...")
    
    error_by_element = defaultdict(list)
    error_by_value = defaultdict(int)
    error_by_pattern = defaultdict(list)
    
    for error in enumeration_errors:
        value = error.get('value', 'unknown')
        path = error.get('path', 'unknown')
        reason = error.get('reason', 'unknown')
        
        # Extract element name from path
        element_match = re.search(r'/([^/]+)$', path)
        element_name = element_match.group(1) if element_match else 'unknown'
        
        error_by_element[element_name].append(error)
        error_by_value[value] += 1
        
        # Extract expected values from reason
        expected_match = re.search(r'\[(.*?)\]', reason)
        if expected_match:
            expected_values = expected_match.group(1)
            error_by_pattern[expected_values].append((element_name, value))
    
    # Report by element
    print(f"\n📊 Enumeration errors by element:")
    for element, errors in sorted(error_by_element.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {element}: {len(errors)} errors")
        if len(errors) <= 3:  # Show details for elements with few errors
            for error in errors:
                print(f"      Value: '{error.get('value', 'unknown')}' - {error.get('reason', 'unknown')}")
    
    # Report by value frequency
    print(f"\n📊 Most common invalid enumeration values:")
    for value, count in sorted(error_by_value.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   '{value}': {count} errors")
    
    # Report by expected enumeration patterns
    print(f"\n📊 Expected enumeration patterns:")
    for expected, elements in sorted(error_by_pattern.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   Expected: [{expected}]")
        print(f"      Elements: {len(elements)}")
        for element, value in elements[:3]:  # Show first 3 elements
            print(f"         {element}: '{value}'")
        if len(elements) > 3:
            print(f"         ... and {len(elements) - 3} more")
    
    return enumeration_errors

def find_enumeration_types_in_schema():
    """Find all enumeration types in the schema for analysis."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("\n🔍 Schema Enumeration Types Analysis")
    print("=" * 40)
    
    enumeration_types = []
    
    # Check all types for enumeration constraints
    for name, xsd_type in generator.schema.maps.types.items():
        if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration:
            enum_values = [str(val) for val in xsd_type.enumeration]
            enumeration_types.append((name, enum_values))
        elif hasattr(xsd_type, 'facets') and xsd_type.facets:
            for facet_name, facet in xsd_type.facets.items():
                if facet_name and 'enumeration' in str(facet_name).lower():
                    # Try to extract enumeration values
                    if hasattr(facet, 'enumeration') and facet.enumeration:
                        enum_values = [str(val) for val in facet.enumeration]
                        enumeration_types.append((name, enum_values))
                        break
    
    print(f"Found {len(enumeration_types)} enumeration types in schema:")
    
    for i, (name, values) in enumerate(enumeration_types[:10]):  # Show first 10
        print(f"   {i+1}. {name}")
        print(f"      Values: {values[:5]}{'...' if len(values) > 5 else ''} ({len(values)} total)")
    
    if len(enumeration_types) > 10:
        print(f"   ... and {len(enumeration_types) - 10} more")
    
    return enumeration_types

if __name__ == "__main__":
    enumeration_errors = analyze_enumeration_errors()
    enumeration_types = find_enumeration_types_in_schema()
    
    if enumeration_errors and enumeration_types:
        print(f"\n🎯 Summary:")
        print(f"   - Validation errors: {len(enumeration_errors)}")
        print(f"   - Schema enum types: {len(enumeration_types)}")
        print(f"   - Fix opportunities: High (many invalid values can be mapped to valid enums)")