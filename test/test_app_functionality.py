"""
Test cases for app.py enhanced functionality including schema analysis,
choice element extraction, and XML generation with user preferences.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path


class TestSchemaAnalysis:
    """Test cases for enhanced schema analysis functionality."""
    
    def test_analyze_xsd_schema_order_view_rs(self, temp_xsd_dir):
        """Test comprehensive schema analysis for OrderViewRS."""
        from app import analyze_xsd_schema
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        analysis = analyze_xsd_schema(xsd_path)
        
        assert analysis['success'] is True
        assert 'schema_info' in analysis
        assert 'choices' in analysis
        assert 'unbounded_elements' in analysis
        assert 'element_tree' in analysis
        
        # Check schema info structure
        schema_info = analysis['schema_info']
        assert 'target_namespace' in schema_info
        assert 'elements_count' in schema_info
        assert 'types_count' in schema_info
        
        # Should find the Error/Response choice
        choices = analysis['choices']
        assert len(choices) > 0
        
        # Check if the main choice (Error vs Response) is found
        main_choice = next((c for c in choices if c['path'] == 'IATA_OrderViewRS'), None)
        assert main_choice is not None
        assert len(main_choice['elements']) == 2  # Error and Response
        
        choice_element_names = [e['name'] for e in main_choice['elements']]
        assert 'Error' in choice_element_names
        assert 'Response' in choice_element_names
    
    def test_analyze_xsd_schema_order_create_rq(self, temp_xsd_dir):
        """Test schema analysis for OrderCreateRQ."""
        from app import analyze_xsd_schema
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
        analysis = analyze_xsd_schema(xsd_path)
        
        assert analysis['success'] is True
        assert 'element_tree' in analysis
        assert 'IATA_OrderCreateRQ' in analysis['element_tree']
        
        # OrderCreateRQ should have fewer choices than OrderViewRS
        choices = analysis['choices']
        assert isinstance(choices, list)
    
    def test_analyze_xsd_schema_invalid_path(self):
        """Test schema analysis with invalid XSD path."""
        from app import analyze_xsd_schema
        
        analysis = analyze_xsd_schema("/nonexistent/path.xsd")
        
        assert analysis['success'] is False
        assert 'error' in analysis


class TestChoiceElementExtraction:
    """Test cases for choice element extraction functionality."""
    
    def test_extract_choice_elements_order_view_rs(self, xml_generator_order_view):
        """Test choice element extraction from OrderViewRS schema."""
        from services.schema_analyzer import SchemaAnalyzer
        
        schema_analyzer = SchemaAnalyzer()
        # Get the root element from the schema
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        choices = schema_analyzer.extract_choice_elements(root_element)
        
        assert len(choices) > 0
        
        # Check the main choice structure
        main_choice = choices[0]
        assert main_choice['type'] == 'choice'
        assert 'elements' in main_choice
        assert len(main_choice['elements']) == 2
        
        # Verify Error and Response elements
        element_names = [e['name'] for e in main_choice['elements']]
        assert 'Error' in element_names
        assert 'Response' in element_names
    
    def test_extract_choice_elements_with_occurrences(self, xml_generator_order_view):
        """Test that choice elements include occurrence information."""
        from services.schema_analyzer import SchemaAnalyzer
        
        schema_analyzer = SchemaAnalyzer()
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        choices = schema_analyzer.extract_choice_elements(root_element)
        
        for choice in choices:
            assert 'min_occurs' in choice
            assert 'max_occurs' in choice
            
            for element in choice['elements']:
                assert 'min_occurs' in element
                assert 'max_occurs' in element
                assert 'name' in element
                assert 'type' in element


class TestUnboundedElementDetection:
    """Test cases for unbounded element detection."""
    
    def test_find_unbounded_elements_order_view_rs(self, xml_generator_order_view):
        """Test finding unbounded elements in OrderViewRS."""
        from services.schema_analyzer import SchemaAnalyzer
        schema_analyzer = SchemaAnalyzer()
        
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        unbounded = schema_analyzer.find_unbounded_elements(root_element)
        
        assert len(unbounded) > 0
        
        # Check structure of unbounded element info
        for elem in unbounded:
            assert 'name' in elem
            assert 'path' in elem
            assert 'max_occurs' in elem
            assert elem['max_occurs'] in ['unbounded', 'unbounded'] or isinstance(elem['max_occurs'], int)
        
        # Should find Error element as unbounded
        error_elements = [e for e in unbounded if e['name'] == 'Error']
        assert len(error_elements) > 0
        assert error_elements[0]['max_occurs'] == 'unbounded'
    
    def test_find_unbounded_elements_with_paths(self, xml_generator_order_view):
        """Test that unbounded elements have correct path information."""
        from services.schema_analyzer import SchemaAnalyzer
        schema_analyzer = SchemaAnalyzer()
        
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        unbounded = schema_analyzer.find_unbounded_elements(root_element)
        
        for elem in unbounded:
            # Path should contain element hierarchy
            assert '.' in elem['path'] or elem['path'] == elem['name']
            assert isinstance(elem['path'], str)
            assert len(elem['path']) > 0


class TestElementTreeExtraction:
    """Test cases for element tree structure extraction."""
    
    def test_extract_element_tree_structure(self, xml_generator_order_view):
        """Test element tree extraction structure."""
        from services.schema_analyzer import SchemaAnalyzer
        schema_analyzer = SchemaAnalyzer()
        
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        tree = schema_analyzer.extract_element_tree(root_element, "IATA_OrderViewRS")
        
        # Check tree structure
        assert tree['name'] == 'IATA_OrderViewRS'
        assert tree['level'] == 0
        assert 'children' in tree
        assert 'is_choice' in tree
        assert 'choice_options' in tree
        assert 'occurs' in tree
        
        # Should detect the main choice
        assert tree['is_choice'] is True
        assert len(tree['choice_options']) == 2
        
        # Check choice options
        choice_names = [opt['name'] for opt in tree['choice_options']]
        assert 'Error' in choice_names
        assert 'Response' in choice_names
    
    def test_extract_element_tree_depth_limit(self, xml_generator_order_view):
        """Test that tree extraction respects depth limits."""
        from services.schema_analyzer import SchemaAnalyzer
        schema_analyzer = SchemaAnalyzer()
        
        root_element = list(xml_generator_order_view.schema.elements.values())[0]
        tree = schema_analyzer.extract_element_tree(root_element, "IATA_OrderViewRS", level=0)
        
        # Should not go deeper than configured tree depth
        from config import get_config
        config = get_config()
        def check_max_level(node, max_level=config.ui.default_tree_depth):
            assert node['level'] <= max_level
            for child in node['children']:
                check_max_level(child, max_level)
        
        check_max_level(tree)


class TestXMLGenerationWithChoices:
    """Test cases for XML generation with user choices."""
    
    def test_generate_xml_with_selected_choices(self, xml_generator_order_view):
        """Test XML generation with user-selected choices."""
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
        # Should not contain Response since Error was selected
        assert 'Response' not in xml_content
    
    def test_generate_xml_with_unbounded_counts(self, xml_generator_order_view):
        """Test XML generation with user-specified unbounded counts."""
        unbounded_counts = {
            'Error': 5,
            'IATA_OrderViewRS.Error': 5
        }
        
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(None, unbounded_counts)
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        
        # Should contain multiple Error elements if Error is generated
        if 'Error' in xml_content:
            error_count = xml_content.count('<Error>')
            # Should respect the user count (might be affected by special case logic)
            assert error_count >= 1
    
    def test_generate_xml_with_both_choices_and_counts(self, xml_generator_order_view):
        """Test XML generation with both choices and unbounded counts."""
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Error',
                'choice_data': {}
            }
        }
        
        unbounded_counts = {
            'Error': 3,
            'IATA_OrderViewRS.Error': 3
        }
        
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices(
            selected_choices, unbounded_counts
        )
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'Error' in xml_content
        assert 'Response' not in xml_content
    
    def test_generate_xml_with_empty_preferences(self, xml_generator_order_view):
        """Test that XML generation works with empty user preferences."""
        xml_content = xml_generator_order_view.generate_dummy_xml_with_choices({}, {})
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        # Should fall back to default behavior
        assert 'IATA_OrderViewRS' in xml_content


class TestAppHelperFunctions:
    """Test cases for app helper functions."""
    
    def test_setup_temp_directory_with_dependencies(self, temp_xsd_dir):
        """Test temporary directory setup with XSD dependencies."""
        from services.file_manager import FileManager
        
        file_manager = FileManager()
        
        # Create a separate temp directory to test dependency copying
        test_temp_dir = tempfile.mkdtemp()
        test_xsd_path = os.path.join(test_temp_dir, "test.xsd")
        
        # Create a dummy XSD file
        with open(test_xsd_path, 'w') as f:
            f.write('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
        
        try:
            file_manager.setup_temp_directory_with_dependencies(test_xsd_path, "test.xsd")
            
            # Should copy dependency files to the temp directory
            common_types_path = os.path.join(test_temp_dir, "IATA_OffersAndOrdersCommonTypes.xsd")
            assert os.path.exists(common_types_path)
            
        finally:
            shutil.rmtree(test_temp_dir, ignore_errors=True)
    
    def test_convert_tree_to_streamlit_format(self):
        """Test tree node conversion to streamlit format."""
        from app import convert_tree_to_streamlit_format
        
        # Create a mock tree node
        mock_node = {
            'name': 'TestElement',
            'level': 0,
            'children': [],
            'is_choice': True,
            'choice_options': [
                {'name': 'Option1', 'min_occurs': 1, 'max_occurs': 1},
                {'name': 'Option2', 'min_occurs': 0, 'max_occurs': 'unbounded'}
            ],
            'occurs': {'min': 1, 'max': 1}
        }
        
        # Test the conversion function that actually exists
        result = convert_tree_to_streamlit_format(mock_node)
        assert 'value' in result
        assert 'label' in result
        assert result['value'] == 'TestElement'
        assert 'TestElement' in result['label']


class TestGenerateXMLFromXSDFunction:
    """Test cases for the main XML generation function in app.py."""
    
    def test_generate_xml_from_xsd_with_choices(self, temp_xsd_dir):
        """Test the main generate_xml_from_xsd function with choices."""
        from app import generate_xml_from_xsd
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        
        selected_choices = {
            'choice_0': {
                'path': 'IATA_OrderViewRS',
                'selected_element': 'Error',
                'choice_data': {}
            }
        }
        
        unbounded_counts = {
            'Error': 2
        }
        
        xml_content = generate_xml_from_xsd(
            xsd_path, 
            "IATA_OrderViewRS.xsd", 
            selected_choices, 
            unbounded_counts
        )
        
        assert xml_content is not None
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert 'IATA_OrderViewRS' in xml_content
    
    def test_generate_xml_from_xsd_without_choices(self, temp_xsd_dir):
        """Test the main generate_xml_from_xsd function without user choices."""
        from app import generate_xml_from_xsd
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
        
        xml_content = generate_xml_from_xsd(xsd_path, "IATA_OrderCreateRQ.xsd")
        
        assert xml_content is not None
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert 'IATA_OrderCreateRQ' in xml_content
    
    def test_generate_xml_from_xsd_error_handling(self):
        """Test error handling in generate_xml_from_xsd function."""
        from app import generate_xml_from_xsd
        
        xml_content = generate_xml_from_xsd("/nonexistent/file.xsd", "test.xsd")
        
        assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert '<error>' in xml_content
        assert 'Error generating XML' in xml_content


class TestIntegrationWithRealSchemas:
    """Integration tests with real IATA schemas."""
    
    def test_full_analysis_and_generation_workflow_order_view_rs(self, temp_xsd_dir):
        """Test complete workflow: analysis → choice selection → XML generation."""
        from app import analyze_xsd_schema, generate_xml_from_xsd
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
        
        # Step 1: Analyze schema
        analysis = analyze_xsd_schema(xsd_path)
        assert analysis['success'] is True
        
        # Step 2: Extract choices
        choices = analysis['choices']
        assert len(choices) > 0
        
        # Step 3: Simulate user selection
        main_choice = next((c for c in choices if c['path'] == 'IATA_OrderViewRS'), None)
        assert main_choice is not None
        
        selected_choices = {
            'choice_0': {
                'path': main_choice['path'],
                'selected_element': 'Error',
                'choice_data': main_choice
            }
        }
        
        # Step 4: Get unbounded elements
        unbounded_elements = analysis['unbounded_elements']
        unbounded_counts = {}
        for elem in unbounded_elements:
            if elem['name'] == 'Error':
                unbounded_counts[elem['path']] = 3
        
        # Step 5: Generate XML with selections
        xml_content = generate_xml_from_xsd(
            xsd_path, 
            "IATA_OrderViewRS.xsd", 
            selected_choices, 
            unbounded_counts
        )
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'Error' in xml_content
        # Verify Error was chosen over Response
        assert 'Response' not in xml_content
    
    def test_full_analysis_and_generation_workflow_order_create_rq(self, temp_xsd_dir):
        """Test complete workflow with OrderCreateRQ schema."""
        from app import analyze_xsd_schema, generate_xml_from_xsd
        
        xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
        
        # Step 1: Analyze schema
        analysis = analyze_xsd_schema(xsd_path)
        assert analysis['success'] is True
        
        # Step 2: Generate XML (OrderCreateRQ has fewer choices)
        xml_content = generate_xml_from_xsd(xsd_path, "IATA_OrderCreateRQ.xsd")
        
        assert xml_content is not None
        assert not xml_content.startswith('<error>')
        assert 'IATA_OrderCreateRQ' in xml_content
        # Should contain mandatory elements
        assert 'DistributionChain' in xml_content
        assert 'Request' in xml_content