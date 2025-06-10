"""
Unit tests for services.xml_validator module.

Tests XMLValidator functionality including XML validation against XSD schemas,
error categorization, detailed validation reporting, and error handling scenarios.
"""

import os
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from services.xml_validator import XMLValidator
from services.file_manager import FileManager


class TestXMLValidatorInit:
    """Test XMLValidator initialization."""
    
    def test_init_with_config(self):
        """Test XMLValidator initialization with config instance."""
        config = Mock()
        validator = XMLValidator(config)
        assert validator.file_manager is not None
    
    def test_init_without_config(self):
        """Test XMLValidator initialization without config (uses default)."""
        validator = XMLValidator()
        assert validator.file_manager is not None


class TestXMLValidatorErrorCategorization:
    """Test error categorization functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = XMLValidator()
    
    def test_categorize_errors_enumeration(self):
        """Test categorization of enumeration errors."""
        mock_errors = [
            Mock(message="XsdEnumerationFacets validation error"),
            Mock(message="Value not in enumeration list"),
            Mock(message="Other error")
        ]
        
        result = self.validator._categorize_errors(mock_errors)
        
        assert len(result['enumeration_errors']) == 1
        assert len(result['boolean_errors']) == 0
        assert len(result['pattern_errors']) == 0
        assert len(result['structural_errors']) == 2
    
    def test_categorize_errors_boolean(self):
        """Test categorization of boolean errors."""
        mock_errors = [
            Mock(message="with XsdAtomicBuiltin(name='xs:boolean') validation error"),
            Mock(message="Boolean type error"),
            Mock(message="Other error")
        ]
        
        result = self.validator._categorize_errors(mock_errors)
        
        assert len(result['enumeration_errors']) == 0
        assert len(result['boolean_errors']) == 1
        assert len(result['pattern_errors']) == 0
        assert len(result['structural_errors']) == 2
    
    def test_categorize_errors_pattern(self):
        """Test categorization of pattern errors."""
        mock_errors = [
            Mock(message="Pattern validation failed"),
            Mock(message="Does not match required pattern"),
            Mock(message="Other error")
        ]
        
        result = self.validator._categorize_errors(mock_errors)
        
        assert len(result['enumeration_errors']) == 0
        assert len(result['boolean_errors']) == 0
        assert len(result['pattern_errors']) == 2
        assert len(result['structural_errors']) == 1
    
    def test_categorize_errors_mixed(self):
        """Test categorization of mixed error types."""
        mock_errors = [
            Mock(message="XsdEnumerationFacets error"),
            Mock(message="with XsdAtomicBuiltin(name='xs:boolean') error"),
            Mock(message="Pattern validation failed"),
            Mock(message="Structural error"),
            Mock(message="Another pattern issue")
        ]
        
        result = self.validator._categorize_errors(mock_errors)
        
        assert len(result['enumeration_errors']) == 1
        assert len(result['boolean_errors']) == 1
        assert len(result['pattern_errors']) == 2
        assert len(result['structural_errors']) == 1
    
    def test_categorize_errors_empty(self):
        """Test categorization with empty error list."""
        result = self.validator._categorize_errors([])
        
        assert len(result['enumeration_errors']) == 0
        assert len(result['boolean_errors']) == 0
        assert len(result['pattern_errors']) == 0
        assert len(result['structural_errors']) == 0


class TestXMLValidatorErrorFormatting:
    """Test error formatting functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = XMLValidator()
    
    def test_format_validation_error_complete(self):
        """Test formatting error with complete information."""
        mock_error = Mock()
        mock_error.path = "/root/element[1]/subelement"
        mock_error.message = "Validation failed for element"
        mock_error.lineno = 42
        
        result = self.validator.format_validation_error(mock_error)
        
        assert result['message'] == "Validation failed for element"
        assert result['path'] == "/root/element[1]/subelement"
        assert result['element_name'] == "subelement"
        assert result['line'] == 42
    
    def test_format_validation_error_with_namespace(self):
        """Test formatting error with namespaced element."""
        mock_error = Mock()
        mock_error.path = "/root/ns:element[1]/ns:subelement"
        mock_error.message = "Namespace validation error"
        mock_error.lineno = 24
        
        result = self.validator.format_validation_error(mock_error)
        
        assert result['element_name'] == "subelement"
        assert result['path'] == "/root/ns:element[1]/ns:subelement"
    
    def test_format_validation_error_simple_path(self):
        """Test formatting error with simple element name."""
        mock_error = Mock()
        mock_error.path = "element"
        mock_error.message = "Simple error"
        mock_error.lineno = None
        
        result = self.validator.format_validation_error(mock_error)
        
        assert result['element_name'] == "Unknown"
        assert result['line'] is None
    
    def test_format_validation_error_no_path(self):
        """Test formatting error without path information."""
        mock_error = Mock()
        mock_error.message = "Error without path"
        # No path attribute
        del mock_error.path
        del mock_error.lineno
        
        result = self.validator.format_validation_error(mock_error)
        
        assert result['path'] == "Unknown path"
        assert result['element_name'] == "Unknown"
        assert result['line'] is None
    
    def test_format_validation_error_exception(self):
        """Test formatting error when exception occurs."""
        mock_error = Mock()
        # Make message property raise exception when accessed
        type(mock_error).message = PropertyMock(side_effect=Exception("Error accessing message"))
        
        result = self.validator.format_validation_error(mock_error)
        
        assert "Mock" in result['message']  # str(error) representation
        assert result['path'] == "Unknown"
        assert result['element_name'] == "Unknown"
        assert result['line'] is None


