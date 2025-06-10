#!/usr/bin/env python3
"""
Test that pattern constraints are now properly extracted and applied.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import StringTypeGenerator
import xmlschema

def test_pattern_constraint_fix():
    """Test the complete pattern constraint flow."""
    
    print("🔍 Test Pattern Constraint Fix")
    print("=" * 60)
    
    common_types_path = 'resource/21_3_5_distribution_schemas/IATA_OffersAndOrdersCommonTypes.xsd'
    main_schema_path = 'resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd'
    
    # Load schemas
    common_schema = xmlschema.XMLSchema(common_types_path)
    gen = XMLGenerator(main_schema_path)
    
    print("1. Testing pattern constraint extraction and application:")
    print("-" * 60)
    
    # Find pattern types to test
    pattern_types = []
    for type_name, type_obj in common_schema.types.items():
        if hasattr(type_obj, 'facets') and type_obj.facets:
            for facet_name, facet in type_obj.facets.items():
                local_name = str(facet_name).split('}')[-1] if '}' in str(facet_name) else str(facet_name)
                if local_name == 'pattern' and hasattr(facet, 'regexps') and facet.regexps:
                    pattern_types.append((type_name, type_obj, facet.regexps[0]))
                    if len(pattern_types) >= 8:  # Test 8 different patterns
                        break
    
    print(f"Found {len(pattern_types)} pattern types to test")
    
    success_count = 0
    total_tests = 0
    
    for type_name, type_obj, expected_pattern in pattern_types:
        print(f"\n   Testing: {type_name}")
        print(f"   Expected pattern: {expected_pattern}")
        
        total_tests += 1
        
        # 1. Test constraint extraction
        constraints = gen._extract_type_constraints(type_obj)
        extracted_pattern = constraints.get('pattern')
        
        print(f"   Extracted pattern: {repr(extracted_pattern)}")
        
        if extracted_pattern == expected_pattern:
            print(f"   ✅ Pattern extraction: PASS")
        else:
            print(f"   ❌ Pattern extraction: FAIL")
            continue
        
        # 2. Test value generation with pattern
        try:
            value = gen._generate_value_for_type(type_obj, type_name.replace('Type', '').replace('_', ''))
            print(f"   Generated value: {repr(value)}")
            
            # 3. Test pattern compliance
            string_gen = StringTypeGenerator()
            is_compliant = string_gen.test_pattern_compliance(value, extracted_pattern)
            print(f"   Pattern compliant: {is_compliant}")
            
            if is_compliant:
                print(f"   ✅ Full flow: PASS")
                success_count += 1
            else:
                print(f"   ⚠️  Full flow: Generated value doesn't match pattern")
                
                # Try regenerating with explicit pattern validation
                new_value = string_gen.validate_and_regenerate_pattern(value, extracted_pattern)
                new_compliant = string_gen.test_pattern_compliance(new_value, extracted_pattern)
                print(f"   Regenerated value: {repr(new_value)}")
                print(f"   Regenerated compliant: {new_compliant}")
                
                if new_compliant:
                    print(f"   ✅ Pattern regeneration: PASS")
                    success_count += 1
                
        except Exception as e:
            print(f"   ❌ Value generation error: {e}")
    
    print(f"\n2. Testing specific IATA patterns from our pattern library:")
    print("-" * 60)
    
    # Test our pattern library against these real patterns
    string_gen = StringTypeGenerator()
    library_tests = 0
    library_success = 0
    
    real_patterns = [pattern for _, _, pattern in pattern_types]
    
    for pattern in real_patterns[:5]:  # Test first 5
        print(f"\n   Testing pattern: {pattern}")
        library_tests += 1
        
        # Check if pattern is in our library
        if pattern in string_gen.AVIATION_PATTERNS:
            print(f"   ✅ Pattern in library")
            # Test library generation
            lib_value = string_gen.AVIATION_PATTERNS[pattern]()
            lib_compliant = string_gen.test_pattern_compliance(lib_value, pattern)
            print(f"   Library value: {repr(lib_value)}")
            print(f"   Library compliant: {lib_compliant}")
            if lib_compliant:
                library_success += 1
        else:
            print(f"   ⚠️  Pattern NOT in library, testing dynamic generation")
            # Test dynamic generation
            dyn_value = string_gen.generate_dynamic_pattern_value(pattern)
            dyn_compliant = string_gen.test_pattern_compliance(dyn_value, pattern)
            print(f"   Dynamic value: {repr(dyn_value)}")
            print(f"   Dynamic compliant: {dyn_compliant}")
            if dyn_compliant:
                library_success += 1
    
    print(f"\n3. Testing pattern integration in XML generation:")
    print("-" * 60)
    
    # Test that patterns work in actual XML generation
    try:
        # Generate a small test XML with choice Response to include types with patterns
        test_xml = gen.generate_dummy_xml_with_choices(
            {'Response': True}, 
            {'OrderTotalAmount': 1}
        )
        
        print(f"   XML generation successful: {len(test_xml)} characters")
        
        # Look for some pattern-constrained values in the XML
        if test_xml and '<' in test_xml:
            print(f"   ✅ XML contains structured content")
            
            # Simple check for non-empty elements
            import re
            empty_elements = re.findall(r'<([^>]+)></\1>', test_xml)
            print(f"   Empty elements found: {len(empty_elements)}")
            
            if len(empty_elements) == 0:
                print(f"   ✅ No empty elements - patterns likely working")
            else:
                print(f"   ⚠️  Found {len(empty_elements)} empty elements")
        
    except Exception as e:
        print(f"   ❌ XML generation failed: {e}")
    
    print(f"\n4. Summary:")
    print("-" * 60)
    print(f"   Pattern extraction tests: {success_count}/{total_tests}")
    print(f"   Pattern library tests: {library_success}/{library_tests}")
    print(f"   Overall success rate: {(success_count + library_success)}/{(total_tests + library_tests)} ({((success_count + library_success)/(total_tests + library_tests)*100):.1f}%)")
    
    if success_count == total_tests:
        print(f"   🎉 All pattern constraint tests PASSED!")
    elif success_count > total_tests * 0.8:
        print(f"   ✅ Most pattern constraint tests passed")
    else:
        print(f"   ⚠️  Some pattern constraint tests failed")
    
    print(f"\n5. Debugging recommendations:")
    print("-" * 60)
    print(f"   1. Add logging to _extract_type_constraints to see constraint extraction")
    print(f"   2. Add logging to StringTypeGenerator.validate_constraints for pattern application")
    print(f"   3. Consider expanding AVIATION_PATTERNS library for better coverage")
    print(f"   4. Test pattern validation with actual XSD validation tools")

if __name__ == "__main__":
    test_pattern_constraint_fix()