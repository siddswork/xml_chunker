"""
XML Transformation Workflow UI

This module contains the Streamlit UI components for the XML transformation workflow,
including file upload, XSLT transformation, and equivalence testing.
"""

import streamlit as st
from typing import Dict, Any, List, Optional

from ui.common_components import (
    render_expandable_content,
    show_success_message,
    show_error_message,
    show_warning_message,
    render_metrics_row,
    create_centered_button
)


def render_xml_transformation_workflow(xslt_processor):
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
        render_transformation_tab(xslt_processor)
    
    # TAB 3: COMPARE & TEST
    with tab3:
        render_comparison_tab(xslt_processor)


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
                show_success_message(f"✅ **{uploaded_xml.name}** loaded successfully")
                
                # Preview XML
                render_expandable_content(
                    "Preview XML Content",
                    xml_content[:1000] + "..." if len(xml_content) > 1000 else xml_content,
                    language="xml"
                )
        
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
                show_success_message("✅ XML content loaded")
        
        elif xml_source == "Use Generated XML":
            if 'generated_xml' in st.session_state and st.session_state['generated_xml']:
                st.session_state['transformation_xml'] = st.session_state['generated_xml']
                st.session_state['xml_filename'] = f"{st.session_state.get('uploaded_file_name', 'schema').replace('.xsd', '')}_generated.xml"
                show_success_message("✅ Using previously generated XML")
                
                # Preview generated XML
                render_expandable_content(
                    "Preview Generated XML Content",
                    st.session_state['generated_xml'][:1000] + "..." if len(st.session_state['generated_xml']) > 1000 else st.session_state['generated_xml'],
                    language="xml"
                )
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
                show_success_message(f"✅ **{uploaded_xslt.name}** loaded successfully")
                
                # Preview XSLT
                render_expandable_content(
                    "Preview XSLT Content",
                    xslt_content[:1000] + "..." if len(xslt_content) > 1000 else xslt_content,
                    language="xml"
                )
        
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
                show_success_message("✅ XSLT content loaded")
    
    # Show current status
    if st.session_state.get('transformation_xml') and st.session_state.get('transformation_xslt'):
        st.markdown("---")
        show_success_message("🎉 Both XML and XSLT files are ready for transformation!")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"📄 XML: {st.session_state.get('xml_filename', 'Unknown')}")
        with col_info2:
            st.info(f"🔄 XSLT: {st.session_state.get('xslt_filename', 'Unknown')}")


def render_transformation_tab(xslt_processor):
    """Render the transformation tab."""
    st.markdown("### 🔄 XML Transformation")
    
    # Check if files are loaded
    if not st.session_state.get('transformation_xml') or not st.session_state.get('transformation_xslt'):
        show_warning_message("⚠️ Please upload both XML and XSLT files in the **Upload Files** tab first.")
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
                    show_success_message(f"Added parameter: {param_name}")
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
    transform_clicked = create_centered_button(
        "🚀 **Transform XML**",
        "transform_btn",
        "primary"
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
            show_success_message("✅ Transformation completed successfully!")
            
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
            show_error_message("❌ Transformation failed!")
            show_error_message(f"**Error:** {result['error']}")
            
            if result.get('error_type') == 'xslt_parse':
                st.info("💡 Check your XSLT syntax. Common issues include missing namespaces or malformed XPath expressions.")
            elif result.get('error_type') == 'xml_parse':
                st.info("💡 Check your XML syntax. The input XML may be malformed.")


def render_comparison_tab(xslt_processor):
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
                show_success_message(f"✅ Reference XSLT loaded: {ref_xslt_file.name}")
        
        else:  # Paste Content
            ref_xslt_content = st.text_area(
                "Paste Reference XSLT:",
                height=200,
                key="ref_xslt_paste"
            )
            
            if ref_xslt_content.strip():
                st.session_state['ref_xslt'] = ref_xslt_content
                show_success_message("✅ Reference XSLT loaded")
    
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
                show_success_message(f"✅ Test XSLT loaded: {test_xslt_file.name}")
        
        elif test_source == "Paste Content":
            test_xslt_content = st.text_area(
                "Paste Test XSLT:",
                height=200,
                key="test_xslt_paste"
            )
            
            if test_xslt_content.strip():
                st.session_state['test_xslt'] = test_xslt_content
                show_success_message("✅ Test XSLT loaded")
        
        else:  # Use Current XSLT
            if st.session_state.get('transformation_xslt'):
                st.session_state['test_xslt'] = st.session_state['transformation_xslt']
                show_success_message("✅ Using current transformation XSLT")
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
            show_success_message("✅ Using current XML for testing")
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
            show_success_message(f"✅ Loaded {len(test_xmls)} test XML files")
    
    elif test_xml_option == "Generate Test Cases":
        st.info("💡 This feature would integrate with your XSD generator to create multiple XML variants for comprehensive testing.")
    
    # Run comparison
    if st.session_state.get('ref_xslt') and st.session_state.get('test_xslt') and test_xmls:
        st.markdown("---")
        
        run_comparison = create_centered_button(
            "🔍 **Run Equivalence Test**",
            "run_comparison_btn",
            "primary"
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
        metrics = {
            "Total Tests": result['total_test_cases'],
            "Equivalent": result['equivalent_outputs'],
            "Failed": result['failed_transformations'],
            "Success Rate": f"{result['success_rate']:.1f}%"
        }
        render_metrics_row(metrics, 4)
        
        # Overall result
        if result['overall_equivalent']:
            show_success_message("🎉 **XSLTs are functionally equivalent!**")
        else:
            show_warning_message("⚠️ **XSLTs produce different outputs**")
        
        st.info(result['summary'])
        
        # Detailed results
        with st.expander("View Detailed Test Results"):
            for i, test_result in enumerate(result['detailed_results']):
                st.markdown(f"**Test Case {i+1}:**")
                
                if test_result['success']:
                    if test_result['equivalent']:
                        show_success_message("✅ Outputs are equivalent")
                    else:
                        show_error_message("❌ Outputs differ")
                        
                        # Show side-by-side comparison
                        col_ref, col_test = st.columns(2)
                        with col_ref:
                            st.markdown("**Reference Output:**")
                            ref_output = test_result['xslt1_result']['output_xml']
                            st.code(ref_output[:500] + "..." if len(ref_output) > 500 else ref_output, language="xml")
                        with col_test:
                            st.markdown("**Test Output:**")
                            test_output = test_result['xslt2_result']['output_xml']
                            st.code(test_output[:500] + "..." if len(test_output) > 500 else test_output, language="xml")
                else:
                    show_error_message(f"❌ Test failed: {test_result.get('error', 'Unknown error')}")
                
                st.markdown("---")