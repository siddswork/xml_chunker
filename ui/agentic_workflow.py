"""
Agentic XSLT Analysis Workflow UI

This module contains the Streamlit UI components for the agentic XSLT analysis workflow,
including file upload, intelligent chunking, and insights display.
"""

import streamlit as st
import tempfile
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Import agentic system components
agentic_system_available = False
try:
    import sys
    
    # Add agentic_test_gen to path for imports
    agentic_path = Path(__file__).parent.parent / "agentic_test_gen"
    if agentic_path.exists():
        sys.path.insert(0, str(agentic_path))
        from src.core.xslt_chunker import XSLTChunker, ChunkType, DEFAULT_HELPER_PATTERNS
        from src.utils.streaming_file_reader import StreamingFileReader
        from src.utils.token_counter import TokenCounter
        agentic_system_available = True
except ImportError:
    agentic_system_available = False


def analyze_potential_helper_patterns(content: str) -> Dict[str, Any]:
    """
    Analyze XSLT content to detect potential helper patterns that might not be detected
    by current patterns, and suggest alternative configurations.
    """
    import re
    
    potential_helpers = []
    suggestions = []
    
    # Look for template names that might be helpers but not detected by current patterns
    template_pattern = r'<xsl:template\s+name="([^"]+)"'
    all_templates = re.findall(template_pattern, content)
    
    # Check for different naming patterns
    patterns_to_check = {
        'MapForce (vmf)': r'(?:vmf:)?vmf\d+',
        'Saxon (f:func)': r'(?:f:)?func\d+',
        'Custom (util/helper)': r'(?:util:)?helper[\w_]*',
        'Generic utility': r'(?:\w+:)?(?:helper|util|fn)\w*',
        'Transform functions': r'(?:\w+:)?(?:transform|convert|map|format)\w*',
        'Processing functions': r'(?:\w+:)?(?:process|handle|build)\w*'
    }
    
    detected_patterns = {}
    
    for template_name in all_templates:
        for pattern_name, pattern in patterns_to_check.items():
            if re.search(pattern, template_name, re.IGNORECASE):
                if pattern_name not in detected_patterns:
                    detected_patterns[pattern_name] = []
                detected_patterns[pattern_name].append(template_name)
    
    # Look for functions that look like helpers but don't match any pattern
    possible_helpers = []
    for template_name in all_templates:
        # Simple heuristics for potential helpers
        if (len(template_name) > 8 and  # Reasonably long name
            ('_' in template_name or ':' in template_name) and  # Has namespace or underscore
            not any(re.search(pattern, template_name, re.IGNORECASE) 
                   for pattern in patterns_to_check.values())):
            possible_helpers.append(template_name)
    
    return {
        'total_templates': len(all_templates),
        'detected_patterns': detected_patterns,
        'unmatched_potential_helpers': possible_helpers[:10],  # Limit to first 10
        'all_template_names': all_templates
    }


def render_agentic_xslt_workflow():
    """Render the Agentic XSLT Analysis workflow."""
    st.markdown('<div class="main-header">Agentic XSLT Analysis</div>', unsafe_allow_html=True)
    st.markdown('Intelligent analysis of XSLT transformations using AI-powered chunking and pattern detection')
    
    # Create tabs for agentic workflow
    tab1, tab2, tab3 = st.tabs(["📁 **Upload & Analyze**", "✂️ **Intelligent Chunking**", "📊 **Insights & Export**"])
    
    # TAB 1: UPLOAD & ANALYZE
    with tab1:
        render_agentic_upload_tab()
    
    # TAB 2: INTELLIGENT CHUNKING
    with tab2:
        render_agentic_chunking_tab()
    
    # TAB 3: INSIGHTS & EXPORT
    with tab3:
        render_agentic_insights_tab()


