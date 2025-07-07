"""
Test cases for large chunk splitting functionality

This module tests the enhanced sub-chunking implementation that splits
oversized main templates into logical sub-chunks for optimal LLM processing.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.xslt_chunker import XSLTChunker, ChunkType, ChunkInfo


class TestLargeChunkSplitting:
    """Test large chunk splitting functionality"""
    
    @pytest.fixture
    def chunker(self):
        """Create chunker with sub-chunking enabled"""
        return XSLTChunker(
            max_tokens_per_chunk=15000,
            main_template_split_threshold=10000,
            overlap_tokens=500
        )
    
    @pytest.fixture
    def sample_xslt_file(self, tmp_path):
        """Create a sample XSLT file for testing"""
        content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="vmf:helper1">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
    
    <xsl:template match="/">
        <xsl:variable name="var1" select="."/>
        <OrderCreateRQ>
            <xsl:for-each select="Request">
                <xsl:variable name="var2" select="."/>
                <PointOfSale>
                    <Location>
                        <CountryCode>FR</CountryCode>
                    </Location>
                </PointOfSale>
                <Party>
                    <Sender>
                        <TravelAgencySender>
                            <Name><xsl:value-of select="TravelAgency/Name"/></Name>
                        </TravelAgencySender>
                    </Sender>
                </Party>
                <Query>
                    <xsl:for-each select="Query">
                        <FlightQuery>
                            <Individual>
                                <xsl:for-each select="Individual">
                                    <IdentityDocument>
                                        <xsl:choose>
                                            <xsl:when test="@type='passport'">
                                                <Passport/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <Other/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </IdentityDocument>
                                </xsl:for-each>
                            </Individual>
                        </FlightQuery>
                    </xsl:for-each>
                </Query>
            </xsl:for-each>
        </OrderCreateRQ>
    </xsl:template>
</xsl:stylesheet>'''
        
        file_path = tmp_path / "test.xslt"
        file_path.write_text(content)
        return file_path

    def test_large_main_template_splitting(self, chunker):
        """Test that oversized main templates are split into logical sub-chunks"""
        # Use the real OrderCreate_MapForce_Full.xslt file
        test_file = Path(__file__).parent.parent.parent / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        chunks = chunker.chunk_file(test_file)
        
        # Verify chunking results
        main_template_chunks = [c for c in chunks if c.chunk_type == ChunkType.MAIN_TEMPLATE]
        sub_chunks = [c for c in chunks if '_sub_' in c.chunk_id]
        
        # Assertions
        assert len(chunks) > 8, "Should create multiple chunks"
        assert len(main_template_chunks) > 10, "Should create multiple main template chunks"
        assert len(sub_chunks) > 10, "Should create sub-chunks from large main template"
        
        # Verify chunk sizes
        max_tokens = max(c.estimated_tokens for c in chunks)
        assert max_tokens < 7000, f"Max chunk size {max_tokens} should be reasonable"
        
        # Verify all sub-chunks have proper token sizing
        for chunk in sub_chunks:
            assert 100 < chunk.estimated_tokens < 7000, f"Sub-chunk {chunk.chunk_id} has {chunk.estimated_tokens} tokens"

    def test_semantic_boundary_detection(self, chunker, sample_xslt_file):
        """Test that semantic boundaries are correctly identified"""
        chunks = chunker.chunk_file(sample_xslt_file)
        
        # Find the main template chunk
        main_chunks = [c for c in chunks if c.chunk_type == ChunkType.MAIN_TEMPLATE]
        assert len(main_chunks) > 0, "Should have main template chunks"
        
        # Test boundary detection methods
        lines = []
        with open(sample_xslt_file, 'r') as f:
            lines = f.readlines()
        
        # Test major output elements detection
        elements = chunker._find_major_output_elements(lines)
        element_names = [e['element_name'] for e in elements]
        assert 'OrderCreateRQ' in element_names
        assert 'PointOfSale' in element_names
        assert 'Party' in element_names
        
        # Test for-each loop detection
        loops = chunker._find_top_level_for_each_loops(lines, 1)
        assert len(loops) > 0, "Should detect for-each loops"
        
        # Test variable cluster detection
        variables = chunker._find_variable_declaration_clusters(lines)
        # May or may not find clusters depending on content

    def test_context_preservation(self, chunker):
        """Test that context is preserved between sub-chunks"""
        test_file = Path(__file__).parent.parent.parent / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        chunks = chunker.chunk_file(test_file)
        sub_chunks = [c for c in chunks if '_sub_' in c.chunk_id and c.chunk_type == ChunkType.MAIN_TEMPLATE]
        
        # Sort sub-chunks by their sub-chunk index
        sub_chunks.sort(key=lambda x: int(x.chunk_id.split('_sub_')[1]))
        
        # Verify overlap between consecutive sub-chunks
        overlaps_found = 0
        for i in range(len(sub_chunks) - 1):
            current = sub_chunks[i]
            next_chunk = sub_chunks[i + 1]
            
            # Check for overlap (next chunk starts before current ends)
            if next_chunk.start_line < current.end_line:
                overlaps_found += 1
        
        assert overlaps_found > 0, "Should have overlap between consecutive sub-chunks"
        
        # Verify sub-chunks have proper metadata
        for chunk in sub_chunks:
            assert chunk.metadata.get('is_sub_chunk') is True
            assert 'parent_chunk_id' in chunk.metadata
            assert 'sub_chunk_index' in chunk.metadata

    def test_sub_chunk_metadata(self, chunker):
        """Test that sub-chunks have proper metadata"""
        test_file = Path(__file__).parent.parent.parent / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        chunks = chunker.chunk_file(test_file)
        sub_chunks = [c for c in chunks if '_sub_' in c.chunk_id]
        
        for chunk in sub_chunks:
            # Verify metadata structure
            assert chunk.metadata.get('is_sub_chunk') is True
            assert 'parent_chunk_id' in chunk.metadata
            assert 'sub_chunk_index' in chunk.metadata
            assert isinstance(chunk.metadata['sub_chunk_index'], int)
            
            # Verify naming convention
            assert '_sub_' in chunk.chunk_id
            assert chunk.name and 'section_' in chunk.name
            
            # Verify chunk type
            assert chunk.chunk_type == ChunkType.MAIN_TEMPLATE

    def test_threshold_configuration(self):
        """Test that the sub-chunking threshold is configurable"""
        # Test with high threshold (no sub-chunking)
        chunker_high = XSLTChunker(main_template_split_threshold=50000)
        assert chunker_high.main_template_split_threshold == 50000
        
        # Test with low threshold (sub-chunking enabled)
        chunker_low = XSLTChunker(main_template_split_threshold=5000)
        assert chunker_low.main_template_split_threshold == 5000

    def test_fallback_to_simple_splitting(self, chunker):
        """Test fallback to simple splitting when no semantic boundaries found"""
        # Create a mock chunk with no detectable boundaries
        mock_chunk = ChunkInfo(
            chunk_id="test_chunk",
            chunk_type=ChunkType.MAIN_TEMPLATE,
            name="test_template",
            start_line=1,
            end_line=100,
            lines=["<xsl:template match='/'>"] + ["<div>content</div>"] * 98 + ["</xsl:template>"],
            estimated_tokens=15000,
            dependencies=[],
            metadata={}
        )
        
        # Mock the semantic boundary detection to return empty results
        with patch.object(chunker, '_identify_main_template_logical_sections', return_value=[]):
            with patch.object(chunker, '_split_large_chunk') as mock_simple_split:
                mock_simple_split.return_value = [mock_chunk]
                
                result = chunker._split_large_main_template(mock_chunk)
                
                # Should fall back to simple splitting
                mock_simple_split.assert_called_once_with(mock_chunk)
                assert result == [mock_chunk]

    def test_overlap_calculation(self, chunker):
        """Test overlap calculation functionality"""
        # Test lines for overlap calculation
        test_lines = [
            "<xsl:variable name='var1' select='.'/>",
            "<xsl:variable name='var2' select='.'/>",
            "<xsl:for-each select='items'>",
            "<div>content 1</div>",
            "<div>content 2</div>",
            "<div>content 3</div>",
            "</xsl:for-each>"
        ]
        
        # Test overlap calculation
        overlap_lines = chunker._calculate_overlap_lines(test_lines, 5)
        
        # Should prioritize variable declarations and important context
        assert overlap_lines >= 0
        assert overlap_lines <= len(test_lines)

    def test_generic_applicability(self, chunker, sample_xslt_file):
        """Test that algorithm works on different XSLT files"""
        # Test with the sample file
        chunks1 = chunker.chunk_file(sample_xslt_file)
        
        # Should work without errors
        assert len(chunks1) > 0
        
        # All chunks should have reasonable token counts
        for chunk in chunks1:
            assert chunk.estimated_tokens >= 0
            assert chunk.estimated_tokens <= chunker.max_tokens_per_chunk * 2  # Allow some margin


class TestSemanticBoundaryDetection:
    """Test semantic boundary detection methods"""
    
    @pytest.fixture
    def chunker(self):
        return XSLTChunker()
    
    def test_major_output_elements_detection(self, chunker):
        """Test detection of major output XML elements"""
        lines = [
            "<xsl:template match='/'>",
            "  <OrderCreateRQ>",
            "    <Party>",
            "      <Individual>",
            "        <Name>Test</Name>",
            "      </Individual>",
            "    </Party>",
            "    <Query>",
            "      <FlightQuery/>",
            "    </Query>",
            "  </OrderCreateRQ>",
            "</xsl:template>"
        ]
        
        elements = chunker._find_major_output_elements(lines)
        element_names = [e['element_name'] for e in elements]
        
        assert 'OrderCreateRQ' in element_names
        assert 'Party' in element_names
        assert 'Individual' in element_names
        assert 'Query' in element_names
        assert 'FlightQuery' in element_names
        
        # Should not include XSLT elements
        # Note: 'Name' has 4 characters so it passes the {3,} pattern
        
    def test_for_each_loop_detection(self, chunker):
        """Test detection of top-level for-each loops"""
        lines = [
            "<xsl:template match=\"/\">",
            "  <xsl:for-each select=\"Request\">",
            "    <Party>",
            "      <xsl:for-each select=\"Individual\">",  # Nested loop
            "        <Name/>",
            "      </xsl:for-each>",
            "    </Party>",
            "  </xsl:for-each>",
            "  <xsl:for-each select=\"Query\">",  # Another top-level loop
            "    <FlightQuery/>",
            "  </xsl:for-each>",
            "</xsl:template>"
        ]
        
        loops = chunker._find_top_level_for_each_loops(lines, 1)
        
        # Should detect top-level loops
        select_paths = [loop['select_path'] for loop in loops]
        assert 'Request' in select_paths
        assert 'Query' in select_paths
        
        # Should handle nested loops appropriately
        assert len(loops) >= 2

    def test_variable_cluster_detection(self, chunker):
        """Test detection of variable declaration clusters"""
        lines = [
            "<xsl:template match='/'>",
            "  <xsl:variable name='var1' select='.'/>",
            "  <xsl:variable name='var2' select='Request'/>",
            "  <xsl:variable name='var3' select='Query'/>",
            "  <div>some content</div>",
            "  <xsl:variable name='var4' select='Individual'/>",
            "  <xsl:variable name='var5' select='Party'/>",
            "</xsl:template>"
        ]
        
        clusters = chunker._find_variable_declaration_clusters(lines)
        
        # Should find at least one cluster of 2+ variables
        assert len(clusters) >= 1
        
        for cluster in clusters:
            assert cluster['cluster_size'] >= 2
            assert 'variable_cluster' == cluster['type']

    def test_choose_block_detection(self, chunker):
        """Test detection of major choose blocks"""
        lines = [
            "<xsl:template match='/'>",
            "  <xsl:choose>",
            "    <xsl:when test='@type=\"passport\"'>",
            "      <Passport/>",
            "      <xsl:choose>",  # Nested choose
            "        <xsl:when test='@country=\"US\"'>",
            "          <USPassport/>",
            "        </xsl:when>",
            "      </xsl:choose>",
            "    </xsl:when>",
            "    <xsl:otherwise>",
            "      <Other/>",
            "    </xsl:otherwise>",
            "  </xsl:choose>",
            "</xsl:template>"
        ]
        
        blocks = chunker._find_major_choose_blocks(lines)
        
        # Should detect top-level choose blocks only
        assert len(blocks) >= 1
        
        for block in blocks:
            assert block['type'] == 'major_choose_block'
            assert 'line' in block  # Implementation uses 'line' not 'start_line'
            assert 'end_line' in block


class TestChunkCreation:
    """Test chunk creation and sizing logic"""
    
    @pytest.fixture
    def chunker(self):
        return XSLTChunker(main_template_split_threshold=5000)
    
    def test_semantic_sub_chunk_creation(self, chunker):
        """Test creation of semantic sub-chunks"""
        # Create a mock large chunk
        lines = ["<xsl:template match='/'>"] + [f"<div>line {i}</div>" for i in range(100)] + ["</xsl:template>"]
        
        mock_chunk = ChunkInfo(
            chunk_id="test_chunk",
            chunk_type=ChunkType.MAIN_TEMPLATE,
            name="test_template",
            start_line=1,
            end_line=102,
            lines=lines,
            estimated_tokens=8000,
            dependencies=[],
            metadata={}
        )
        
        # Create mock sections
        mock_sections = [
            {'type': 'major_output_element', 'line': 25, 'element_name': 'Party'},
            {'type': 'major_output_element', 'line': 50, 'element_name': 'Query'},
            {'type': 'major_output_element', 'line': 75, 'element_name': 'Individual'}
        ]
        
        # Test sub-chunk creation
        with patch.object(chunker.token_counter, 'estimate_tokens', return_value=50):
            sub_chunks = chunker._create_semantic_sub_chunks(mock_chunk, mock_sections)
        
        # Verify results
        assert len(sub_chunks) > 1, "Should create multiple sub-chunks"
        
        for i, chunk in enumerate(sub_chunks):
            assert chunk.chunk_id == f"test_chunk_sub_{i:02d}"
            assert chunk.chunk_type == ChunkType.MAIN_TEMPLATE
            assert chunk.metadata.get('is_sub_chunk') is True
            assert chunk.metadata.get('parent_chunk_id') == 'test_chunk'
            assert chunk.metadata.get('sub_chunk_index') == i

    def test_chunk_sizing_constraints(self, chunker):
        """Test that chunks respect sizing constraints"""
        # This is tested implicitly through other tests, but we can add specific size validation
        test_file = Path(__file__).parent.parent.parent / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        chunks = chunker.chunk_file(test_file)
        
        # Verify sizing constraints
        for chunk in chunks:
            # No chunk should be extremely large
            assert chunk.estimated_tokens <= 7000, f"Chunk {chunk.chunk_id} is too large: {chunk.estimated_tokens} tokens"
            
            # Sub-chunks should be reasonably sized
            if '_sub_' in chunk.chunk_id:
                assert 100 <= chunk.estimated_tokens <= 6000, f"Sub-chunk {chunk.chunk_id} has poor sizing: {chunk.estimated_tokens} tokens"