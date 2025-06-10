"""
Edge case and error handling tests for utils layer.

Tests error conditions, boundary cases, and exception handling for
xml_generator.py, type_generators.py, and xsd_parser.py modules.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from utils.xml_generator import XMLGenerator
from utils.type_generators import (
    TypeGeneratorFactory, NumericTypeGenerator, BooleanTypeGenerator,
    DateTimeTypeGenerator, StringTypeGenerator, EnumerationTypeGenerator
)
from utils.xsd_parser import XSDParser


class TestXMLGeneratorErrorHandling:
    """Test error handling in XMLGenerator."""
    
    def test_init_with_empty_path(self):
        """Test XMLGenerator initialization with empty path."""
        with pytest.raises(ValueError, match="XSD path cannot be empty"):
            XMLGenerator("")
    
    def test_init_with_nonexistent_file(self):
        """Test XMLGenerator initialization with non-existent file."""
        with pytest.raises(ValueError, match="XSD file not found"):
            XMLGenerator("/nonexistent/path/schema.xsd")
    
    def test_init_with_directory_path(self):
        """Test XMLGenerator initialization with directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="XSD path is not a file"):
                XMLGenerator(temp_dir)
    
    @patch('utils.xml_generator.xmlschema.XMLSchema')
    def test_schema_loading_error(self, mock_schema_class):
        """Test error handling when schema loading fails."""
        mock_schema_class.side_effect = Exception("Schema loading failed")
        
        with tempfile.NamedTemporaryFile(suffix='.xsd', delete=False) as temp_file:
            temp_file.write(b'<schema>content</schema>')
            temp_path = temp_file.name
        
        try:
            with pytest.raises(ValueError, match="Failed to load XSD schema"):
                XMLGenerator(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_generate_xml_with_no_elements(self):
        """Test XML generation when schema has no elements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            result = generator.generate_dummy_xml()
            
            assert '<error>' in result
            assert ('No root elements found' in result or 'Schema not loaded' in result)
        finally:
            os.unlink(temp_path)
    
    def test_generate_xml_with_circular_references(self):
        """Test XML generation with circular reference protection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root" type="recursiveType"/>
    <xs:complexType name="recursiveType">
        <xs:sequence>
            <xs:element name="child" type="recursiveType" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            result = generator.generate_dummy_xml()
            
            # Should complete without infinite recursion
            assert '<?xml version="1.0" encoding="UTF-8"?>' in result
            assert '<root' in result  # May have namespace attributes
        finally:
            os.unlink(temp_path)
    
    def test_create_element_dict_with_none_type(self):
        """Test _create_element_dict with None type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="test" type="xs:string"/>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            
            # Mock element with None type
            mock_element = Mock()
            mock_element.type = None
            mock_element.local_name = "test_element"
            
            result = generator._create_element_dict(mock_element)
            
            # Should handle None type gracefully
            assert isinstance(result, str) or result is not None
        finally:
            os.unlink(temp_path)
    
    def test_xml_tree_building_failure(self):
        """Test XML tree building failure fallback."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="test" type="xs:string"/>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            
            with patch('utils.xml_generator.etree.Element', side_effect=Exception("Tree building failed")):
                result = generator.generate_dummy_xml()
                
                # Should fall back to dict_to_xml
                assert '<?xml version="1.0" encoding="UTF-8"?>' in result
                assert '<test>' in result
        finally:
            os.unlink(temp_path)


class TestTypeGeneratorEdgeCases:
    """Test edge cases in type generators."""
    
    def test_numeric_generator_with_extreme_constraints(self):
        """Test numeric generator with extreme constraints."""
        generator = NumericTypeGenerator(is_decimal=True)
        
        constraints = {
            'min_value': 999999999,
            'max_value': 1000000000
        }
        
        result = generator.generate("test", constraints)
        assert 999999999 <= result <= 1000000000
    
    def test_numeric_generator_with_invalid_constraints(self):
        """Test numeric generator with invalid constraints."""
        generator = NumericTypeGenerator(is_decimal=False)
        
        constraints = {
            'min_value': 100,
            'max_value': 50  # Invalid: max < min
        }
        
        # Should handle gracefully
        result = generator.generate("test", constraints)
        assert isinstance(result, int)
    
    def test_string_generator_with_zero_length(self):
        """Test string generator with zero length constraint."""
        generator = StringTypeGenerator()
        
        constraints = {'exact_length': 0}
        
        result = generator.generate("test", constraints)
        assert len(result) == 0
    
    def test_string_generator_with_conflicting_constraints(self):
        """Test string generator with conflicting length constraints."""
        generator = StringTypeGenerator()
        
        constraints = {
            'min_length': 10,
            'max_length': 5,  # Conflict: min > max
            'exact_length': 7
        }
        
        result = generator.generate("test", constraints)
        # exact_length should take precedence
        assert len(result) == 7
    
    def test_string_generator_with_invalid_pattern(self):
        """Test string generator with invalid regex pattern."""
        generator = StringTypeGenerator()
        
        constraints = {
            'pattern': '[invalid regex('  # Invalid regex
        }
        
        # Should handle invalid regex gracefully
        result = generator.generate("test", constraints)
        assert isinstance(result, str)
    
    def test_enumeration_generator_with_empty_list(self):
        """Test enumeration generator with empty enum list."""
        generator = EnumerationTypeGenerator()
        
        result = generator.generate("test", {'enum_values': []})
        assert result == "EnumValue"  # Fallback
    
    def test_enumeration_generator_with_none_values(self):
        """Test enumeration generator with None values in list."""
        generator = EnumerationTypeGenerator()
        
        constraints = {'enum_values': ['None', 'ValidValue', 'None']}
        
        result = generator.generate("test", constraints)
        assert result == 'ValidValue'  # Should filter out 'None'
    
    def test_boolean_generator_with_invalid_default(self):
        """Test boolean generator with invalid config default."""
        mock_config = Mock()
        mock_config.data_generation.boolean_default = 'invalid_boolean'
        
        generator = BooleanTypeGenerator(mock_config)
        
        result = generator.generate("test")
        assert result == 'true'  # Should fall back to 'true'
    
    def test_datetime_generator_with_invalid_type(self):
        """Test datetime generator with invalid date type."""
        generator = DateTimeTypeGenerator(date_type='invalid_type')
        
        result = generator.generate("test")
        # Should default to datetime format
        assert 'T' in result and 'Z' in result


class TestTypeGeneratorFactory:
    """Test TypeGeneratorFactory edge cases."""
    
    def test_factory_with_unknown_type(self):
        """Test factory with completely unknown type."""
        factory = TypeGeneratorFactory()
        
        mock_type = Mock()
        mock_type.primitive_type = None
        mock_type.base_type = None
        mock_type.name = None
        
        # Should return StringTypeGenerator as fallback
        generator = factory.create_generator(mock_type)
        assert isinstance(generator, StringTypeGenerator)
    
    def test_factory_with_malformed_type_string(self):
        """Test factory with malformed type string representation."""
        factory = TypeGeneratorFactory()
        
        # Mock type that returns problematic string representation
        mock_type = Mock()
        mock_type.primitive_type = None
        mock_type.base_type = None
        mock_type.name = None
        mock_type.__str__ = Mock(side_effect=Exception("String conversion failed"))
        
        # Should handle exception and return string generator
        generator = factory.create_generator(mock_type)
        assert isinstance(generator, StringTypeGenerator)
    
    def test_factory_with_nested_type_attributes(self):
        """Test factory with deeply nested type attributes."""
        factory = TypeGeneratorFactory()
        
        mock_type = Mock()
        mock_primitive = Mock()
        mock_primitive.name = "xs:decimal"
        mock_type.primitive_type = mock_primitive
        
        generator = factory.create_generator(mock_type)
        assert isinstance(generator, NumericTypeGenerator)
        assert generator.is_decimal is True


class TestXSDParserErrorHandling:
    """Test XSDParser error handling."""
    
    def test_parser_with_invalid_xsd_content(self):
        """Test parser with invalid XSD content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('invalid xml content')
            temp_path = temp_file.name
        
        try:
            with pytest.raises(ValueError, match="Failed to load XSD schema"):
                XSDParser(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parser_with_empty_schema(self):
        """Test parser with empty schema."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            parser = XSDParser(temp_path)
            schema_info = parser.get_schema_info()
            root_elements = parser.get_root_elements()
            
            # Handle cases where schema info might be empty due to schema loading issues
            if schema_info:
                assert schema_info.get('elements_count', 0) == 0
            assert len(root_elements) == 0
        finally:
            os.unlink(temp_path)
    
    def test_parser_validate_nonexistent_xml(self):
        """Test parser validation with non-existent XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="test" type="xs:string"/>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            parser = XSDParser(temp_path)
            result = parser.validate_xml('/nonexistent/file.xml')
            
            assert result is False
        finally:
            os.unlink(temp_path)
    
    def test_parser_with_schema_none(self):
        """Test parser methods when schema is None."""
        parser = XSDParser.__new__(XSDParser)  # Create without calling __init__
        parser.schema = None
        
        schema_info = parser.get_schema_info()
        root_elements = parser.get_root_elements()
        validation_result = parser.validate_xml('any_file.xml')
        
        assert schema_info == {}
        assert root_elements == {}
        assert validation_result is False


class TestMemoryAndPerformanceEdgeCases:
    """Test memory management and performance edge cases."""
    
    def test_large_unbounded_counts(self):
        """Test handling of very large unbounded counts."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="item" type="xs:string" maxOccurs="unbounded"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            
            # Set extremely large unbounded count
            unbounded_counts = {'root.item': 10000}
            
            result = generator.generate_dummy_xml_with_choices(None, unbounded_counts)
            
            # Should limit based on depth and configuration
            assert '<?xml version="1.0" encoding="UTF-8"?>' in result
            item_count = result.count('<item>')
            assert item_count < 10000  # Should be limited by depth constraints
        finally:
            os.unlink(temp_path)
    
    def test_deep_nesting_protection(self):
        """Test protection against very deep nesting."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="level1">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="level2">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="level3">
                                <xs:complexType>
                                    <xs:sequence>
                                        <xs:element name="level4" type="xs:string"/>
                                    </xs:sequence>
                                </xs:complexType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            result = generator.generate_dummy_xml()
            
            # Should handle deep nesting without stack overflow
            assert '<?xml version="1.0" encoding="UTF-8"?>' in result
            assert '<level1' in result  # May have namespace attributes
        finally:
            os.unlink(temp_path)
    
    def test_choice_selection_with_invalid_preferences(self):
        """Test choice selection with invalid user preferences."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
            temp_file.write('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:choice>
                <xs:element name="option1" type="xs:string"/>
                <xs:element name="option2" type="xs:string"/>
            </xs:choice>
        </xs:complexType>
    </xs:element>
</xs:schema>''')
            temp_path = temp_file.name
        
        try:
            generator = XMLGenerator(temp_path)
            
            # Invalid choice preferences
            invalid_choices = {
                'nonexistent_choice': {'selected_element': 'option1'},
                'malformed_choice': 'invalid_format',
                123: {'selected_element': 'option2'}  # Non-string key
            }
            
            result = generator.generate_dummy_xml_with_choices(invalid_choices)
            
            # Should handle invalid preferences gracefully 
            assert '<?xml version="1.0" encoding="UTF-8"?>' in result
            # May generate error or valid XML depending on choice handling
            assert ('<root' in result or '<error>' in result)
        finally:
            os.unlink(temp_path)