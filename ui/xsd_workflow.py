"""
XSD to XML Generation Workflow UI

This module contains the Streamlit UI components for the XSD to XML generation workflow,
including schema analysis, configuration, and XML generation with validation.
"""

import streamlit as st
import io
import json
import os
import tempfile
import re
from streamlit_tree_select import tree_select
from typing import Dict, Any, List, Optional

from ui.common_components import (
    render_file_upload_section,
    setup_file_processing,
    cleanup_temp_directory,
    render_metrics_row,
    render_expandable_content,
    show_success_message,
    show_error_message,
    show_warning_message
)


def render_xsd_to_xml_workflow(config, file_manager, xml_validator, schema_analyzer, config_manager):
    """Render the XSD to XML Generation workflow."""
    st.markdown('<div class="main-header">XSD to XML Generation</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    uploaded_file = render_file_upload_section(
        file_types=["xsd"],
        title="Upload XSD Schema",
        help_text="Upload an XSD schema file to analyze and generate XML"
    )
    
    if uploaded_file is not None:
        file_content, file_name, temp_file_path = setup_file_processing(uploaded_file)
        
        # Setup dependencies for schema analysis
        file_manager.setup_temp_directory_with_dependencies(temp_file_path, file_name)
        
        # Show file info briefly
        st.success(f"✅ **{file_name}** uploaded successfully")
        
        # Create tabs for the workflow
        tab1, tab2, tab3 = st.tabs(["🔍 **Analyze Schema**", "⚙️ **Configure Generation**", "🚀 **Generate & Validate**"])
        
        # TAB 1: ANALYZE SCHEMA
        with tab1:
            render_tab1_schema_analysis(temp_file_path, file_content, schema_analyzer)
        
        # TAB 2: CONFIGURE GENERATION
        with tab2:
            render_tab2_configure_generation(config, config_manager)
        
        # TAB 3: GENERATE & VALIDATE
        with tab3:
            render_tab3_generate_validate(config, file_manager, xml_validator)
        
        # Cleanup temp directory when done
        cleanup_temp_directory()
    
    else:
        st.info("📁 Please upload an XSD file to begin analyzing and generating XML.")


def analyze_xsd_schema(xsd_file_path, schema_analyzer):
    """Analyze XSD schema to extract choice elements and structure."""
    return schema_analyzer.analyze_xsd_schema(xsd_file_path)


def convert_tree_to_streamlit_format(node, parent_path="", node_counter=None):
    """Convert our tree node format to streamlit_tree_select format."""
    # Initialize counter if not provided
    if node_counter is None:
        node_counter = {'count': 0}
    
    # Create unique value for this node with counter to prevent duplicates
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
        min_val = node['occurs']['min']
        max_val = node['occurs']['max']
        type_info = f"[{min_val}:{max_val}]"
    
    # Show type info for simple types
    if '_type_info' in node:
        icon = "📄"
        type_info = "[Simple]"
    
    # Create label with icon and type info
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


def clean_selection_display_name(selection):
    """Clean up tree selection names for display in the summary."""
    if not selection:
        return selection
    
    # Remove the trailing unique number (e.g., "_77", "_123")
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


def render_tab1_schema_analysis(temp_file_path, file_content, schema_analyzer):
    """Render Tab 1: Schema Analysis content."""
    st.markdown("### 📊 Schema Analysis")
    
    with st.spinner("Analyzing XSD schema..."):
        analysis = analyze_xsd_schema(temp_file_path, schema_analyzer)
        
        if analysis['success']:
            schema_info = analysis['schema_info']
            choices = analysis['choices']
            unbounded_elements = analysis['unbounded_elements']
            element_tree = analysis['element_tree']
            
            # Store analysis results in session state for other tabs
            st.session_state['schema_analysis'] = analysis
            
            # Display schema information in a clean layout
            metrics = {
                "Elements": schema_info.get('elements_count', 0),
                "Types": schema_info.get('types_count', 0),
                "Choices Found": len(choices) if choices else 0
            }
            render_metrics_row(metrics, 3)
            
            # Namespace info
            if schema_info.get('target_namespace'):
                st.info(f"**Target Namespace:** `{schema_info.get('target_namespace')}`")
            
            # XSD Content in an expandable section
            render_expandable_content(
                "📄 View XSD Content",
                file_content,
                language="xml",
                max_height=400,
                expanded=False
            )
            
            st.markdown("---")
            
            # Schema Structure - Full width display
            st.markdown("### 🌳 Schema Structure")
            render_schema_tree(element_tree, file_content)
            
        else:
            show_error_message(f"Error analyzing schema: {analysis['error']}")
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
    show_success_message(f"✅ Configured {len(choices)} choices: {len(root_choices)} root-level, {len(nested_choices)} nested")
    
    return selected_choices


def render_unbounded_elements(unbounded_elements, config):
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