def render_agentic_upload_tab():
    """Render the XSLT upload and initial analysis tab."""
    st.markdown("### 📁 Upload XSLT Files")
    
    # File upload section
    st.markdown("#### Upload XSLT Files for Analysis")
    
    uploaded_xslt = st.file_uploader(
        "Choose XSLT file(s)",
        type=['xsl', 'xslt'],
        accept_multiple_files=True,
        help="Upload one or more XSLT files for intelligent analysis"
    )
    
    if uploaded_xslt:
        st.markdown("---")
        st.markdown("#### 📊 File Analysis Summary")
        
        # Process uploaded files
        xslt_files = []
        for file in uploaded_xslt:
            content = file.getvalue().decode("utf-8")
            
            # Basic file info
            file_info = {
                'name': file.name,
                'content': content,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            xslt_files.append(file_info)
        
        # Store in session state
        st.session_state['agentic_xslt_files'] = xslt_files
        
        # Display file summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Files Uploaded", len(xslt_files))
        with col2:
            total_size = sum(f['size'] for f in xslt_files)
            st.metric("Total Size", f"{total_size / 1024:.1f} KB")
        with col3:
            total_lines = sum(f['lines'] for f in xslt_files)
            st.metric("Total Lines", f"{total_lines:,}")
        
        # File details
        st.markdown("#### 📋 File Details")
        for i, file_info in enumerate(xslt_files, 1):
            with st.expander(f"📄 {file_info['name']} ({file_info['size']} bytes, {file_info['lines']:,} lines)"):
                st.code(file_info['content'][:1000] + "..." if len(file_info['content']) > 1000 else file_info['content'], language="xml")
        
        # Quick analysis using StreamingFileReader
        if agentic_system_available:
            st.markdown("---")
            st.markdown("#### 🔍 Quick Analysis")
            
            with st.spinner("Performing quick analysis..."):
                analysis_results = []
                
                for file_info in xslt_files:
                    # Create temporary file for analysis
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as temp_file:
                        temp_file.write(file_info['content'])
                        temp_path = Path(temp_file.name)
                    
                    try:
                        # Use StreamingFileReader for metadata
                        reader = StreamingFileReader()
                        metadata = reader.get_file_metadata(temp_path)
                        
                        # Basic pattern detection
                        template_count = file_info['content'].count('<xsl:template')
                        variable_count = file_info['content'].count('<xsl:variable')
                        choose_count = file_info['content'].count('<xsl:choose>')
                        
                        analysis = {
                            'name': file_info['name'],
                            'encoding': metadata.encoding,
                            'estimated_tokens': metadata.estimated_tokens,
                            'template_count': template_count,
                            'variable_count': variable_count,
                            'choose_count': choose_count
                        }
                        
                        analysis_results.append(analysis)
                        
                    finally:
                        # Cleanup temp file
                        temp_path.unlink(missing_ok=True)
            
            # Display analysis results
            if analysis_results:
                for analysis in analysis_results:
                    st.markdown(f"**{analysis['name']}:**")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("Templates", analysis['template_count'])
                    with col_b:
                        st.metric("Variables", analysis['variable_count'])
                    with col_c:
                        st.metric("Choose Blocks", analysis['choose_count'])
                    with col_d:
                        st.metric("Est. Tokens", f"{analysis['estimated_tokens']:,}")
        
        st.success("✅ Files uploaded successfully! Proceed to the **Intelligent Chunking** tab for detailed analysis.")
    
    else:
        st.info("📁 Please upload XSLT files to begin the agentic analysis workflow.")


def render_agentic_chunking_tab():
    """Render the intelligent chunking analysis tab."""
    st.markdown("### ✂️ Intelligent XSLT Chunking")
    
    # Check if files are uploaded
    if 'agentic_xslt_files' not in st.session_state or not st.session_state['agentic_xslt_files']:
        st.warning("⚠️ Please upload XSLT files in the **Upload & Analyze** tab first.")
        return
    
    xslt_files = st.session_state['agentic_xslt_files']
    
    # Configuration section
    st.markdown("#### ⚙️ Chunking Configuration")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        max_tokens = st.number_input(
            "Max Tokens per Chunk",
            min_value=1000,
            max_value=50000,
            value=15000,
            step=1000,
            help="Maximum number of tokens allowed per chunk"
        )
    
    with col_config2:
        overlap_tokens = st.number_input(
            "Overlap Tokens",
            min_value=0,
            max_value=2000,
            value=500,
            step=100,
            help="Number of tokens to overlap between chunks"
        )
    
    # File selection for chunking
    st.markdown("#### 📂 Select File for Chunking")
    
    file_names = [f['name'] for f in xslt_files]
    selected_file_name = st.selectbox(
        "Choose file to analyze:",
        file_names,
        help="Select which XSLT file to perform detailed chunking analysis on"
    )
    
    # Chunking analysis button
    col_chunk1, col_chunk2, col_chunk3 = st.columns([1, 1, 1])
    
    with col_chunk2:
        analyze_clicked = st.button(
            "🚀 **Analyze Chunks**",
            type="primary",
            use_container_width=True,
            key="analyze_chunks_btn"
        )
    
    # Perform chunking analysis
    if analyze_clicked and agentic_system_available:
        selected_file = next(f for f in xslt_files if f['name'] == selected_file_name)
        
        with st.spinner("🔄 Performing intelligent XSLT chunking..."):
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as temp_file:
                temp_file.write(selected_file['content'])
                temp_path = Path(temp_file.name)
            
            try:
                # Initialize chunker
                chunker = XSLTChunker(max_tokens_per_chunk=max_tokens, overlap_tokens=overlap_tokens)
                
                # Perform chunking
                start_time = time.time()
                chunks = chunker.chunk_file(temp_path)
                processing_time = time.time() - start_time
                
                # Store results
                st.session_state['agentic_chunks'] = chunks
                st.session_state['chunking_config'] = {
                    'max_tokens': max_tokens,
                    'overlap_tokens': overlap_tokens,
                    'file_name': selected_file_name,
                    'processing_time': processing_time
                }
                
            finally:
                # Cleanup temp file
                temp_path.unlink(missing_ok=True)
    
    # Display chunking results
    if 'agentic_chunks' in st.session_state and st.session_state['agentic_chunks']:
        chunks = st.session_state['agentic_chunks']
        config = st.session_state['chunking_config']
        
        st.markdown("---")
        st.markdown("#### 📊 Chunking Results")
        
        # Summary metrics
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        
        with col_res1:
            st.metric("Total Chunks", len(chunks))
        with col_res2:
            total_tokens = sum(chunk.estimated_tokens for chunk in chunks)
            st.metric("Total Tokens", f"{total_tokens:,}")
        with col_res3:
            avg_tokens = total_tokens // len(chunks) if chunks else 0
            st.metric("Avg Tokens/Chunk", f"{avg_tokens:,}")
        with col_res4:
            st.metric("Processing Time", f"{config['processing_time']:.2f}s")
        
        # Chunk type distribution
        st.markdown("#### 📈 Chunk Type Distribution")
        
        chunk_types = {}
        helper_templates = []
        
        for chunk in chunks:
            chunk_type = chunk.chunk_type.value
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            if chunk.chunk_type == ChunkType.HELPER_TEMPLATE:
                helper_templates.append({
                    'name': chunk.name or 'Unnamed',
                    'tokens': chunk.estimated_tokens,
                    'dependencies': len(chunk.dependencies)
                })
        
        # Display chunk type metrics
        type_cols = st.columns(len(chunk_types))
        for i, (chunk_type, count) in enumerate(chunk_types.items()):
            with type_cols[i]:
                percentage = (count / len(chunks)) * 100
                st.metric(chunk_type.replace('_', ' ').title(), f"{count} ({percentage:.1f}%)")
        
        # Helper templates section with smart feedback
        st.markdown("#### 🔧 Helper Templates Analysis")
        
        if helper_templates:
            st.success(f"✅ **{len(helper_templates)} helper templates detected** using current MapForce patterns")
            
            for i, helper in enumerate(helper_templates[:5], 1):
                st.markdown(f"**{i}. {helper['name']}** - {helper['tokens']} tokens, {helper['dependencies']} dependencies")
            
            if len(helper_templates) > 5:
                st.info(f"... and {len(helper_templates) - 5} more helper templates")
        else:
            # No helpers detected - provide intelligent feedback
            st.warning("⚠️ **No helper templates detected** with current patterns")
            
            # Analyze the XSLT content for potential patterns
            if st.session_state.get('agentic_xslt_files'):
                file_content = st.session_state['agentic_xslt_files'][0]['content']  # Use first file for analysis
                pattern_analysis = analyze_potential_helper_patterns(file_content)
                
                if pattern_analysis['detected_patterns'] or pattern_analysis['unmatched_potential_helpers']:
                    st.markdown("##### 🔍 Pattern Analysis & Suggestions")
                    
                    # Show detected patterns from other systems
                    if pattern_analysis['detected_patterns']:
                        st.info("**Alternative patterns detected in your XSLT:**")
                        for pattern_name, templates in pattern_analysis['detected_patterns'].items():
                            if pattern_name != 'MapForce (vmf)':  # Skip the current default
                                st.markdown(f"- **{pattern_name}**: {', '.join(templates[:3])}")
                                if len(templates) > 3:
                                    st.markdown(f"  ... and {len(templates) - 3} more")
                    
                    # Show unmatched potential helpers
                    if pattern_analysis['unmatched_potential_helpers']:
                        st.info("**Unmatched templates that might be helpers:**")
                        unmatched = pattern_analysis['unmatched_potential_helpers']
                        st.markdown(f"- {', '.join(unmatched[:5])}")
                        if len(unmatched) > 5:
                            st.markdown(f"  ... and {len(unmatched) - 5} more")
                    
                    # Provide actionable suggestions
                    with st.expander("💡 **Click for helper pattern configuration suggestions**"):
                        st.markdown("**To improve helper template detection:**")
                        
                        if any('Saxon' in p for p in pattern_analysis['detected_patterns']):
                            st.markdown("1. ✨ Try **Saxon patterns** - your XSLT contains `f:func` style templates")
                            st.code("chunker = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['saxon']])")
                        
                        if any('util' in t.lower() or 'helper' in t.lower() for t in pattern_analysis['unmatched_potential_helpers']):
                            st.markdown("2. ✨ Try **Custom/Utility patterns** - detected utility-style templates")
                            st.code("chunker = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['custom']])")
                        
                        if pattern_analysis['unmatched_potential_helpers']:
                            st.markdown("3. ✨ Try **Generic patterns** - broader detection")
                            st.code("chunker = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['generic']])")
                        
                        st.markdown("4. ✨ **Combine multiple patterns** for comprehensive detection")
                        st.code("""chunker = XSLTChunker(helper_patterns=[
    DEFAULT_HELPER_PATTERNS['mapforce'],
    DEFAULT_HELPER_PATTERNS['saxon'],
    DEFAULT_HELPER_PATTERNS['custom']
])""")
                        
                        st.markdown("5. 🛠️ **Create custom patterns** for your specific naming conventions")
                        if pattern_analysis['unmatched_potential_helpers']:
                            example_template = pattern_analysis['unmatched_potential_helpers'][0]
                            st.code(f"# Example custom pattern for templates like '{example_template}'\ncustom_pattern = r'{example_template.split('_')[0]}_\\\\w+'")
                else:
                    st.info("💡 Your XSLT appears to use main templates without separate helper templates, or uses a unique naming pattern not covered by current detection.")
            
            st.markdown("---")
            st.markdown("**Current Detection**: Using MapForce patterns (`vmf:vmf1_*`, `vmf2_*`, etc.)")
            st.markdown("**Need different patterns?** See suggestions above or contact support for custom pattern configuration.")
        
        # Chunk preview
        st.markdown("#### 📄 Chunk Preview")
        
        chunk_options = [f"Chunk {i+1}: {chunk.chunk_id} ({chunk.chunk_type.value}) - Lines {chunk.start_line}-{chunk.end_line} ({chunk.estimated_tokens} tokens)" for i, chunk in enumerate(chunks)]
        selected_chunk_idx = st.selectbox(
            "Select chunk to preview:",
            range(len(chunk_options)),
            format_func=lambda x: chunk_options[x]
        )
        
        if selected_chunk_idx is not None:
            selected_chunk = chunks[selected_chunk_idx]
            
            col_preview1, col_preview2 = st.columns([3, 1])
            
            with col_preview1:
                st.markdown(f"**Chunk:** {selected_chunk.chunk_id}")
                st.markdown(f"**Type:** {selected_chunk.chunk_type.value}")
                st.markdown(f"**Lines:** {selected_chunk.start_line}-{selected_chunk.end_line}")
                st.markdown(f"**Tokens:** {selected_chunk.estimated_tokens}")
                
                if selected_chunk.name:
                    st.markdown(f"**Name:** {selected_chunk.name}")
                
                # Show chunk content
                st.code(selected_chunk.text[:1000] + "..." if len(selected_chunk.text) > 1000 else selected_chunk.text, language="xml", height=300)
            
            with col_preview2:
                st.markdown("**Dependencies:**")
                if selected_chunk.dependencies:
                    for dep in selected_chunk.dependencies[:10]:
                        st.markdown(f"• `{dep}`")
                    if len(selected_chunk.dependencies) > 10:
                        st.markdown(f"• ... and {len(selected_chunk.dependencies) - 10} more")
                else:
                    st.markdown("*No dependencies found*")
                
                st.markdown("**Metadata:**")
                for key, value in selected_chunk.metadata.items():
                    if isinstance(value, bool):
                        status = "✅" if value else "❌"
                        st.markdown(f"• {key}: {status}")
                    else:
                        st.markdown(f"• {key}: {value}")


def render_agentic_insights_tab():
    """Render the insights and export tab."""
    st.markdown("### 📊 Analysis Insights & Export")
    
    # Check if chunking analysis is available
    if 'agentic_chunks' not in st.session_state or not st.session_state['agentic_chunks']:
        st.warning("⚠️ Please perform chunking analysis in the **Intelligent Chunking** tab first.")
        return
    
    chunks = st.session_state['agentic_chunks']
    config = st.session_state['chunking_config']
    
    # Advanced insights
    st.markdown("#### 🎯 Key Insights")
    
    # Calculate insights
    total_dependencies = sum(len(chunk.dependencies) for chunk in chunks)
    unique_deps = set()
    for chunk in chunks:
        unique_deps.update(chunk.dependencies)
    
    var_deps = [d for d in unique_deps if d.startswith('var:')]
    template_deps = [d for d in unique_deps if d.startswith('template:')]
    function_deps = [d for d in unique_deps if d.startswith('function:')]
    
    choose_chunks = sum(1 for c in chunks if c.metadata.get('has_choose_blocks', False))
    xpath_chunks = sum(1 for c in chunks if c.metadata.get('has_xpath', False))
    
    # Display insights
    col_insights1, col_insights2, col_insights3 = st.columns(3)
    
    with col_insights1:
        st.markdown("**📊 Dependency Analysis**")
        st.metric("Total Dependencies", total_dependencies)
        st.metric("Unique Dependencies", len(unique_deps))
        st.metric("Variable References", len(var_deps))
        st.metric("Template Calls", len(template_deps))
        st.metric("Function Calls", len(function_deps))
    
    with col_insights2:
        st.markdown("**🔍 Pattern Detection**")
        st.metric("Chunks with Choose Blocks", choose_chunks)
        st.metric("Chunks with XPath", xpath_chunks)
        
        complexity_scores = [c.metadata.get('complexity_score', 0) for c in chunks]
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        st.metric("Average Complexity", f"{avg_complexity:.2f}")
    
    with col_insights3:
        st.markdown("**⚙️ Processing Stats**")
        st.metric("File", config['file_name'])
        st.metric("Max Tokens", f"{config['max_tokens']:,}")
        st.metric("Processing Time", f"{config['processing_time']:.2f}s")
        
        tokens_per_second = sum(c.estimated_tokens for c in chunks) / config['processing_time']
        st.metric("Tokens/Second", f"{tokens_per_second:,.0f}")
    
    # Export options
    st.markdown("---")
    st.markdown("#### 💾 Export Analysis")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("📊 **Export Summary JSON**", use_container_width=True):
            # Create summary data
            summary_data = {
                'file_name': config['file_name'],
                'analysis_timestamp': time.time(),
                'chunking_config': config,
                'summary': {
                    'total_chunks': len(chunks),
                    'total_tokens': sum(c.estimated_tokens for c in chunks),
                    'chunk_types': {},
                    'dependencies': {
                        'total': total_dependencies,
                        'unique': len(unique_deps),
                        'variables': len(var_deps),
                        'templates': len(template_deps),
                        'functions': len(function_deps)
                    },
                    'patterns': {
                        'choose_blocks': choose_chunks,
                        'xpath_expressions': xpath_chunks,
                        'average_complexity': avg_complexity
                    }
                }
            }
            
            # Add chunk type distribution
            for chunk in chunks:
                chunk_type = chunk.chunk_type.value
                summary_data['summary']['chunk_types'][chunk_type] = summary_data['summary']['chunk_types'].get(chunk_type, 0) + 1
            
            summary_json = json.dumps(summary_data, indent=2, default=str)
            
            st.download_button(
                label="💾 Download Summary",
                data=summary_json,
                file_name=f"{config['file_name']}_agentic_summary.json",
                mime="application/json"
            )
    
    with col_export2:
        if st.button("📋 **Export Detailed JSON**", use_container_width=True):
            # Create detailed data
            detailed_data = {
                'file_name': config['file_name'],
                'analysis_timestamp': time.time(),
                'chunking_config': config,
                'chunks': []
            }
            
            for chunk in chunks:
                chunk_data = {
                    'chunk_id': chunk.chunk_id,
                    'chunk_type': chunk.chunk_type.value,
                    'name': chunk.name,
                    'start_line': chunk.start_line,
                    'end_line': chunk.end_line,
                    'line_count': chunk.line_count,
                    'estimated_tokens': chunk.estimated_tokens,
                    'dependencies': chunk.dependencies,
                    'metadata': chunk.metadata,
                    'text_preview': chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                }
                detailed_data['chunks'].append(chunk_data)
            
            detailed_json = json.dumps(detailed_data, indent=2, default=str)
            
            st.download_button(
                label="💾 Download Detailed",
                data=detailed_json,
                file_name=f"{config['file_name']}_agentic_detailed.json",
                mime="application/json"
            )
    
    with col_export3:
        if st.button("📝 **Export Markdown Report**", use_container_width=True):
            # Create markdown report
            report = f"""# Agentic XSLT Analysis Report

## File Information
- **File:** {config['file_name']}
- **Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Processing Time:** {config['processing_time']:.2f} seconds

## Configuration
- **Max Tokens per Chunk:** {config['max_tokens']:,}
- **Overlap Tokens:** {config['overlap_tokens']}

## Summary
- **Total Chunks:** {len(chunks)}
- **Total Tokens:** {sum(c.estimated_tokens for c in chunks):,}
- **Average Tokens per Chunk:** {sum(c.estimated_tokens for c in chunks) // len(chunks) if chunks else 0:,}

## Chunk Type Distribution
"""
            
            # Add chunk type distribution
            chunk_types = {}
            for chunk in chunks:
                chunk_type = chunk.chunk_type.value
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            for chunk_type, count in chunk_types.items():
                percentage = (count / len(chunks)) * 100
                report += f"- **{chunk_type.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"
            
            report += f"""
## Dependencies Analysis
- **Total Dependencies:** {total_dependencies}
- **Unique Dependencies:** {len(unique_deps)}
- **Variable References:** {len(var_deps)}
- **Template Calls:** {len(template_deps)}
- **Function Calls:** {len(function_deps)}

## Pattern Detection
- **Chunks with Choose Blocks:** {choose_chunks}
- **Chunks with XPath Expressions:** {xpath_chunks}
- **Average Complexity Score:** {avg_complexity:.2f}

## Chunk Details
"""
            
            for i, chunk in enumerate(chunks[:10], 1):
                report += f"""
### Chunk {i}: {chunk.chunk_id}
- **Type:** {chunk.chunk_type.value}
- **Name:** {chunk.name or 'N/A'}
- **Lines:** {chunk.start_line}-{chunk.end_line}
- **Tokens:** {chunk.estimated_tokens}
- **Dependencies:** {len(chunk.dependencies)}
"""
            
            if len(chunks) > 10:
                report += f"\n*... and {len(chunks) - 10} more chunks*\n"
            
            st.download_button(
                label="💾 Download Report",
                data=report,
                file_name=f"{config['file_name']}_agentic_report.md",
                mime="text/markdown"
            )
    
    # Success message
    st.success("🎉 Analysis complete! Export your results using the buttons above.")


def check_agentic_system_availability():
    """Check if the agentic system is available for import."""
    return agentic_system_available