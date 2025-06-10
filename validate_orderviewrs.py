#!/usr/bin/env python3
"""
Detailed validation script for IATA_OrderViewRS XML generation.

This script generates XML from IATA_OrderViewRS.xsd and performs comprehensive
validation analysis to classify and categorize all validation errors.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from collections import defaultdict
import re

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
import xmlschema


def classify_validation_error(error):
    """
    Classify validation errors into categories for analysis.
    
    Args:
        error: xmlschema validation error object
        
    Returns:
        dict with classification information
    """
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
        'constraint_type': None
    }
    
    # Extract element name from path
    if error_path:
        path_parts = error_path.split('/')
        if path_parts:
            classification['element_name'] = path_parts[-1] if path_parts[-1] else path_parts[-2]
    
    # Enumeration constraint violations
    if 'XsdEnumerationFacets' in error_msg or 'not an element of the set' in error_msg:
        classification['category'] = 'enumeration_violation'
        classification['constraint_type'] = 'enumeration'
        classification['fixable'] = True
        classification['severity'] = 'warning'  # Expected for dummy data
        
        # Further classify enumeration types
        if 'currency' in error_msg.lower() or 'CurCode' in error_msg:
            classification['subcategory'] = 'currency_code'
        elif 'country' in error_msg.lower():
            classification['subcategory'] = 'country_code'
        elif 'language' in error_msg.lower():
            classification['subcategory'] = 'language_code'
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
    elif 'pattern' in error_msg.lower() or 'does not match pattern' in error_msg:
        classification['category'] = 'pattern_violation'
        classification['constraint_type'] = 'pattern'
        classification['fixable'] = True
        classification['severity'] = 'warning'  # Expected for dummy data
        
        # Extract pattern information
        pattern_match = re.search(r"pattern '([^']+)'", error_msg)
        if pattern_match:
            classification['pattern'] = pattern_match.group(1)
            
        # Classify pattern types
        if 'email' in error_msg.lower() or '@' in error_msg:
            classification['subcategory'] = 'email_pattern'
        elif 'phone' in error_msg.lower() or r'\d' in error_msg:
            classification['subcategory'] = 'phone_pattern'
        elif 'date' in error_msg.lower() or 'time' in error_msg.lower():
            classification['subcategory'] = 'datetime_pattern'
        else:
            classification['subcategory'] = 'general_pattern'
    
    # Length constraint violations
    elif 'length' in error_msg.lower() and ('too long' in error_msg or 'too short' in error_msg):
        classification['category'] = 'length_violation'
        classification['constraint_type'] = 'length'
        classification['fixable'] = True
        classification['severity'] = 'warning'
        
        if 'maxLength' in error_msg:
            classification['subcategory'] = 'max_length_exceeded'
        elif 'minLength' in error_msg:
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
                
        if 'string' in error_msg:
            classification['subcategory'] = 'string_as_number'
        elif 'invalid literal' in error_msg:
            classification['subcategory'] = 'invalid_number_format'
        else:
            classification['subcategory'] = 'general_numeric_error'
    
    # Structural errors (missing elements, wrong order, etc.)
    elif any(struct_error in error_msg for struct_error in [
        'missing child element', 'unexpected child element', 'not expected', 
        'required element', 'element not allowed'
    ]):
        classification['category'] = 'structural_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        
        if 'missing child element' in error_msg:
            classification['subcategory'] = 'missing_required_element'
        elif 'unexpected child element' in error_msg:
            classification['subcategory'] = 'unexpected_element'
        elif 'not expected' in error_msg:
            classification['subcategory'] = 'element_not_expected'
        else:
            classification['subcategory'] = 'general_structural_error'
    
    # Namespace errors
    elif 'namespace' in error_msg.lower():
        classification['category'] = 'namespace_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        classification['subcategory'] = 'namespace_mismatch'
    
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
    elif 'empty' in error_msg.lower() or 'null' in error_msg.lower():
        classification['category'] = 'empty_value_error'
        classification['fixable'] = True
        classification['severity'] = 'error'
        classification['subcategory'] = 'unexpected_empty_value'
    
    return classification


def analyze_validation_errors(errors):
    """
    Analyze and categorize validation errors.
    
    Args:
        errors: List of xmlschema validation errors
        
    Returns:
        dict with detailed analysis
    """
    analysis = {
        'total_errors': len(errors),
        'categories': defaultdict(int),
        'subcategories': defaultdict(int),
        'fixable_count': 0,
        'critical_count': 0,
        'warning_count': 0,
        'by_element': defaultdict(list),
        'by_data_type': defaultdict(int),
        'by_constraint_type': defaultdict(int),
        'sample_errors': defaultdict(list),
        'classification_details': []
    }
    
    for error in errors:
        classification = classify_validation_error(error)
        analysis['classification_details'].append(classification)
        
        # Update counters
        analysis['categories'][classification['category']] += 1
        analysis['subcategories'][classification['subcategory']] += 1
        
        if classification['fixable']:
            analysis['fixable_count'] += 1
        
        if classification['severity'] == 'error':
            analysis['critical_count'] += 1
        elif classification['severity'] == 'warning':
            analysis['warning_count'] += 1
        
        # Group by element
        if classification['element_name']:
            analysis['by_element'][classification['element_name']].append(classification)
        
        # Group by data type
        if classification['data_type']:
            analysis['by_data_type'][classification['data_type']] += 1
        
        # Group by constraint type
        if classification['constraint_type']:
            analysis['by_constraint_type'][classification['constraint_type']] += 1
        
        # Collect sample errors (max 3 per category)
        if len(analysis['sample_errors'][classification['category']]) < 3:
            analysis['sample_errors'][classification['category']].append({
                'message': classification['message'],
                'path': classification['path'],
                'subcategory': classification['subcategory']
            })
    
    return analysis


def generate_and_validate_xml():
    """
    Generate XML from IATA_OrderViewRS.xsd and validate it.
    
    Returns:
        tuple: (xml_content, validation_errors, analysis)
    """
    print("Generating XML from IATA_OrderViewRS.xsd...")
    xsd_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        # Generate XML
        generator = XMLGenerator(xsd_path)
        xml_content = generator.generate_dummy_xml()
        
        print(f"Generated XML size: {len(xml_content)} characters")
        
        # Create temporary XML file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(xml_content)
            temp_xml_path = temp_file.name
        
        print(f"Temporary XML file: {temp_xml_path}")
        
        try:
            # Validate using xmlschema
            print("Validating XML against schema...")
            errors = list(generator.schema.iter_errors(temp_xml_path))
            print(f"Found {len(errors)} validation errors")
            
            # Analyze errors
            print("Analyzing validation errors...")
            analysis = analyze_validation_errors(errors)
            
            return xml_content, errors, analysis
            
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_xml_path):
                os.unlink(temp_xml_path)
                
    except Exception as e:
        print(f"Error during XML generation or validation: {e}")
        raise


def print_analysis_summary(analysis):
    """Print a summary of the validation error analysis."""
    print("\n" + "=" * 80)
    print(" VALIDATION ERROR ANALYSIS SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Validation Errors: {analysis['total_errors']}")
    print(f"Critical Errors (need fixing): {analysis['critical_count']}")
    print(f"Warnings (expected for dummy data): {analysis['warning_count']}")
    print(f"Fixable Errors: {analysis['fixable_count']}")
    
    print(f"\n--- Error Categories ---")
    for category, count in sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / analysis['total_errors']) * 100
        print(f"{category:25}: {count:4} ({percentage:5.1f}%)")
    
    print(f"\n--- Top Subcategories ---")
    top_subcategories = sorted(analysis['subcategories'].items(), key=lambda x: x[1], reverse=True)[:10]
    for subcategory, count in top_subcategories:
        percentage = (count / analysis['total_errors']) * 100
        print(f"{subcategory:25}: {count:4} ({percentage:5.1f}%)")
    
    if analysis['by_data_type']:
        print(f"\n--- Errors by Data Type ---")
        for data_type, count in sorted(analysis['by_data_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"{data_type:15}: {count:4}")
    
    if analysis['by_constraint_type']:
        print(f"\n--- Errors by Constraint Type ---")
        for constraint_type, count in sorted(analysis['by_constraint_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"{constraint_type:15}: {count:4}")


def print_sample_errors(analysis):
    """Print sample errors for each category."""
    print("\n" + "=" * 80)
    print(" SAMPLE ERRORS BY CATEGORY")
    print("=" * 80)
    
    for category, samples in analysis['sample_errors'].items():
        if samples:
            print(f"\n--- {category.upper().replace('_', ' ')} ---")
            for i, sample in enumerate(samples, 1):
                print(f"{i}. Path: {sample['path']}")
                print(f"   Type: {sample['subcategory']}")
                print(f"   Message: {sample['message'][:100]}...")
                print()


def save_detailed_analysis(analysis, output_file):
    """Save detailed analysis to JSON file."""
    # Convert defaultdict to regular dict for JSON serialization
    analysis_dict = {}
    for key, value in analysis.items():
        if isinstance(value, defaultdict):
            analysis_dict[key] = dict(value)
        else:
            analysis_dict[key] = value
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed analysis saved to: {output_file}")


def main():
    """Run the validation analysis."""
    print("🔍 IATA_OrderViewRS Validation Error Analysis")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir(project_root)
    
    try:
        # Generate and validate XML
        xml_content, errors, analysis = generate_and_validate_xml()
        
        # Print analysis
        print_analysis_summary(analysis)
        print_sample_errors(analysis)
        
        # Save detailed analysis
        timestamp = "20240608"  # Use consistent timestamp for analysis
        analysis_file = f"validation_analysis_{timestamp}.json"
        save_detailed_analysis(analysis, analysis_file)
        
        # Save a sample of the generated XML
        xml_sample_file = f"generated_xml_sample_{timestamp}.xml"
        with open(xml_sample_file, 'w', encoding='utf-8') as f:
            # Save first 50 lines for analysis
            lines = xml_content.split('\n')
            f.write('\n'.join(lines[:50]))
            if len(lines) > 50:
                f.write(f'\n\n<!-- ... truncated {len(lines) - 50} lines for brevity -->')
        
        print(f"XML sample saved to: {xml_sample_file}")
        
        print("\n✅ Validation analysis completed successfully!")
        print(f"📊 Total errors analyzed: {analysis['total_errors']}")
        print(f"📁 Analysis data saved for detailed review")
        
        return analysis
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()