class TestXMLValidatorValidateXMLAgainstSchema:
    """Test main validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = XMLValidator()
    
    @patch('services.xml_validator.XSDParser')
    def test_validate_xml_success(self, mock_parser_class):
        """Test successful XML validation."""
        # Mock XSDParser and schema
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser.validate_xml.return_value = True
        mock_parser_class.return_value = mock_parser
        
        # Mock schema validation
        mock_errors = [
            Mock(message="enum error"),
            Mock(message="boolean error")
        ]
        mock_schema.iter_errors.return_value = iter(mock_errors)
        
        # Mock file manager
        with patch.object(self.validator.file_manager, 'create_temp_file') as mock_create:
            with patch.object(self.validator.file_manager, 'cleanup_temp_file') as mock_cleanup:
                mock_create.return_value = '/tmp/test.xml'
                
                xml_content = '<?xml version="1.0"?><test>content</test>'
                xsd_path = '/path/to/schema.xsd'
                
                result = self.validator.validate_xml_against_schema(xml_content, xsd_path)
                
                assert result['success'] is True
                assert result['is_valid'] is True
                assert result['total_errors'] == 2
                assert 'error_breakdown' in result
                assert 'categorized_errors' in result
                assert 'detailed_errors' in result
                
                # Verify file operations
                mock_create.assert_called_once_with(xml_content, '.xml')
                mock_cleanup.assert_called_once_with('/tmp/test.xml')
    
    @patch('services.xml_validator.XSDParser')
    def test_validate_xml_with_uploaded_content(self, mock_parser_class):
        """Test validation when XSD file doesn't exist but content is provided."""
        # Mock XSDParser
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser.validate_xml.return_value = False
        mock_parser_class.return_value = mock_parser
        
        mock_schema.iter_errors.return_value = iter([])
        
        # Mock file manager for XSD recreation
        with patch.object(self.validator.file_manager, 'create_temp_file') as mock_create_xml:
            with patch.object(self.validator.file_manager, 'write_temp_xsd_with_dependencies') as mock_write_xsd:
                with patch.object(self.validator.file_manager, 'cleanup_temp_file') as mock_cleanup_file:
                    with patch.object(self.validator.file_manager, 'cleanup_temp_directory') as mock_cleanup_dir:
                        with patch('os.path.exists', return_value=False):
                            
                            mock_create_xml.return_value = '/tmp/test.xml'
                            mock_write_xsd.return_value = ('/tmp/schema.xsd', '/tmp/temp_dir')
                            
                            xml_content = '<?xml version="1.0"?><test>content</test>'
                            xsd_path = '/nonexistent/schema.xsd'
                            uploaded_name = 'schema.xsd'
                            uploaded_content = '<?xml version="1.0"?><schema>content</schema>'
                            
                            result = self.validator.validate_xml_against_schema(
                                xml_content, xsd_path, uploaded_name, uploaded_content
                            )
                            
                            assert result['success'] is True
                            assert result['is_valid'] is False
                            
                            # Verify XSD was recreated
                            mock_write_xsd.assert_called_once_with(uploaded_content, uploaded_name)
                            mock_cleanup_dir.assert_called_once_with('/tmp/temp_dir')
    
    @patch('services.xml_validator.XSDParser')
    def test_validate_xml_with_existing_xsd(self, mock_parser_class):
        """Test validation when XSD file exists."""
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser.validate_xml.return_value = True
        mock_parser_class.return_value = mock_parser
        
        mock_schema.iter_errors.return_value = iter([])
        
        with patch.object(self.validator.file_manager, 'create_temp_file') as mock_create:
            with patch.object(self.validator.file_manager, 'cleanup_temp_file') as mock_cleanup:
                with patch('os.path.exists', return_value=True):
                    
                    mock_create.return_value = '/tmp/test.xml'
                    
                    xml_content = '<?xml version="1.0"?><test>content</test>'
                    xsd_path = '/existing/schema.xsd'
                    
                    result = self.validator.validate_xml_against_schema(xml_content, xsd_path)
                    
                    assert result['success'] is True
                    # Should use existing XSD path directly
                    mock_parser_class.assert_called_once_with('/existing/schema.xsd')
    
    def test_validate_xml_exception_handling(self):
        """Test validation with exception handling."""
        with patch.object(self.validator.file_manager, 'create_temp_file') as mock_create:
            mock_create.side_effect = Exception("File creation failed")
            
            xml_content = '<?xml version="1.0"?><test>content</test>'
            xsd_path = '/path/to/schema.xsd'
            
            result = self.validator.validate_xml_against_schema(xml_content, xsd_path)
            
            assert result['success'] is False
            assert result['is_valid'] is False
            assert 'error' in result
            assert "File creation failed" in result['error']


