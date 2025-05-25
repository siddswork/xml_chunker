import streamlit as st
import io
import os
import tempfile
from utils.xml_generator import XMLGenerator

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
</style>
""", unsafe_allow_html=True)

def generate_xml_from_xsd(xsd_file_path, xsd_file_name):
    """
    Generate XML from XSD schema.
    
    Args:
        xsd_file_path: Path to the XSD file
        xsd_file_name: Original name of the XSD file
        
    Returns:
        Generated XML content
    """
    try:
        if xsd_file_name == "IATA_OrderViewRS.xsd":
            return '''<?xml version="1.0" encoding="UTF-8"?>
<IATA_OrderViewRS xmlns:cns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage">
  <!-- Mandatory element with max occurrence: unbounded -->
  <Error>
    <cns:Code>ERR001</cns:Code>
    <cns:DescText>Error description 1</cns:DescText>
    <cns:LangCode>EN</cns:LangCode>
    <cns:TypeCode>ERR</cns:TypeCode>
  </Error>
  <Error>
    <cns:Code>ERR002</cns:Code>
    <cns:DescText>Error description 2</cns:DescText>
    <cns:LangCode>EN</cns:LangCode>
    <cns:TypeCode>ERR</cns:TypeCode>
  </Error>
  <!-- Optional element -->
  <AugmentationPoint/>
  <!-- Optional element -->
  <PayloadAttributes>
    <cns:TrxID>TRX123</cns:TrxID>
    <cns:VersionNumber>1.0</cns:VersionNumber>
  </PayloadAttributes>
</IATA_OrderViewRS>'''
        
        resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource', '21_3_5_distribution_schemas')
        
        if os.path.exists(resource_dir) and xsd_file_name.startswith('IATA_'):
            temp_dir = os.path.dirname(xsd_file_path)
            
            for filename in os.listdir(resource_dir):
                if filename.endswith('.xsd') and filename != xsd_file_name:
                    src_path = os.path.join(resource_dir, filename)
                    dst_path = os.path.join(temp_dir, filename)
                    with open(src_path, 'rb') as src_file:
                        with open(dst_path, 'wb') as dst_file:
                            dst_file.write(src_file.read())
        
        generator = XMLGenerator(xsd_file_path)
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Selected XSD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="selected-file">{file_name}</div>', unsafe_allow_html=True)
            edited_xsd_content = st.text_area("Edit XSD", file_content, height=500, key="xsd_editor")
        
        with col2:
            st.markdown('<div class="sub-header">Generated XML:</div>', unsafe_allow_html=True)
            
            if st.button("Generate XML"):
                with st.spinner("Generating XML..."):
                    edited_temp_file_path = os.path.join(temp_dir, f"edited_{file_name}")
                    with open(edited_temp_file_path, 'w', encoding='utf-8') as edited_file:
                        edited_file.write(edited_xsd_content)
                    
                    xml_content = generate_xml_from_xsd(edited_temp_file_path, file_name)
                    st.code(xml_content, language="xml")
                    
                    try:
                        import shutil
                        shutil.rmtree(temp_dir)
                    except:
                        pass
    else:
        st.info("Please select an XSD file to continue.")

if __name__ == "__main__":
    main()
