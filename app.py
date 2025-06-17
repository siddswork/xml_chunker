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
import json
import os
import tempfile
from utils.xml_generator import XMLGenerator
from utils.xsd_parser import XSDParser
from streamlit_tree_select import tree_select
from config import get_config
from services.file_manager import FileManager
from services.xml_validator import XMLValidator
from services.schema_analyzer import SchemaAnalyzer
from services.xslt_processor import XSLTProcessor
from utils.config_manager import ConfigManager

# Initialize configuration and services
config = get_config()
file_manager = FileManager(config)
xml_validator = XMLValidator(config)
schema_analyzer = SchemaAnalyzer(config)
xslt_processor = XSLTProcessor(config)
config_manager = ConfigManager(config)

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

def generate_xml_from_xsd(xsd_file_path, xsd_file_name, selected_choices=None, unbounded_counts=None, generation_mode="Minimalistic", optional_selections=None, custom_values=None):
    """
    Generate XML from XSD schema with user-specified choices and generation mode.
    
    Args:
        xsd_file_path: Path to the XSD file
        xsd_file_name: Original name of the XSD file
        selected_choices: Dictionary of selected choices for generation
        unbounded_counts: Dictionary of counts for unbounded elements
        generation_mode: Generation strategy ("Minimalistic", "Complete", "Custom")
        optional_selections: List of optional element paths to include (for Custom mode)
        custom_values: Dictionary of custom values for specific elements
        
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
            optional_selections=optional_selections,
            custom_values=custom_values
        )
    except Exception as e:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
  <message>Error generating XML: {str(e)}</message>
</error>"""

def render_file_upload_section():
    """Render the file upload section and return uploaded file."""
    st.markdown("---")
    st.markdown("### 📁 Upload XSD Schema")
    
    uploaded_file = st.file_uploader(
        "Select a XSD file to begin", 
        type=["xsd"], 
        help="Upload an XSD schema file to analyze and generate XML"
    )
    
    return uploaded_file