def render_config_file_section(config_manager):
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
                # Show loading indicator
                with st.spinner("📋 Loading configuration..."):
                    config_content = uploaded_config.getvalue().decode("utf-8")
                    config_data = config_manager.load_config(io.StringIO(config_content))
                
                # Store enhanced configuration data
                st.session_state['enhanced_config_data'] = config_data
                
                # Convert to generator options and store in session state
                with st.spinner("🔄 Processing configuration..."):
                    generator_options = config_manager.convert_config_to_generator_options(config_data)
                
                st.session_state['selected_choices'] = generator_options.get('selected_choices', {})
                st.session_state['unbounded_counts'] = generator_options.get('unbounded_counts', {})
                st.session_state['current_generation_mode'] = generator_options.get('generation_mode', 'Minimalistic')
                st.session_state['optional_element_selections'] = generator_options.get('optional_selections', [])
                st.session_state['custom_values'] = generator_options.get('custom_values', {})
                
                show_success_message(f"✅ Configuration loaded: {config_data['metadata']['name']}")
                
                # Show configuration summary
                if 'data_contexts' in config_data:
                    context_names = list(config_data['data_contexts'].keys())
                    st.info(f"📊 Enhanced configuration with {len(context_names)} data contexts: {', '.join(context_names)}")
                
                # Show warnings if any
                schema_name = st.session_state.get('uploaded_file_name', '')
                warnings = config_manager.validate_config_compatibility(config_data, schema_name)
                if warnings:
                    for warning in warnings:
                        show_warning_message(f"⚠️ {warning}")

                # Mark that configuration has been loaded
                st.session_state['config_loaded'] = True
                
            except Exception as e:
                show_error_message(f"❌ Error loading configuration: {str(e)}")
    
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
                
                show_success_message("✅ Configuration ready for download!")
                
            except Exception as e:
                show_error_message(f"❌ Error creating configuration: {str(e)}")


def render_tab2_configure_generation(config, config_manager):
    """Render Tab 2: Configure Generation content."""
    st.markdown("### ⚙️ Generation Configuration")
    
    # Check if schema analysis is available
    if 'schema_analysis' not in st.session_state or not st.session_state['schema_analysis']:
        show_warning_message("⚠️ Please analyze the schema in the **Analyze Schema** tab first.")
        st.stop()
    
    analysis = st.session_state['schema_analysis']
    schema_info = analysis['schema_info']
    choices = analysis['choices']
    unbounded_elements = analysis['unbounded_elements']
    element_tree = analysis['element_tree']
    
    # Configuration file section
    render_config_file_section(config_manager)
    
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
    unbounded_counts = render_unbounded_elements(unbounded_elements, config)
    
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
        show_success_message("🎉 **Configuration Complete!** Ready to generate XML in the next tab.")
    else:
        show_warning_message("⚠️ Please configure all choice elements before proceeding.")


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


def generate_xml_from_xsd(xsd_file_path, xsd_file_name, selected_choices=None, unbounded_counts=None, 
                         generation_mode="Minimalistic", optional_selections=None, custom_values=None, 
                         file_manager=None, config=None):
    """Generate XML from XSD schema with user-specified choices and generation mode."""
    try:
        # Setup dependencies
        file_manager.setup_temp_directory_with_dependencies(xsd_file_path, xsd_file_name)
        
        # Check if we have enhanced configuration data
        enhanced_config = st.session_state.get('enhanced_config_data')
        
        # Create XMLGenerator with progress indication
        if enhanced_config:
            # Small delay to show the spinner before heavy processing
            import time
            time.sleep(0.1)
        
        from utils.xml_generator import XMLGenerator
        generator = XMLGenerator(xsd_file_path, config_data=enhanced_config)
        
        # Pass user selections and generation mode to generator
        return generator.generate_dummy_xml_with_options(
            selected_choices=selected_choices, 
            unbounded_counts=unbounded_counts,
            generation_mode=generation_mode,
            optional_selections=optional_selections,
            custom_values=custom_values
        )
    except Exception as e:
        error_msg = f"Error generating XML: {str(e)}"
        print(f"XMLGenerator Error: {error_msg}")  # Log for debugging
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
  <message>{error_msg}</message>
