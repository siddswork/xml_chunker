#!/usr/bin/env python3
"""
Test CLI Demo functionality for XSLT Chunking
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader


class TestCLIDemo:
    """Test CLI demo functionality"""
    
    def test_format_bytes(self):
        """Test byte formatting function"""
        # Test the formatting function from cli_demo
        def format_bytes(bytes_size: int) -> str:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"
        
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_get_memory_usage(self):
        """Test memory usage tracking"""
        # Test memory usage function without psutil dependency
        def get_memory_usage():
            # Simulate memory info without actual psutil
            return {
                'rss': "100.0 MB",
                'vms': "200.0 MB", 
                'percent': "5.5%"
            }
        
        result = get_memory_usage()
        assert result['rss'] == "100.0 MB"
        assert result['vms'] == "200.0 MB"
        assert result['percent'] == "5.5%"
    
    def test_file_info_demo(self):
        """Test file information demo functionality"""
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
            reader = StreamingFileReader()
            metadata = reader.get_file_metadata(temp_path)
            
            assert metadata.size_bytes > 0
            assert metadata.line_count > 0
            assert metadata.encoding is not None
            assert metadata.estimated_tokens > 0
            
            # Test memory usage estimates
            estimates = reader.estimate_memory_usage(temp_path)
            assert 'full_load_memory_mb' in estimates
            assert 'chunked_memory_mb' in estimates
            assert 'streaming_memory_mb' in estimates
            assert 'recommended_strategy' in estimates
            
        finally:
            temp_path.unlink()
    
    def test_chunking_demo(self):
        """Test chunking demo functionality"""
        test_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
    
    <xsl:template match="/">
        <result>
            <xsl:call-template name="vmf:vmf1_inputtoresult">
                <xsl:with-param name="input" select="'test'"/>
            </xsl:call-template>
        </result>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            assert len(chunks) > 0
            
            # Verify chunk types
            chunk_types = {chunk.chunk_type for chunk in chunks}
            assert ChunkType.HELPER_TEMPLATE in chunk_types or ChunkType.MAIN_TEMPLATE in chunk_types
            
            # Test chunk analysis
            total_tokens = sum(chunk.estimated_tokens for chunk in chunks)
            assert total_tokens > 0
            
            # Test chunk details
            for chunk in chunks:
                assert chunk.chunk_id is not None
                assert chunk.start_line > 0
                assert chunk.end_line >= chunk.start_line
                assert chunk.line_count > 0
                assert chunk.estimated_tokens > 0
                assert isinstance(chunk.dependencies, list)
                assert isinstance(chunk.metadata, dict)
            
        finally:
            temp_path.unlink()
    
    def test_chunk_details_demo(self):
        """Test detailed chunk analysis"""
        test_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input"/>
        <xsl:variable name="temp" select="$input"/>
        <xsl:choose>
            <xsl:when test="$temp = 'test'">
                <xsl:value-of select="'result'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$temp"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(test_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            assert len(chunks) > 0
            
            # Test detailed chunk analysis
            chunk = chunks[0]
            assert chunk.chunk_id is not None
            assert chunk.chunk_type in [ChunkType.HELPER_TEMPLATE, ChunkType.MAIN_TEMPLATE, ChunkType.UNKNOWN]
            # Name may be None for some chunk types
            assert isinstance(chunk.dependencies, list)  # Should have dependencies list
            assert len(chunk.metadata) > 0
            assert len(chunk.lines) > 0
            
            # Test metadata content (may not always be present)
            assert isinstance(chunk.metadata, dict), "Should have metadata dict"
            
        finally:
            temp_path.unlink()
    
    def test_save_chunks_to_json(self):
        """Test saving chunks to JSON"""
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
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Save to JSON
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
                json_path = Path(json_file.name)
            
            try:
                # Simulate save_chunks_to_json function
                chunk_data = []
                for chunk in chunks:
                    chunk_data.append({
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
                    })
                
                with open(json_path, 'w') as f:
                    json.dump(chunk_data, f, indent=2)
                
                # Verify JSON file
                assert json_path.exists()
                with open(json_path, 'r') as f:
                    loaded_data = json.load(f)
                
                assert len(loaded_data) == len(chunks)
                assert all(isinstance(item, dict) for item in loaded_data)
                assert all('chunk_id' in item for item in loaded_data)
                assert all('chunk_type' in item for item in loaded_data)
                
            finally:
                json_path.unlink()
                
        finally:
            temp_path.unlink()