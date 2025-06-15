"""
XML Chunker - Main Streamlit Application

This is the main entry point for the XML Chunker application, a modular Streamlit 
interface for parsing XSD schemas and generating compliant dummy XML files.

The application specializes in IATA NDC (New Distribution Capability) XSD schemas, 
providing advanced analysis, choice element handling, and validation-aware XML generation.

Key Features:
- Interactive XSD file upload with dependency resolution
- Real-time schema analysis with tree visualization
- Choice element selection and unbounded element configuration
- Type-aware XML generation with validation compliance
- Comprehensive error categorization and reporting

Architecture:
This module serves as the presentation layer, orchestrating the following services:
- FileManager: File operations and temporary directory management
- XMLValidator: XML validation against XSD schemas with detailed error reporting
- SchemaAnalyzer: XSD schema analysis and structure extraction
- XMLGenerator: Universal XML generation engine

Author: XML Chunker Development Team
License: MIT
"""

import streamlit as st
import io
import os
import tempfile
from utils.xml_generator import XMLGenerator
from utils.xsd_parser import XSDParser
from streamlit_tree_select import tree_select
from config import get_config
from services.file_manager import FileManager
from services.xml_validator import XMLValidator
from services.schema_analyzer import SchemaAnalyzer

# Initialize configuration and services
config = get_config()
file_manager = FileManager(config)
xml_validator = XMLValidator(config)
schema_analyzer = SchemaAnalyzer(config)

