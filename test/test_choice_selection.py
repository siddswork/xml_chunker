"""
Test cases for choice selection critical fixes.
"""

import pytest
import os
from utils.xml_generator import XMLGenerator


class TestChoiceSelection:
    """Test choice selection functionality."""
    
    def test_choice_detection(self, temp_xsd_dir):
        """Test that choice elements are correctly detected."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        root_elements = list(generator.schema.elements.keys())
        root_element = generator.schema.elements[root_elements[0]]
        
        choice_elements = generator._get_choice_elements(root_element)
        choice_names = [e.local_name for e in choice_elements]
        
        # Should detect Error and Response as choice elements
        assert 'Error' in choice_names
        assert 'Response' in choice_names
        assert len(choice_names) == 2
    
    def test_response_choice_selection(self, temp_xsd_dir):
        """Test that Response choice is correctly selected."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Response'
            }
        }
        
        root_elements = list(generator.schema.elements.keys())
        root_element = generator.schema.elements[root_elements[0]]
        choice_elements = generator._get_choice_elements(root_element)
        
        generator.user_choices = selected_choices
        selected = generator._select_choice_element(choice_elements, 'IATA_OrderViewRS')
        
        assert selected is not None
        assert selected.local_name == 'Response'
    
    def test_error_choice_selection(self, temp_xsd_dir):
        """Test that Error choice is correctly selected."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS', 
                'selected_element': 'Error'
            }
        }
        
        root_elements = list(generator.schema.elements.keys())
        root_element = generator.schema.elements[root_elements[0]]
        choice_elements = generator._get_choice_elements(root_element)
        
        generator.user_choices = selected_choices
        selected = generator._select_choice_element(choice_elements, 'IATA_OrderViewRS')
        
        assert selected is not None
        assert selected.local_name == 'Error'
    
    def test_default_choice_selection(self, temp_xsd_dir):
        """Test default choice selection when no preference given."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        root_elements = list(generator.schema.elements.keys())
        root_element = generator.schema.elements[root_elements[0]]
        choice_elements = generator._get_choice_elements(root_element)
        
        # No user choices set
        selected = generator._select_choice_element(choice_elements, 'IATA_OrderViewRS')
        
        assert selected is not None
        assert selected.local_name == 'Error'  # Should default to first element
    
    def test_response_xml_generation(self, temp_xsd_dir):
        """Test that Response choice generates Response XML."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Response'
            }
        }
        
        xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
        
        # Should contain Response element, not Error
        assert '<Response>' in xml_content or '<Response ' in xml_content
        assert '<Error>' not in xml_content and '<Error ' not in xml_content
    
    def test_error_xml_generation(self, temp_xsd_dir):
        """Test that Error choice generates Error XML."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Error'
            }
        }
        
        xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
        
        # Should contain Error element, not Response
        assert '<Error>' in xml_content or '<Error ' in xml_content
        assert '<Response>' not in xml_content and '<Response ' not in xml_content
    
    def test_choice_exclusivity(self, temp_xsd_dir):
        """Test that only one choice element is generated, not both."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Response'
            }
        }
        
        xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
        
        # Count occurrences
        error_count = xml_content.count('<Error>')
        response_count = xml_content.count('<Response>')
        
        # Should have Response but no Error
        assert response_count > 0
        assert error_count == 0
        
        # Test the opposite
        selected_choices['choice_0']['selected_element'] = 'Error'
        xml_content = generator.generate_dummy_xml_with_choices(selected_choices)
        
        error_count = xml_content.count('<Error>')
        response_count = xml_content.count('<Response>')
        
        assert error_count > 0
        assert response_count == 0


class TestNullChecks:
    """Test null value handling."""
    
    def test_max_occurs_none_handling(self, temp_xsd_dir):
        """Test that max_occurs=None is handled correctly."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        # This should not raise any TypeError about None comparison
        xml_content = generator.generate_dummy_xml()
        assert xml_content is not None
        assert '<?xml version="1.0"' in xml_content
    
    def test_element_without_max_occurs(self, temp_xsd_dir):
        """Test handling of elements without max_occurs attribute."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
        generator = XMLGenerator(xsd_path)
        
        # Should handle elements that might not have max_occurs properly
        xml_content = generator.generate_dummy_xml()
        assert xml_content is not None
        assert '<?xml version="1.0"' in xml_content


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_invalid_xsd_path(self):
        """Test handling of invalid XSD path."""
        with pytest.raises(ValueError, match="XSD file not found"):
            XMLGenerator("nonexistent.xsd")
    
    def test_malformed_xsd_content(self, tmp_path):
        """Test handling of malformed XSD content."""
        malformed_xsd = tmp_path / "malformed.xsd"
        malformed_xsd.write_text("invalid xml content")
        
        with pytest.raises(ValueError, match="Invalid XSD schema"):
            XMLGenerator(str(malformed_xsd))
    
    def test_xml_generation_with_corrupted_schema(self, temp_xsd_dir):
        """Test XML generation gracefully handles schema issues."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        # Simulate corrupted schema by removing critical data
        generator.schema = None
        
        xml_content = generator.generate_dummy_xml()
        assert '<error>' in xml_content
        assert 'Schema not loaded or is None' in xml_content


class TestMemoryManagement:
    """Test memory management and cleanup."""
    
    def test_processed_types_cleanup(self, temp_xsd_dir):
        """Test that processed_types set is properly cleaned up."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        # Generate XML multiple times
        for _ in range(3):
            xml_content = generator.generate_dummy_xml()
            assert xml_content is not None
            
        # processed_types should be reset for each generation
        assert len(generator.processed_types) == 0
    
    def test_circular_reference_protection(self, temp_xsd_dir):
        """Test that circular references are properly detected and handled."""
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        generator = XMLGenerator(xsd_path)
        
        xml_content = generator.generate_dummy_xml()
        
        # Should not contain excessive recursion indicators
        assert xml_content.count("Maximum depth reached") == 0
        assert xml_content.count("Circular reference") == 0
        assert len(xml_content) < 100000  # Reasonable size limit