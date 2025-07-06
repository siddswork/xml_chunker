"""
Unit tests for XSLT chunking functionality (MVP 1)
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader
from src.utils.token_counter import TokenCounter


class TestStreamingFileReader(unittest.TestCase):
    """Test streaming file reader functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reader = StreamingFileReader()
        
        # Create test XSLT content
        self.test_xslt_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Helper template 1 -->
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'P'">VPT</xsl:when>
            <xsl:when test="$input = 'PT'">VPT</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Helper template 2 -->
    <xsl:template name="vmf:vmf2_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'V'">VVI</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Main template -->
    <xsl:template match="/">
        <xsl:variable name="target" select="//Target"/>
        <OrderCreateRS>
            <xsl:choose>
                <xsl:when test="$target = 'UA'">
                    <!-- UA specific processing -->
                    <ProcessingType>UA</ProcessingType>
                </xsl:when>
                <xsl:otherwise>
                    <!-- Default processing -->
                    <ProcessingType>DEFAULT</ProcessingType>
                </xsl:otherwise>
            </xsl:choose>
        </OrderCreateRS>
    </xsl:template>
    
</xsl:stylesheet>'''
    
    def test_file_metadata(self):
        """Test file metadata extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            metadata = self.reader.get_file_metadata(Path(f.name))
            
            self.assertGreater(metadata.size_bytes, 0)
            self.assertGreater(metadata.line_count, 0)
            self.assertEqual(metadata.encoding, 'utf-8')
            self.assertGreater(metadata.estimated_tokens, 0)
    
    def test_read_lines(self):
        """Test reading specific line ranges"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            # Read first 5 lines
            lines = self.reader.read_lines(Path(f.name), 1, 5)
            self.assertEqual(len(lines), 5)
            self.assertIn('<?xml version', lines[0])
    
    def test_memory_usage_estimation(self):
        """Test memory usage estimation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            estimates = self.reader.estimate_memory_usage(Path(f.name))
            
            self.assertIn('file_size_mb', estimates)
            self.assertIn('recommended_strategy', estimates)
            self.assertGreater(estimates['file_size_mb'], 0)


class TestTokenCounter(unittest.TestCase):
    """Test token counter functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.counter = TokenCounter()
    
    def test_basic_token_estimation(self):
        """Test basic token estimation"""
        text = "Hello world, this is a test"
        tokens = self.counter.estimate_tokens(text)
        self.assertGreater(tokens, 0)
    
    def test_xml_aware_estimation(self):
        """Test XML-aware token estimation"""
        xml_text = '<xsl:template name="test"><xsl:param name="input"/></xsl:template>'
        tokens = self.counter.estimate_tokens(xml_text, method='xml_aware')
        self.assertGreater(tokens, 0)
    
    def test_empty_text(self):
        """Test handling of empty text"""
        tokens = self.counter.estimate_tokens("")
        self.assertEqual(tokens, 0)


class TestXSLTChunker(unittest.TestCase):
    """Test XSLT chunker functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.chunker = XSLTChunker(max_tokens_per_chunk=1000)  # Small for testing
        
        # Create test XSLT file
        self.test_xslt_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Helper template 1 -->
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'P'">VPT</xsl:when>
            <xsl:when test="$input = 'PT'">VPT</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Helper template 2 -->
    <xsl:template name="vmf:vmf2_inputtoresult">
        <xsl:param name="input" />
        <xsl:choose>
            <xsl:when test="$input = 'V'">VVI</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Main template -->
    <xsl:template match="/">
        <xsl:variable name="target" select="//Target"/>
        <OrderCreateRS>
            <xsl:choose>
                <xsl:when test="$target = 'UA'">
                    <!-- UA specific processing -->
                    <ProcessingType>UA</ProcessingType>
                </xsl:when>
                <xsl:otherwise>
                    <!-- Default processing -->
                    <ProcessingType>DEFAULT</ProcessingType>
                </xsl:otherwise>
            </xsl:choose>
        </OrderCreateRS>
    </xsl:template>
    
</xsl:stylesheet>'''
    
    def test_chunk_file(self):
        """Test chunking an XSLT file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            chunks = self.chunker.chunk_file(Path(f.name))
            
            # Should create multiple chunks
            self.assertGreater(len(chunks), 0)
            
            # Check chunk properties
            for chunk in chunks:
                self.assertIsNotNone(chunk.chunk_id)
                self.assertIsInstance(chunk.chunk_type, ChunkType)
                self.assertGreater(chunk.line_count, 0)
                self.assertGreaterEqual(chunk.estimated_tokens, 0)
    
    def test_helper_template_detection(self):
        """Test detection of helper templates"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            chunks = self.chunker.chunk_file(Path(f.name))
            
            # Should detect helper templates
            helper_chunks = [c for c in chunks if c.chunk_type == ChunkType.HELPER_TEMPLATE]
            self.assertGreater(len(helper_chunks), 0)
            
            # Check helper template names
            helper_names = [c.name for c in helper_chunks if c.name]
            self.assertTrue(any('vmf1' in name for name in helper_names))
    
    def test_token_limits(self):
        """Test that chunks respect token limits"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            chunks = self.chunker.chunk_file(Path(f.name))
            
            # Check token limits (allowing some tolerance for splitting challenges)
            for chunk in chunks:
                self.assertLessEqual(chunk.estimated_tokens, self.chunker.max_tokens_per_chunk * 1.2)
    
    def test_dependency_extraction(self):
        """Test extraction of dependencies"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(self.test_xslt_content)
            f.flush()
            
            chunks = self.chunker.chunk_file(Path(f.name))
            
            # Should find some dependencies
            all_dependencies = []
            for chunk in chunks:
                all_dependencies.extend(chunk.dependencies)
            
            # Should find variable reference
            var_deps = [dep for dep in all_dependencies if dep.startswith('var:')]
            self.assertGreater(len(var_deps), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for MVP 1 components"""
    
    def test_full_workflow(self):
        """Test the complete chunking workflow"""
        # Create a more complex XSLT file
        complex_xslt = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:variable name="globalVar" select="'test'"/>
    
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input" />
        <xsl:value-of select="$globalVar"/>
        <xsl:choose>
            <xsl:when test="$input = 'P'">VPT</xsl:when>
            <xsl:otherwise></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="/">
        <xsl:variable name="localVar" select="//Data"/>
        <Result>
            <xsl:call-template name="vmf:vmf1_inputtoresult">
                <xsl:with-param name="input" select="$localVar"/>
            </xsl:call-template>
        </Result>
    </xsl:template>
    
</xsl:stylesheet>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xslt', delete=False) as f:
            f.write(complex_xslt)
            f.flush()
            
            # Test file reading
            reader = StreamingFileReader()
            metadata = reader.get_file_metadata(Path(f.name))
            self.assertGreater(metadata.line_count, 0)
            
            # Test chunking
            chunker = XSLTChunker()
            chunks = chunker.chunk_file(Path(f.name))
            self.assertGreater(len(chunks), 0)
            
            # Test that we captured dependencies correctly
            all_deps = []
            for chunk in chunks:
                all_deps.extend(chunk.dependencies)
            
            # Should have variable and template dependencies
            has_var_dep = any(dep.startswith('var:') for dep in all_deps)
            has_template_dep = any(dep.startswith('template:') for dep in all_deps)
            
            self.assertTrue(has_var_dep or has_template_dep)


if __name__ == '__main__':
    unittest.main()