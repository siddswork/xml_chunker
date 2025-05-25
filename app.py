import os
import streamlit as st
from pathlib import Path
import io

st.set_page_config(
    page_title="XML Chunker",
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
    .file-list {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        max-height: 300px;
        overflow-y: auto;
    }
    .selected-file {
        background-color: #f0f2f6;
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
    .content-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .columns-container {
        display: flex;
        gap: 20px;
    }
    .column {
        flex: 1;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

def list_xsd_files(folder_path):
    """List all XSD files in the specified folder."""
    if not folder_path:
        return []
    
    xsd_files = []
    try:
        for file in os.listdir(folder_path):
            if file.lower().endswith('.xsd'):
                xsd_files.append(file)
        return sorted(xsd_files)
    except Exception as e:
        st.error(f"Error listing XSD files: {e}")
        return []

def read_file_content(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

def generate_dummy_xml():
    """Generate a dummy XML file (placeholder)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<dummy>
  <message>XML generation will be implemented in future versions</message>
</dummy>"""

def main():
    st.markdown('<div class="main-header">XML Chunker</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    st.sidebar.markdown('<div class="sub-header">Settings</div>', unsafe_allow_html=True)
    
    default_folder = str(Path.home() / "repos" / "xml_chunker" / "resource" / "21_3_5_distribution_schemas")
    
    xsd_files = list_xsd_files(default_folder)
    
    default_index = 0
    if "IATA_OrderCreateRQ.xsd" in xsd_files:
        default_index = xsd_files.index("IATA_OrderCreateRQ.xsd")
    
    uploaded_file = st.sidebar.file_uploader("Select a XSD file", type=["xsd"])
    
    st.sidebar.markdown('<div class="sub-header">Or select from existing files:</div>', unsafe_allow_html=True)
    selected_file = st.sidebar.selectbox(
        "Select an XSD file:",
        xsd_files,
        index=default_index
    )
    
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")
        file_name = uploaded_file.name
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Selected XSD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="selected-file">{file_name}</div>', unsafe_allow_html=True)
            st.markdown('<div class="content-display">' + file_content + '</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="sub-header">Generated XML:</div>', unsafe_allow_html=True)
            
            if st.button("Generate XML"):
                xml_content = generate_dummy_xml()
                st.markdown('<div class="xml-display">' + xml_content + '</div>', unsafe_allow_html=True)
    
    elif selected_file:
        file_path = os.path.join(default_folder, selected_file)
        file_content = read_file_content(file_path)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Selected XSD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="selected-file">{selected_file}</div>', unsafe_allow_html=True)
            st.markdown('<div class="content-display">' + file_content + '</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="sub-header">Generated XML:</div>', unsafe_allow_html=True)
            
            if st.button("Generate XML"):
                xml_content = generate_dummy_xml()
                st.markdown('<div class="xml-display">' + xml_content + '</div>', unsafe_allow_html=True)
    
    else:
        st.warning("Please select an XSD file to continue.")

if __name__ == "__main__":
    main()