class TestXMLValidatorIntegration:
    """Integration tests for XMLValidator with real XML/XSD content."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = XMLValidator()
    
    def test_validate_simple_xml_success(self):
        """Test validation of simple valid XML."""
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="element" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <element>test value</element>
</root>'''
        
        # Create temporary XSD file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as xsd_file:
            xsd_file.write(xsd_content)
            xsd_path = xsd_file.name
        
        try:
            result = self.validator.validate_xml_against_schema(xml_content, xsd_path)
            
            assert result['success'] is True
            assert result['is_valid'] is True
            assert result['total_errors'] == 0
            
        finally:
            os.unlink(xsd_path)
    
    def test_validate_simple_xml_failure(self):
        """Test validation of invalid XML."""
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="required" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <wrong_element>test value</wrong_element>
</root>'''
        
        # Create temporary XSD file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as xsd_file:
            xsd_file.write(xsd_content)
            xsd_path = xsd_file.name
        
        try:
            result = self.validator.validate_xml_against_schema(xml_content, xsd_path)
            
            assert result['success'] is True
            assert result['is_valid'] is False
            assert result['total_errors'] > 0
            assert 'error_breakdown' in result
            
        finally:
            os.unlink(xsd_path)
    
    def test_validate_with_uploaded_content_integration(self):
        """Test validation using uploaded XSD content."""
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="test" type="xs:string"/>
</xs:schema>'''
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<test>valid content</test>'''
        
        result = self.validator.validate_xml_against_schema(
            xml_content, 
            '/nonexistent/path.xsd',
            'test.xsd',
            xsd_content
        )
        
        assert result['success'] is True
        assert result['is_valid'] is True
        assert result['total_errors'] == 0


class TestXMLValidatorErrorHandling:
    """Test error handling in various scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = XMLValidator()
    
    @patch('services.xml_validator.XSDParser')
    def test_parser_creation_failure(self, mock_parser_class):
        """Test handling of parser creation failure."""
        mock_parser_class.side_effect = Exception("Parser creation failed")
        
        with patch.object(self.validator.file_manager, 'create_temp_file', return_value='/tmp/test.xml'):
            with patch.object(self.validator.file_manager, 'cleanup_temp_file'):
                
                result = self.validator.validate_xml_against_schema(
                    '<test>content</test>', '/path/to/schema.xsd'
                )
                
                assert result['success'] is False
                assert "Parser creation failed" in result['error']
    
    @patch('services.xml_validator.XSDParser')
    def test_schema_iteration_failure(self, mock_parser_class):
        """Test handling of schema iteration failure."""
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_schema.iter_errors.side_effect = Exception("Schema iteration failed")
        mock_parser_class.return_value = mock_parser
        
        with patch.object(self.validator.file_manager, 'create_temp_file', return_value='/tmp/test.xml'):
            with patch.object(self.validator.file_manager, 'cleanup_temp_file'):
                
                result = self.validator.validate_xml_against_schema(
                    '<test>content</test>', '/path/to/schema.xsd'
                )
                
                assert result['success'] is False
                assert "Schema iteration failed" in result['error']
    
    def test_cleanup_failure_handling(self):
        """Test that cleanup failures don't affect validation results."""
        with patch.object(self.validator.file_manager, 'create_temp_file', return_value='/tmp/test.xml'):
            # Mock os.unlink to fail inside cleanup_temp_file, but the method handles it gracefully
            with patch('os.unlink', side_effect=Exception("Cleanup failed")):
                with patch('os.path.exists', return_value=True):
                    with patch('services.xml_validator.XSDParser') as mock_parser_class:
                        
                        mock_parser = Mock()
                        mock_schema = Mock()
                        mock_parser.schema = mock_schema
                        mock_parser.validate_xml.return_value = True
                        mock_schema.iter_errors.return_value = iter([])
                        mock_parser_class.return_value = mock_parser
                        
                        result = self.validator.validate_xml_against_schema(
                            '<test>content</test>', '/path/to/schema.xsd'
                        )
                        
                        # Should still succeed despite cleanup failure (method handles it gracefully)
                        assert result['success'] is True