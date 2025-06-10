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

def convert_tree_to_streamlit_format(node, parent_path=""):
    """
    Convert our tree node format to streamlit_tree_select format.
    
    Args:
        node: Our tree node data
        parent_path: Path for unique node identification
        
    Returns:
        Dictionary in streamlit_tree_select format
    """
    # Create unique value for this node
    node_value = f"{parent_path}.{node['name']}" if parent_path else node['name']
    
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
        type_info = "[1:1]"
    
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
            children.append({
                "label": choice_label,
                "value": f"{node_value}.choice.{option['name']}"
            })
    
    # Add regular children
    if node.get('children', []):
        for child in node['children']:
            child_node = convert_tree_to_streamlit_format(child, node_value)
            children.append(child_node)
    
    # Add error/type info as children if present
    if '_type_info' in node:
        children.append({
            "label": f"ℹ️ {node['_type_info']}",
            "value": f"{node_value}.info"
        })
    
    if '_error' in node:
        error_icon = "📄" if "Simple type element" in node['_error'] else "⚠️"
        children.append({
            "label": f"{error_icon} {node['_error']}",
            "value": f"{node_value}.error"
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

def generate_xml_from_xsd(xsd_file_path, xsd_file_name, selected_choices=None, unbounded_counts=None):
    """
    Generate XML from XSD schema with user-specified choices.
    
    Args:
        xsd_file_path: Path to the XSD file
        xsd_file_name: Original name of the XSD file
        selected_choices: Dictionary of selected choices for generation
        unbounded_counts: Dictionary of counts for unbounded elements
        
    Returns:
        Generated XML content
    """
    try:
        file_manager.setup_temp_directory_with_dependencies(xsd_file_path, xsd_file_name)
        generator = XMLGenerator(xsd_file_path)
        
        # Pass user selections to generator if available
        if selected_choices or unbounded_counts:
            return generator.generate_dummy_xml_with_choices(selected_choices, unbounded_counts)
        else:
            return generator.generate_dummy_xml()
    except Exception as e:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
  <message>Error generating XML: {str(e)}</message>
</error>"""

def main():
    st.markdown('<div class="main-header">XML Chunker</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    st.sidebar.markdown('<div class="sub-header">Settings</div>', unsafe_allow_html=True)
    
    uploaded_file = st.sidebar.file_uploader("Select a XSD file", type=["xsd"])
    
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")
        file_name = uploaded_file.name
        
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(uploaded_file.getvalue())
        
        # Set up dependencies for schema analysis
        file_manager.setup_temp_directory_with_dependencies(temp_file_path, file_name)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Selected XSD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="selected-file">{file_name}</div>', unsafe_allow_html=True)
            st.code(file_content, language="xml")
        
        with col2:
            st.markdown('<div class="sub-header">Schema Analysis & Controls:</div>', unsafe_allow_html=True)
            
            with st.spinner("Analyzing XSD schema..."):
                analysis = analyze_xsd_schema(temp_file_path)
                
                if analysis['success']:
                    schema_info = analysis['schema_info']
                    choices = analysis['choices']
                    unbounded_elements = analysis['unbounded_elements']
                    element_tree = analysis['element_tree']
                    
                    # Compact schema info
                    with st.expander("📊 Schema Info", expanded=False):
                        st.caption(f"**Namespace:** {schema_info.get('target_namespace', 'N/A')}")
                        st.caption(f"**Elements:** {schema_info.get('elements_count', 0)} | **Types:** {schema_info.get('types_count', 0)}")
                    
                    # Tree structure display with professional tree component
                    with st.expander("🌳 Schema Structure", expanded=True):
                        if element_tree:
                            st.markdown("*Interactive schema tree - expand/collapse nodes to explore structure*")
                            
                            # Convert our tree format to streamlit_tree_select format
                            tree_nodes = []
                            for root_name, tree in element_tree.items():
                                tree_node = convert_tree_to_streamlit_format(tree)
                                tree_nodes.append(tree_node)
                            
                            # Display the tree with streamlit_tree_select
                            if tree_nodes:
                                # Add legend and helpful information
                                st.info("""💡 **Symbol Legend & Tips:**

🔀 **Choice Elements** - Select one option from multiple choices

🔄 **Repeating Elements** - Can occur multiple times (1-∞, 2-5, etc.)

📝 **Single Elements** - Occurs exactly once [1:1]

📄 **Simple Types** - Basic data types (string, int, etc.)

⚬ **Choice Options** - Available options within a choice element

ℹ️ **Type Information** - Additional schema details

⚠️ **Warnings/Errors** - Schema processing messages

*If tree text appears dim, try switching to Streamlit's light theme in Settings > Theme*""")
                                
                                selected = tree_select(
                                    tree_nodes,
                                    key="schema_tree",
                                    check_model="leaf",  # Only leaf nodes can be checked
                                    expanded=[tree_nodes[0]['value']] if tree_nodes else [],  # Expand root by default
                                    no_cascade=True  # Don't cascade selections
                                )
                                
                                # Show selected information
                                if selected and selected.get('checked'):
                                    st.markdown("---")
                                    st.markdown("**Selected Elements:**")
                                    for item in selected['checked']:
                                        st.markdown(f"• `{item}`")
                        else:
                            st.info("No schema structure could be extracted from this XSD file.")
                    
                    # Choice selection
                    selected_choices = {}
                    if choices:
                        with st.expander("🔀 Choice Selection", expanded=True):
                            st.caption("Select which elements to generate for choice constraints:")
                            for i, choice in enumerate(choices):
                                choice_key = f"choice_{i}"
                                options = [f"{elem['name']} ({elem['min_occurs']}-{elem['max_occurs']})" 
                                          for elem in choice['elements']]
                                
                                selected_option = st.selectbox(
                                    f"Choice at {choice['path']}:",
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
                    
                    # Unbounded element counts
                    unbounded_counts = {}
                    if unbounded_elements:
                        with st.expander("⚙️ Unbounded Elements", expanded=True):
                            st.caption("Set count for elements with maxOccurs > 1 or unbounded:")
                            for elem in unbounded_elements:
                                max_display = elem['max_occurs'] if elem['max_occurs'] != 'unbounded' else '∞'
                                count = st.number_input(
                                    f"{elem['name']} (max: {max_display}):",
                                    min_value=1,
                                    max_value=config.elements.max_unbounded_count if elem['max_occurs'] == 'unbounded' else min(config.elements.max_unbounded_count, int(elem['max_occurs'])),
                                    value=config.elements.default_element_count,
                                    key=f"count_{elem['path']}",
                                    help=f"Number of {elem['name']} elements to generate"
                                )
                                unbounded_counts[elem['path']] = count
                    
                    # Store selections in session state for XML generation
                    st.session_state['selected_choices'] = selected_choices
                    st.session_state['unbounded_counts'] = unbounded_counts
                    
                else:
                    st.error(f"Error analyzing schema: {analysis['error']}")
                    st.session_state['selected_choices'] = {}
                    st.session_state['unbounded_counts'] = {}
        
        # XML Generation Section (below both columns) - Full width
        st.markdown("---")
        st.markdown('<div class="sub-header">XML Generation:</div>', unsafe_allow_html=True)
        
        # Show current selections summary in a centered column
        col_summary1, col_summary2, col_summary3 = st.columns([1, 2, 1])
        with col_summary2:
            if 'selected_choices' in st.session_state and st.session_state['selected_choices']:
                st.caption("**Selected Choices:**")
                for choice_key, choice_data in st.session_state['selected_choices'].items():
                    st.caption(f"• {choice_data['path']}: {choice_data['selected_element']}")
            
            if 'unbounded_counts' in st.session_state and st.session_state['unbounded_counts']:
                st.caption("**Unbounded Counts:**")
                for path, count in st.session_state['unbounded_counts'].items():
                    element_name = path.split('.')[-1]
                    st.caption(f"• {element_name}: {count}")
        
        # Action buttons in centered columns
        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([1, 1, 1, 1, 1])
        
        with col_btn3:
            generate_clicked = st.button("🚀 Generate XML", key="generate_xml_btn", help="Generate XML based on your selections")
        
        # Handle XML generation
        if generate_clicked:
            with st.spinner("Generating XML with your selections..."):
                # Get user selections from session state
                selected_choices = st.session_state.get('selected_choices', {})
                unbounded_counts = st.session_state.get('unbounded_counts', {})
                
                xml_content = generate_xml_from_xsd(
                    temp_file_path, 
                    file_name, 
                    selected_choices, 
                    unbounded_counts
                )
                
                # Store XML content and file info in session state for validation
                st.session_state['generated_xml'] = xml_content
                st.session_state['temp_file_path'] = temp_file_path
                st.session_state['uploaded_file_name'] = file_name
                st.session_state['uploaded_file_content'] = file_content
        
        # Display generated XML and validation controls if XML exists
        if 'generated_xml' in st.session_state and st.session_state['generated_xml']:
            st.markdown('<div class="sub-header">Generated XML:</div>', unsafe_allow_html=True)
            
            # Display XML in a larger area (full width)
            st.code(st.session_state['generated_xml'], language="xml", height=600)
            
            # Action buttons row - Download and Validate
            col_action1, col_action2, col_action3, col_action4, col_action5 = st.columns([1, 1, 1, 1, 1])
            
            with col_action2:
                st.download_button(
                    label="💾 Download XML",
                    data=st.session_state['generated_xml'],
                    file_name=f"{file_name.replace('.xsd', '')}_generated.xml",
                    mime="application/xml"
                )
            
            with col_action4:
                validate_clicked = st.button("✅ Validate XML", key="validate_xml_btn", help="Validate generated XML against XSD schema")
            
            # Handle validation
            if validate_clicked:
                with st.spinner("Validating XML against schema..."):
                    validation_result = validate_xml_against_schema(
                        st.session_state['generated_xml'], 
                        st.session_state['temp_file_path'],
                        st.session_state.get('uploaded_file_name'),
                        st.session_state.get('uploaded_file_content')
                    )
                    
                    if validation_result['success']:
                        error_breakdown = validation_result['error_breakdown']
                        total_errors = validation_result['total_errors']
                        
                        # Display validation results
                        st.markdown("### 📊 Validation Results")
                        
                        if validation_result['is_valid']:
                            st.success("🎉 **XML is valid!** No validation errors found.")
                        else:
                            if total_errors == 0:
                                st.success("🎉 **XML is valid!** No validation errors found.")
                            else:
                                st.warning(f"⚠️ **XML has validation issues** ({total_errors} total errors)")
                        
                        # Show error breakdown
                        if total_errors > 0:
                            col_val1, col_val2, col_val3, col_val4 = st.columns(4)
                            
                            with col_val1:
                                st.metric("Enumeration Errors", error_breakdown['enumeration_errors'], help="Values not in allowed enumeration lists")
                            
                            with col_val2:
                                st.metric("Boolean Errors", error_breakdown['boolean_errors'], help="Invalid boolean values")
                            
                            with col_val3:
                                st.metric("Pattern Errors", error_breakdown['pattern_errors'], help="Values not matching required patterns")
                            
                            with col_val4:
                                st.metric("Structural Errors", error_breakdown['structural_errors'], help="Missing required elements or invalid structure")
                            
                            # Show categorized errors
                            if validation_result.get('categorized_errors'):
                                st.markdown("#### 📋 Detailed Error Analysis")
                                
                                categorized_errors = validation_result['categorized_errors']
                                
                                # Create tabs for each error type
                                tab_names = []
                                tab_contents = []
                                
                                if categorized_errors['enumeration_errors']:
                                    tab_names.append(f"🔤 Enumeration ({len(categorized_errors['enumeration_errors'])})")
                                    tab_contents.append(('enumeration_errors', categorized_errors['enumeration_errors']))
                                
                                if categorized_errors['boolean_errors']:
                                    tab_names.append(f"✅ Boolean ({len(categorized_errors['boolean_errors'])})")
                                    tab_contents.append(('boolean_errors', categorized_errors['boolean_errors']))
                                
                                if categorized_errors['pattern_errors']:
                                    tab_names.append(f"🎯 Pattern ({len(categorized_errors['pattern_errors'])})")
                                    tab_contents.append(('pattern_errors', categorized_errors['pattern_errors']))
                                
                                if categorized_errors['structural_errors']:
                                    tab_names.append(f"🏗️ Structural ({len(categorized_errors['structural_errors'])})")
                                    tab_contents.append(('structural_errors', categorized_errors['structural_errors']))
                                
                                if tab_names:
                                    tabs = st.tabs(tab_names)
                                    
                                    for i, (tab, (error_type, errors)) in enumerate(zip(tabs, tab_contents)):
                                        with tab:
                                            if error_type == 'enumeration_errors':
                                                st.markdown("**Enumeration Violations:**")
                                                st.caption("Values that don't match allowed enumeration lists. Expected for dummy data.")
                                            elif error_type == 'boolean_errors':
                                                st.markdown("**Boolean Type Errors:**")
                                                st.caption("Invalid boolean values. These indicate type generation issues.")
                                            elif error_type == 'pattern_errors':
                                                st.markdown("**Pattern Violations:**")
                                                st.caption("Values that don't match required regex patterns. Expected for dummy data.")
                                            elif error_type == 'structural_errors':
                                                st.markdown("**Structural Issues:**")
                                                st.caption("Missing required elements or invalid XML structure. These should be minimal.")
                                            
                                            # Display errors in a nice format
                                            for j, error in enumerate(errors, 1):
                                                formatted_error = format_validation_error(error)
                                                
                                                with st.expander(f"Error {j}: {formatted_error['element_name']}", expanded=False):
                                                    st.text(f"📍 Path: {formatted_error['path']}")
                                                    st.text(f"💬 Message: {formatted_error['message']}")
                                                    if formatted_error['line']:
                                                        st.text(f"📍 Line: {formatted_error['line']}")
                                                
                                                # Show only first 10 errors per category to avoid overwhelming UI
                                                if j >= 10 and len(errors) > 10:
                                                    st.info(f"... and {len(errors) - 10} more {error_type.replace('_', ' ')} errors")
                                                    break
                        
                        # Provide helpful tips
                        if total_errors > 0:
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
        
        # Cleanup temp directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            st.warning(f"Could not clean up temporary files: {e}")
            
    else:
        st.info("Please select an XSD file to continue.")

if __name__ == "__main__":
    main()
