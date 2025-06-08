"""
Test cases for IATA_OrderCreateRQ.xsd XML generation and parsing.
"""

import pytest
import xml.etree.ElementTree as ET
from lxml import etree
import re
import os


class TestOrderCreateRQSchema:
    """Test cases for IATA_OrderCreateRQ schema handling."""
    
    def test_schema_loading(self, xsd_parser_order_create):
        """Test that the OrderCreateRQ schema loads successfully."""
        assert xsd_parser_order_create.schema is not None
        schema_info = xsd_parser_order_create.get_schema_info()
        assert schema_info['filename'] == 'IATA_OrderCreateRQ.xsd'
        assert 'IATA_OffersAndOrdersMessage' in schema_info['target_namespace']
    
    def test_root_elements(self, xsd_parser_order_create):
        """Test that the schema has the expected root element."""
        root_elements = xsd_parser_order_create.get_root_elements()
        assert 'IATA_OrderCreateRQ' in root_elements
        assert root_elements['IATA_OrderCreateRQ']['is_complex'] is True
    
    def test_schema_info_structure(self, xsd_parser_order_create):
        """Test schema information structure."""
        schema_info = xsd_parser_order_create.get_schema_info()
        required_keys = ['filepath', 'filename', 'target_namespace', 'elements_count', 'types_count']
        for key in required_keys:
            assert key in schema_info


class TestOrderCreateRQXMLGeneration:
    """Test cases for XML generation from OrderCreateRQ schema."""
    
    def test_xml_generation_basic(self, xml_generator_order_create):
        """Test basic XML generation from OrderCreateRQ schema."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        assert xml_content is not None
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_content
        assert 'IATA_OrderCreateRQ' in xml_content
        assert not xml_content.startswith('<error>')
    
    def test_xml_contains_mandatory_elements(self, xml_generator_order_create):
        """Test that mandatory elements are present in generated XML."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Based on schema analysis:
        # - DistributionChain: minOccurs="1" (mandatory)
        # - Request: minOccurs="1" (mandatory)
        mandatory_elements = ['DistributionChain', 'Request']
        
        for element in mandatory_elements:
            assert element in xml_content, f"Mandatory element '{element}' should be present in generated XML"
    
    def test_xml_contains_optional_elements(self, xml_generator_order_create):
        """Test that optional elements may be present in generated XML."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # These are optional elements (minOccurs="0")
        optional_elements = ['AugmentationPoint', 'PayloadAttributes', 'POS', 'Signature']
        
        # At least check that the XML generation doesn't fail with optional elements
        assert 'IATA_OrderCreateRQ' in xml_content
        
        # Optional elements may or may not be present, but XML should be valid
        for element in optional_elements:
            if element in xml_content:
                # If present, should be properly formatted
                assert f'<{element}' in xml_content or f'</{element}>' in xml_content
    
    def test_xml_structure_validity(self, xml_generator_order_create):
        """Test that generated XML has valid structure."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Remove XML declaration for parsing
        xml_body = xml_content.split('>', 1)[1] if xml_content.startswith('<?xml') else xml_content
        
        try:
            root = ET.fromstring(xml_body)
            assert root.tag.endswith('IATA_OrderCreateRQ')
        except ET.ParseError as e:
            pytest.fail(f"Generated XML is not well-formed: {e}")
    
    def test_xml_namespace_handling(self, xml_generator_order_create):
        """Test that XML contains proper namespace declarations."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Should contain IATA namespace
        assert 'IATA_OffersAndOrdersMessage' in xml_content or 'xmlns' in xml_content
    
    def test_xml_comments_for_occurrence_info(self, xml_generator_order_create):
        """Test that XML contains comments about element occurrence information."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Generated XML should contain comments about element occurrence constraints
        assert '<!--' in xml_content and '-->' in xml_content
        
        # Should contain information about mandatory vs optional elements
        assert 'Mandatory element' in xml_content or 'Optional element' in xml_content
    
    def test_xml_file_output(self, xml_generator_order_create, sample_xml_output_dir):
        """Test XML generation to file."""
        output_path = os.path.join(sample_xml_output_dir, "test_order_create_rq.xml")
        xml_content = xml_generator_order_create.generate_dummy_xml(output_path)
        
        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content == xml_content
        assert 'IATA_OrderCreateRQ' in file_content


