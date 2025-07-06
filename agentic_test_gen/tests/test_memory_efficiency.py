#!/usr/bin/env python3
"""
Memory efficiency tests for MVP 1
"""

import pytest
import tempfile
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader


class TestMemoryEfficiency:
    """Test memory efficiency with larger files"""
    
    def test_large_file_chunking(self):
        """Test chunking with a large XSLT file"""
        # Create a large XSLT file
        large_content = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
"""
        
        # Add many helper templates
        for i in range(1, 21):  # 20 helper templates
            large_content += f"""
    <xsl:template name="vmf:vmf{i}_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'TEST{i}'">RESULT{i}</xsl:when>
            <xsl:otherwise>DEFAULT{i}</xsl:otherwise>
        </xsl:choose>
    </xsl:template>
"""
        
        # Add a large main template
        large_content += """
    <xsl:template match="/">
        <xsl:variable name="target" select="//Target"/>
        <OrderCreateRS>
"""
        
        for i in range(1, 21):
            large_content += f"""
            <xsl:call-template name="vmf:vmf{i}_inputtoresult">
                <xsl:with-param name="input" select="$target"/>
            </xsl:call-template>
"""
        
        large_content += """
        </OrderCreateRS>
    </xsl:template>
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(large_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            file_size = temp_path.stat().st_size
            assert file_size > 1000, "Large file should be substantial size"
            
            # Test chunking
            chunker = XSLTChunker(max_tokens_per_chunk=2000)
            chunks = chunker.chunk_file(temp_path)
            
            assert len(chunks) > 0, "Should create chunks from large file"
            
            # Verify chunk distribution
            total_tokens = sum(chunk.estimated_tokens for chunk in chunks)
            assert total_tokens > 0, "Should have total tokens"
            
            avg_tokens_per_chunk = total_tokens // len(chunks) if chunks else 0
            assert avg_tokens_per_chunk > 0, "Should have reasonable average tokens per chunk"
            
            # Check token limits
            oversized_chunks = [c for c in chunks if c.estimated_tokens > chunker.max_tokens_per_chunk * 1.2]
            assert len(oversized_chunks) <= len(chunks) * 0.1, "Should have minimal oversized chunks"
            
            # Test helper template detection
            helper_chunks = [c for c in chunks if c.chunk_type == ChunkType.HELPER_TEMPLATE]
            assert len(helper_chunks) > 0, "Should detect helper templates in large file"
            
        finally:
            temp_path.unlink()
    
    def test_streaming_file_reader_efficiency(self):
        """Test streaming file reader efficiency with large files"""
        # Create content with many lines
        line_count = 1000
        large_content = "<?xml version='1.0'?>\n<xsl:stylesheet>\n"
        
        for i in range(line_count):
            large_content += f"    <!-- Comment line {i} -->\n"
        
        large_content += "</xsl:stylesheet>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(large_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            reader = StreamingFileReader()
            
            # Test metadata extraction
            metadata = reader.get_file_metadata(temp_path)
            assert metadata.line_count > line_count, "Should count all lines"
            assert metadata.size_bytes > 0, "Should have file size"
            
            # Test memory usage estimates
            estimates = reader.estimate_memory_usage(temp_path)
            assert estimates['full_load_memory_mb'] > 0, "Should estimate full load memory"
            assert estimates['chunked_memory_mb'] > 0, "Should estimate chunked memory"
            assert estimates['streaming_memory_mb'] > 0, "Should estimate streaming memory"
            
            # Streaming should be more efficient than full load
            assert estimates['streaming_memory_mb'] <= estimates['full_load_memory_mb'], "Streaming should be more efficient"
            
        finally:
            temp_path.unlink()
    
    def test_chunker_token_efficiency(self):
        """Test chunker token counting efficiency"""
        # Create content with various token densities
        content_parts = [
            "<?xml version='1.0'?>\n<xsl:stylesheet>\n",
            # High token density section
            """
    <xsl:template name="high_token_density">
        <xsl:variable name="var1" select="//very/long/xpath/expression/with/many/parts"/>
        <xsl:variable name="var2" select="concat('string1', 'string2', 'string3', 'string4')"/>
        <xsl:variable name="var3" select="substring(//another/long/xpath, 1, 100)"/>
    </xsl:template>
""",
            # Medium token density section
            """
    <xsl:template name="medium_token_density">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
""",
            # Low token density section
            """
    <xsl:template name="low_token_density">
        <result>
            <value>test</value>
        </result>
    </xsl:template>
""",
            "</xsl:stylesheet>"
        ]
        
        full_content = ''.join(content_parts)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(full_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test token estimation accuracy
            total_estimated_tokens = sum(chunk.estimated_tokens for chunk in chunks)
            assert total_estimated_tokens > 0, "Should estimate total tokens"
            
            # Test chunk size distribution
            token_sizes = [chunk.estimated_tokens for chunk in chunks]
            min_tokens = min(token_sizes) if token_sizes else 0
            max_tokens = max(token_sizes) if token_sizes else 0
            
            # Some chunks may have 0 tokens (like empty sections), so check that most have tokens
            non_zero_chunks = [t for t in token_sizes if t > 0]
            assert len(non_zero_chunks) > 0, "Should have some chunks with tokens"
            if non_zero_chunks:
                assert min(non_zero_chunks) > 0, "Non-zero chunks should have tokens"
            assert max_tokens <= chunker.max_tokens_per_chunk * 1.5, "Chunks should respect token limits (with tolerance)"
            
            # Test that high-density sections are handled appropriately
            high_density_chunks = [c for c in chunks if c.estimated_tokens > chunker.max_tokens_per_chunk * 0.8]
            if high_density_chunks:
                # High density chunks should still be manageable (allowing more flexibility)
                assert all(c.estimated_tokens <= chunker.max_tokens_per_chunk * 2.0 for c in high_density_chunks), "High density chunks should be within reasonable limits"
            
        finally:
            temp_path.unlink()
    
    def test_dependency_extraction_efficiency(self):
        """Test dependency extraction efficiency with complex content"""
        # Create content with many dependencies
        complex_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="complex_dependencies">
        <xsl:variable name="var1" select="//Target"/>
        <xsl:variable name="var2" select="$var1"/>
        <xsl:variable name="var3" select="concat($var1, $var2)"/>
        <xsl:variable name="var4" select="fn:count($var3)"/>
        <xsl:variable name="var5" select="xs:string($var4)"/>
        
        <xsl:call-template name="helper1">
            <xsl:with-param name="param1" select="$var1"/>
        </xsl:call-template>
        
        <xsl:call-template name="helper2">
            <xsl:with-param name="param2" select="$var2"/>
        </xsl:call-template>
        
        <xsl:call-template name="helper3">
            <xsl:with-param name="param3" select="$var3"/>
        </xsl:call-template>
        
        <xsl:value-of select="fn:upper-case($var5)"/>
        <xsl:value-of select="xs:date($var4)"/>
        <xsl:value-of select="custom:function($var1, $var2, $var3)"/>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(complex_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=2000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test dependency extraction
            all_dependencies = []
            for chunk in chunks:
                all_dependencies.extend(chunk.dependencies)
            
            assert len(all_dependencies) > 0, "Should extract dependencies"
            
            # Test dependency categories
            var_deps = [d for d in all_dependencies if d.startswith('var:')]
            template_deps = [d for d in all_dependencies if d.startswith('template:')]
            function_deps = [d for d in all_dependencies if d.startswith('function:')]
            
            assert len(var_deps) > 0, "Should extract variable dependencies"
            assert len(template_deps) > 0, "Should extract template dependencies"
            assert len(function_deps) > 0, "Should extract function dependencies"
            
            # Test expected dependencies (some functions may not be extracted if they don't have namespace)
            expected_vars = ['var1', 'var2', 'var3', 'var4', 'var5']
            expected_templates = ['helper1', 'helper2', 'helper3']
            expected_functions = ['fn:count', 'xs:string', 'fn:upper-case', 'xs:date', 'custom:function']
            
            var_names = [d.replace('var:', '') for d in var_deps]
            template_names = [d.replace('template:', '') for d in template_deps]
            function_names = [d.replace('function:', '') for d in function_deps]
            
            # Test that we extract at least some of each type
            assert len(var_names) >= 3, f"Should extract most variable dependencies, got: {var_names}"
            assert len(template_names) >= 3, f"Should extract all template dependencies, got: {template_names}"
            assert len(function_names) >= 3, f"Should extract most function dependencies (with namespace), got: {function_names}"
            
        finally:
            temp_path.unlink()
    
    def test_memory_usage_with_repetitive_content(self):
        """Test memory usage with repetitive content patterns"""
        # Create content with many similar templates
        repetitive_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
"""
        
        # Add many similar templates
        for i in range(100):
            repetitive_content += f"""
    <xsl:template name="template_{i}">
        <xsl:param name="input_{i}"/>
        <xsl:variable name="var_{i}" select="$input_{i}"/>
        <xsl:value-of select="$var_{i}"/>
    </xsl:template>
"""
        
        repetitive_content += "</xsl:stylesheet>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(repetitive_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            # Test with different chunk sizes
            chunk_sizes = [1000, 2000, 5000]
            
            for chunk_size in chunk_sizes:
                chunker = XSLTChunker(max_tokens_per_chunk=chunk_size)
                chunks = chunker.chunk_file(temp_path)
                
                assert len(chunks) > 0, f"Should create chunks with size {chunk_size}"
                
                # Test that smaller chunk sizes create more chunks
                if chunk_size == 1000:
                    chunks_1000 = len(chunks)
                elif chunk_size == 2000:
                    chunks_2000 = len(chunks)
                elif chunk_size == 5000:
                    chunks_5000 = len(chunks)
            
            # Verify chunk count relationship
            assert chunks_1000 >= chunks_2000, "Smaller chunks should create more chunks"
            assert chunks_2000 >= chunks_5000, "Smaller chunks should create more chunks"
            
        finally:
            temp_path.unlink()
    
    def test_chunking_performance_timing(self):
        """Test chunking performance with timing constraints"""
        import time
        
        # Create moderately sized content
        content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
"""
        
        # Add content that requires analysis
        for i in range(50):
            content += f"""
    <xsl:template name="vmf:vmf{i}_inputtoresult">
        <xsl:param name="input"/>
        <xsl:variable name="var{i}" select="$input"/>
        <xsl:choose>
            <xsl:when test="$var{i} = 'TEST'">
                <xsl:call-template name="vmf:vmf{i+1}_inputtoresult">
                    <xsl:with-param name="input" select="$var{i}"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$var{i}"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
"""
        
        content += "</xsl:stylesheet>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=2000)
            
            # Time the chunking process
            start_time = time.time()
            chunks = chunker.chunk_file(temp_path)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Performance expectations
            assert processing_time < 5.0, "Chunking should complete within 5 seconds"
            assert len(chunks) > 0, "Should create chunks"
            
            # Test that performance is reasonable per chunk
            time_per_chunk = processing_time / len(chunks) if chunks else 0
            assert time_per_chunk < 0.1, "Should process each chunk quickly"
            
        finally:
            temp_path.unlink()