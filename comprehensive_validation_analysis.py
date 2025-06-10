#!/usr/bin/env python3
"""
Comprehensive validation error analysis for XML generated from IATA_OrderViewRS.xsd.
Categorizes all error types, counts them, and identifies generic fix strategies.
"""

import xmlschema
import re
import json
from collections import defaultdict, Counter
from datetime import datetime

def analyze_all_validation_errors():
    """Comprehensive analysis of all validation errors with categorization and fix strategies."""
    
    schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    
    print("🔍 Comprehensive Validation Error Analysis")
    print("=" * 60)
    
    # Generate fresh XML for analysis
    print("1. Generating XML for analysis...")
    from utils.xml_generator import XMLGenerator
    
    generator = XMLGenerator(schema_path)
    xml_content = generator.generate_dummy_xml_with_choices({'Response': True}, {})
    
    with open('comprehensive_validation_test.xml', 'w') as f:
        f.write(xml_content)
    
    print(f"   Generated XML: {len(xml_content)} characters")
    
    # Load schema and validate
    print("2. Validating XML against schema...")
    schema = xmlschema.XMLSchema(schema_path)
    
    all_errors = list(schema.iter_errors(xml_content))
    print(f"   Total validation errors: {len(all_errors)}")
    
    # Comprehensive error categorization
    error_categories = {
        'pattern_validation': [],
        'empty_decimal': [],
        'invalid_decimal_format': [],
        'duration_format': [],
        'boolean_format': [],
        'date_format': [],
        'enumeration_mismatch': [],
        'length_constraint': [],
        'missing_required': [],
        'unexpected_element': [],
        'namespace_issues': [],
        'type_mismatch': [],
        'other': []
    }
    
    # Error pattern analysis
    print("3. Categorizing errors...")
    
    for error in all_errors:
        error_msg = str(error)
        categorized = False
        
        # Pattern validation errors
        if "doesn't match any pattern" in error_msg or "pattern" in error_msg.lower():
            pattern_match = re.search(r"pattern.*?\['([^']+)'\]", error_msg)
            pattern = pattern_match.group(1) if pattern_match else "unknown"
            
            element_match = re.search(r"Path: ([^\n]+)", error_msg)
            element_path = element_match.group(1) if element_match else "unknown"
            
            error_categories['pattern_validation'].append({
                'pattern': pattern,
                'element_path': element_path,
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Empty decimal errors
        elif "invalid value '' for xs:decimal" in error_msg:
            element_match = re.search(r"Path: ([^\n]+)", error_msg)
            element_path = element_match.group(1) if element_match else "unknown"
            element_name = element_path.split('/')[-1] if element_path != "unknown" else "unknown"
            
            error_categories['empty_decimal'].append({
                'element_name': element_name,
                'element_path': element_path,
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Invalid decimal format (non-empty but wrong format)
        elif "xs:decimal" in error_msg and "invalid value" in error_msg and "invalid value ''" not in error_msg:
            error_categories['invalid_decimal_format'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Duration format errors
        elif "is not an xs:duration value" in error_msg or "duration" in error_msg.lower():
            element_match = re.search(r"Path: ([^\n]+)", error_msg)
            element_path = element_match.group(1) if element_match else "unknown"
            element_name = element_path.split('/')[-1] if element_path != "unknown" else "unknown"
            
            # Extract the invalid value
            value_match = re.search(r"failed decoding '([^']+)'", error_msg)
            invalid_value = value_match.group(1) if value_match else "unknown"
            
            error_categories['duration_format'].append({
                'element_name': element_name,
                'element_path': element_path,
                'invalid_value': invalid_value,
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Boolean format errors
        elif "xs:boolean" in error_msg and "invalid value" in error_msg:
            error_categories['boolean_format'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Date/DateTime format errors
        elif any(date_type in error_msg for date_type in ["xs:date", "xs:dateTime", "xs:time"]) and "invalid" in error_msg:
            error_categories['date_format'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Enumeration mismatch errors
        elif "is not an element of the enumeration" in error_msg or "enumeration" in error_msg.lower():
            error_categories['enumeration_mismatch'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Length constraint errors
        elif any(constraint in error_msg for constraint in ["minLength", "maxLength", "length"]):
            error_categories['length_constraint'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Missing required elements
        elif "missing" in error_msg.lower() and "required" in error_msg.lower():
            error_categories['missing_required'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Unexpected elements
        elif "unexpected" in error_msg.lower() or "not allowed" in error_msg.lower():
            error_categories['unexpected_element'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Namespace issues
        elif "namespace" in error_msg.lower():
            error_categories['namespace_issues'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Type mismatch (catch-all for other type issues)
        elif "type" in error_msg.lower() and any(word in error_msg for word in ["invalid", "failed", "expected"]):
            error_categories['type_mismatch'].append({
                'full_error': error_msg[:300] + "..."
            })
            categorized = True
        
        # Everything else
        if not categorized:
            error_categories['other'].append({
                'full_error': error_msg[:300] + "..."
            })
    
    # Generate comprehensive analysis
    analysis_results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'xml_file_size': len(xml_content),
            'total_errors': len(all_errors),
            'schema_file': schema_path
        },
        'error_summary': {},
        'detailed_analysis': {},
        'fix_strategies': {}
    }
    
    print("4. Analyzing error patterns and fix strategies...")
    
    # Analyze each category
    for category, errors in error_categories.items():
        if not errors:
            continue
            
        count = len(errors)
        analysis_results['error_summary'][category] = count
        
        print(f"\n📊 {category.upper()}: {count} errors")
        
        if category == 'pattern_validation':
            # Analyze pattern types
            pattern_stats = Counter([e['pattern'] for e in errors])
            analysis_results['detailed_analysis'][category] = {
                'pattern_breakdown': dict(pattern_stats),
                'top_patterns': pattern_stats.most_common(5),
                'sample_errors': errors[:3]
            }
            
            print(f"   Top patterns:")
            for pattern, count in pattern_stats.most_common(5):
                print(f"     '{pattern}': {count} errors")
                
            # Fix strategy
            analysis_results['fix_strategies'][category] = {
                'difficulty': 'EASY',
                'confidence': 'HIGH',
                'strategy': 'Enhance StringTypeGenerator pattern matching with specific generators for each pattern',
                'implementation': [
                    'Map each pattern to a specific value generator function',
                    'Add pattern validation in string generator validate_constraints method',
                    'Create pattern-specific value generators (flight numbers, codes, etc.)',
                    'Test against each pattern regex to ensure compliance'
                ],
                'estimated_fix_rate': '95%',
                'dependencies': 'None - self-contained fix'
            }
        
        elif category == 'empty_decimal':
            # Analyze decimal element types
            element_stats = Counter([e['element_name'] for e in errors])
            analysis_results['detailed_analysis'][category] = {
                'element_breakdown': dict(element_stats),
                'top_elements': element_stats.most_common(10),
                'sample_errors': errors[:5]
            }
            
            print(f"   Top empty decimal elements:")
            for element, count in element_stats.most_common(5):
                print(f"     {element}: {count} errors")
                
            # Fix strategy
            analysis_results['fix_strategies'][category] = {
                'difficulty': 'MEDIUM',
                'confidence': 'MEDIUM',
                'strategy': 'Fix multi-instance element generation and type detection issues',
                'implementation': [
                    'Investigate why some decimal elements generate as empty in lists',
                    'Fix circular reference protection for list processing',
                    'Add comprehensive fallback for all decimal types',
                    'Ensure proper simple vs complex type detection'
                ],
                'estimated_fix_rate': '70%',
                'dependencies': 'Requires deeper investigation of list processing'
            }
        
        elif category == 'duration_format':
            # Analyze duration elements
            element_stats = Counter([e['element_name'] for e in errors])
            value_stats = Counter([e['invalid_value'] for e in errors])
            
            analysis_results['detailed_analysis'][category] = {
                'element_breakdown': dict(element_stats),
                'invalid_values': dict(value_stats),
                'sample_errors': errors[:3]
            }
            
            print(f"   Duration elements: {list(element_stats.keys())}")
            print(f"   Invalid values: {list(value_stats.keys())[:3]}")
            
            # Fix strategy
            analysis_results['fix_strategies'][category] = {
                'difficulty': 'EASY',
                'confidence': 'HIGH',
                'strategy': 'Ensure duration type detection and ISO 8601 format generation',
                'implementation': [
                    'Verify duration type detection in TypeGeneratorFactory',
                    'Ensure DateTimeTypeGenerator duration case is being used',
                    'Add fallback duration generation for undetected duration types',
                    'Test with valid ISO 8601 duration formats (PT1H30M, etc.)'
                ],
                'estimated_fix_rate': '100%',
                'dependencies': 'Duration support already implemented, needs verification'
            }
        
        elif category == 'boolean_format':
            analysis_results['detailed_analysis'][category] = {
                'sample_errors': errors[:3]
            }
            
            # Fix strategy
            analysis_results['fix_strategies'][category] = {
                'difficulty': 'EASY',
                'confidence': 'HIGH',
                'strategy': 'Fix boolean value generation to use valid XML Schema boolean values',
                'implementation': [
                    'Ensure BooleanTypeGenerator uses "true"/"false" not "True"/"False"',
                    'Add validation for boolean type detection',
                    'Test boolean generation compliance'
                ],
                'estimated_fix_rate': '100%',
                'dependencies': 'Boolean generator already exists'
            }
        
        elif category == 'enumeration_mismatch':
            analysis_results['detailed_analysis'][category] = {
                'sample_errors': errors[:3]
            }
            
            # Fix strategy
            analysis_results['fix_strategies'][category] = {
                'difficulty': 'EASY',
                'confidence': 'HIGH',
                'strategy': 'Verify enumeration value extraction and selection',
                'implementation': [
                    'Debug enumeration constraint extraction',
                    'Ensure EnumerationTypeGenerator receives valid enum values',
                    'Add fallback for invalid/missing enumeration values',
                    'Test enumeration value selection and rotation'
                ],
                'estimated_fix_rate': '90%',
                'dependencies': 'Enumeration support already implemented'
            }
        
        else:
            # Generic analysis for other categories
            analysis_results['detailed_analysis'][category] = {
                'sample_errors': errors[:3]
            }
            
            if category in ['date_format', 'length_constraint']:
                difficulty = 'EASY'
                confidence = 'HIGH'
                fix_rate = '90%'
            elif category in ['type_mismatch', 'missing_required']:
                difficulty = 'MEDIUM'
                confidence = 'MEDIUM'
                fix_rate = '60%'
            else:
                difficulty = 'HARD'
                confidence = 'LOW'
                fix_rate = '30%'
                
            analysis_results['fix_strategies'][category] = {
                'difficulty': difficulty,
                'confidence': confidence,
                'strategy': f'Investigate and fix {category} issues',
                'estimated_fix_rate': fix_rate,
                'dependencies': 'Requires detailed investigation'
            }
    
    # Identify easy fixes and calculate potential impact
    easy_fixes = []
    total_easy_fix_potential = 0
    
    for category, strategy in analysis_results['fix_strategies'].items():
        if strategy['difficulty'] == 'EASY' and strategy['confidence'] == 'HIGH':
            error_count = analysis_results['error_summary'].get(category, 0)
            estimated_fixes = int(error_count * float(strategy['estimated_fix_rate'].rstrip('%')) / 100)
            
            easy_fixes.append({
                'category': category,
                'error_count': error_count,
                'estimated_fixes': estimated_fixes,
                'fix_rate': strategy['estimated_fix_rate']
            })
            total_easy_fix_potential += estimated_fixes
    
    analysis_results['easy_fixes_summary'] = {
        'total_potential_fixes': total_easy_fix_potential,
        'current_total_errors': len(all_errors),
        'potential_reduction_percentage': round((total_easy_fix_potential / len(all_errors)) * 100, 1),
        'easy_fix_categories': easy_fixes
    }
    
    # Print summary
    print(f"\n🎯 EASY FIXES IDENTIFIED:")
    print(f"   Potential fixes: {total_easy_fix_potential} errors")
    print(f"   Potential reduction: {analysis_results['easy_fixes_summary']['potential_reduction_percentage']}%")
    print(f"   Easy fix categories: {len(easy_fixes)}")
    
    for fix in easy_fixes:
        print(f"     {fix['category']}: {fix['estimated_fixes']} fixes ({fix['fix_rate']})")
    
    # Save comprehensive analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'comprehensive_validation_analysis_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    return analysis_results

if __name__ == "__main__":
    results = analyze_all_validation_errors()
    print(f"\n🎉 Comprehensive analysis complete!")
    print(f"   Total errors analyzed: {results['metadata']['total_errors']}")
    print(f"   Categories identified: {len(results['error_summary'])}")
    print(f"   Easy fix potential: {results['easy_fixes_summary']['potential_reduction_percentage']}% reduction")