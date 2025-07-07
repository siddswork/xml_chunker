"""
Common UI Components

Shared Streamlit components used across different workflows.
"""

import streamlit as st
import io
import json
import os
import tempfile
from typing import Dict, Any, List, Optional


def apply_custom_css():
    """Apply custom CSS styling for the application."""
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


def render_navigation_sidebar(current_section: str, available_workflows: List[str]) -> str:
    """Render the navigation sidebar and return the selected workflow."""
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        # Determine current index
        current_index = 0
        for i, workflow in enumerate(available_workflows):
            if workflow.endswith(current_section):
                current_index = i
                break
        
        selected_workflow = st.radio(
            "Choose Workflow:",
            available_workflows,
            key="navigation_radio",
            index=current_index
        )
        
        st.markdown("---")
        
        return selected_workflow


def render_workflow_help(section: str):
    """Render workflow-specific help in the sidebar."""
    if section == 'XSD to XML Generation':
        st.markdown("""
        ### 🔧 XSD to XML Generation
        
        **Workflow:**
        1. 🔍 **Analyze Schema** - Upload and explore XSD structure
        2. ⚙️ **Configure Generation** - Set choices and options  
        3. 🚀 **Generate & Validate** - Create XML and validate
        
        Perfect for creating test data from schema definitions.
        """)
    elif section == 'XML Transformation':
        st.markdown("""
        ### 🔄 XML Transformation
        
        **Workflow:**
        1. 📄 **Upload Files** - Load XML and XSLT files
        2. 🔄 **Transform** - Apply XSLT transformation
        3. ⚖️ **Compare & Test** - Test XSLT equivalence
        
        Perfect for testing and comparing XSLT stylesheets.
        """)
    elif section == 'Agentic XSLT Analysis':
        st.markdown("""
        ### 🤖 Agentic XSLT Analysis
        
        **Workflow:**
        1. 📁 **Upload XSLT** - Load XSLT files for analysis
        2. ✂️ **Intelligent Chunking** - AI-powered template detection
        3. 📊 **Analysis & Insights** - Pattern analysis and dependencies
        
        Perfect for understanding complex XSLT transformations with AI assistance.
        """)


def render_file_upload_section(file_types: List[str], accept_multiple: bool = False, 
                              title: str = "Upload Files", help_text: str = None):
    """Render a generic file upload section."""
    st.markdown("---")
    st.markdown(f"### 📁 {title}")
    
    uploaded_file = st.file_uploader(
        f"Select {', '.join(file_types).upper()} file{'s' if accept_multiple else ''} to begin",
        type=file_types,
        accept_multiple_files=accept_multiple,
        help=help_text or f"Upload {', '.join(file_types).upper()} file{'s' if accept_multiple else ''}"
    )
    
    return uploaded_file


def setup_file_processing(uploaded_file, config=None):
    """Process uploaded file and setup session state."""
    file_content = uploaded_file.getvalue().decode("utf-8")
    file_name = uploaded_file.name
    
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file_name)
    
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(uploaded_file.getvalue())
    
    # Set up dependencies for schema analysis if config provided
    if config and hasattr(config, 'file_manager'):
        config.file_manager.setup_temp_directory_with_dependencies(temp_file_path, file_name)
    
    # Store file info in session state for cross-tab access
    st.session_state['uploaded_file_name'] = file_name
    st.session_state['uploaded_file_content'] = file_content
    st.session_state['temp_file_path'] = temp_file_path
    st.session_state['temp_dir'] = temp_dir
    
    return file_content, file_name, temp_file_path


def cleanup_temp_directory():
    """Clean up temporary directories."""
    if st.session_state.get('temp_dir'):
        try:
            import shutil
            shutil.rmtree(st.session_state['temp_dir'], ignore_errors=True)
        except Exception:
            pass  # Silent cleanup


def render_metrics_row(metrics: Dict[str, Any], num_columns: int = 4):
    """Render a row of metrics with the specified number of columns."""
    if not metrics:
        return
    
    cols = st.columns(num_columns)
    metric_items = list(metrics.items())
    
    for i, (label, value) in enumerate(metric_items[:num_columns]):
        with cols[i % num_columns]:
            if isinstance(value, dict) and 'value' in value:
                st.metric(label, value['value'], delta=value.get('delta'))
            else:
                st.metric(label, value)


def render_expandable_content(title: str, content: str, language: str = "text", 
                            max_height: int = 400, expanded: bool = False):
    """Render content in an expandable section."""
    with st.expander(title, expanded=expanded):
        if language == "text":
            st.text(content)
        else:
            st.code(content, language=language, height=max_height)


def render_download_buttons(downloads: List[Dict[str, Any]], num_columns: int = 3):
    """Render multiple download buttons in columns."""
    if not downloads:
        return
    
    cols = st.columns(num_columns)
    
    for i, download in enumerate(downloads):
        with cols[i % num_columns]:
            st.download_button(
                label=download['label'],
                data=download['data'],
                file_name=download['file_name'],
                mime=download.get('mime', 'text/plain'),
                use_container_width=True,
                key=download.get('key', f"download_{i}")
            )


def show_success_message(message: str, details: Optional[str] = None):
    """Show a success message with optional details."""
    st.success(message)
    if details:
        st.info(details)


def show_error_message(message: str, details: Optional[str] = None):
    """Show an error message with optional details."""
    st.error(message)
    if details:
        st.error(f"**Details:** {details}")


def show_warning_message(message: str, details: Optional[str] = None):
    """Show a warning message with optional details."""
    st.warning(message)
    if details:
        st.info(details)


def render_progress_indicator(current_step: int, total_steps: int, step_names: List[str]):
    """Render a progress indicator showing current workflow step."""
    progress = current_step / total_steps
    st.progress(progress)
    
    if step_names and current_step <= len(step_names):
        current_step_name = step_names[current_step - 1] if current_step > 0 else "Not Started"
        st.caption(f"Step {current_step}/{total_steps}: {current_step_name}")


def create_centered_button(label: str, key: str, button_type: str = "primary", 
                          width_ratios: List[int] = [1, 1, 1]) -> bool:
    """Create a centered button using columns."""
    cols = st.columns(width_ratios)
    
    with cols[1]:  # Middle column
        return st.button(
            label,
            key=key,
            type=button_type,
            use_container_width=True
        )