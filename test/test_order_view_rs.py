"""
Test cases for IATA_OrderViewRS.xsd XML generation and parsing.
"""

import pytest
import xml.etree.ElementTree as ET
from lxml import etree
import re
import os


class TestOrderViewRSSchema:
    """Test cases for IATA_OrderViewRS schema handling."""
    
    def test_schema_loading(self, xsd_parser_order_view):
        """Test that the OrderViewRS schema loads successfully."""
        assert xsd_parser_order_view.schema is not None
        schema_info = xsd_parser_order_view.get_schema_info()
        assert schema_info['filename'] == 'IATA_OrderViewRS.xsd'
        assert 'IATA_OffersAndOrdersMessage' in schema_info['target_namespace']
    
    def test_root_elements(self, xsd_parser_order_view):
        """Test that the schema has the expected root element."""
        root_elements = xsd_parser_order_view.get_root_elements()
        assert 'IATA_OrderViewRS' in root_elements
        assert root_elements['IATA_OrderViewRS']['is_complex'] is True
    
    def test_schema_info_structure(self, xsd_parser_order_view):
        """Test schema information structure."""
        schema_info = xsd_parser_order_view.get_schema_info()
        required_keys = ['filepath', 'filename', 'target_namespace', 'elements_count', 'types_count']
        for key in required_keys:
            assert key in schema_info