</error>"""


def validate_xml_against_schema(xml_content, xsd_file_path, uploaded_file_name=None, uploaded_file_content=None, xml_validator=None):
    """Validate generated XML against the XSD schema."""
    return xml_validator.validate_xml_against_schema(xml_content, xsd_file_path, uploaded_file_name, uploaded_file_content)


def format_validation_error(error, xml_validator):
    """Format a validation error for display."""
    return xml_validator.format_validation_error(error)


def render_validation_results(validation_result, xml_validator):
    """Render detailed validation results with error breakdown."""
    st.markdown("#### 🔍 Validation Results")
    
    if not validation_result['success']:
        show_error_message(f"❌ **Validation failed:** {validation_result['error']}")
        return
    
    error_breakdown = validation_result['error_breakdown']
    total_errors = validation_result['total_errors']
    
    # Display validation results
    if validation_result['is_valid']:
        show_success_message("🎉 **XML is valid!** No validation errors found.")
    else:
        if total_errors == 0:
            show_success_message("🎉 **XML is valid!** No validation errors found.")
        else:
            show_warning_message(f"⚠️ **XML has validation issues** ({total_errors} total errors)")
    
    # Show error breakdown in metrics
    if total_errors > 0:
        metrics = {
            "Enumeration": error_breakdown['enumeration_errors'],
            "Boolean": error_breakdown['boolean_errors'],
            "Pattern": error_breakdown['pattern_errors'],
            "Structural": error_breakdown['structural_errors']
        }
        render_metrics_row(metrics, 4)
        
        # Show detailed errors in expandable sections
        if validation_result.get('categorized_errors'):
            st.markdown("**Detailed Error Analysis:**")
            
            categorized_errors = validation_result['categorized_errors']
            
            # Create expandable sections for each error type
            if categorized_errors['enumeration_errors']:
                with st.expander(f"🔤 Enumeration Errors ({len(categorized_errors['enumeration_errors'])})", expanded=False):
                    st.caption("Values that don't match allowed enumeration lists. Expected for dummy data.")
                    for i, error in enumerate(categorized_errors['enumeration_errors'][:5], 1):
                        formatted_error = format_validation_error(error, xml_validator)
                        st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                    if len(categorized_errors['enumeration_errors']) > 5:
                        st.info(f"... and {len(categorized_errors['enumeration_errors']) - 5} more enumeration errors")
            
            if categorized_errors['boolean_errors']:
                with st.expander(f"✅ Boolean Errors ({len(categorized_errors['boolean_errors'])})", expanded=False):
                    st.caption("Invalid boolean values. These indicate type generation issues.")
                    for i, error in enumerate(categorized_errors['boolean_errors'][:5], 1):
                        formatted_error = format_validation_error(error, xml_validator)
                        st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                    if len(categorized_errors['boolean_errors']) > 5:
                        st.info(f"... and {len(categorized_errors['boolean_errors']) - 5} more boolean errors")
            
            if categorized_errors['pattern_errors']:
                with st.expander(f"🎯 Pattern Errors ({len(categorized_errors['pattern_errors'])})", expanded=False):
                    st.caption("Values that don't match required regex patterns. Expected for dummy data.")
                    for i, error in enumerate(categorized_errors['pattern_errors'][:5], 1):
                        formatted_error = format_validation_error(error, xml_validator)
                        st.text(f"{i}. {formatted_error['element_name']}: {formatted_error['message']}")
                    if len(categorized_errors['pattern_errors']) > 5:
                        st.info(f"... and {len(categorized_errors['pattern_errors']) - 5} more pattern errors")
            
            if categorized_errors['structural_errors']:
                with st.expander(f"🏗️ Structural Errors ({len(categorized_errors['structural_errors'])})", expanded=True):
                    st.caption("Missing required elements or invalid XML structure. These should be minimal.")
                    for i, error in enumerate(categorized_errors['structural_errors'][:10], 1):
                        formatted_error = format_validation_error(error, xml_validator)
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


def render_tab3_generate_validate(config, file_manager, xml_validator):
    """Render Tab 3: Generate & Validate content."""
    st.markdown("### 🚀 XML Generation & Validation")
    
    # Check if configuration is complete
    if 'schema_analysis' not in st.session_state or not st.session_state['schema_analysis']:
        show_warning_message("⚠️ Please analyze the schema in the **Analyze Schema** tab first.")
        st.stop()
    
    if 'current_generation_mode' not in st.session_state:
        show_warning_message("⚠️ Please configure generation settings in the **Configure Generation** tab first.")
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
    
    # Check if we should auto-generate XML after config load
    auto_generate = st.session_state.get('config_loaded', False) and st.session_state.get('enhanced_config_data') and not st.session_state.get('auto_generated_completed', False)
    
    # Handle XML generation
    if generate_clicked or auto_generate:
        enhanced_config = st.session_state.get('enhanced_config_data')
        if enhanced_config:
            if auto_generate:
                spinner_msg = "🚀 Auto-generating XML with enhanced configuration..."
            else:
                spinner_msg = "🚀 Generating XML with enhanced configuration (loading schema & applying data contexts)..."
        else:
            spinner_msg = "🔄 Generating XML (loading schema & processing structure)..."
            
        with st.spinner(spinner_msg):
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
                custom_values,
                file_manager,
                config
            )
            
            # Store XML content for validation and download
            st.session_state['generated_xml'] = xml_content
            
            # Mark auto-generation as completed if it was triggered
            if auto_generate:
                st.session_state['auto_generated_completed'] = True
                st.session_state['config_loaded'] = False  # Reset flag
    
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
                    uploaded_file_content,
                    xml_validator
                )
                
                render_validation_results(validation_result, xml_validator)
    else:
        st.info("👆 Click **Generate XML** above to create your XML file.")