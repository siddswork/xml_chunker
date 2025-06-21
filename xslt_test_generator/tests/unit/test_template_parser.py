"""Unit tests for XSLT Template Parser."""

import pytest
from pathlib import Path
import tempfile
import os

from xslt_test_generator.analysis.template_parser import XSLTTemplateParser, XSLTTemplate, XSLTVariable


class TestXSLTTemplateParser:
    """Test cases for XSLT Template Parser."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return XSLTTemplateParser()
    
    @pytest.fixture
    def sample_xslt_file(self, temp_dir):
        """Create sample XSLT file for testing."""
        xslt_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Global variable -->
    <xsl:variable name="defaultTitle" select="'Sample Document'"/>
    <xsl:param name="debugMode" select="false()"/>
    
    <!-- Root template -->
    <xsl:template match="/">
        <html>
            <head>
                <title><xsl:value-of select="$defaultTitle"/></title>
            </head>
            <body>
                <xsl:apply-templates select="//item"/>
            </body>
        </html>
    </xsl:template>
    
    <!-- Item template with conditional logic -->
    <xsl:template match="item" mode="detailed">
        <xsl:variable name="priority" select="@priority"/>
        <div class="item">
            <h3><xsl:value-of select="@name"/></h3>
            <xsl:if test="@priority = 'high'">
                <span class="priority-high">HIGH PRIORITY</span>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="@type = 'urgent'">
                    <xsl:call-template name="urgentItemTemplate">
                        <xsl:with-param name="item" select="."/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="@type = 'normal'">
                    <p><xsl:value-of select="description"/></p>
                </xsl:when>
                <xsl:otherwise>
                    <p>Unknown item type</p>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>
    
    <!-- Named template for urgent items -->
    <xsl:template name="urgentItemTemplate">
        <xsl:param name="item"/>
        <div class="urgent">
            <p><strong>URGENT:</strong> <xsl:value-of select="$item/description"/></p>
            <xsl:if test="$item/deadline">
                <p class="deadline">Deadline: <xsl:value-of select="$item/deadline"/></p>
            </xsl:if>
        </div>
    </xsl:template>
    
    <!-- Recursive template -->
    <xsl:template name="processCategories">
        <xsl:param name="categories"/>
        <xsl:for-each select="$categories">
            <div class="category">
                <xsl:value-of select="@name"/>
                <xsl:if test="category">
                    <xsl:call-template name="processCategories">
                        <xsl:with-param name="categories" select="category"/>
                    </xsl:call-template>
                </xsl:if>
            </div>
        </xsl:for-each>
    </xsl:template>
    
</xsl:stylesheet>'''
        
        xslt_file = temp_dir / "complex_sample.xsl"
        xslt_file.write_text(xslt_content)
        return str(xslt_file)
    
    @pytest.fixture
    def corrupted_xslt_file(self, temp_dir):
        """Create corrupted XSLT file for error testing."""
        corrupted_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output>
            <xsl:unclosed-tag>
        </output>
    <!-- Missing closing stylesheet tag -->'''
        
        corrupted_file = temp_dir / "corrupted.xsl"
        corrupted_file.write_text(corrupted_content)
        return str(corrupted_file)
    
    def test_parser_initialization(self, parser):
        """Test parser initialization."""
        assert parser.namespaces['xsl'] == 'http://www.w3.org/1999/XSL/Transform'
        assert parser.templates == {}
        assert parser.variables == {}
        assert parser.file_path is None
    
    def test_parse_xslt_file_success(self, parser, sample_xslt_file):
        """Test successful XSLT file parsing."""
        result = parser.parse_xslt_file(sample_xslt_file)
        
        # Check basic structure
        assert 'templates' in result
        assert 'variables' in result
        assert 'file_path' in result
        assert 'analysis_summary' in result
        assert 'error' not in result
        
        # Check templates were parsed
        templates = result['templates']
        assert len(templates) >= 4  # root, item, urgentItemTemplate, processCategories
        
        # Check specific templates
        assert any(t.match_pattern == '/' for t in templates.values())
        assert any(t.name == 'urgentItemTemplate' for t in templates.values())
        assert any(t.name == 'processCategories' for t in templates.values())
        
        # Check variables were parsed
        variables = result['variables']
        assert len(variables) >= 2  # defaultTitle, debugMode
        
        # Check analysis summary
        summary = result['analysis_summary']
        assert summary['total_templates'] >= 4
        assert summary['total_variables'] >= 2
        assert summary['named_templates'] >= 2
        assert summary['match_templates'] >= 2
    
    def test_parse_corrupted_file(self, parser, corrupted_xslt_file):
        """Test parsing corrupted XSLT file."""
        result = parser.parse_xslt_file(corrupted_xslt_file)
        
        assert 'error' in result
        assert 'XML parsing error' in result['error']
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing non-existent file."""
        result = parser.parse_xslt_file("/nonexistent/file.xsl")
        
        assert 'error' in result
    
    def test_template_extraction(self, parser, sample_xslt_file):
        """Test template extraction details."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Find root template
        root_template = next((t for t in templates.values() if t.match_pattern == '/'), None)
        assert root_template is not None
        assert root_template.match_pattern == '/'
        assert root_template.name is None
        assert 'html' in root_template.output_elements
        assert 'head' in root_template.output_elements
        assert 'body' in root_template.output_elements
        
        # Find named template
        urgent_template = templates.get('urgentItemTemplate')
        assert urgent_template is not None
        assert urgent_template.name == 'urgentItemTemplate'
        assert urgent_template.match_pattern is None
        assert 'div' in urgent_template.output_elements
        assert 'p' in urgent_template.output_elements
    
    def test_variable_extraction(self, parser, sample_xslt_file):
        """Test variable extraction details."""
        result = parser.parse_xslt_file(sample_xslt_file)
        variables = result['variables']
        
        # Find global variable
        default_title = variables.get('defaultTitle')
        assert default_title is not None
        assert default_title.name == 'defaultTitle'
        assert default_title.variable_type == 'variable'
        assert default_title.scope == 'global'
        assert default_title.select_expression == "'Sample Document'"
        
        # Find global parameter
        debug_mode = variables.get('debugMode')
        assert debug_mode is not None
        assert debug_mode.name == 'debugMode'
        assert debug_mode.variable_type == 'parameter'
        assert debug_mode.scope == 'global'
        assert debug_mode.select_expression == "false()"
    
    def test_template_calls_extraction(self, parser, sample_xslt_file):
        """Test template call extraction."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Find template with calls
        item_template = next((t for t in templates.values() if t.match_pattern == 'item'), None)
        assert item_template is not None
        assert 'urgentItemTemplate' in item_template.calls_templates
    
    def test_conditional_logic_extraction(self, parser, sample_xslt_file):
        """Test conditional logic extraction."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Find template with conditional logic
        item_template = next((t for t in templates.values() if t.match_pattern == 'item'), None)
        assert item_template is not None
        assert len(item_template.conditional_logic) >= 2  # if and choose
        
        # Check specific conditions
        conditions = [cond['condition'] for cond in item_template.conditional_logic if 'condition' in cond]
        assert any("@priority = 'high'" in cond for cond in conditions)
    
    def test_xpath_expression_extraction(self, parser, sample_xslt_file):
        """Test XPath expression extraction."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Check XPath expressions were extracted
        all_xpaths = []
        for template in templates.values():
            all_xpaths.extend(template.xpath_expressions)
        
        assert "//item" in all_xpaths
        assert "@name" in all_xpaths
        assert "@priority" in all_xpaths
        assert "@type = 'urgent'" in all_xpaths
    
    def test_variable_usage_extraction(self, parser, sample_xslt_file):
        """Test variable usage extraction."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Find template that uses variables
        root_template = next((t for t in templates.values() if t.match_pattern == '/'), None)
        assert root_template is not None
        assert 'defaultTitle' in root_template.uses_variables
    
    def test_complexity_calculation(self, parser, sample_xslt_file):
        """Test complexity score calculation."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Check that complexity scores were calculated
        for template in templates.values():
            assert template.complexity_score >= 1
        
        # More complex templates should have higher scores
        item_template = next((t for t in templates.values() if t.match_pattern == 'item'), None)
        root_template = next((t for t in templates.values() if t.match_pattern == '/'), None)
        
        # Item template has conditional logic, should be more complex
        assert item_template.complexity_score > root_template.complexity_score
    
    def test_recursion_detection(self, parser, sample_xslt_file):
        """Test recursive template detection."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Find recursive template
        recursive_template = templates.get('processCategories')
        assert recursive_template is not None
        assert recursive_template.is_recursive is True
        
        # Non-recursive templates
        urgent_template = templates.get('urgentItemTemplate')
        assert urgent_template is not None
        assert urgent_template.is_recursive is False
    
    def test_template_relationships(self, parser, sample_xslt_file):
        """Test template relationship analysis."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Check called_by_templates relationships
        urgent_template = templates.get('urgentItemTemplate')
        assert urgent_template is not None
        
        # Should be called by item template
        item_template_key = next((key for key, t in templates.items() if t.match_pattern == 'item'), None)
        assert item_template_key in urgent_template.called_by_templates
    
    def test_output_element_extraction(self, parser, sample_xslt_file):
        """Test output element extraction."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Check output elements
        root_template = next((t for t in templates.values() if t.match_pattern == '/'), None)
        assert root_template is not None
        
        expected_elements = {'html', 'head', 'title', 'body'}
        assert expected_elements.issubset(set(root_template.output_elements))
    
    def test_template_hash_generation(self, parser, sample_xslt_file):
        """Test template hash generation."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # All templates should have hashes
        for template in templates.values():
            assert template.template_hash
            assert len(template.template_hash) == 16  # MD5 hash truncated to 16 chars
    
    def test_analysis_summary_generation(self, parser, sample_xslt_file):
        """Test analysis summary generation."""
        result = parser.parse_xslt_file(sample_xslt_file)
        summary = result['analysis_summary']
        
        # Check summary fields
        assert 'total_templates' in summary
        assert 'named_templates' in summary
        assert 'match_templates' in summary
        assert 'recursive_templates' in summary
        assert 'total_variables' in summary
        assert 'avg_complexity' in summary
        assert 'most_complex_template' in summary
        
        # Check values make sense
        assert summary['total_templates'] >= 4
        assert summary['named_templates'] >= 2
        assert summary['match_templates'] >= 2
        assert summary['recursive_templates'] >= 1
        assert summary['avg_complexity'] > 0
    
    def test_template_content_preservation(self, parser, sample_xslt_file):
        """Test that template content is preserved."""
        result = parser.parse_xslt_file(sample_xslt_file)
        templates = result['templates']
        
        # Check that template content is stored
        for template in templates.values():
            assert template.template_content
            # XML serialization may use namespace prefixes, so check for template element
            assert 'template' in template.template_content
            assert 'xmlns' in template.template_content  # Should have namespace declaration
    
    def test_large_template_handling(self, parser, temp_dir):
        """Test handling of large templates."""
        # Create a large template
        large_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <large>'''
        
        # Add many elements to make it large
        for i in range(100):
            large_content += f'<item{i}><xsl:value-of select="//data{i}"/></item{i}>'
        
        large_content += '''
        </large>
    </xsl:template>
</xsl:stylesheet>'''
        
        large_file = temp_dir / "large.xsl"
        large_file.write_text(large_content)
        
        result = parser.parse_xslt_file(str(large_file))
        
        # Should handle large files successfully
        assert 'error' not in result
        assert len(result['templates']) >= 1
        
        # Check complexity adjustment for large content
        template = next(iter(result['templates'].values()))
        assert template.complexity_score >= 3  # Should get complexity bonus for size