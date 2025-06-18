#!/usr/bin/env python3
"""
Test the UI improvements for schema analysis.
"""

import os
from services.schema_analyzer import SchemaAnalyzer
from config import get_config

def test_ui_improvements():
    """Test enhanced choice detection and tree depth."""
    
    print("🧪 Testing UI Improvements")
    print("=" * 40)
    
    # Load configuration
    config = get_config()
    analyzer = SchemaAnalyzer(config)
    
    # Test with IATA_OrderViewRS.xsd
    # Get the project root directory (parent of test directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    resource_dir = os.path.join(project_root, 'resource', '21_3_5_distribution_schemas')
    xsd_path = os.path.join(resource_dir, 'IATA_OrderViewRS.xsd')
    
    print(f"📋 Testing with: {os.path.basename(xsd_path)}")
    print(f"🔧 Tree depth limit: {config.ui.default_tree_depth}")
    
    # Analyze schema
    analysis = analyzer.analyze_xsd_schema(xsd_path)
    
    if analysis['success']:
        choices = analysis['choices']
        element_tree = analysis['element_tree']
        
        print(f"\n🔀 Choice Detection Results:")
        print(f"   Total choices found: {len(choices)}")
        
        # Categorize choices
        root_choices = [c for c in choices if '.' not in c['path'] or c['path'].count('.') == 0]
        nested_choices = [c for c in choices if '.' in c['path'] and c['path'].count('.') > 0]
        
        print(f"   Root-level choices: {len(root_choices)}")
        print(f"   Nested choices: {len(nested_choices)}")
        
        # Show choice details
        for i, choice in enumerate(choices):
            print(f"\n   Choice {i+1}:")
            print(f"     Path: {choice['path']}")
            print(f"     Elements: {[elem['name'] for elem in choice['elements']]}")
            print(f"     Type: {'Root' if choice['path'] in [c['path'] for c in root_choices] else 'Nested'}")
        
        print(f"\n🌳 Tree Structure Results:")
        for root_name, tree in element_tree.items():
            print(f"   Root: {root_name}")
            
            def count_tree_depth(node, current_depth=0):
                max_depth = current_depth
                if 'children' in node:
                    for child in node['children']:
                        child_depth = count_tree_depth(child, current_depth + 1)
                        max_depth = max(max_depth, child_depth)
                return max_depth
            
            def count_tree_nodes(node):
                count = 1
                if 'children' in node:
                    for child in node['children']:
                        count += count_tree_nodes(child)
                return count
            
            tree_depth = count_tree_depth(tree)
            tree_nodes = count_tree_nodes(tree)
            
            print(f"     Max depth: {tree_depth}")
            print(f"     Total nodes: {tree_nodes}")
            
            # Show a few levels of the tree
            def show_tree(node, indent=""):
                print(f"{indent}- {node['name']} {node.get('occurs', {})}")
                if node.get('is_choice'):
                    print(f"{indent}  🔀 CHOICE: {[opt['name'] for opt in node.get('choice_options', [])]}")
                if 'children' in node and len(indent) < 12:  # Limit display depth
                    for child in node['children'][:3]:  # Show first 3 children
                        show_tree(child, indent + "  ")
                    if len(node['children']) > 3:
                        print(f"{indent}  ... and {len(node['children']) - 3} more children")
            
            print(f"     Structure preview:")
            show_tree(tree, "       ")
        
        print(f"\n✅ UI Improvements Test Complete!")
        print(f"   - Enhanced choice detection: {'✓' if len(choices) > 1 else '?'}")
        print(f"   - Deeper tree extraction: {'✓' if any(count_tree_depth(tree) > 4 for tree in element_tree.values()) else '?'}")
        print(f"   - Nested choice detection: {'✓' if len(nested_choices) > 0 else '?'}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")

if __name__ == "__main__":
    test_ui_improvements()