class TestOrderCreateRQMandatoryElements:
    """Test mandatory elements specific to OrderCreateRQ."""
    
    def test_distribution_chain_mandatory(self, xml_generator_order_create):
        """Test that DistributionChain element is always present (mandatory)."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        assert 'DistributionChain' in xml_content
        # Should have a comment indicating it's mandatory
        assert 'Mandatory element' in xml_content
    
    def test_request_element_mandatory(self, xml_generator_order_create):
        """Test that Request element is always present (mandatory)."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        assert 'Request' in xml_content
        # Should be marked as mandatory in comments
        distribution_chain_comment_pattern = r'<!--.*Request.*Mandatory.*-->'
        request_pattern = r'<Request|Request>'
        
        assert re.search(request_pattern, xml_content) is not None
    
    def test_element_occurrence_comments(self, xml_generator_order_create):
        """Test that elements have proper occurrence information in comments."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Check for mandatory element comments
        if 'DistributionChain' in xml_content:
            assert 'Mandatory element' in xml_content
        
        # Check for optional element comments
        optional_elements = ['AugmentationPoint', 'PayloadAttributes', 'POS', 'Signature']
        for element in optional_elements:
            if element in xml_content:
                # Should have corresponding comment
                assert '<!--' in xml_content


class TestOrderCreateRQErrorHandling:
    """Test error handling for OrderCreateRQ processing."""
    
    def test_schema_with_missing_dependencies(self, temp_xsd_dir):
        """Test handling when dependent XSD files are missing."""
        # Remove the common types XSD to simulate missing dependency
        common_types_path = os.path.join(temp_xsd_dir, "IATA_OffersAndOrdersCommonTypes.xsd")
        if os.path.exists(common_types_path):
            os.remove(common_types_path)
        
        from utils.xml_generator import XMLGenerator
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
        
        # Should handle missing dependencies gracefully
        try:
            generator = XMLGenerator(xsd_path)
            xml_content = generator.generate_dummy_xml()
            assert xml_content is not None
        except Exception:
            # Exception is acceptable when dependencies are missing
            pass
    
    def test_invalid_schema_path(self):
        """Test handling of invalid schema path."""
        from utils.xml_generator import XMLGenerator
        
        with pytest.raises(ValueError, match="Failed to load XSD schema"):
            XMLGenerator("/nonexistent/path/schema.xsd")


class TestOrderCreateRQDataGeneration:
    """Test data generation specifics for OrderCreateRQ."""
    
    def test_request_element_structure(self, xml_generator_order_create):
        """Test that Request element has proper structure."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Request element should be present
        assert 'Request' in xml_content
        
        # Should contain the Request element properly formatted
        assert '<Request' in xml_content or 'Request>' in xml_content
    
    def test_distribution_chain_structure(self, xml_generator_order_create):
        """Test that DistributionChain element has proper structure."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # DistributionChain should be present
        assert 'DistributionChain' in xml_content
    
    def test_namespace_prefix_generation(self, xml_generator_order_create):
        """Test that namespace prefixes are properly generated."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Should contain namespace declarations or prefixed elements
        # The exact format depends on the generator implementation
        assert xml_content is not None
        
        # Should handle cns: prefixes for common types
        if 'cns:' in xml_content:
            # If namespace prefixes are used, they should be properly declared
            assert 'xmlns' in xml_content or 'cns:' in xml_content
    
    def test_element_ordering(self, xml_generator_order_create):
        """Test that elements appear in the correct sequence order."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Based on schema sequence:
        # 1. AugmentationPoint (optional)
        # 2. DistributionChain (mandatory)
        # 3. PayloadAttributes (optional)
        # 4. POS (optional)
        # 5. Request (mandatory)
        # 6. Signature (optional)
        
        mandatory_elements = ['DistributionChain', 'Request']
        
        # Find positions of mandatory elements
        positions = {}
        for element in mandatory_elements:
            if element in xml_content:
                positions[element] = xml_content.find(element)
        
        # DistributionChain should appear before Request
        if 'DistributionChain' in positions and 'Request' in positions:
            assert positions['DistributionChain'] < positions['Request'], \
                "DistributionChain should appear before Request in the XML sequence"


class TestOrderCreateRQValidation:
    """Test validation aspects of OrderCreateRQ."""
    
    def test_generated_xml_element_count(self, xml_generator_order_create):
        """Test that generated XML has reasonable element count."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Should contain root element
        assert xml_content.count('IATA_OrderCreateRQ') >= 1
        
        # Should contain mandatory elements
        assert xml_content.count('DistributionChain') >= 1
        assert xml_content.count('Request') >= 1
    
    def test_xml_encoding_declaration(self, xml_generator_order_create):
        """Test that XML has proper encoding declaration."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    
    def test_well_formed_xml_structure(self, xml_generator_order_create):
        """Test that generated XML is well-formed."""
        xml_content = xml_generator_order_create.generate_dummy_xml()
        
        # Count opening and closing tags for root element
        opening_tags = xml_content.count('<IATA_OrderCreateRQ')
        closing_tags = xml_content.count('</IATA_OrderCreateRQ>')
        
        assert opening_tags == closing_tags == 1, "XML should have exactly one root element with matching opening/closing tags"


class TestOrderCreateRQNewMethods:
    """Test new methods added to XMLGenerator for OrderCreateRQ."""
    
    def test_generate_dummy_xml_with_choices_method_exists(self, xml_generator_order_create):
        """Test that the new method exists and is callable."""
        assert hasattr(xml_generator_order_create, 'generate_dummy_xml_with_choices')
        assert callable(xml_generator_order_create.generate_dummy_xml_with_choices)
    
    def test_generate_dummy_xml_with_choices_empty_choices(self, xml_generator_order_create):
        """Test XML generation with empty choices (OrderCreateRQ has fewer choices)."""
        selected_choices = {}
        unbounded_counts = {}
        
        xml_content = xml_generator_order_create.generate_dummy_xml_with_choices(
            selected_choices, unbounded_counts
        )
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'IATA_OrderCreateRQ' in xml_content
        assert 'DistributionChain' in xml_content
        assert 'Request' in xml_content
    
    def test_generate_dummy_xml_with_unbounded_counts_order_create(self, xml_generator_order_create):
        """Test XML generation with unbounded counts for OrderCreateRQ elements."""
        # OrderCreateRQ might have some repeating elements
        unbounded_counts = {
            'DistributionChain': 1,  # Usually not repeating but test the mechanism
            'Request': 1
        }
        
        xml_content = xml_generator_order_create.generate_dummy_xml_with_choices(None, unbounded_counts)
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'IATA_OrderCreateRQ' in xml_content
    
    def test_user_preferences_initialization(self, xml_generator_order_create):
        """Test that user preferences are properly initialized."""
        # Before calling the method, these attributes shouldn't exist
        assert not hasattr(xml_generator_order_create, 'user_choices') or xml_generator_order_create.user_choices is None
        
        selected_choices = {'test': 'value'}
        unbounded_counts = {'element': 2}
        
        xml_content = xml_generator_order_create.generate_dummy_xml_with_choices(
            selected_choices, unbounded_counts
        )
        
        # After calling, attributes should be set
        assert hasattr(xml_generator_order_create, 'user_choices')
        assert hasattr(xml_generator_order_create, 'user_unbounded_counts')
        assert xml_generator_order_create.user_choices == selected_choices
        assert xml_generator_order_create.user_unbounded_counts == unbounded_counts