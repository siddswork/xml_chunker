#!/usr/bin/env python3
"""
Test script to validate recursion depth restrictions work for all IATA schemas.
Generates XML for all XSD files ending with RQ.xsd or RS.xsd in the resource folder.
"""

import os
import time
import traceback
from pathlib import Path
from utils.xml_generator import XMLGenerator


def test_all_rq_rs_schemas():
    """Test XML generation for all RQ/RS schemas to ensure recursion limits work."""
    
    # Define the resource directory
    resource_dir = Path(__file__).parent / "resource" / "21_3_5_distribution_schemas"
    
    if not resource_dir.exists():
        print(f"❌ Resource directory not found: {resource_dir}")
        return False
    
    # Find all RQ/RS XSD files, excluding common types
    xsd_files = []
    exclude_files = {
        "IATA_OffersAndOrdersCommonTypes.xsd",
        "IATA_PaymentClearanceCommonTypes.xsd"
    }
    
    for file_path in resource_dir.glob("*.xsd"):
        filename = file_path.name
        if (filename.endswith("RQ.xsd") or filename.endswith("RS.xsd")) and filename not in exclude_files:
            xsd_files.append(file_path)
    
    if not xsd_files:
        print(f"❌ No RQ/RS XSD files found in {resource_dir}")
        return False
    
    print(f"🔍 Found {len(xsd_files)} RQ/RS schema files to test:")
    for xsd_file in sorted(xsd_files):
        print(f"  - {xsd_file.name}")
    print()
    
    # Test results tracking
    results = {
        'total': len(xsd_files),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test each schema
    for xsd_file in sorted(xsd_files):
        print(f"🧪 Testing: {xsd_file.name}")
        
        try:
            # Start timing
            start_time = time.time()
            
            # Create XML generator
            generator = XMLGenerator(str(xsd_file))
            
            # Generate XML
            xml_content = generator.generate_dummy_xml()
            
            # End timing
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Validate results
            if xml_content and not xml_content.startswith('<error>'):
                xml_size = len(xml_content)
                print(f"  ✅ SUCCESS - Generated {xml_size:,} chars in {generation_time:.2f}s")
                
                # Check for depth limit indicators
                depth_indicators = [
                    '_recursion_limit',
                    '_circular_ref', 
                    '_type_reuse',
                    'Maximum depth reached',
                    'Circular reference',
                    'already processed'
                ]
                
                found_limits = []
                for indicator in depth_indicators:
                    if indicator in xml_content:
                        found_limits.append(indicator)
                
                if found_limits:
                    print(f"  🛡️  Depth protection active: {', '.join(found_limits)}")
                
                results['success'] += 1
                
                # Show performance warnings for slow schemas
                if generation_time > 5.0:
                    print(f"  ⚠️  SLOW GENERATION: {generation_time:.2f}s (consider further optimization)")
                elif generation_time > 2.0:
                    print(f"  ⚡ Moderate time: {generation_time:.2f}s")
                
            else:
                print(f"  ❌ FAILED - Error in generated XML")
                if xml_content.startswith('<error>'):
                    # Extract error message
                    error_start = xml_content.find('<message>') + 9
                    error_end = xml_content.find('</message>')
                    if error_start > 8 and error_end > error_start:
                        error_msg = xml_content[error_start:error_end]
                        print(f"     Error: {error_msg}")
                
                results['failed'] += 1
                results['errors'].append({
                    'file': xsd_file.name,
                    'error': 'Generated error XML',
                    'time': generation_time
                })
        
        except Exception as e:
            end_time = time.time()
            generation_time = end_time - start_time
            
            print(f"  ❌ EXCEPTION - {type(e).__name__}: {str(e)}")
            
            # Check if it's a stack overflow or recursion error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['recursion', 'stack', 'depth']):
                print(f"  🚨 RECURSION ERROR DETECTED! Our fixes may not be working properly.")
            
            results['failed'] += 1
            results['errors'].append({
                'file': xsd_file.name,
                'error': f"{type(e).__name__}: {str(e)}",
                'time': generation_time
            })
        
        print()  # Empty line for readability
    
    # Print summary
    print("=" * 80)
    print("🏁 FINAL RESULTS:")
    print(f"   Total schemas tested: {results['total']}")
    print(f"   ✅ Successful: {results['success']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   Success rate: {results['success']/results['total']*100:.1f}%")
    
    if results['errors']:
        print(f"\n❌ FAILED SCHEMAS:")
        for error in results['errors']:
            print(f"   - {error['file']}: {error['error']} (took {error['time']:.2f}s)")
    
    # Determine overall success using assertions
    if results['failed'] == 0:
        print(f"\n🎉 ALL SCHEMAS PASSED! Recursion depth restrictions are working correctly.")
        assert True, "All schemas passed successfully"
    elif results['success'] > results['failed']:
        print(f"\n⚠️  Most schemas passed, but {results['failed']} failed. Check errors above.")
        # Show detailed error information in assertion
        error_details = "; ".join([f"{e['file']}: {e['error']}" for e in results['errors']])
        assert False, f"Some schemas failed: {error_details}"
    else:
        print(f"\n🚨 MAJOR ISSUES! More than half the schemas failed. Recursion fixes may need work.")
        error_details = "; ".join([f"{e['file']}: {e['error']}" for e in results['errors']])
        assert False, f"Major failures in schema processing: {error_details}"


if __name__ == "__main__":
    print("🚀 Starting comprehensive XSD schema recursion test...")
    print("This will test XML generation for all RQ/RS schemas to ensure recursion limits work.\n")
    
    try:
        test_all_rq_rs_schemas()
        print("\n✨ Test completed successfully! All recursion depth restrictions are working.")
        exit(0)
    except AssertionError as e:
        print(f"\n💥 Test completed with failures: {e}")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        exit(1)