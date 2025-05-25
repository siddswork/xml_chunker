import streamlit as st
import io
import html

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
</style>
""", unsafe_allow_html=True)

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
    
    uploaded_file = st.sidebar.file_uploader("Select a XSD file", type=["xsd"])
    
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")
        file_name = uploaded_file.name
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Selected XSD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="selected-file">{file_name}</div>', unsafe_allow_html=True)
            st.code(file_content, language="xml")
        
        with col2:
            st.markdown('<div class="sub-header">Generated XML:</div>', unsafe_allow_html=True)
            
            if st.button("Generate XML"):
                xml_content = generate_dummy_xml()
                st.code(xml_content, language="xml")
    else:
        st.info("Please select an XSD file to continue.")

if __name__ == "__main__":
    main()
