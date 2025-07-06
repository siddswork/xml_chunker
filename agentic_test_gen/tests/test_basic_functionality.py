#!/usr/bin/env python3
"""
Basic functionality tests for MVP 1
"""

import pytest
import tempfile
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader
from src.utils.token_counter import TokenCounter


class TestBasicFunctionality:
    """Test basic functionality without external dependencies"""
    
    def test_imports(self):
        """Test that all required modules import successfully"""
        # All imports should work without errors
        assert XSLTChunker is not None
        assert ChunkType is not None
        assert StreamingFileReader is not None
        assert TokenCounter is not None
    
    def test_token_counter(self):
        """Test token counter functionality"""
        counter = TokenCounter()
        
        # Test basic token counting
        test_text = "Hello world, this is a test"
        tokens = counter.estimate_tokens(test_text)
        assert tokens > 0, "Token count should be greater than 0"
        assert isinstance(tokens, int), "Token count should be integer"
        
        # Test empty string
        empty_tokens = counter.estimate_tokens("")
        assert empty_tokens == 0, "Empty string should have 0 tokens"
        
        # Test longer text
        long_text = "This is a longer piece of text that should have more tokens " * 10
        long_tokens = counter.estimate_tokens(long_text)
        assert long_tokens > tokens, "Longer text should have more tokens"
    
    def test_streaming_file_reader(self):
        """Test streaming file reader with temp file"""
        reader = StreamingFileReader()
        
        test_content = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="test">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            metadata = reader.get_file_metadata(temp_path)
            
            # Test metadata properties
            assert metadata.size_bytes > 0, "File should have size"
            assert metadata.line_count > 0, "File should have lines"
            assert metadata.encoding is not None, "File should have encoding"
            assert metadata.estimated_tokens > 0, "File should have estimated tokens"
            
            # Test expected values (line count may differ by 1 due to final newline handling)
            expected_lines = len(test_content.splitlines())
            assert abs(metadata.line_count - expected_lines) <= 1, f"Line count should be close to content lines: {metadata.line_count} vs {expected_lines}"
            assert metadata.size_bytes == len(test_content.encode('utf-8')), "Size should match content"
            
            # Test memory usage estimates
            estimates = reader.estimate_memory_usage(temp_path)
            assert 'full_load_memory_mb' in estimates
            assert 'chunked_memory_mb' in estimates
            assert 'streaming_memory_mb' in estimates
            assert 'recommended_strategy' in estimates
            
            # Memory estimates should be reasonable
            assert estimates['full_load_memory_mb'] > 0
            assert estimates['chunked_memory_mb'] > 0
            assert estimates['streaming_memory_mb'] > 0
            assert estimates['recommended_strategy'] in ['full_load', 'chunked', 'streaming']
            
        finally:
            temp_path.unlink()
    
    def test_xslt_chunker_basic(self):
        """Test XSLT chunker with basic content"""
        chunker_test_content = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Helper template -->
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'P'">VPT</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Main template -->
    <xsl:template match="/">
        <xsl:variable name="target" select="//Target"/>
        <Result>
            <xsl:call-template name="vmf:vmf1_inputtoresult">
                <xsl:with-param name="input" select="$target"/>
            </xsl:call-template>
        </Result>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(chunker_test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Basic chunk validation
            assert len(chunks) > 0, "Should create chunks"
            assert isinstance(chunks, list), "Should return list of chunks"
            
            # Test chunk properties
            for i, chunk in enumerate(chunks):
                assert chunk.chunk_id is not None, f"Chunk {i} should have ID"
                assert chunk.chunk_type in [ChunkType.HELPER_TEMPLATE, ChunkType.MAIN_TEMPLATE, ChunkType.VARIABLE_SECTION, ChunkType.IMPORT_SECTION, ChunkType.NAMESPACE_SECTION, ChunkType.CHOOSE_BLOCK, ChunkType.UNKNOWN], f"Chunk {i} should have valid type"
                assert chunk.start_line > 0, f"Chunk {i} should have valid start line"
                assert chunk.end_line >= chunk.start_line, f"Chunk {i} should have valid end line"
                assert chunk.line_count > 0, f"Chunk {i} should have line count"
                assert chunk.estimated_tokens > 0, f"Chunk {i} should have token estimate"
                assert isinstance(chunk.dependencies, list), f"Chunk {i} should have dependencies list"
                assert isinstance(chunk.metadata, dict), f"Chunk {i} should have metadata dict"
                assert isinstance(chunk.lines, list), f"Chunk {i} should have lines list"
                assert len(chunk.lines) == chunk.line_count, f"Chunk {i} line count should match lines list"
            
            # Test chunk type detection
            chunk_types = [chunk.chunk_type for chunk in chunks]
            assert ChunkType.HELPER_TEMPLATE in chunk_types or ChunkType.MAIN_TEMPLATE in chunk_types, "Should detect template types"
            
            # Test helper template detection
            helper_chunks = [c for c in chunks if c.chunk_type == ChunkType.HELPER_TEMPLATE]
            if helper_chunks:
                assert any('vmf' in (chunk.name or '') for chunk in helper_chunks), "Should detect helper templates"
            
            # Test dependency extraction
            all_deps = []
            for chunk in chunks:
                all_deps.extend(chunk.dependencies)
            
            if all_deps:
                assert any(dep.startswith('var:') for dep in all_deps), "Should extract variable dependencies"
                assert any(dep.startswith('template:') for dep in all_deps), "Should extract template dependencies"
            
        finally:
            temp_path.unlink()
    
    def test_chunker_error_handling(self):
        """Test chunker error handling"""
        chunker = XSLTChunker()
        
        # Test with non-existent file
        non_existent_path = Path("/non/existent/file.xslt")
        with pytest.raises(FileNotFoundError):
            chunker.chunk_file(non_existent_path)
        
        # Test with invalid XML
        invalid_xml = """<?xml version="1.0"?>
<xsl:stylesheet>
    <xsl:template name="test">
        <unclosed tag>
    </xsl:template>
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(invalid_xml)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            # Should handle invalid XML gracefully
            chunks = chunker.chunk_file(temp_path)
            assert isinstance(chunks, list), "Should return list even with invalid XML"
            
        finally:
            temp_path.unlink()
    
    def test_chunker_configuration(self):
        """Test chunker configuration options"""
        # Test different token limits
        test_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <result>test</result>
    </xsl:template>
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            # Test different max_tokens_per_chunk values
            for max_tokens in [500, 1000, 2000]:
                chunker = XSLTChunker(max_tokens_per_chunk=max_tokens)
                chunks = chunker.chunk_file(temp_path)
                
                assert len(chunks) > 0, f"Should create chunks with {max_tokens} token limit"
                assert chunker.max_tokens_per_chunk == max_tokens, f"Should set token limit to {max_tokens}"
                
                # Verify token limits (allowing some tolerance)
                for chunk in chunks:
                    assert chunk.estimated_tokens <= max_tokens * 1.5, f"Chunk should respect token limit (with tolerance)"
            
        finally:
            temp_path.unlink()
    
    def test_chunk_content_integrity(self):
        """Test that chunk content maintains integrity"""
        test_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="test1">
        <xsl:value-of select="'line1'"/>
        <xsl:value-of select="'line2'"/>
    </xsl:template>
    
    <xsl:template name="test2">
        <xsl:value-of select="'line3'"/>
        <xsl:value-of select="'line4'"/>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test that chunks contain expected content
            original_lines = test_content.splitlines()
            
            for chunk in chunks:
                # Verify line ranges
                assert chunk.start_line <= chunk.end_line, "Start line should be <= end line"
                assert chunk.start_line > 0, "Start line should be positive"
                assert chunk.end_line <= len(original_lines), "End line should be within file bounds"
                
                # Verify line content matches
                expected_lines = original_lines[chunk.start_line-1:chunk.end_line]
                assert len(chunk.lines) == len(expected_lines), "Chunk lines should match expected count"
                
                # Verify text content
                assert chunk.text is not None, "Chunk should have text content"
                assert len(chunk.text) > 0, "Chunk text should not be empty"
                assert chunk.text == '\n'.join(chunk.lines), "Chunk text should match joined lines"
            
        finally:
            temp_path.unlink()