st.set_page_config(
    page_title=config.ui.default_page_title,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .selected-file {
        background-color: #5830D8;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
    .content-display {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        max-height: 500px;
        overflow-y: auto;
        font-family: monospace;
        white-space: pre-wrap;
        margin-top: 10px;
    }
    .generate-button {
        margin-top: 20px;
    }
    .xml-display {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        max-height: 500px;
        overflow-y: auto;
        font-family: monospace;
        white-space: pre-wrap;
        margin-top: 10px;
        background-color: #f8f9fa;
    }
    
    /* Custom styles for streamlit_tree_select to make text brighter */
    .stTreeSelect {
        color: #ffffff !important;
    }
    
    /* Target the tree select component specifically */
    iframe[title="streamlit_tree_select.tree_select"] {
        background: transparent !important;
    }
    
    /* Style for tree nodes - make text bright white */
    .stTreeSelect .rc-tree {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    .stTreeSelect .rc-tree .rc-tree-node-content-wrapper {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    .stTreeSelect .rc-tree .rc-tree-node-content-wrapper:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
    }
    
    .stTreeSelect .rc-tree .rc-tree-node-content-wrapper.rc-tree-node-selected {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    /* Tree select container styling */
    .stTreeSelect .rc-tree-list {
        background: transparent !important;
    }
    
    .stTreeSelect .rc-tree-treenode {
        color: #ffffff !important;
    }
    
    /* Tree icons styling */
    .stTreeSelect .rc-tree-switcher {
        color: #ffffff !important;
    }
    
    .stTreeSelect .rc-tree-checkbox {
        border-color: #ffffff !important;
    }
    
    /* Force text color in dark mode */
    .stTreeSelect * {
        color: #ffffff !important;
    }
    
    /* Additional styling for better visibility */
    div[data-testid="stExpander"] .stTreeSelect {
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

def analyze_xsd_schema(xsd_file_path):
    """
    Analyze XSD schema to extract choice elements and structure.
    
    Args:
        xsd_file_path: Path to the XSD file
        
    Returns:
        Dictionary containing schema analysis
    """
    return schema_analyzer.analyze_xsd_schema(xsd_file_path)

def convert_tree_to_streamlit_format(node, parent_path="", node_counter=None):
    """
    Convert our tree node format to streamlit_tree_select format.
    
    Args:
        node: Our tree node data
        parent_path: Path for unique node identification
        node_counter: Counter to ensure unique values
        
    Returns:
        Dictionary in streamlit_tree_select format
    """
    # Initialize counter if not provided
    if node_counter is None:
        node_counter = {'count': 0}
    
    # Create unique value for this node with counter to prevent duplicates
    # Clean the node name to avoid special characters that might cause issues
    clean_name = str(node.get('name', 'Unknown')).replace(' ', '_').replace(':', '_').replace('[', '_').replace(']', '_')
    base_value = f"{parent_path}.{clean_name}" if parent_path else clean_name
    node_value = f"{base_value}_{node_counter['count']}"
    node_counter['count'] += 1
    
    # Determine icon and type info based on node type
    if node['is_choice']:
        icon = "🔀"
        type_info = "CHOICE"
    elif node.get('is_unbounded', False) or (node['occurs']['max'] not in ['1', 1]):
        icon = "🔄"
        max_display = "∞" if node['occurs']['max'] == 'unbounded' else node['occurs']['max']
        type_info = f"[{node['occurs']['min']}-{max_display}]"
    else:
        icon = "📝"
        # CRITICAL: Show actual min/max occurs, not hardcoded [1:1]
        min_val = node['occurs']['min']
        max_val = node['occurs']['max']
        type_info = f"[{min_val}:{max_val}]"
    
    # Show type info for simple types
    if '_type_info' in node:
        icon = "📄"
        type_info = "[Simple]"
    
    # Create label with icon and type info - clean format without unicode blocks
    if node['is_choice']:
        label = f"🔀 {node['name']} {type_info}"
    elif node.get('is_unbounded', False) or (node['occurs']['max'] not in ['1', 1]):
        label = f"🔄 {node['name']} {type_info}"
    elif '_type_info' in node:
        label = f"📄 {node['name']} {type_info}"
    else:
        label = f"📝 {node['name']} {type_info}"
    
    # Create the tree select node
    tree_node = {
        "label": label,
        "value": node_value
    }
    
    # Add children if they exist
    children = []
    
    # Add choice options as special children
    if node['is_choice'] and node.get('choice_options', []):
        for option in node['choice_options']:
            max_display = "∞" if option['max_occurs'] == 'unbounded' or option['max_occurs'] is None else option['max_occurs']
            choice_label = f"⚬ {option['name']} ({option['min_occurs']}-{max_display})"
            choice_value = f"{node_value}.choice.{option['name']}_{node_counter['count']}"
            node_counter['count'] += 1
            children.append({
                "label": choice_label,
                "value": choice_value
            })
    
    # Add regular children
    if node.get('children', []):
        for child in node['children']:
            child_node = convert_tree_to_streamlit_format(child, base_value, node_counter)
            children.append(child_node)
    
    # Add error/type info as children if present
    if '_type_info' in node:
        info_value = f"{node_value}.info_{node_counter['count']}"
        node_counter['count'] += 1
        children.append({
            "label": f"ℹ️ {node['_type_info']}",
            "value": info_value
        })
    
    if '_error' in node:
        error_icon = "📄" if "Simple type element" in node['_error'] else "⚠️"
        error_value = f"{node_value}.error_{node_counter['count']}"
        node_counter['count'] += 1
        children.append({
            "label": f"{error_icon} {node['_error']}",
            "value": error_value
        })
    
    if children:
        tree_node["children"] = children
    
    return tree_node

def format_validation_error(error):
    """
    Format a validation error for display.
    
    Args:
        error: xmlschema validation error object
        
    Returns:
        Dictionary with formatted error information
    """
    return xml_validator.format_validation_error(error)

def clean_selection_display_name(selection):
    """
    Clean up tree selection names for display in the summary.
    
    Args:
        selection: Raw selection string like "IATA_OrderViewRS.Response.DataLists.BaggageAllowanceList.BaggageAllowance.PieceAllowance_77"
        
    Returns:
        Cleaned display string like "IATA_OrderViewRS → Response → DataLists → BaggageAllowanceList → BaggageAllowance → PieceAllowance"
    """
    if not selection:
        return selection
    
    # Remove the trailing unique number (e.g., "_77", "_123")
    # Pattern: remove _[number] at the end
    import re
    cleaned = re.sub(r'_\d+$', '', selection)
    
    # Replace dots with arrows for better readability
    if '.' in cleaned:
        path_parts = cleaned.split('.')
        # Take the last 5-6 parts to avoid too long display, but show meaningful context
        if len(path_parts) > 6:
            path_parts = ['...'] + path_parts[-5:]
        return ' → '.join(path_parts)
    else:
        return cleaned

def validate_xml_against_schema(xml_content, xsd_file_path, uploaded_file_name=None, uploaded_file_content=None):
    """
    Validate generated XML against the XSD schema.
    
    Args:
        xml_content: XML content to validate
        xsd_file_path: Path to the XSD schema file (may not exist)
        uploaded_file_name: Original uploaded file name
        uploaded_file_content: Original uploaded file content
        
    Returns:
        Dictionary containing validation results
    """
    return xml_validator.validate_xml_against_schema(xml_content, xsd_file_path, uploaded_file_name, uploaded_file_content)

def generate_xml_from_xsd(xsd_file_path, xsd_file_name, selected_choices=None, unbounded_counts=None, generation_mode="Minimalistic", optional_selections=None):
    """
    Generate XML from XSD schema with user-specified choices and generation mode.
    
    Args:
        xsd_file_path: Path to the XSD file
        xsd_file_name: Original name of the XSD file
        selected_choices: Dictionary of selected choices for generation
        unbounded_counts: Dictionary of counts for unbounded elements
        generation_mode: Generation strategy ("Minimalistic", "Complete", "Custom")
        optional_selections: List of optional element paths to include (for Custom mode)
        
    Returns:
        Generated XML content
    """
    try:
        file_manager.setup_temp_directory_with_dependencies(xsd_file_path, xsd_file_name)
        generator = XMLGenerator(xsd_file_path)
        
        # Pass user selections and generation mode to generator
        return generator.generate_dummy_xml_with_options(
            selected_choices=selected_choices, 
            unbounded_counts=unbounded_counts,
            generation_mode=generation_mode,
            optional_selections=optional_selections
        )
    except Exception as e:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
  <message>Error generating XML: {str(e)}</message>
</error>"""

def main():
    st.markdown('<div class="main-header">XML Chunker</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    # File upload section - always visible at the top
    st.markdown("---")
    st.markdown("### 📁 Upload XSD Schema")
    
    uploaded_file = st.file_uploader("Select a XSD file to begin", type=["xsd"], help="Upload an XSD schema file to analyze and generate XML")
    
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")
        file_name = uploaded_file.name
        
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(uploaded_file.getvalue())
        
        # Set up dependencies for schema analysis
        file_manager.setup_temp_directory_with_dependencies(temp_file_path, file_name)
        
        # Store file info in session state for cross-tab access
        st.session_state['uploaded_file_name'] = file_name
        st.session_state['uploaded_file_content'] = file_content
        st.session_state['temp_file_path'] = temp_file_path
        st.session_state['temp_dir'] = temp_dir
        
        # Show file info briefly
        st.success(f"✅ **{file_name}** uploaded successfully")
        
        # Create tabs for the workflow
        tab1, tab2, tab3 = st.tabs(["🔍 **Analyze Schema**", "⚙️ **Configure Generation**", "🚀 **Generate & Validate**"])
        
        # TAB 1: ANALYZE SCHEMA
        with tab1:
            st.markdown("### 📊 Schema Analysis")
            
            with st.spinner("Analyzing XSD schema..."):
                analysis = analyze_xsd_schema(temp_file_path)
                
                if analysis['success']:
                    schema_info = analysis['schema_info']
                    choices = analysis['choices']
                    unbounded_elements = analysis['unbounded_elements']
                    element_tree = analysis['element_tree']
                    
                    # Store analysis results in session state for other tabs
                    st.session_state['schema_analysis'] = analysis
                    
                    # Display schema information in a clean layout
                    col_info1, col_info2, col_info3 = st.columns(3)
                    
                    with col_info1:
                        st.metric("Elements", schema_info.get('elements_count', 0))
                    
                    with col_info2:
                        st.metric("Types", schema_info.get('types_count', 0))
                    
                    with col_info3:
                        st.metric("Choices Found", len(choices) if choices else 0)
                    
                    # Namespace info
                    if schema_info.get('target_namespace'):
                        st.info(f"**Target Namespace:** `{schema_info.get('target_namespace')}`")
                    
                    # XSD Content in an expandable section
                    with st.expander("📄 View XSD Content", expanded=False):
                        st.code(file_content, language="xml", height=400)
                    
                    st.markdown("---")
                    
                    # Schema Structure - Full width display
                    st.markdown("### 🌳 Schema Structure")
                    
                    if element_tree:
                        st.markdown("*Interactive schema tree - explore the XSD structure*")
                        
                        # Convert our tree format to streamlit_tree_select format
                        tree_nodes = []
                        global_counter = {'count': 0}  # Single counter for all nodes to ensure uniqueness
                        for root_name, tree in element_tree.items():
                            tree_node = convert_tree_to_streamlit_format(tree, "", global_counter)
                            tree_nodes.append(tree_node)
                        
                        # Display the tree with streamlit_tree_select
                        if tree_nodes:
                            # Add legend for exploration
                            st.info("""💡 **Schema Structure Legend:**

🔀 **Choice Elements** - Select one option from multiple choices

🔄 **Repeating Elements** - Can occur multiple times (1-∞, 2-5, etc.)

📝 **Required Elements** - Must occur [1:1] or [1:∞]

📄 **Optional Elements** - May occur [0:1] or [0:∞]

⚬ **Choice Options** - Available options within a choice element

ℹ️ **Type Information** - Additional schema details

*Explore the tree structure to understand your schema*""")
                            
                            # Auto-expand more levels to show tree structure better
                            auto_expanded = []
                            if tree_nodes:
                                # Expand root
                                auto_expanded.append(tree_nodes[0]['value'])
                                # Expand first few levels automatically
                                def add_expanded_children(node, max_level=2, current_level=0):
                                    if current_level < max_level and 'children' in node:
                                        for child in node['children'][:3]:  # Limit to first 3 children per level
                                            auto_expanded.append(child['value'])
                                            add_expanded_children(child, max_level, current_level + 1)
                                
                                add_expanded_children(tree_nodes[0])
                            
                            # Display tree for exploration (read-only in analysis mode)
                            selected = tree_select(
                                tree_nodes,
                                key="schema_tree_analysis",
                                check_model="leaf",
                                expanded=auto_expanded,
                                no_cascade=True,
                                disabled=False
                            )
                            
                            # Show selected information for exploration
                            if selected and selected.get('checked'):
                                st.markdown("---")
                                st.markdown("**Selected for Exploration:**")
                                for item in selected['checked']:
                                    clean_display = clean_selection_display_name(item)
                                    st.markdown(f"• `{clean_display}`")
                        else:
                            st.info("No schema structure could be extracted from this XSD file.")
                    
                else:
                    st.error(f"Error analyzing schema: {analysis['error']}")
                    st.session_state['schema_analysis'] = None
        
        # TAB 2: CONFIGURE GENERATION
        with tab2:
            st.markdown("### ⚙️ Generation Configuration")
            
            # Check if schema analysis is available
            if 'schema_analysis' not in st.session_state or not st.session_state['schema_analysis']:
                st.warning("⚠️ Please analyze the schema in the **Analyze Schema** tab first.")
                st.stop()
            
            analysis = st.session_state['schema_analysis']
            schema_info = analysis['schema_info']
            choices = analysis['choices']
            unbounded_elements = analysis['unbounded_elements']
            element_tree = analysis['element_tree']
            
            # XML Generation Mode Selection
            st.markdown("#### 🎯 Generation Strategy")
            st.markdown("Choose how to generate XML from optional elements:")
            
            generation_mode = st.radio(
                "Generation Mode:",
                options=["Minimalistic", "Complete", "Custom"],
                index=0,
                key="generation_mode",
                help="Minimalistic: Required + shallow optional | Complete: All elements | Custom: Tree selection",
                horizontal=True
            )
            
            if generation_mode == "Minimalistic":
                st.info("🔹 **Minimalistic**: Includes required elements + optional elements at depth < 2 (recommended for most cases)")
            elif generation_mode == "Complete":
                st.warning("🔹 **Complete**: Includes ALL optional elements up to depth 6 (may create very large XMLs)")
            else:  # Custom
                st.info("🔹 **Custom**: Select specific optional elements using the tree selector below")
            
            st.markdown("---")
            
            # Custom Mode: Element Selection Tree
            if generation_mode == "Custom":
                st.markdown("#### 🌳 Custom Element Selection")
                
                if element_tree:
                    st.markdown("*Select optional elements to include in XML generation*")
                    st.warning("**Custom Mode**: ☑️ Check optional elements (📄 [0:1]) you want to include. Required elements (📝 [1:1]) are always included.")
                    
                    # Convert our tree format to streamlit_tree_select format
                    tree_nodes = []
                    global_counter = {'count': 0}
                    for root_name, tree in element_tree.items():
                        tree_node = convert_tree_to_streamlit_format(tree, "", global_counter)
                        tree_nodes.append(tree_node)
                    
                    if tree_nodes:
                        st.info("""💡 **Element Selection Guide:**

📝 **Required Elements [1:1]** - Always included (cannot uncheck)

📄 **Optional Elements [0:1]** - Check to include in XML generation

🔄 **Repeating Elements [1:∞]** - Always included if required, optional if [0:∞]

🔀 **Choice Elements** - Use choice selection below for these

⚬ **Choice Options** - Available within choice elements

*Check the optional elements you want in your generated XML*""")
                        
                        # Auto-expand for better selection experience
                        auto_expanded = []
                        if tree_nodes:
                            auto_expanded.append(tree_nodes[0]['value'])
                            def add_expanded_children(node, max_level=2, current_level=0):
                                if current_level < max_level and 'children' in node:
                                    for child in node['children'][:3]:
                                        auto_expanded.append(child['value'])
                                        add_expanded_children(child, max_level, current_level + 1)
                            add_expanded_children(tree_nodes[0])
                        
                        selected = tree_select(
                            tree_nodes,
                            key="custom_element_selection",
                            check_model="leaf",
                            expanded=auto_expanded,
                            no_cascade=True,
                            disabled=False
                        )
                        
                        # Store selections
                        if selected and selected.get('checked'):
                            st.markdown("**Selected Optional Elements:**")
                            optional_selections = []
                            for item in selected['checked']:
                                clean_display = clean_selection_display_name(item)
                                st.markdown(f"• `{clean_display}`")
                                optional_selections.append(item)
                            st.session_state['optional_element_selections'] = optional_selections
                        else:
                            st.session_state['optional_element_selections'] = []
                
                st.markdown("---")
            
            # Choice Selection Section
            selected_choices = {}
            if choices:
                st.markdown("#### 🔀 Choice Elements")
                st.markdown(f"Select elements for choice constraints ({len(choices)} choices found):")
                
                # Group choices by depth for better organization
                root_choices = [c for c in choices if '.' not in c['path'] or c['path'].count('.') == 0]
                nested_choices = [c for c in choices if '.' in c['path'] and c['path'].count('.') > 0]
                
                # Display root-level choices first
                if root_choices:
                    st.markdown("**Root-level Choices:**")
                    for i, choice in enumerate(root_choices):
                        choice_key = f"choice_{i}"
                        options = [f"{elem['name']} ({elem['min_occurs']}-{elem['max_occurs']})" 
                                  for elem in choice['elements']]
                        
                        selected_option = st.selectbox(
                            f"Choice at `{choice['path']}`:",
                            options,
                            key=choice_key,
                            help=f"Select one option from this choice (min: {choice['min_occurs']}, max: {choice['max_occurs']})"
                        )
                        
                        # Extract the element name from selection
                        selected_element = selected_option.split(' (')[0]
                        selected_choices[choice_key] = {
                            'path': choice['path'],
                            'selected_element': selected_element,
                            'choice_data': choice
                        }
                
                # Display nested choices
                if nested_choices:
                    st.markdown("**Nested Choices:**")
                    base_index = len(root_choices)
                    for i, choice in enumerate(nested_choices):
                        choice_key = f"choice_{base_index + i}"
                        options = [f"{elem['name']} ({elem['min_occurs']}-{elem['max_occurs']})" 
                                  for elem in choice['elements']]
                        
                        # Create a more readable path display
                        path_display = choice['path'].replace('.', ' → ')
                        
                        selected_option = st.selectbox(
                            f"Nested choice at `{path_display}`:",
                            options,
                            key=choice_key,
                            help=f"Select one option from this nested choice (min: {choice['min_occurs']}, max: {choice['max_occurs']})"
                        )
                        
                        # Extract the element name from selection
                        selected_element = selected_option.split(' (')[0]
                        selected_choices[choice_key] = {
                            'path': choice['path'],
                            'selected_element': selected_element,
                            'choice_data': choice
                        }
                
                # Show summary
                st.success(f"✅ Configured {len(choices)} choices: {len(root_choices)} root-level, {len(nested_choices)} nested")
                st.markdown("---")
            
            # Unbounded element counts
            unbounded_counts = {}
            if unbounded_elements:
                st.markdown("#### 🔄 Repeating Elements")
                st.markdown("Set count for elements with maxOccurs > 1 or unbounded:")
                
                for elem in unbounded_elements:
                    max_display = elem['max_occurs'] if elem['max_occurs'] != 'unbounded' else '∞'
                    count = st.number_input(
                        f"**{elem['name']}** (max: {max_display}):",
                        min_value=1,
                        max_value=config.elements.max_unbounded_count if elem['max_occurs'] == 'unbounded' else min(config.elements.max_unbounded_count, int(elem['max_occurs'])),
                        value=config.elements.default_element_count,
                        key=f"count_{elem['path']}",
                        help=f"Number of {elem['name']} elements to generate"
                    )
                    unbounded_counts[elem['path']] = count
                
                st.markdown("---")
            
            # Store all selections in session state
            st.session_state['selected_choices'] = selected_choices
            st.session_state['unbounded_counts'] = unbounded_counts
            st.session_state['current_generation_mode'] = generation_mode
            
            # Configuration Summary
            st.markdown("#### 📋 Configuration Summary")
            
            col_sum1, col_sum2 = st.columns(2)
            
            with col_sum1:
                st.markdown(f"**Generation Mode:** `{generation_mode}`")
                if generation_mode == "Custom" and 'optional_element_selections' in st.session_state:
                    selections = st.session_state['optional_element_selections']
                    st.markdown(f"**Optional Elements Selected:** {len(selections)}")
                
                if selected_choices:
                    st.markdown(f"**Choices Configured:** {len(selected_choices)}")
            
            with col_sum2:
                if unbounded_counts:
                    st.markdown(f"**Unbounded Elements:** {len(unbounded_counts)}")
                    total_elements = sum(unbounded_counts.values())
                    st.markdown(f"**Total Repeating Elements:** {total_elements}")
            
            # Ready indicator
            if selected_choices or not choices:  # Ready if choices are configured or no choices exist
                st.success("🎉 **Configuration Complete!** Ready to generate XML in the next tab.")
            else:
                st.warning("⚠️ Please configure all choice elements before proceeding.")
        
        # TAB 3: GENERATE & VALIDATE
        with tab3:
            st.markdown("### 🚀 XML Generation & Validation")
            
            # Check if configuration is complete
            if 'schema_analysis' not in st.session_state or not st.session_state['schema_analysis']:
                st.warning("⚠️ Please analyze the schema in the **Analyze Schema** tab first.")
                st.stop()
            
            if 'current_generation_mode' not in st.session_state:
                st.warning("⚠️ Please configure generation settings in the **Configure Generation** tab first.")
                st.stop()
            
            # Show current configuration summary
            st.markdown("#### 📋 Current Configuration")
            
            # Create 4 columns for detailed configuration display
            col_schema, col_mode, col_repeating, col_choices = st.columns(4)
            
            # Schema Information (First column)
            with col_schema:
                st.markdown("**📄 Schema**")
                file_name = st.session_state.get('uploaded_file_name', 'unknown.xsd')
                analysis = st.session_state.get('schema_analysis', {})
                
                if analysis and analysis.get('success'):
                    schema_info = analysis.get('schema_info', {})
                    st.markdown(f"• **File:** `{file_name}`")
                    st.markdown(f"• **Elements:** {schema_info.get('elements_count', 0)}")
                    st.markdown(f"• **Types:** {schema_info.get('types_count', 0)}")
                    
                    # Show namespace if available (truncated)
                    namespace = schema_info.get('target_namespace', '')
                    if namespace:
                        # Truncate long namespaces for display
                        display_ns = namespace if len(namespace) <= 30 else f"{namespace[:27]}..."
                        st.markdown(f"• **Namespace:** `{display_ns}`")
                    else:
                        st.markdown("• **Namespace:** None")
                else:
                    st.markdown(f"• **File:** `{file_name}`")
                    st.markdown("• **Status:** Analysis failed")
            
            # Generation Mode (Second column)
            with col_mode:
                st.markdown("**⚙️ Generation Mode**")
                current_mode = st.session_state.get('current_generation_mode', 'Minimalistic')
                st.markdown(f"• **Mode:** `{current_mode}`")
                
                if current_mode == "Minimalistic":
                    st.markdown("• **Strategy:** Required + shallow optional")
                elif current_mode == "Complete":
                    st.markdown("• **Strategy:** All optional elements")
                elif current_mode == "Custom":
                    st.markdown("• **Strategy:** User-selected elements")
                    
                    # Show custom selections count
                    if 'optional_element_selections' in st.session_state:
                        selections = st.session_state['optional_element_selections']
                        st.markdown(f"• **Optional Selected:** {len(selections)}")
                    else:
                        st.markdown("• **Optional Selected:** 0")
                else:
                    st.markdown("• **Strategy:** Unknown")
            
            # Repeating Elements (Third column)
            with col_repeating:
                st.markdown("**🔄 Repeating Elements**")
                
                if 'unbounded_counts' in st.session_state and st.session_state['unbounded_counts']:
                    unbounded_counts = st.session_state['unbounded_counts']
                    total_elements = sum(unbounded_counts.values())
                    st.markdown(f"• **Total Count:** {total_elements}")
                    st.markdown(f"• **Elements:** {len(unbounded_counts)}")
                    
                    # Show first few elements with their counts
                    count_items = list(unbounded_counts.items())
                    for path, count in count_items[:2]:  # Show first 2
                        element_name = path.split('.')[-1]  # Get last part of path
                        st.markdown(f"• **{element_name}:** {count}")
                    
                    if len(count_items) > 2:
                        st.markdown(f"• **... and {len(count_items) - 2} more**")
                else:
                    st.markdown("• **Total Count:** 0")
                    st.markdown("• **Elements:** None configured")
            
            # Choices (Fourth column)
            with col_choices:
                st.markdown("**🔀 Choices**")
                
                if 'selected_choices' in st.session_state and st.session_state['selected_choices']:
                    selected_choices = st.session_state['selected_choices']
                    st.markdown(f"• **Configured:** {len(selected_choices)}")
                    
                    # Show first few choices with their selections
                    choice_items = list(selected_choices.items())
                    for choice_key, choice_data in choice_items[:2]:  # Show first 2
                        path = choice_data.get('path', 'Unknown')
                        selected = choice_data.get('selected_element', 'Unknown')
                        
                        # Truncate long paths and selections for display
                        display_path = path if len(path) <= 15 else f"{path[:12]}..."
                        display_selected = selected if len(selected) <= 15 else f"{selected[:12]}..."
                        
                        st.markdown(f"• **{display_path}:** {display_selected}")
                    
                    if len(choice_items) > 2:
                        st.markdown(f"• **... and {len(choice_items) - 2} more**")
                else:
                    # Check if choices exist but aren't configured
                    analysis = st.session_state.get('schema_analysis', {})
                    if analysis and analysis.get('success'):
                        choices = analysis.get('choices', [])
                        if choices:
                            st.markdown(f"• **Available:** {len(choices)}")
                            st.markdown("• **Configured:** 0")
                            st.markdown("• **Status:** ⚠️ Needs configuration")
                        else:
                            st.markdown("• **Available:** 0")
                            st.markdown("• **Status:** ✅ No choices in schema")
                    else:
                        st.markdown("• **Status:** Unknown")
            
            st.markdown("---")
            
            # XML Generation Section
            st.markdown("#### 🎯 Generate XML")
            
            col_gen1, col_gen2, col_gen3 = st.columns([1, 1, 1])
            
            with col_gen2:
                generate_clicked = st.button(
                    "🚀 **Generate XML**", 
                    key="generate_xml_btn", 
                    help="Generate XML based on your configuration",
                    type="primary",
                    use_container_width=True
                )
            
            # Handle XML generation
            if generate_clicked:
                with st.spinner("🔄 Generating XML with your configuration..."):
                    # Get user selections from session state
                    selected_choices = st.session_state.get('selected_choices', {})
                    unbounded_counts = st.session_state.get('unbounded_counts', {})
                    generation_mode = st.session_state.get('current_generation_mode', 'Minimalistic')
                    optional_selections = st.session_state.get('optional_element_selections', [])
                    
                    temp_file_path = st.session_state.get('temp_file_path')
                    file_name = st.session_state.get('uploaded_file_name')
                    
                    xml_content = generate_xml_from_xsd(
                        temp_file_path, 
                        file_name, 
                        selected_choices, 
                        unbounded_counts,
                        generation_mode,
                        optional_selections
                    )
                    
                    # Store XML content for validation and download
                    st.session_state['generated_xml'] = xml_content
            
            # Display generated XML if available
            if 'generated_xml' in st.session_state and st.session_state['generated_xml']:
                st.markdown("---")
                st.markdown("#### 📄 Generated XML")
                
                # Display XML in a code block
                st.code(st.session_state['generated_xml'], language="xml", height=500)
                
                # Action buttons for download and validation
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    st.download_button(
                        label="💾 **Download XML**",
                        data=st.session_state['generated_xml'],
                        file_name=f"{st.session_state.get('uploaded_file_name', 'schema').replace('.xsd', '')}_generated.xml",
                        mime="application/xml",
                        use_container_width=True
                    )
                
                with col_action3:
                    validate_clicked = st.button(
                        "✅ **Validate XML**", 
                        key="validate_xml_btn", 
                        help="Validate generated XML against XSD schema",
                        use_container_width=True
                    )
                
                # Handle validation
                if validate_clicked:
                    st.markdown("---")
                    st.markdown("#### 🔍 Validation Results")
                    
                    with st.spinner("🔄 Validating XML against schema..."):
                        temp_file_path = st.session_state.get('temp_file_path')
                        uploaded_file_name = st.session_state.get('uploaded_file_name')
                        uploaded_file_content = st.session_state.get('uploaded_file_content')
                        
                        validation_result = validate_xml_against_schema(
                            st.session_state['generated_xml'], 
                            temp_file_path,
                            uploaded_file_name,
                            uploaded_file_content
                        )
                        
                        if validation_result['success']:
                            error_breakdown = validation_result['error_breakdown']
                            total_errors = validation_result['total_errors']
                            
                            # Display validation results
                            if validation_result['is_valid']:
                                st.success("🎉 **XML is valid!** No validation errors found.")
                            else:
                                if total_errors == 0:
                                    st.success("🎉 **XML is valid!** No validation errors found.")
                                else:
                                    st.warning(f"⚠️ **XML has validation issues** ({total_errors} total errors)")
                            
                            # Show error breakdown in metrics
                            if total_errors > 0:
                                col_val1, col_val2, col_val3, col_val4 = st.columns(4)
                                
                                with col_val1:
                                    st.metric("Enumeration", error_breakdown['enumeration_errors'])
                                
                                with col_val2:
                                    st.metric("Boolean", error_breakdown['boolean_errors'])
                                
                                with col_val3:
                                    st.metric("Pattern", error_breakdown['pattern_errors'])
                                
                                with col_val4:
                                    st.metric("Structural", error_breakdown['structural_errors'])
                                
                                # Show detailed errors in expandable sections
                                if validation_result.get('categorized_errors'):
                                    st.markdown("**Detailed Error Analysis:**")
                                    
                                    categorized_errors = validation_result['categorized_errors']
                                    
                                    # Create expandable sections for each error type
                                    if categorized_errors['enumeration_errors']:
                                        with st.expander(f"🔤 Enumeration Errors ({len(categorized_errors['enumeration_errors'])})", expanded=False):
                                            st.caption("Values that don't match allowed enumeration lists. Expected for dummy data.")
                                            for i, error in enumerate(categorized_errors['enumeration_errors'][:5], 1):
                                                formatted_error = format_validation_error(error)
                                                st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                                            if len(categorized_errors['enumeration_errors']) > 5:
                                                st.info(f"... and {len(categorized_errors['enumeration_errors']) - 5} more enumeration errors")
                                    
                                    if categorized_errors['boolean_errors']:
                                        with st.expander(f"✅ Boolean Errors ({len(categorized_errors['boolean_errors'])})", expanded=False):
                                            st.caption("Invalid boolean values. These indicate type generation issues.")
                                            for i, error in enumerate(categorized_errors['boolean_errors'][:5], 1):
                                                formatted_error = format_validation_error(error)
                                                st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                                            if len(categorized_errors['boolean_errors']) > 5:
                                                st.info(f"... and {len(categorized_errors['boolean_errors']) - 5} more boolean errors")
                                    
                                    if categorized_errors['pattern_errors']:
                                        with st.expander(f"🎯 Pattern Errors ({len(categorized_errors['pattern_errors'])})", expanded=False):
                                            st.caption("Values that don't match required regex patterns. Expected for dummy data.")
                                            for i, error in enumerate(categorized_errors['pattern_errors'][:5], 1):
                                                formatted_error = format_validation_error(error)
                                                st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                                            if len(categorized_errors['pattern_errors']) > 5:
                                                st.info(f"... and {len(categorized_errors['pattern_errors']) - 5} more pattern errors")
                                    
                                    if categorized_errors['structural_errors']:
                                        with st.expander(f"🏗️ Structural Errors ({len(categorized_errors['structural_errors'])})", expanded=True):
                                            st.caption("Missing required elements or invalid XML structure. These should be minimal.")
                                            for i, error in enumerate(categorized_errors['structural_errors'][:10], 1):
                                                formatted_error = format_validation_error(error)
                                                st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                                            if len(categorized_errors['structural_errors']) > 10:
                                                st.info(f"... and {len(categorized_errors['structural_errors']) - 10} more structural errors")
                                
                                # Helpful tips
                                st.info("""
💡 **Understanding Validation Errors:**

• **Enumeration errors** are expected for dummy data - real values would need to match specific lists
• **Boolean errors** indicate type generation issues (being actively improved)  
• **Pattern errors** are expected for dummy data - real values would need specific formats
• **Structural errors** indicate missing required elements or wrong XML structure (should be minimal)

The XML structure is correct even with data constraint violations.
                                """)
                        else:
                            st.error(f"❌ **Validation failed:** {validation_result['error']}")
            else:
                st.info("👆 Click **Generate XML** above to create your XML file.")
        
        # Cleanup temp directory when done  
        if st.session_state.get('temp_dir'):
            try:
                import shutil
                shutil.rmtree(st.session_state['temp_dir'], ignore_errors=True)
            except Exception as e:
                pass  # Silent cleanup
    
    else:
        st.info("📁 Please upload an XSD file to begin analyzing and generating XML.")

if __name__ == "__main__":
    main()