#!/usr/bin/env python3
"""
Test that tree values are unique to prevent streamlit_tree_select errors.
"""

import os
import sys
sys.path.append('.')

from services.schema_analyzer import SchemaAnalyzer
from app import convert_tree_to_streamlit_format
from config import get_config

def test_unique_tree_values():
    """Test that all tree node values are unique."""
    
    print("🧪 Testing Tree Value Uniqueness")
    print("=" * 40)
    
    # Load configuration and analyzer
    config = get_config()
    analyzer = SchemaAnalyzer(config)
    
    # Test with IATA_OrderViewRS.xsd
    # Get the project root directory (parent of test directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    resource_dir = os.path.join(project_root, 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    print(f"📋 Testing with: {os.path.basename(xsd_path)}")
    
    # Analyze schema
    analysis = analyzer.analyze_xsd_schema(xsd_path)
    
    if analysis['success']:
        element_tree = analysis['element_tree']
        
        print(f"🌳 Converting tree to streamlit format...")
        
        # Convert tree format (same as in UI)
        tree_nodes = []
        global_counter = {'count': 0}
        for root_name, tree in element_tree.items():
            tree_node = convert_tree_to_streamlit_format(tree, "", global_counter)
            tree_nodes.append(tree_node)
        
        # Collect all values from the tree
        all_values = []
        
        def collect_values(node):
            all_values.append(node['value'])
            if 'children' in node:
                for child in node['children']:
                    collect_values(child)
        
        for tree_node in tree_nodes:
            collect_values(tree_node)
        
        print(f"📊 Analysis Results:")
        print(f"   Total nodes: {len(all_values)}")
        print(f"   Unique values: {len(set(all_values))}")
        print(f"   Duplicates: {len(all_values) - len(set(all_values))}")
        
        # Check for duplicates
        if len(all_values) == len(set(all_values)):
            print(f"✅ SUCCESS: All tree values are unique!")
        else:
            print(f"❌ FAILURE: Found duplicate values!")
            
            # Find and show duplicates
            seen = set()
            duplicates = set()
            for value in all_values:
                if value in seen:
                    duplicates.add(value)
                seen.add(value)
            
            print(f"🔍 Duplicate values found:")
            for dup in sorted(duplicates):
                count = all_values.count(dup)
                print(f"   '{dup}' appears {count} times")
        
        # Show a sample of generated values
        print(f"\n📋 Sample of generated values:")
        for i, value in enumerate(sorted(all_values)[:10]):
            print(f"   {i+1}: {value}")
        if len(all_values) > 10:
            print(f"   ... and {len(all_values) - 10} more")
            
    else:
        print(f"❌ Analysis failed: {analysis['error']}")

if __name__ == "__main__":
    test_unique_tree_values()