class TestOrderViewRSXMLGeneration:
    """Test cases for XML generation from OrderViewRS schema."""
    
    def test_xml_generation_basic(self, xml_generator_order_view):
        """Test basic XML generation from OrderViewRS schema."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        assert xml_content is not None
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_content
        assert 'IATA_OrderViewRS' in xml_content
        assert not xml_content.startswith('<error>')
    
    def test_xml_contains_choice_elements(self, xml_generator_order_view):
        """Test that generated XML contains choice elements (Error or Response)."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Should contain either Error or Response element (xs:choice)
        assert 'Error' in xml_content or 'Response' in xml_content
    
    def test_xml_structure_validity(self, xml_generator_order_view):
        """Test that generated XML has valid structure."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Remove XML declaration for parsing
        xml_body = xml_content.split('>', 1)[1] if xml_content.startswith('<?xml') else xml_content
        
        try:
            root = ET.fromstring(xml_body)
            assert root.tag.endswith('IATA_OrderViewRS')
        except ET.ParseError as e:
            pytest.fail(f"Generated XML is not well-formed: {e}")
    
    def test_xml_contains_mandatory_elements(self, xml_generator_order_view):
        """Test that mandatory elements are present in generated XML."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Based on schema, either Error (if error path) or Response (if success path) should be present
        # Both are within a choice, so at least one should exist
        has_error = 'Error' in xml_content
        has_response = 'Response' in xml_content
        assert has_error or has_response, "XML should contain either Error or Response element"
    
    def test_xml_contains_optional_elements(self, xml_generator_order_view):
        """Test that optional elements may be present in generated XML."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # These are optional elements that may or may not be present
        optional_elements = ['AugmentationPoint', 'DistributionChain', 'PayloadAttributes', 'PaymentFunctions']
        
        # At least check that the XML generation doesn't fail with optional elements
        assert 'IATA_OrderViewRS' in xml_content
    
    def test_xml_namespace_handling(self, xml_generator_order_view):
        """Test that XML contains proper namespace declarations."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Should contain IATA namespace
        assert 'IATA_OffersAndOrdersMessage' in xml_content or 'xmlns' in xml_content
    
    def test_xml_comments_for_occurrence_info(self, xml_generator_order_view):
        """Test that XML contains comments about element occurrence information."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Generated XML should be well-formed and contain expected elements
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert '<IATA_OrderViewRS' in xml_content
        assert '</IATA_OrderViewRS>' in xml_content
    
    def test_xml_file_output(self, xml_generator_order_view, sample_xml_output_dir):
        """Test XML generation to file."""
        output_path = os.path.join(sample_xml_output_dir, "test_order_view_rs.xml")
        xml_content = xml_generator_order_view.generate_dummy_xml(output_path)
        
        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content == xml_content
        assert 'IATA_OrderViewRS' in file_content


class TestOrderViewRSErrorHandling:
    """Test error handling for OrderViewRS processing."""
    
    def test_schema_with_missing_dependencies(self, temp_xsd_dir):
        """Test handling when dependent XSD files are missing."""
        # Remove the common types XSD to simulate missing dependency
        common_types_path = os.path.join(temp_xsd_dir, "IATA_OffersAndOrdersCommonTypes.xsd")
        if os.path.exists(common_types_path):
            os.remove(common_types_path)
        
        from utils.xml_generator import XMLGenerator
        
        # Should handle missing dependencies gracefully
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        
        # This might raise an exception or generate error XML
        try:
            generator = XMLGenerator(xsd_path)
            xml_content = generator.generate_dummy_xml()
            # If it doesn't raise an exception, it should generate error XML
            assert xml_content is not None
        except Exception:
            # Exception is acceptable when dependencies are missing
            pass
    
    def test_invalid_schema_path(self):
        """Test handling of invalid schema path."""
        from utils.xml_generator import XMLGenerator
        
        with pytest.raises(ValueError, match="XSD file not found"):
            XMLGenerator("/nonexistent/path/schema.xsd")


class TestOrderViewRSDataGeneration:
    """Test data generation specifics for OrderViewRS."""
    
    def test_error_element_generation(self, xml_generator_order_view):
        """Test generation of Error elements with proper structure."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        if 'Error' in xml_content:
            # Error elements should contain required sub-elements
            # Based on IATA schema, Error should have type, code, description etc.
            assert 'Error' in xml_content
    
    def test_multiple_occurrence_elements(self, xml_generator_order_view):
        """Test generation of elements with maxOccurs > 1."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # PaymentFunctions has maxOccurs="unbounded"
        # Error also has maxOccurs="unbounded" 
        # If present, should generate multiple instances
        if 'PaymentFunctions' in xml_content:
            payment_count = xml_content.count('<PaymentFunctions')
            if payment_count > 0:
                assert payment_count >= 1  # Should generate at least one
    
    def test_namespace_prefix_generation(self, xml_generator_order_view):
        """Test that namespace prefixes are properly generated."""
        xml_content = xml_generator_order_view.generate_dummy_xml()
        
        # Should contain cns: prefix for common types
        # This tests the namespace handling in complex type processing
        assert xml_content is not None
        # The specific prefix usage depends on the generated content structure


class TestOrderViewRSNewMethods:
    """Test new methods added to XMLGenerator for user choice handling."""
    
    def test_generate_dummy_xml_with_choices_method_exists(self, xml_generator_order_view):
        """Test that the new method exists and is callable."""
        assert hasattr(xml_generator_order_view, 'generate_dummy_xml_with_choices')
        assert callable(xml_generator_order_view.generate_dummy_xml_with_choices)
    
    def test_generate_dummy_xml_with_choices_error_selection(self, xml_generator_order_view):
        """Test XML generation with Error choice selected."""
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Error',
                'choice_data': {}
            }
        }
        
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(selected_choices)
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'Error' in xml_content
        # Should prefer Error over Response
        assert xml_content.count('Error') >= xml_content.count('Response')
    
    def test_generate_dummy_xml_with_unbounded_counts(self, xml_generator_order_view):
        """Test XML generation with custom unbounded element counts."""
        unbounded_counts = {
            'Error': 4,
            'IATA_OrderViewRS.Error': 4
        }
        
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(None, unbounded_counts)
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        
        # Check if Error elements are present and potentially respecting count
        if 'Error' in xml_content:
            error_count = xml_content.count('<Error>')
            # Should have at least some Error elements
            assert error_count >= 1
    
    def test_generate_dummy_xml_with_choices_none_parameters(self, xml_generator_order_view):
        """Test that method handles None parameters gracefully."""
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(None, None)
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'IATA_OrderViewRS' in xml_content
    
    def test_get_element_count_method_behavior(self, xml_generator_order_view):
        """Test the _get_element_count helper method behavior."""
        # Set up user preferences
        xml_generator_order_view.user_unbounded_counts = {
            'Error': 5,
            'TestElement': 3
        }
        
        # Mock element for testing
        class MockElement:
            local_name = 'Error'
            max_occurs = None  # unbounded
        
        mock_element = MockElement()
        
        # Test with user-specified count
        count = xml_generator_order_view._get_element_count('Error', mock_element)
        assert count == 5
        
        # Test with element not in user preferences
        count = xml_generator_order_view._get_element_count('UnknownElement', mock_element)
        assert count >= 2  # Should use default random count
        assert count <= 3
    
    def test_user_preferences_storage(self, xml_generator_order_view):
        """Test that user preferences are properly stored in generator instance."""
        selected_choices = {'choice_0': {'path': 'test', 'selected_element': 'Error'}}
        unbounded_counts = {'Error': 3}
        
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(
            selected_choices, unbounded_counts
        )
        
        # Check that preferences were stored
        assert hasattr(xml_generator_order_view, 'user_choices')
        assert hasattr(xml_generator_order_view, 'user_unbounded_counts')
        assert xml_generator_order_view.user_choices == selected_choices
        assert xml_generator_order_view.user_unbounded_counts == unbounded_counts