def render_schema_tree(element_tree, file_content, key="schema_tree_analysis"):
    """Render the schema tree component with legend and selection handling."""
    if not element_tree:
        st.info("No schema structure could be extracted from this XSD file.")
        return None
    
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
        
        # Display tree for exploration
        selected = tree_select(
            tree_nodes,
            key=key,
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
        
        return selected
    
    return None

def render_tab1_schema_analysis(temp_file_path, file_content):
    """Render Tab 1: Schema Analysis content."""
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
            render_schema_tree(element_tree, file_content)
            
        else:
            st.error(f"Error analyzing schema: {analysis['error']}")
            st.session_state['schema_analysis'] = None

def render_choice_selection(choices):
    """Render choice selection UI and return selected choices."""
    selected_choices = {}
    if not choices:
        return selected_choices
    
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
    
    return selected_choices

def render_unbounded_elements(unbounded_elements):
    """Render unbounded elements configuration and return counts."""
    unbounded_counts = {}
    if not unbounded_elements:
        return unbounded_counts
    
    st.markdown("#### 🔄 Repeating Elements")
    st.markdown("Set count for elements with maxOccurs > 1 or unbounded:")
    
    for elem in unbounded_elements:
        max_display = elem['max_occurs'] if elem['max_occurs'] != 'unbounded' else '∞'
        
        # Create a more readable path display similar to choice elements
        if 'path' in elem and elem['path'] and '.' in elem['path']:
            path_display = elem['path'].replace('.', ' → ')
            element_label = f"**{elem['name']}** at `{path_display}` (max: {max_display}):"
        else:
            element_label = f"**{elem['name']}** (max: {max_display}):"
        
        count = st.number_input(
            element_label,
            min_value=1,
            max_value=config.elements.max_unbounded_count if elem['max_occurs'] == 'unbounded' else min(config.elements.max_unbounded_count, int(elem['max_occurs'])),
            value=config.elements.default_element_count,
            key=f"count_{elem['path']}",
            help=f"Number of {elem['name']} elements to generate at path: {elem.get('path', 'root')}"
        )
        unbounded_counts[elem['path']] = count
    
    return unbounded_counts

def render_config_file_section():
    """Render configuration file upload/export section."""
    st.markdown("#### 📁 Configuration File")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.markdown("**Import Configuration**")
        uploaded_config = st.file_uploader(
            "Upload configuration file",
            type=["json"],
            key="config_upload",
            help="Upload a JSON configuration file to auto-populate settings"
        )
        
        if uploaded_config:
            try:
                config_content = uploaded_config.getvalue().decode("utf-8")
                config_data = config_manager.load_config(io.StringIO(config_content))
                
                # Convert to generator options and store in session state
                generator_options = config_manager.convert_config_to_generator_options(config_data)
                
                st.session_state['selected_choices'] = generator_options.get('selected_choices', {})
                st.session_state['unbounded_counts'] = generator_options.get('unbounded_counts', {})
                st.session_state['current_generation_mode'] = generator_options.get('generation_mode', 'Minimalistic')
                st.session_state['optional_element_selections'] = generator_options.get('optional_selections', [])
                st.session_state['custom_values'] = generator_options.get('custom_values', {})
                
                st.success(f"✅ Configuration loaded: {config_data['metadata']['name']}")
                
                # Show warnings if any
                schema_name = st.session_state.get('uploaded_file_name', '')
                warnings = config_manager.validate_config_compatibility(config_data, schema_name)
                if warnings:
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")
                
                # Refresh the page to show loaded settings
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error loading configuration: {str(e)}")
    
    with col_config2:
        st.markdown("**Export Current Settings**")
        
        if st.button("📤 **Export Configuration**", key="export_config_btn", use_container_width=True):
            try:
                # Get current settings from session state
                selected_choices = st.session_state.get('selected_choices', {})
                unbounded_counts = st.session_state.get('unbounded_counts', {})
                generation_mode = st.session_state.get('current_generation_mode', 'Minimalistic')
                optional_selections = st.session_state.get('optional_element_selections', [])
                schema_name = st.session_state.get('uploaded_file_name', 'unknown.xsd')
                
                # Create configuration
                config_data = config_manager.create_config_from_ui_state(
                    schema_name=schema_name,
                    generation_mode=generation_mode,
                    selected_choices=selected_choices,
                    unbounded_counts=unbounded_counts,
                    optional_selections=optional_selections,
                    config_name=f"Configuration for {schema_name}",
                    config_description=f"Auto-generated configuration for {schema_name} with {generation_mode} mode"
                )
                
                # Offer download
                config_json = json.dumps(config_data, indent=2, ensure_ascii=False)
                config_filename = f"{schema_name.replace('.xsd', '')}_config.json"
                
                st.download_button(
                    label="💾 **Download Configuration**",
                    data=config_json,
                    file_name=config_filename,
                    mime="application/json",
                    use_container_width=True
                )
                
                st.success("✅ Configuration ready for download!")
                
            except Exception as e:
                st.error(f"❌ Error creating configuration: {str(e)}")

def render_tab2_configure_generation():
    """Render Tab 2: Configure Generation content."""
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
    
    # Configuration file section
    render_config_file_section()
    
    st.markdown("---")
    
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
            
            # Use the schema tree renderer with a different key for custom selection
            selected = render_schema_tree(element_tree, "", key="custom_element_selection")
            
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
    selected_choices = render_choice_selection(choices)
    
    # Add separator if choices exist
    if choices:
        st.markdown("---")
    
    # Unbounded element counts
    unbounded_counts = render_unbounded_elements(unbounded_elements)
    
    # Add separator if unbounded elements exist
    if unbounded_elements:
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

def render_configuration_summary():
    """Render the detailed 4-column configuration summary."""
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

def render_validation_results(validation_result):
    """Render detailed validation results with error breakdown."""
    st.markdown("#### 🔍 Validation Results")
    
    if not validation_result['success']:
        st.error(f"❌ **Validation failed:** {validation_result['error']}")
        return
    
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

def render_tab3_generate_validate():
    """Render Tab 3: Generate & Validate content."""
    st.markdown("### 🚀 XML Generation & Validation")
    
    # Check if configuration is complete
    if 'schema_analysis' not in st.session_state or not st.session_state['schema_analysis']:
        st.warning("⚠️ Please analyze the schema in the **Analyze Schema** tab first.")
        st.stop()
    
    if 'current_generation_mode' not in st.session_state:
        st.warning("⚠️ Please configure generation settings in the **Configure Generation** tab first.")
        st.stop()
    
    # Show current configuration summary
    render_configuration_summary()
    
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
            
            custom_values = st.session_state.get('custom_values', {})
            
            xml_content = generate_xml_from_xsd(
                temp_file_path, 
                file_name, 
                selected_choices, 
                unbounded_counts,
                generation_mode,
                optional_selections,
                custom_values
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
                
                render_validation_results(validation_result)
    else:
        st.info("👆 Click **Generate XML** above to create your XML file.")

def cleanup_temp_directory():
    """Clean up temporary directories."""
    if st.session_state.get('temp_dir'):
        try:
            import shutil
            shutil.rmtree(st.session_state['temp_dir'], ignore_errors=True)
        except Exception as e:
            pass  # Silent cleanup

def setup_file_processing(uploaded_file):
    """Process uploaded file and setup session state."""
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
    
    return file_content, file_name, temp_file_path

def render_xsd_to_xml_workflow():
    """Render the XSD to XML Generation workflow."""
    st.markdown('<div class="main-header">XSD to XML Generation</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    uploaded_file = render_file_upload_section()
    
    if uploaded_file is not None:
        file_content, file_name, temp_file_path = setup_file_processing(uploaded_file)
        
        # Show file info briefly
        st.success(f"✅ **{file_name}** uploaded successfully")
        
        # Create tabs for the workflow
        tab1, tab2, tab3 = st.tabs(["🔍 **Analyze Schema**", "⚙️ **Configure Generation**", "🚀 **Generate & Validate**"])
        
        # TAB 1: ANALYZE SCHEMA
        with tab1:
            render_tab1_schema_analysis(temp_file_path, file_content)
        
        # TAB 2: CONFIGURE GENERATION
        with tab2:
            render_tab2_configure_generation()
        
        # TAB 3: GENERATE & VALIDATE
        with tab3:
            render_tab3_generate_validate()
        
        # Cleanup temp directory when done
        cleanup_temp_directory()
    
    else:
        st.info("📁 Please upload an XSD file to begin analyzing and generating XML.")

def render_xml_transformation_workflow():
    """Render the XML Transformation workflow."""
    st.markdown('<div class="main-header">XML Transformation</div>', unsafe_allow_html=True)
    st.markdown('Transform XML using XSLT stylesheets and compare outputs')
    
    # Create tabs for transformation workflow
    tab1, tab2, tab3 = st.tabs(["📄 **Upload Files**", "🔄 **Transform**", "⚖️ **Compare & Test**"])
    
    # TAB 1: UPLOAD FILES
    with tab1:
        render_transformation_upload_tab()
    
    # TAB 2: TRANSFORM
    with tab2:
        render_transformation_tab()
    
    # TAB 3: COMPARE & TEST
    with tab3:
        render_comparison_tab()

def render_transformation_upload_tab():
    """Render the file upload tab for transformation workflow."""
    st.markdown("### 📄 Upload XML and XSLT Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### XML Input")
        
        # Option to use generated XML or upload new XML
        xml_source = st.radio(
            "XML Source:",
            ["Upload XML File", "Paste XML Content", "Use Generated XML"],
            key="xml_source_option"
        )
        
        if xml_source == "Upload XML File":
            uploaded_xml = st.file_uploader(
                "Choose XML file",
                type=['xml'],
                key="xml_upload"
            )
            
            if uploaded_xml:
                xml_content = uploaded_xml.getvalue().decode("utf-8")
                st.session_state['transformation_xml'] = xml_content
                st.session_state['xml_filename'] = uploaded_xml.name
                st.success(f"✅ **{uploaded_xml.name}** loaded successfully")
                
                # Preview XML
                with st.expander("Preview XML Content"):
                    st.code(xml_content[:1000] + "..." if len(xml_content) > 1000 else xml_content, language="xml")
        
        elif xml_source == "Paste XML Content":
            xml_content = st.text_area(
                "Paste XML content:",
                height=300,
                key="xml_paste",
                placeholder="<root>...</root>"
            )
            
            if xml_content.strip():
                st.session_state['transformation_xml'] = xml_content
                st.session_state['xml_filename'] = "pasted_content.xml"
                st.success("✅ XML content loaded")
        
        elif xml_source == "Use Generated XML":
            if 'generated_xml' in st.session_state and st.session_state['generated_xml']:
                st.session_state['transformation_xml'] = st.session_state['generated_xml']
                st.session_state['xml_filename'] = f"{st.session_state.get('uploaded_file_name', 'schema').replace('.xsd', '')}_generated.xml"
                st.success("✅ Using previously generated XML")
                
                # Preview generated XML
                with st.expander("Preview Generated XML Content"):
                    st.code(st.session_state['generated_xml'][:1000] + "..." if len(st.session_state['generated_xml']) > 1000 else st.session_state['generated_xml'], language="xml")
            else:
                st.info("💡 No generated XML available. Please generate XML in the **XSD to XML Generation** section first.")
    
    with col2:
        st.markdown("#### XSLT Stylesheet")
        
        xslt_source = st.radio(
            "XSLT Source:",
            ["Upload XSLT File", "Paste XSLT Content"],
            key="xslt_source_option"
        )
        
        if xslt_source == "Upload XSLT File":
            uploaded_xslt = st.file_uploader(
                "Choose XSLT file",
                type=['xsl', 'xslt'],
                key="xslt_upload"
            )
            
            if uploaded_xslt:
                xslt_content = uploaded_xslt.getvalue().decode("utf-8")
                st.session_state['transformation_xslt'] = xslt_content
                st.session_state['xslt_filename'] = uploaded_xslt.name
                st.success(f"✅ **{uploaded_xslt.name}** loaded successfully")
                
                # Preview XSLT
                with st.expander("Preview XSLT Content"):
                    st.code(xslt_content[:1000] + "..." if len(xslt_content) > 1000 else xslt_content, language="xml")
        
        elif xslt_source == "Paste XSLT Content":
            xslt_content = st.text_area(
                "Paste XSLT content:",
                height=300,
                key="xslt_paste",
                placeholder='<?xml version="1.0"?>\n<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n...\n</xsl:stylesheet>'
            )
            
            if xslt_content.strip():
                st.session_state['transformation_xslt'] = xslt_content
                st.session_state['xslt_filename'] = "pasted_stylesheet.xsl"
                st.success("✅ XSLT content loaded")
    
    # Show current status
    if st.session_state.get('transformation_xml') and st.session_state.get('transformation_xslt'):
        st.markdown("---")
        st.success("🎉 Both XML and XSLT files are ready for transformation!")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"📄 XML: {st.session_state.get('xml_filename', 'Unknown')}")
        with col_info2:
            st.info(f"🔄 XSLT: {st.session_state.get('xslt_filename', 'Unknown')}")

def render_transformation_tab():
    """Render the transformation tab."""
    st.markdown("### 🔄 XML Transformation")
    
    # Check if files are loaded
    if not st.session_state.get('transformation_xml') or not st.session_state.get('transformation_xslt'):
        st.warning("⚠️ Please upload both XML and XSLT files in the **Upload Files** tab first.")
        return
    
    # Show loaded files info
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"📄 XML: {st.session_state.get('xml_filename', 'Unknown')}")
    with col_info2:
        st.info(f"🔄 XSLT: {st.session_state.get('xslt_filename', 'Unknown')}")
    
    st.markdown("---")
    
    # XSLT Parameters (optional)
    st.markdown("#### XSLT Parameters (Optional)")
    
    with st.expander("Add XSLT Parameters"):
        st.markdown("Define parameters to pass to the XSLT transformation:")
        
        if 'xslt_parameters' not in st.session_state:
            st.session_state['xslt_parameters'] = {}
        
        # Add parameter interface
        col_param1, col_param2, col_param3 = st.columns([2, 2, 1])
        
        with col_param1:
            param_name = st.text_input("Parameter Name", key="new_param_name")
        with col_param2:
            param_value = st.text_input("Parameter Value", key="new_param_value")
        with col_param3:
            if st.button("Add", key="add_param_btn"):
                if param_name and param_value:
                    st.session_state['xslt_parameters'][param_name] = param_value
                    st.success(f"Added parameter: {param_name}")
                    st.rerun()
        
        # Show existing parameters
        if st.session_state['xslt_parameters']:
            st.markdown("**Current Parameters:**")
            for name, value in st.session_state['xslt_parameters'].items():
                col_del1, col_del2, col_del3 = st.columns([2, 2, 1])
                with col_del1:
                    st.text(name)
                with col_del2:
                    st.text(value)
                with col_del3:
                    if st.button("🗑️", key=f"del_{name}", help="Delete parameter"):
                        del st.session_state['xslt_parameters'][name]
                        st.rerun()
    
    st.markdown("---")
    
    # Transform button
    col_transform1, col_transform2, col_transform3 = st.columns([1, 1, 1])
    
    with col_transform2:
        transform_clicked = st.button(
            "🚀 **Transform XML**",
            type="primary",
            use_container_width=True,
            key="transform_btn"
        )
    
    # Handle transformation
    if transform_clicked:
        with st.spinner("🔄 Transforming XML..."):
            xml_content = st.session_state['transformation_xml']
            xslt_content = st.session_state['transformation_xslt']
            parameters = st.session_state.get('xslt_parameters', {}) if st.session_state.get('xslt_parameters') else None
            
            result = xslt_processor.transform_xml(xml_content, xslt_content, parameters)
            st.session_state['transformation_result'] = result
    
    # Display transformation result
    if 'transformation_result' in st.session_state:
        result = st.session_state['transformation_result']
        
        st.markdown("---")
        st.markdown("#### 📊 Transformation Result")
        
        if result['success']:
            st.success("✅ Transformation completed successfully!")
            
            # Display transformed XML
            st.markdown("**Transformed XML:**")
            st.code(result['output_xml'], language="xml", height=400)
            
            # Download button
            col_download1, col_download2, col_download3 = st.columns([1, 1, 1])
            with col_download2:
                st.download_button(
                    label="💾 **Download Transformed XML**",
                    data=result['output_xml'],
                    file_name=f"transformed_{st.session_state.get('xml_filename', 'output.xml')}",
                    mime="application/xml",
                    use_container_width=True
                )
        else:
            st.error("❌ Transformation failed!")
            st.error(f"**Error:** {result['error']}")
            
            if result.get('error_type') == 'xslt_parse':
                st.info("💡 Check your XSLT syntax. Common issues include missing namespaces or malformed XPath expressions.")
            elif result.get('error_type') == 'xml_parse':
                st.info("💡 Check your XML syntax. The input XML may be malformed.")

def render_comparison_tab():
    """Render the comparison and testing tab."""
    st.markdown("### ⚖️ XSLT Comparison & Testing")
    
    st.markdown("""
    Compare two XSLT stylesheets to test equivalence or analyze differences.
    This is useful for validating LLM-generated XSLT against reference implementations.
    """)
    
    # Two-column layout for XSLT comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 Reference XSLT (MapForce/Original)")
        
        ref_source = st.radio(
            "Reference XSLT Source:",
            ["Upload File", "Paste Content"],
            key="ref_xslt_source"
        )
        
        if ref_source == "Upload File":
            ref_xslt_file = st.file_uploader(
                "Upload Reference XSLT",
                type=['xsl', 'xslt'],
                key="ref_xslt_upload"
            )
            
            if ref_xslt_file:
                ref_xslt_content = ref_xslt_file.getvalue().decode("utf-8")
                st.session_state['ref_xslt'] = ref_xslt_content
                st.success(f"✅ Reference XSLT loaded: {ref_xslt_file.name}")
        
        else:  # Paste Content
            ref_xslt_content = st.text_area(
                "Paste Reference XSLT:",
                height=200,
                key="ref_xslt_paste"
            )
            
            if ref_xslt_content.strip():
                st.session_state['ref_xslt'] = ref_xslt_content
                st.success("✅ Reference XSLT loaded")
    
    with col2:
        st.markdown("#### 🤖 Test XSLT (LLM-Generated)")
        
        test_source = st.radio(
            "Test XSLT Source:",
            ["Upload File", "Paste Content", "Use Current XSLT"],
            key="test_xslt_source"
        )
        
        if test_source == "Upload File":
            test_xslt_file = st.file_uploader(
                "Upload Test XSLT",
                type=['xsl', 'xslt'],
                key="test_xslt_upload"
            )
            
            if test_xslt_file:
                test_xslt_content = test_xslt_file.getvalue().decode("utf-8")
                st.session_state['test_xslt'] = test_xslt_content
                st.success(f"✅ Test XSLT loaded: {test_xslt_file.name}")
        
        elif test_source == "Paste Content":
            test_xslt_content = st.text_area(
                "Paste Test XSLT:",
                height=200,
                key="test_xslt_paste"
            )
            
            if test_xslt_content.strip():
                st.session_state['test_xslt'] = test_xslt_content
                st.success("✅ Test XSLT loaded")
        
        else:  # Use Current XSLT
            if st.session_state.get('transformation_xslt'):
                st.session_state['test_xslt'] = st.session_state['transformation_xslt']
                st.success("✅ Using current transformation XSLT")
            else:
                st.info("💡 No current XSLT available. Please load XSLT in the Transform tab first.")
    
    # Test XML inputs section
    st.markdown("---")
    st.markdown("#### 📄 Test XML Inputs")
    
    test_xml_option = st.radio(
        "Test XML Source:",
        ["Use Current XML", "Upload Multiple Files", "Generate Test Cases"],
        key="test_xml_option"
    )
    
    test_xmls = []
    
    if test_xml_option == "Use Current XML":
        if st.session_state.get('transformation_xml'):
            test_xmls = [st.session_state['transformation_xml']]
            st.success("✅ Using current XML for testing")
        else:
            st.info("💡 No current XML available. Please load XML first.")
    
    elif test_xml_option == "Upload Multiple Files":
        uploaded_test_files = st.file_uploader(
            "Upload multiple XML test files",
            type=['xml'],
            accept_multiple_files=True,
            key="test_xml_uploads"
        )
        
        if uploaded_test_files:
            test_xmls = []
            for file in uploaded_test_files:
                content = file.getvalue().decode("utf-8")
                test_xmls.append(content)
            st.success(f"✅ Loaded {len(test_xmls)} test XML files")
    
    elif test_xml_option == "Generate Test Cases":
        st.info("💡 This feature would integrate with your XSD generator to create multiple XML variants for comprehensive testing.")
    
    # Run comparison
    if st.session_state.get('ref_xslt') and st.session_state.get('test_xslt') and test_xmls:
        st.markdown("---")
        
        col_test1, col_test2, col_test3 = st.columns([1, 1, 1])
        with col_test2:
            run_comparison = st.button(
                "🔍 **Run Equivalence Test**",
                type="primary",
                use_container_width=True,
                key="run_comparison_btn"
            )
        
        if run_comparison:
            with st.spinner("🔄 Testing XSLT equivalence..."):
                ref_xslt = st.session_state['ref_xslt']
                test_xslt = st.session_state['test_xslt']
                parameters = st.session_state.get('xslt_parameters', {}) if st.session_state.get('xslt_parameters') else None
                
                equivalence_result = xslt_processor.test_xslt_equivalence(
                    test_xmls, ref_xslt, test_xslt, parameters
                )
                
                st.session_state['equivalence_result'] = equivalence_result
    
    # Display equivalence results
    if 'equivalence_result' in st.session_state:
        result = st.session_state['equivalence_result']
        
        st.markdown("---")
        st.markdown("#### 📊 Equivalence Test Results")
        
        # Summary metrics
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        
        with col_metric1:
            st.metric("Total Tests", result['total_test_cases'])
        with col_metric2:
            st.metric("Equivalent", result['equivalent_outputs'])
        with col_metric3:
            st.metric("Failed", result['failed_transformations'])
        with col_metric4:
            st.metric("Success Rate", f"{result['success_rate']:.1f}%")
        
        # Overall result
        if result['overall_equivalent']:
            st.success("🎉 **XSLTs are functionally equivalent!**")
        else:
            st.warning("⚠️ **XSLTs produce different outputs**")
        
        st.info(result['summary'])
        
        # Detailed results
        with st.expander("View Detailed Test Results"):
            for i, test_result in enumerate(result['detailed_results']):
                st.markdown(f"**Test Case {i+1}:**")
                
                if test_result['success']:
                    if test_result['equivalent']:
                        st.success("✅ Outputs are equivalent")
                    else:
                        st.error("❌ Outputs differ")
                        
                        # Show side-by-side comparison
                        col_ref, col_test = st.columns(2)
                        with col_ref:
                            st.markdown("**Reference Output:**")
                            st.code(test_result['xslt1_result']['output_xml'][:500] + "..." if len(test_result['xslt1_result']['output_xml']) > 500 else test_result['xslt1_result']['output_xml'], language="xml")
                        with col_test:
                            st.markdown("**Test Output:**")
                            st.code(test_result['xslt2_result']['output_xml'][:500] + "..." if len(test_result['xslt2_result']['output_xml']) > 500 else test_result['xslt2_result']['output_xml'], language="xml")
                else:
                    st.error(f"❌ Test failed: {test_result.get('error', 'Unknown error')}")
                
                st.markdown("---")

def main():
    # Initialize navigation state
    if 'current_section' not in st.session_state:
        st.session_state['current_section'] = 'XSD to XML Generation'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        current_section = st.radio(
            "Choose Workflow:",
            ["🔧 XSD to XML Generation", "🔄 XML Transformation"],
            key="navigation_radio",
            index=0 if st.session_state['current_section'] == 'XSD to XML Generation' else 1
        )
        
        # Update session state
        if current_section == "🔧 XSD to XML Generation":
            st.session_state['current_section'] = 'XSD to XML Generation'
        else:
            st.session_state['current_section'] = 'XML Transformation'
        
        st.markdown("---")
        
        # Show workflow-specific help
        if st.session_state['current_section'] == 'XSD to XML Generation':
            st.markdown("""
            ### 🔧 XSD to XML Generation
            
            **Workflow:**
            1. 🔍 **Analyze Schema** - Upload and explore XSD structure
            2. ⚙️ **Configure Generation** - Set choices and options  
            3. 🚀 **Generate & Validate** - Create XML and validate
            
            Perfect for creating test data from schema definitions.
            """)
        else:
            st.markdown("""
            ### 🔄 XML Transformation
            
            **Workflow:**
            1. 📄 **Upload Files** - Load XML and XSLT files
            2. 🔄 **Transform** - Apply XSLT transformation
            3. ⚖️ **Compare & Test** - Test XSLT equivalence
            
            Perfect for testing and comparing XSLT stylesheets.
            """)
    
    # Main content area
    if st.session_state['current_section'] == 'XSD to XML Generation':
        render_xsd_to_xml_workflow()
    else:
        render_xml_transformation_workflow()

if __name__ == "__main__":
    main()
