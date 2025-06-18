#!/usr/bin/env python3
"""
Test script to validate the Streamlit UI fix for duplicate tree values.
"""

import os
import sys
sys.path.append('.')

from services.schema_analyzer import SchemaAnalyzer
from app import convert_tree_to_streamlit_format
from config import get_config

def test_streamlit_ui_fix():
    """Test the Streamlit UI fix comprehensively."""
    
    print("🔧 Testing Streamlit UI Tree Fix")
    print("=" * 50)
    
    # Load configuration and analyzer
    config = get_config()
    analyzer = SchemaAnalyzer(config)
    
    # Test with IATA_OrderViewRS.xsd (the problematic schema)
    # Get the project root directory (parent of test directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    resource_dir = os.path.join(project_root, 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    print(f"📋 Testing with: {os.path.basename(xsd_path)}")
    
    # Analyze schema
    analysis = analyzer.analyze_xsd_schema(xsd_path)
    
    if not analysis['success']:
        print(f"❌ Schema analysis failed: {analysis['error']}")
        return
    
    element_tree = analysis['element_tree']
    choices = analysis['choices']
    
    print(f"✅ Schema analysis successful")
    print(f"   - {len(choices)} choices found")
    print(f"   - {len(element_tree)} root elements")
    
    # Convert tree format (simulate what the UI does)
    print(f"\n🌳 Converting tree to Streamlit format...")
    
    try:
        tree_nodes = []
        global_counter = {'count': 0}
        
        for root_name, tree in element_tree.items():
            print(f"   Processing root: {root_name}")
            tree_node = convert_tree_to_streamlit_format(tree, "", global_counter)
            tree_nodes.append(tree_node)
        
        print(f"✅ Tree conversion successful")
        print(f"   - {len(tree_nodes)} root nodes created")
        print(f"   - {global_counter['count']} total nodes processed")
        
        # Validate uniqueness
        all_values = []
        
        def collect_values(node):
            all_values.append(node['value'])
            if 'children' in node:
                for child in node['children']:
                    collect_values(child)
        
        for tree_node in tree_nodes:
            collect_values(tree_node)
        
        unique_values = set(all_values)
        
        print(f"\n📊 Uniqueness Validation:")
        print(f"   - Total nodes: {len(all_values)}")
        print(f"   - Unique values: {len(unique_values)}")
        print(f"   - Duplicates: {len(all_values) - len(unique_values)}")
        
        if len(all_values) == len(unique_values):
            print(f"✅ SUCCESS: All tree values are unique!")
            print(f"   Tree structure is ready for streamlit_tree_select")
        else:
            print(f"❌ FAILURE: Found duplicate values!")
            assert False, "Found duplicate values in tree structure"
        
        # Test the specific problematic path that was causing issues
        pgp_values = [v for v in all_values if 'PGPData' in v and 'choice' in v]
        if pgp_values:
            print(f"\n🔍 PGPData choice values (previously problematic):")
            for value in sorted(pgp_values)[:5]:  # Show first 5
                print(f"   - {value}")
            if len(pgp_values) > 5:
                print(f"   ... and {len(pgp_values) - 5} more")
            
            # Check for uniqueness in PGP values specifically
            pgp_unique = set(pgp_values)
            if len(pgp_values) == len(pgp_unique):
                print(f"✅ PGPData values are now unique ({len(pgp_values)} values)")
            else:
                print(f"❌ PGPData still has duplicates")
                assert False, "PGPData still has duplicates"
        
        print(f"\n🎉 All tests passed! UI tree display should work correctly now.")
        # Test completed successfully
        assert True
        
    except Exception as e:
        print(f"❌ Tree conversion failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Tree conversion failed: {e}"

if __name__ == "__main__":
    test_streamlit_ui_fix()