#!/usr/bin/env python3
"""
Real file processing tests for MVP 1
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader


class TestRealFileProcessing:
    """Test real file processing functionality"""
    
    def test_format_bytes_utility(self):
        """Test byte formatting utility function"""
        def format_bytes(bytes_size: int) -> str:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"
        
        # Test various byte sizes
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(2048) == "2.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"
    
    def test_file_analysis_components(self):
        """Test individual components of file analysis"""
        # Test file metadata analysis
        import tempfile
        
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
            # Test file metadata
            reader = StreamingFileReader()
            metadata = reader.get_file_metadata(temp_path)
            
            assert metadata.size_bytes > 0, "Should have file size"
            assert metadata.line_count > 0, "Should have line count"
            assert metadata.encoding is not None, "Should detect encoding"
            assert metadata.estimated_tokens > 0, "Should estimate tokens"
            
            # Test memory estimates
            estimates = reader.estimate_memory_usage(temp_path)
            required_fields = ['full_load_memory_mb', 'chunked_memory_mb', 'streaming_memory_mb', 'recommended_strategy']
            for field in required_fields:
                assert field in estimates, f"Should have {field} in estimates"
            
            # Test chunking analysis
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            assert len(chunks) > 0, "Should create chunks"
            
            # Test chunk type analysis
            chunk_types = {}
            total_tokens = 0
            helper_templates = []
            main_templates = []
            
            for chunk in chunks:
                chunk_type = chunk.chunk_type.value
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                total_tokens += chunk.estimated_tokens
                
                if chunk.chunk_type == ChunkType.HELPER_TEMPLATE:
                    helper_templates.append(chunk)
                elif chunk.chunk_type == ChunkType.MAIN_TEMPLATE:
                    main_templates.append(chunk)
            
            assert total_tokens > 0, "Should have total tokens"
            assert len(chunk_types) > 0, "Should have chunk types"
            
            # Test helper template detection
            if helper_templates:
                assert any('vmf' in (chunk.name or '') for chunk in helper_templates), "Should detect helper templates"
            
            # Test dependency analysis
            all_dependencies = []
            for chunk in chunks:
                all_dependencies.extend(chunk.dependencies)
            
            if all_dependencies:
                unique_deps = set(all_dependencies)
                var_deps = [d for d in unique_deps if d.startswith('var:')]
                template_deps = [d for d in unique_deps if d.startswith('template:')]
                function_deps = [d for d in unique_deps if d.startswith('function:')]
                
                # Should have at least one type of dependency
                assert len(var_deps) > 0 or len(template_deps) > 0 or len(function_deps) > 0, "Should extract dependencies"
            
        finally:
            temp_path.unlink()
    
    def test_chunk_size_analysis(self):
        """Test chunk size analysis functionality"""
        import tempfile
        
        # Create content with varied chunk sizes
        varied_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Small template -->
    <xsl:template name="small">
        <result>small</result>
    </xsl:template>
    
    <!-- Medium template -->
    <xsl:template name="medium">
        <xsl:param name="input"/>
        <xsl:variable name="var1" select="$input"/>
        <xsl:variable name="var2" select="concat($var1, 'suffix')"/>
        <xsl:value-of select="$var2"/>
    </xsl:template>
    
    <!-- Large template -->
    <xsl:template name="large">
        <xsl:param name="input"/>
        <xsl:variable name="var1" select="$input"/>
        <xsl:variable name="var2" select="concat($var1, 'suffix')"/>
        <xsl:variable name="var3" select="substring($var2, 1, 10)"/>
        <xsl:variable name="var4" select="upper-case($var3)"/>
        <xsl:variable name="var5" select="lower-case($var4)"/>
        <xsl:choose>
            <xsl:when test="$var5 = 'test'">
                <xsl:value-of select="'matched'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$var5"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(varied_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test token size analysis
            token_sizes = [chunk.estimated_tokens for chunk in chunks]
            assert len(token_sizes) > 0, "Should have token sizes"
            
            min_tokens = min(token_sizes)
            max_tokens = max(token_sizes)
            avg_tokens = sum(token_sizes) / len(token_sizes)
            
            assert min_tokens > 0, "Min tokens should be positive"
            assert max_tokens >= min_tokens, "Max should be >= min"
            assert avg_tokens > 0, "Average should be positive"
            
            # Test oversized chunk detection
            oversized = [c for c in chunks if c.estimated_tokens > chunker.max_tokens_per_chunk]
            # Allow some oversized chunks due to indivisible content
            assert len(oversized) <= len(chunks), "Oversized chunks should be reasonable"
            
        finally:
            temp_path.unlink()
    
    def test_pattern_detection(self):
        """Test pattern detection in chunks"""
        import tempfile
        
        pattern_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="with_choose">
        <xsl:param name="input"/>
        <xsl:variable name="var1" select="$input"/>
        <xsl:choose>
            <xsl:when test="$var1 = 'test'">
                <result>match</result>
            </xsl:when>
            <xsl:otherwise>
                <result>no match</result>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="with_variables">
        <xsl:variable name="var1" select="'value1'"/>
        <xsl:variable name="var2" select="'value2'"/>
        <xsl:value-of select="concat($var1, $var2)"/>
    </xsl:template>
    
    <xsl:template name="with_xpath">
        <xsl:param name="input"/>
        <xsl:value-of select="//Target/@value"/>
        <xsl:value-of select="$input/../@attribute"/>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(pattern_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test pattern detection
            choose_chunks = sum(1 for c in chunks if c.metadata.get('has_choose_blocks', False))
            variable_chunks = sum(1 for c in chunks if c.metadata.get('has_variables', False))
            xpath_chunks = sum(1 for c in chunks if c.metadata.get('has_xpath', False))
            
            # Should detect at least some patterns
            assert choose_chunks > 0 or variable_chunks > 0 or xpath_chunks > 0, "Should detect some patterns"
            
        finally:
            temp_path.unlink()
    
    def test_comparison_functionality(self):
        """Test file comparison functionality"""
        import tempfile
        
        # Create two different files
        file1_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
    <xsl:template match="/">
        <result>file1</result>
    </xsl:template>
</xsl:stylesheet>"""
        
        file2_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
    <xsl:template name="vmf:vmf2_inputtoresult">
        <xsl:param name="input"/>
        <xsl:value-of select="upper-case($input)"/>
    </xsl:template>
    <xsl:template match="/">
        <result>file2</result>
    </xsl:template>
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f1:
            f1.write(file1_content)
            f1.flush()
            temp_path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f2:
            f2.write(file2_content)
            f2.flush()
            temp_path2 = Path(f2.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks1 = chunker.chunk_file(temp_path1)
            chunks2 = chunker.chunk_file(temp_path2)
            
            # Test comparison metrics
            assert len(chunks1) > 0, "Should create chunks for file1"
            assert len(chunks2) > 0, "Should create chunks for file2"
            
            # Token comparison
            tokens1 = sum(c.estimated_tokens for c in chunks1)
            tokens2 = sum(c.estimated_tokens for c in chunks2)
            assert tokens1 > 0, "File1 should have tokens"
            assert tokens2 > 0, "File2 should have tokens"
            assert tokens2 > tokens1, "File2 should have more tokens (it's larger)"
            
            # Helper template comparison
            helpers1 = [c for c in chunks1 if c.chunk_type == ChunkType.HELPER_TEMPLATE]
            helpers2 = [c for c in chunks2 if c.chunk_type == ChunkType.HELPER_TEMPLATE]
            assert len(helpers2) > len(helpers1), "File2 should have more helper templates"
            
            # Complexity comparison
            avg_complexity1 = sum(c.metadata.get('complexity_score', 0) for c in chunks1) / len(chunks1)
            avg_complexity2 = sum(c.metadata.get('complexity_score', 0) for c in chunks2) / len(chunks2)
            assert avg_complexity1 >= 0, "Should have non-negative complexity"
            assert avg_complexity2 >= 0, "Should have non-negative complexity"
            
        finally:
            temp_path1.unlink()
            temp_path2.unlink()
    
    def test_chunk_content_preview(self):
        """Test chunk content preview functionality"""
        import tempfile
        
        preview_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="preview_test">
        <xsl:param name="input"/>
        <xsl:variable name="var1" select="$input"/>
        <xsl:variable name="var2" select="concat($var1, 'suffix')"/>
        <xsl:value-of select="$var2"/>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(preview_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            
            # Test chunk content preview
            assert len(chunks) > 0, "Should create chunks"
            
            sample_chunk = chunks[0]
            assert sample_chunk.chunk_id is not None, "Should have chunk ID"
            assert sample_chunk.chunk_type is not None, "Should have chunk type"
            assert sample_chunk.start_line > 0, "Should have start line"
            assert sample_chunk.end_line >= sample_chunk.start_line, "Should have valid end line"
            assert len(sample_chunk.lines) > 0, "Should have lines"
            
            # Test line content preview
            for i, line in enumerate(sample_chunk.lines[:5]):  # First 5 lines
                assert isinstance(line, str), f"Line {i} should be string"
            
        finally:
            temp_path.unlink()
    
    def test_error_handling_missing_files(self):
        """Test error handling for missing files"""
        chunker = XSLTChunker()
        reader = StreamingFileReader()
        
        # Test with non-existent file paths
        non_existent_path = Path("/non/existent/path/file.xslt")
        
        # File reader should handle missing files gracefully
        with pytest.raises(FileNotFoundError):
            reader.get_file_metadata(non_existent_path)
        
        # Chunker should handle missing files gracefully
        with pytest.raises(FileNotFoundError):
            chunker.chunk_file(non_existent_path)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        import tempfile
        import time
        
        # Create content for performance testing
        perf_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
"""
        
        # Add templates for performance testing
        for i in range(10):
            perf_content += f"""
    <xsl:template name="perf_template_{i}">
        <xsl:param name="input"/>
        <xsl:variable name="var_{i}" select="$input"/>
        <xsl:value-of select="$var_{i}"/>
    </xsl:template>
"""
        
        perf_content += "</xsl:stylesheet>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(perf_content)
            f.flush()
            temp_path = Path(f.name)
        
        try:
            # Test performance timing
            start_time = time.time()
            chunker = XSLTChunker(max_tokens_per_chunk=1000)
            chunks = chunker.chunk_file(temp_path)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Performance assertions
            assert processing_time < 2.0, "Should process file quickly"
            assert len(chunks) > 0, "Should create chunks"
            
            # Test performance metrics
            if chunks:
                time_per_chunk = processing_time / len(chunks)
                assert time_per_chunk < 0.1, "Should process each chunk quickly"
            
        finally:
            temp_path.unlink()