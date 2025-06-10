#!/usr/bin/env python3
"""
Comprehensive analysis of the 3663 validation errors from Response choice XML generation.

This script generates the Response choice XML that produces 3663 errors and 
provides detailed classification and analysis for systematic improvement.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from collections import defaultdict, Counter
import re

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
import xmlschema


def classify_validation_error(error):
    """Enhanced classification for the large error set."""
    error_msg = str(error.message)
    error_path = str(error.path)
    
    classification = {
        'message': error_msg,
        'path': error_path,
        'line': getattr(error, 'lineno', None),
        'column': getattr(error, 'offset', None),
        'category': 'unknown',
        'subcategory': 'unknown',
        'severity': 'error',
        'fixable': False,
        'element_name': None,
        'data_type': None,
        'constraint_type': None,
        'xpath_depth': len(error_path.split('/')) if error_path else 0
    }
    
    # Extract element name from path
    if error_path:
        path_parts = [p for p in error_path.split('/') if p]
        if path_parts:
            classification['element_name'] = path_parts[-1]
    
    # Enumeration constraint violations
    if 'XsdEnumerationFacets' in error_msg or 'not an element of the set' in error_msg:
        classification['category'] = 'enumeration_violation'
        classification['constraint_type'] = 'enumeration'
        classification['fixable'] = True
        classification['severity'] = 'warning'
        
        # Extract enumeration values
        enum_match = re.search(r'XsdEnumerationFacets\(\[([^\]]+)\]', error_msg)
        if enum_match:
            classification['allowed_values'] = enum_match.group(1)
        
        # Classify enumeration types
        if any(code in error_msg for code in ['CurCode', 'currency']):
            classification['subcategory'] = 'currency_code'
        elif any(code in error_msg for code in ['CountryCode', 'country']):
            classification['subcategory'] = 'country_code'
        elif any(code in error_msg for code in ['LangCode', 'language']):
            classification['subcategory'] = 'language_code'
        elif 'CodesetValue' in error_msg:
            classification['subcategory'] = 'codeset_value'
        else:
            classification['subcategory'] = 'general_enumeration'
    
    # Boolean type errors
    elif "with XsdAtomicBuiltin(name='xs:boolean')" in error_msg:
        classification['category'] = 'boolean_type_error'
        classification['data_type'] = 'boolean'
        classification['fixable'] = True
        classification['severity'] = 'error'
        
        if "'True'" in error_msg or "'False'" in error_msg:
            classification['subcategory'] = 'capitalized_boolean'
        elif 'string' in error_msg:
            classification['subcategory'] = 'string_as_boolean'
        else:
            classification['subcategory'] = 'invalid_boolean_format'
    
    # Pattern constraint violations
    elif 'pattern' in error_msg.lower() or 'XsdPatternFacets' in error_msg:
        classification['category'] = 'pattern_violation'
        classification['constraint_type'] = 'pattern'
        classification['fixable'] = True
        classification['severity'] = 'warning'
        
        # Extract pattern
        pattern_match = re.search(r"XsdPatternFacets\(\['([^']+)'\]", error_msg)
        if pattern_match:
            classification['pattern'] = pattern_match.group(1)
        
        # Classify pattern types
        if any(keyword in error_msg.lower() for keyword in ['email', '@']):
            classification['subcategory'] = 'email_pattern'
        elif any(keyword in error_msg.lower() for keyword in ['phone', r'\d+']):
            classification['subcategory'] = 'phone_pattern'
        elif any(keyword in error_msg.lower() for keyword in ['date', 'time']):
            classification['subcategory'] = 'datetime_pattern'
        elif 'ID' in error_path and ('ID' in error_msg or 'id' in error_msg.lower()):
            classification['subcategory'] = 'id_pattern'
        else:
            classification['subcategory'] = 'general_pattern'
    
    # Length constraint violations
    elif any(length_type in error_msg for length_type in ['XsdMaxLengthFacet', 'XsdMinLengthFacet', 'XsdLengthFacet']):
        classification['category'] = 'length_violation'
        classification['constraint_type'] = 'length'
        classification['fixable'] = True
        classification['severity'] = 'warning'
        
        if 'XsdMaxLengthFacet' in error_msg:
            classification['subcategory'] = 'max_length_exceeded'
            # Extract max length value
            length_match = re.search(r'XsdMaxLengthFacet\(value=(\d+)', error_msg)
            if length_match:
                classification['max_length'] = int(length_match.group(1))
        elif 'XsdMinLengthFacet' in error_msg:
            classification['subcategory'] = 'min_length_not_met'
        else:
            classification['subcategory'] = 'fixed_length_mismatch'
    
    # Numeric type errors
    elif any(num_type in error_msg for num_type in ['xs:decimal', 'xs:integer', 'xs:int', 'xs:float', 'xs:double']):
        classification['category'] = 'numeric_type_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        
        for num_type in ['decimal', 'integer', 'int', 'float', 'double']:
            if f'xs:{num_type}' in error_msg:
                classification['data_type'] = num_type
                break
        
        if 'failed decoding' in error_msg and "''" in error_msg:
            classification['subcategory'] = 'empty_numeric_value'
        elif 'failed decoding' in error_msg:
            classification['subcategory'] = 'invalid_numeric_format'
        else:
            classification['subcategory'] = 'general_numeric_error'
    
    # Structural errors
    elif any(struct_error in error_msg for struct_error in [
        'missing child element', 'unexpected child element', 'not expected',
        'XsdGroup', 'sequence', 'choice'
    ]):
        classification['category'] = 'structural_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        
        if 'missing child element' in error_msg:
            classification['subcategory'] = 'missing_required_element'
        elif 'unexpected child element' in error_msg:
            classification['subcategory'] = 'unexpected_element'
        elif 'XsdGroup' in error_msg:
            classification['subcategory'] = 'group_validation_error'
        else:
            classification['subcategory'] = 'general_structural_error'
    
    # DateTime format errors
    elif any(dt_type in error_msg for dt_type in ['xs:date', 'xs:dateTime', 'xs:time']):
        classification['category'] = 'datetime_format_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        
        for dt_type in ['date', 'dateTime', 'time']:
            if f'xs:{dt_type}' in error_msg:
                classification['data_type'] = dt_type
                break
        
        classification['subcategory'] = 'invalid_datetime_format'
    
    # Empty value errors
    elif 'empty' in error_msg.lower() or ("failed decoding ''" in error_msg):
        classification['category'] = 'empty_value_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        classification['subcategory'] = 'unexpected_empty_value'
    
    return classification


def analyze_error_patterns(errors):
    """Analyze patterns in the error distribution."""
    analysis = {
        'total_errors': len(errors),
        'categories': defaultdict(int),
        'subcategories': defaultdict(int),
        'elements': defaultdict(int),
        'depths': defaultdict(int),
        'data_types': defaultdict(int),
        'constraint_types': defaultdict(int),
        'fixable_count': 0,
        'critical_count': 0,
        'warning_count': 0,
        'top_error_paths': Counter(),
        'sample_errors': defaultdict(list),
        'priority_fixes': []
    }
    
    for error in errors:
        classification = classify_validation_error(error)
        
        # Update counters
        analysis['categories'][classification['category']] += 1
        analysis['subcategories'][classification['subcategory']] += 1
        analysis['elements'][classification['element_name']] += 1
        analysis['depths'][classification['xpath_depth']] += 1
        
        if classification['data_type']:
            analysis['data_types'][classification['data_type']] += 1
        if classification['constraint_type']:
            analysis['constraint_types'][classification['constraint_type']] += 1
        
        if classification['fixable']:
            analysis['fixable_count'] += 1
        if classification['severity'] == 'error':
            analysis['critical_count'] += 1
        elif classification['severity'] == 'warning':
            analysis['warning_count'] += 1
        
        # Track error paths
        analysis['top_error_paths'][classification['path']] += 1
        
        # Collect sample errors
        if len(analysis['sample_errors'][classification['category']]) < 5:
            analysis['sample_errors'][classification['category']].append(classification)
    
    # Identify priority fixes
    analysis['priority_fixes'] = identify_priority_fixes(analysis)
    
    return analysis


def identify_priority_fixes(analysis):
    """Identify high-priority fixes based on error patterns."""
    fixes = []
    
    # High-impact fixes (many errors, easy to fix)
    if analysis['categories']['boolean_type_error'] > 10:
        fixes.append({
            'priority': 'HIGH',
            'category': 'boolean_type_error',
            'count': analysis['categories']['boolean_type_error'],
            'description': 'Fix boolean value generation to use proper true/false format',
            'effort': 'LOW',
            'impact': 'HIGH'
        })
    
    if analysis['categories']['numeric_type_error'] > 20:
        fixes.append({
            'priority': 'HIGH',
            'category': 'numeric_type_error',
            'count': analysis['categories']['numeric_type_error'],
            'description': 'Fix numeric type generation and empty value handling',
            'effort': 'MEDIUM',
            'impact': 'HIGH'
        })
    
    if analysis['categories']['empty_value_error'] > 20:
        fixes.append({
            'priority': 'HIGH',
            'category': 'empty_value_error',
            'count': analysis['categories']['empty_value_error'],
            'description': 'Prevent generation of empty values for required elements',
            'effort': 'LOW',
            'impact': 'HIGH'
        })
    
    # Medium-impact fixes
    if analysis['categories']['structural_error'] > 50:
        fixes.append({
            'priority': 'MEDIUM',
            'category': 'structural_error',
            'count': analysis['categories']['structural_error'],
            'description': 'Fix XML structure generation and element ordering',
            'effort': 'HIGH',
            'impact': 'MEDIUM'
        })
    
    # Lower priority but important for data quality
    if analysis['categories']['enumeration_violation'] > 50:
        fixes.append({
            'priority': 'LOW',
            'category': 'enumeration_violation',
            'count': analysis['categories']['enumeration_violation'],
            'description': 'Implement realistic enumeration value generation',
            'effort': 'MEDIUM',
            'impact': 'LOW'
        })
    
    if analysis['categories']['pattern_violation'] > 50:
        fixes.append({
            'priority': 'LOW',
            'category': 'pattern_violation',
            'count': analysis['categories']['pattern_violation'],
            'description': 'Generate pattern-compliant values for specific formats',
            'effort': 'MEDIUM',
            'impact': 'LOW'
        })
    
    return sorted(fixes, key=lambda x: (x['priority'], -x['count']))


def generate_response_xml_and_analyze():
    """Generate Response choice XML and analyze all 3663 errors."""
    print("Generating Response choice XML for comprehensive error analysis...")
    
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(xsd_path)
    
    # Generate Response choice XML
    selected_choices = {
        'choice_0': {
            'path': 'IATA_OrderViewRS',
            'selected_element': 'Response',
            'choice_data': {
                'type': 'choice',
                'min_occurs': 1,
                'max_occurs': 1,
                'elements': [
                    {'name': 'Error', 'min_occurs': 1, 'max_occurs': 'unbounded'},
                    {'name': 'Response', 'min_occurs': 1, 'max_occurs': 1}
                ]
            }
        }
    }
    
    xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
    print(f"Generated XML size: {len(xml_content)} characters")
    
    # Validate and get all errors
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(xml_content)
        temp_xml_path = temp_file.name
    
    try:
        print("Validating XML to capture all errors...")
        errors = list(generator.schema.iter_errors(temp_xml_path))
        print(f"Found {len(errors)} validation errors")
        
        if len(errors) != 3663:
            print(f"⚠️  Expected 3663 errors, found {len(errors)}")
        
        # Analyze all errors
        print("Analyzing error patterns...")
        analysis = analyze_error_patterns(errors)
        
        return xml_content, errors, analysis
        
    finally:
        if os.path.exists(temp_xml_path):
            os.unlink(temp_xml_path)


def print_comprehensive_analysis(analysis):
    """Print detailed analysis of all validation errors."""
    print("\n" + "=" * 80)
    print(" COMPREHENSIVE VALIDATION ERROR ANALYSIS")
    print("=" * 80)
    
    print(f"\n📊 OVERVIEW")
    print(f"Total Validation Errors: {analysis['total_errors']}")
    print(f"Critical Errors: {analysis['critical_count']} ({analysis['critical_count']/analysis['total_errors']*100:.1f}%)")
    print(f"Warnings: {analysis['warning_count']} ({analysis['warning_count']/analysis['total_errors']*100:.1f}%)")
    print(f"Fixable Errors: {analysis['fixable_count']} ({analysis['fixable_count']/analysis['total_errors']*100:.1f}%)")
    
    print(f"\n📋 ERROR CATEGORIES (Top 10)")
    for category, count in sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / analysis['total_errors']) * 100
        print(f"{category:30}: {count:4} ({percentage:5.1f}%)")
    
    print(f"\n🔍 ERROR SUBCATEGORIES (Top 15)")
    for subcategory, count in sorted(analysis['subcategories'].items(), key=lambda x: x[1], reverse=True)[:15]:
        percentage = (count / analysis['total_errors']) * 100
        print(f"{subcategory:30}: {count:4} ({percentage:5.1f}%)")
    
    print(f"\n🎯 MOST PROBLEMATIC ELEMENTS (Top 15)")
    for element, count in sorted(analysis['elements'].items(), key=lambda x: x[1], reverse=True)[:15]:
        if element and count > 5:  # Only show significant elements
            percentage = (count / analysis['total_errors']) * 100
            print(f"{element:30}: {count:4} ({percentage:5.1f}%)")
    
    print(f"\n📏 ERROR DISTRIBUTION BY XML DEPTH")
    for depth in sorted(analysis['depths'].keys()):
        count = analysis['depths'][depth]
        if count > 10:  # Only show significant depths
            percentage = (count / analysis['total_errors']) * 100
            print(f"Depth {depth:2}: {count:4} errors ({percentage:5.1f}%)")
    
    if analysis['data_types']:
        print(f"\n🔢 ERRORS BY DATA TYPE")
        for data_type, count in sorted(analysis['data_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"{data_type:15}: {count:4}")
    
    if analysis['constraint_types']:
        print(f"\n⚖️  ERRORS BY CONSTRAINT TYPE")
        for constraint_type, count in sorted(analysis['constraint_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"{constraint_type:15}: {count:4}")


def print_priority_fixes(analysis):
    """Print prioritized list of fixes."""
    print("\n" + "=" * 80)
    print(" PRIORITY FIXES FOR SYSTEMATIC IMPROVEMENT")
    print("=" * 80)
    
    for i, fix in enumerate(analysis['priority_fixes'], 1):
        print(f"\n{i}. {fix['priority']} PRIORITY - {fix['category'].upper().replace('_', ' ')}")
        print(f"   Error Count: {fix['count']}")
        print(f"   Description: {fix['description']}")
        print(f"   Effort: {fix['effort']} | Impact: {fix['impact']}")


def print_sample_errors_detailed(analysis):
    """Print detailed sample errors for each major category."""
    print("\n" + "=" * 80)
    print(" DETAILED SAMPLE ERRORS BY CATEGORY")
    print("=" * 80)
    
    for category, samples in analysis['sample_errors'].items():
        if samples and analysis['categories'][category] > 10:  # Only show categories with significant errors
            print(f"\n--- {category.upper().replace('_', ' ')} ({analysis['categories'][category]} total) ---")
            for i, sample in enumerate(samples, 1):
                print(f"{i}. Element: {sample['element_name']}")
                print(f"   Path: {sample['path']}")
                print(f"   Type: {sample['subcategory']}")
                print(f"   Severity: {sample['severity']} | Fixable: {sample['fixable']}")
                print(f"   Message: {sample['message'][:120]}...")
                print()


def save_comprehensive_analysis(analysis, xml_content, output_file):
    """Save comprehensive analysis to file."""
    # Convert defaultdict and Counter to regular dict for JSON serialization
    analysis_dict = {}
    for key, value in analysis.items():
        if isinstance(value, (defaultdict, Counter)):
            analysis_dict[key] = dict(value)
        else:
            analysis_dict[key] = value
    
    # Add metadata
    analysis_dict['metadata'] = {
        'xml_size_chars': len(xml_content),
        'xml_size_mb': len(xml_content) / (1024 * 1024),
        'analysis_timestamp': '2024-06-08',
        'schema_file': 'IATA_OrderViewRS.xsd',
        'choice_type': 'Response'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nComprehensive analysis saved to: {output_file}")


def main():
    """Run the comprehensive validation error analysis."""
    print("🔍 COMPREHENSIVE IATA_OrderViewRS VALIDATION ERROR ANALYSIS")
    print("Analyzing the full 3663 validation errors from Response choice generation")
    print("=" * 80)
    
    os.chdir(project_root)
    
    try:
        # Generate and analyze
        xml_content, errors, analysis = generate_response_xml_and_analyze()
        
        # Print comprehensive analysis
        print_comprehensive_analysis(analysis)
        print_priority_fixes(analysis)
        print_sample_errors_detailed(analysis)
        
        # Save analysis
        timestamp = "20240608"
        analysis_file = f"comprehensive_validation_analysis_{timestamp}.json"
        save_comprehensive_analysis(analysis, xml_content, analysis_file)
        
        # Save XML sample for reference
        xml_sample_file = f"response_choice_xml_sample_{timestamp}.xml"
        with open(xml_sample_file, 'w', encoding='utf-8') as f:
            lines = xml_content.split('\n')
            f.write('\n'.join(lines[:100]))  # Save first 100 lines
            if len(lines) > 100:
                f.write(f'\n\n<!-- ... truncated {len(lines) - 100} lines for brevity -->')
        
        print(f"XML sample saved to: {xml_sample_file}")
        
        print(f"\n✅ Comprehensive analysis completed successfully!")
        print(f"📊 Total errors analyzed: {analysis['total_errors']}")
        print(f"🎯 Priority fixes identified: {len(analysis['priority_fixes'])}")
        
        return analysis
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()