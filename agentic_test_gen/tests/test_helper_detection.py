#!/usr/bin/env python3
"""
Test helper template detection functionality
"""

import pytest
import re
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType, DEFAULT_HELPER_PATTERNS


class TestHelperDetection:
    """Test helper template detection logic"""
    
    def test_helper_template_pattern(self):
        """Test helper template regex pattern with default MapForce patterns"""
        chunker = XSLTChunker()
        
        # Test cases from the debug file
        test_cases = [
            ("vmf:vmf1_inputtoresult", True, "Helper with namespace"),
            ("vmf:vmf2_inputtoresult", True, "Helper with namespace #2"),
            ("vmf:vmf3_inputtoresult", True, "Helper with namespace #3"),
            ("vmf:vmf4_inputtoresult", True, "Helper with namespace #4"),
            ("vmf1_helper", True, "Helper without namespace"),
            ("vmf2_transform", True, "Helper without namespace #2"),
            ("regular_template", False, "Regular template name"),
            ("match:/", False, "Match template"),
            ("helper_function", False, "Non-vmf helper"),
        ]
        
        for name, should_match, description in test_cases:
            match = chunker._is_helper_template(name)
            assert bool(match) == should_match, f"Pattern failed for {description}: {name}"
    
    def test_template_classification(self):
        """Test template type classification"""
        chunker = XSLTChunker()
        
        # Test cases from the debug file
        test_cases = [
            ("vmf:vmf1_inputtoresult", ChunkType.HELPER_TEMPLATE, "Helper with namespace"),
            ("vmf:vmf2_inputtoresult", ChunkType.HELPER_TEMPLATE, "Helper with namespace #2"),
            ("vmf:vmf3_inputtoresult", ChunkType.HELPER_TEMPLATE, "Helper with namespace #3"),
            ("vmf:vmf4_inputtoresult", ChunkType.HELPER_TEMPLATE, "Helper with namespace #4"),
            ("match:/", ChunkType.MAIN_TEMPLATE, "Root match template"),
            ("regular_template", ChunkType.MAIN_TEMPLATE, "Regular named template"),
        ]
        
        for name, expected_type, description in test_cases:
            template_content = f'<xsl:template name="{name}">'
            template_type = chunker._classify_template_type(name, template_content)
            assert template_type == expected_type, f"Classification failed for {description}: {name}"
    
    def test_helper_template_detection_in_context(self):
        """Test helper template detection in full XSLT context"""
        chunker = XSLTChunker()
        
        # Test with realistic XSLT content
        xslt_content = """<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- This should be detected as a helper template -->
    <xsl:template name="vmf:vmf1_inputtoresult">
        <xsl:param name="input"/>
        <xsl:value-of select="$input"/>
    </xsl:template>
    
    <!-- This should be detected as a main template -->
    <xsl:template match="/">
        <result>
            <xsl:call-template name="vmf:vmf1_inputtoresult">
                <xsl:with-param name="input" select="'test'"/>
            </xsl:call-template>
        </result>
    </xsl:template>
    
    <!-- This should be detected as a helper template -->
    <xsl:template name="vmf2_transform">
        <xsl:param name="data"/>
        <xsl:value-of select="upper-case($data)"/>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        lines = xslt_content.split('\n')
        helper_templates = []
        main_templates = []
        
        for i, line in enumerate(lines):
            if 'xsl:template' in line and ('name=' in line or 'match=' in line):
                # Extract template name or match pattern
                if 'name=' in line:
                    name_match = re.search(r'name="([^"]+)"', line)
                    if name_match:
                        name = name_match.group(1)
                        template_type = chunker._classify_template_type(name, line)
                        if template_type == ChunkType.HELPER_TEMPLATE:
                            helper_templates.append(name)
                        else:
                            main_templates.append(name)
                elif 'match=' in line:
                    match_match = re.search(r'match="([^"]+)"', line)
                    if match_match:
                        match_pattern = match_match.group(1)
                        template_type = chunker._classify_template_type(match_pattern, line)
                        if template_type == ChunkType.HELPER_TEMPLATE:
                            helper_templates.append(match_pattern)
                        else:
                            main_templates.append(match_pattern)
        
        # Verify detection results
        assert "vmf:vmf1_inputtoresult" in helper_templates
        assert "vmf2_transform" in helper_templates
        assert "/" in main_templates
        assert len(helper_templates) == 2
        assert len(main_templates) == 1
    
    def test_helper_pattern_edge_cases(self):
        """Test edge cases in helper template detection"""
        chunker = XSLTChunker()
        
        edge_cases = [
            # Valid helpers (must have digits after vmf according to pattern)
            ("vmf1_util", True, "Numbered helper"),
            ("vmf99_processor", True, "Multi-digit numbered helper"),
            ("vmf:vmf1_helper", True, "Namespace with numbered helper"),
            
            # Invalid helpers (should be main templates)
            ("vmf:function_name", False, "Namespace without digit (not helper pattern)"),
            ("vmf", False, "Just namespace prefix"),
            ("vmf:", False, "Empty namespace"),
            ("not_vmf_template", False, "Contains vmf but not at start"),
            ("template_vmf", False, "vmf at end"),
            ("match://element", False, "Match pattern"),
        ]
        
        for name, should_be_helper, description in edge_cases:
            if name:  # Skip empty string for _classify_template_type
                template_content = f'<xsl:template name="{name}">'
                template_type = chunker._classify_template_type(name, template_content)
                is_helper = template_type == ChunkType.HELPER_TEMPLATE
                assert is_helper == should_be_helper, f"Edge case failed for {description}: {name}"
    
    def test_template_with_attributes(self):
        """Test template detection with various attributes"""
        chunker = XSLTChunker()
        
        template_variants = [
            '<xsl:template name="vmf:vmf1_inputtoresult">',
            '<xsl:template name="vmf:vmf1_inputtoresult" priority="1">',
            '<xsl:template name="vmf:vmf1_inputtoresult" mode="transform">',
            '  <xsl:template name="vmf:vmf1_inputtoresult">',  # With indentation
            '\t<xsl:template name="vmf:vmf1_inputtoresult">',  # With tab
        ]
        
        for template_line in template_variants:
            name_match = re.search(r'name="([^"]+)"', template_line)
            assert name_match, f"Failed to extract name from: {template_line}"
            
            name = name_match.group(1)
            template_type = chunker._classify_template_type(name, template_line)
            assert template_type == ChunkType.HELPER_TEMPLATE, f"Failed to classify helper: {template_line}"
    
    def test_regex_pattern_compilation(self):
        """Test that the helper template regex patterns compile correctly"""
        chunker = XSLTChunker()
        
        # Test that all patterns compile correctly
        for pattern in chunker.helper_patterns:
            compiled_pattern = re.compile(pattern)
            assert compiled_pattern is not None
        
        # Test default MapForce pattern against known good cases
        assert chunker._is_helper_template("vmf:vmf1_inputtoresult")
        assert chunker._is_helper_template("vmf1_helper")
        assert not chunker._is_helper_template("regular_template")
        assert not chunker._is_helper_template("match:/")
    
    def test_configurable_helper_patterns(self):
        """Test configurable helper patterns functionality"""
        # Test 1: Default MapForce patterns
        chunker_default = XSLTChunker()
        assert chunker_default.helper_patterns == [DEFAULT_HELPER_PATTERNS['mapforce']]
        assert chunker_default._is_helper_template("vmf:vmf1_inputtoresult")
        assert chunker_default._is_helper_template("vmf2_helper")
        assert not chunker_default._is_helper_template("f:func1")
        
        # Test 2: Saxon patterns
        chunker_saxon = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['saxon']])
        assert chunker_saxon._is_helper_template("f:func1")
        assert chunker_saxon._is_helper_template("func2")
        assert not chunker_saxon._is_helper_template("vmf:vmf1_inputtoresult")
        
        # Test 3: Custom patterns
        chunker_custom = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['custom']])
        assert chunker_custom._is_helper_template("util:helper_name")
        assert chunker_custom._is_helper_template("helper_function")
        assert not chunker_custom._is_helper_template("vmf:vmf1_inputtoresult")
        
        # Test 4: Multiple patterns
        chunker_multi = XSLTChunker(helper_patterns=[
            DEFAULT_HELPER_PATTERNS['mapforce'],
            DEFAULT_HELPER_PATTERNS['saxon']
        ])
        assert chunker_multi._is_helper_template("vmf:vmf1_inputtoresult")
        assert chunker_multi._is_helper_template("f:func1")
        assert not chunker_multi._is_helper_template("util:helper_name")
        
        # Test 5: Custom regex patterns
        custom_regex = [r'my_helper_\d+', r'(?:ns:)?special_func']
        chunker_custom_regex = XSLTChunker(helper_patterns=custom_regex)
        assert chunker_custom_regex._is_helper_template("my_helper_1")
        assert chunker_custom_regex._is_helper_template("ns:special_func")
        assert chunker_custom_regex._is_helper_template("special_func")
        assert not chunker_custom_regex._is_helper_template("vmf:vmf1_inputtoresult")
    
    def test_template_classification_with_custom_patterns(self):
        """Test template classification with custom patterns"""
        # Test with Saxon patterns
        chunker_saxon = XSLTChunker(helper_patterns=[DEFAULT_HELPER_PATTERNS['saxon']])
        
        test_cases = [
            ("f:func1", ChunkType.HELPER_TEMPLATE),
            ("func2", ChunkType.HELPER_TEMPLATE),
            ("match:/", ChunkType.MAIN_TEMPLATE),
            ("regular_template", ChunkType.MAIN_TEMPLATE),
            ("vmf:vmf1_inputtoresult", ChunkType.MAIN_TEMPLATE),  # Should NOT be helper with Saxon patterns
        ]
        
        for name, expected_type in test_cases:
            result = chunker_saxon._classify_template_type(name, f'<xsl:template name="{name}">')
            assert result == expected_type, f"Classification failed for {name}: expected {expected_type}, got {result}"
    
    def test_default_patterns_constant(self):
        """Test that default patterns are correctly defined"""
        assert 'mapforce' in DEFAULT_HELPER_PATTERNS
        assert 'saxon' in DEFAULT_HELPER_PATTERNS
        assert 'custom' in DEFAULT_HELPER_PATTERNS
        assert 'generic' in DEFAULT_HELPER_PATTERNS
        
        # Test that all patterns are valid regex
        for pattern_name, pattern in DEFAULT_HELPER_PATTERNS.items():
            try:
                re.compile(pattern)
            except re.error:
                pytest.fail(f"Invalid regex pattern for {pattern_name}: {pattern}")
    
    def test_backward_compatibility(self):
        """Test that existing code continues to work without changes"""
        # Old way (should still work)
        chunker_old = XSLTChunker()
        
        # Test that it still detects MapForce helpers by default
        assert chunker_old._is_helper_template("vmf:vmf1_inputtoresult")
        assert chunker_old._is_helper_template("vmf2_helper")
        assert not chunker_old._is_helper_template("regular_template")
        
        # Test template classification works the same
        assert chunker_old._classify_template_type("vmf:vmf1_inputtoresult", "") == ChunkType.HELPER_TEMPLATE
        assert chunker_old._classify_template_type("regular_template", "") == ChunkType.MAIN_TEMPLATE