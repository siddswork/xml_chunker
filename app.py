import os
import streamlit as st
from pathlib import Path

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

def main():
    st.markdown('<div class="main-header">XML Chunker</div>', unsafe_allow_html=True)
    st.markdown('Parse XSD schemas and generate dummy XML files')
    
    st.sidebar.markdown('<div class="sub-header">Settings</div>', unsafe_allow_html=True)
    
    folder_path = st.sidebar.text_input("Enter folder path containing XSD files:", 
                                        value=str(Path.home() / "repos" / "xml_chunker" / "resource" / "21_3_5_distribution_schemas"))
    
    if st.sidebar.button("Browse..."):
        st.sidebar.info("In a full implementation, this would open a file browser dialog.")
    
    if folder_path:
        st.sidebar.markdown('<div class="sub-header">XSD Files</div>', unsafe_allow_html=True)
        xsd_files = list_xsd_files(folder_path)
        
        if xsd_files:
            selected_file = st.sidebar.selectbox("Select an XSD file:", xsd_files)
            
            if selected_file:
                file_path = os.path.join(folder_path, selected_file)
                
                st.markdown(f'<div class="sub-header">Selected XSD: {selected_file}</div>', unsafe_allow_html=True)
                
                file_content = read_file_content(file_path)
                st.markdown('<div class="sub-header">XSD Content:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="content-display">{file_content}</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="generate-button">', unsafe_allow_html=True)
                if st.button("Generate XML"):
                    st.info("XML generation functionality will be implemented in future versions.")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.sidebar.warning("No XSD files found in the selected folder.")
    else:
        st.warning("Please enter a folder path containing XSD files.")

if __name__ == "__main__":
    main()
