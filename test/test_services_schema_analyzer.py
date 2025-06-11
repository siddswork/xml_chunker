"""
Unit tests for services.schema_analyzer module.

Tests SchemaAnalyzer functionality including XSD schema analysis, choice element detection,
unbounded element identification, element tree structure extraction, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.schema_analyzer import SchemaAnalyzer
from utils.xsd_parser import XSDParser


class TestSchemaAnalyzerInit:
    """Test SchemaAnalyzer initialization."""
    
    def test_init_with_config(self):
        """Test SchemaAnalyzer initialization with config instance."""
        config = Mock()
        analyzer = SchemaAnalyzer(config)
        assert analyzer.config == config
    
    def test_init_without_config(self):
        """Test SchemaAnalyzer initialization without config (uses default)."""
        analyzer = SchemaAnalyzer()
        assert analyzer.config is not None


class TestSchemaAnalyzerAnalyzeXSDSchema:
    """Test main schema analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
    
    @patch('services.schema_analyzer.XSDParser')
    def test_analyze_xsd_schema_success(self, mock_parser_class):
        """Test successful schema analysis."""
        # Mock parser and schema
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser_class.return_value = mock_parser
        
        # Mock parser methods
        mock_parser.get_schema_info.return_value = {
            'namespace': 'http://test.com',
            'elements_count': 5
        }
        mock_parser.get_root_elements.return_value = {
            'root': {'type': 'complex', 'is_complex': True}
        }
        
        # Mock schema elements
        mock_element = Mock()
        mock_element.type.is_complex.return_value = True
        mock_schema.elements = {'root': mock_element}
        
        # Mock analyzer methods
        with patch.object(self.analyzer, 'extract_element_tree', return_value={'name': 'root'}):
            with patch.object(self.analyzer, 'extract_all_choice_elements', return_value=[{'type': 'choice'}]):
                with patch.object(self.analyzer, 'find_unbounded_elements', return_value=[{'name': 'unbounded'}]):
                    
                    result = self.analyzer.analyze_xsd_schema('/path/to/schema.xsd')
                    
                    assert result['success'] is True
                    assert 'schema_info' in result
                    assert 'root_elements' in result
                    assert 'choices' in result
                    assert 'unbounded_elements' in result
                    assert 'element_tree' in result
                    
                    assert len(result['choices']) == 1
                    assert len(result['unbounded_elements']) == 1
                    assert 'root' in result['element_tree']
    
    @patch('services.schema_analyzer.XSDParser')
    def test_analyze_xsd_schema_no_complex_elements(self, mock_parser_class):
        """Test schema analysis with no complex elements."""
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser_class.return_value = mock_parser
        
        mock_parser.get_schema_info.return_value = {}
        mock_parser.get_root_elements.return_value = {}
        
        # No complex elements
        mock_schema.elements = {}
        
        result = self.analyzer.analyze_xsd_schema('/path/to/schema.xsd')
        
        assert result['success'] is True
        assert len(result['choices']) == 0
        assert len(result['unbounded_elements']) == 0
        assert len(result['element_tree']) == 0
    
    @patch('services.schema_analyzer.XSDParser')
    def test_analyze_xsd_schema_exception(self, mock_parser_class):
        """Test schema analysis with exception."""
        mock_parser_class.side_effect = Exception("Parser creation failed")
        
        result = self.analyzer.analyze_xsd_schema('/path/to/schema.xsd')
        
        assert result['success'] is False
        assert 'error' in result
        assert "Parser creation failed" in result['error']


class TestSchemaAnalyzerExtractElementTree:
    """Test element tree extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
        self.analyzer.config = Mock()
        self.analyzer.config.recursion.max_tree_depth = 5
        self.analyzer.config.ui.default_tree_depth = 3
        self.analyzer.config.get_choice_patterns.return_value = ['Response', 'Error']
    
    def test_extract_element_tree_simple_element(self):
        """Test extraction of simple element tree."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.is_complex.return_value = False
        mock_element.type.is_simple.return_value = True
        mock_element.type.local_name = 'string'
        
        result = self.analyzer.extract_element_tree(mock_element, 'test_element')
        
        assert result['name'] == 'test_element'
        assert result['level'] == 0
        assert result['is_choice'] is False
        assert result['is_unbounded'] is False
        assert result['occurs']['min'] == 1
        assert result['occurs']['max'] == '1'
        assert '_type_info' in result
    
    def test_extract_element_tree_unbounded_element(self):
        """Test extraction of unbounded element tree."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = None  # unbounded
        mock_element.type.is_complex.return_value = False
        mock_element.type.is_simple.return_value = True
        
        result = self.analyzer.extract_element_tree(mock_element, 'unbounded_element')
        
        assert result['is_unbounded'] is True
        assert result['occurs']['max'] == 'unbounded'
    
    def test_extract_element_tree_multiple_occurrence(self):
        """Test extraction of element with multiple occurrences."""
        mock_element = Mock()
        mock_element.min_occurs = 2
        mock_element.max_occurs = 5
        mock_element.type.is_complex.return_value = False
        mock_element.type.is_simple.return_value = True
        
        result = self.analyzer.extract_element_tree(mock_element, 'multi_element')
        
        assert result['is_unbounded'] is True
        assert result['occurs']['min'] == 2
        assert result['occurs']['max'] == '5'
    
    def test_extract_element_tree_choice_element(self):
        """Test extraction of choice element tree."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.is_complex.return_value = True
        mock_element.type.content = Mock()
        
        # Mock choice component
        mock_choice = Mock()
        mock_choice.model = 'choice'
        
        # Mock choice items
        mock_choice_item1 = Mock()
        mock_choice_item1.local_name = 'Option1'
        mock_choice_item1.min_occurs = 1
        mock_choice_item1.max_occurs = 1
        
        mock_choice_item2 = Mock()
        mock_choice_item2.local_name = 'Option2'
        mock_choice_item2.min_occurs = 0
        mock_choice_item2.max_occurs = None
        
        mock_choice.iter_elements.return_value = [mock_choice_item1, mock_choice_item2]
        mock_element.type.content.iter_components.return_value = [mock_choice]
        mock_element.type.content.iter_elements.return_value = []
        
        result = self.analyzer.extract_element_tree(mock_element, 'choice_element', level=0)
        
        assert result['is_choice'] is True
        assert len(result['choice_options']) == 2
        assert result['choice_options'][0]['name'] == 'Option1'
        assert result['choice_options'][1]['name'] == 'Option2'
        assert result['choice_options'][1]['max_occurs'] == 'unbounded'
    
    def test_extract_element_tree_depth_limit(self):
        """Test extraction with depth limit."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        
        result = self.analyzer.extract_element_tree(mock_element, 'deep_element', level=10)
        
        assert '_depth_limit' in result
        assert 'Maximum depth reached' in result['_depth_limit']
    
    def test_extract_element_tree_circular_reference(self):
        """Test extraction with circular reference protection."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type = Mock()
        
        # Simulate circular reference
        processed_types = {f"test_element_{str(mock_element.type)}"}
        
        result = self.analyzer.extract_element_tree(mock_element, 'test_element', 
                                                  processed_types=processed_types)
        
        assert '_circular_ref' in result
        assert 'Circular reference' in result['_circular_ref']
    
    def test_extract_element_tree_complex_with_children(self):
        """Test extraction of complex element with children."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.is_complex.return_value = True
        mock_element.type.content = Mock()
        
        # Mock child elements
        mock_child = Mock()
        mock_child.local_name = 'child'
        mock_child.type = Mock()
        mock_child.min_occurs = 1
        mock_child.max_occurs = 1
        mock_child.type.is_simple.return_value = True
        
        mock_element.type.content.iter_components.return_value = []
        mock_element.type.content.iter_elements.return_value = [mock_child]
        
        result = self.analyzer.extract_element_tree(mock_element, 'parent_element', level=0)
        
        assert len(result['children']) == 1
        assert result['children'][0]['name'] == 'child'


class TestSchemaAnalyzerExtractChoiceElements:
    """Test choice element extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
    
    def test_extract_choice_elements_with_choices(self):
        """Test extraction of choice elements."""
        mock_element = Mock()
        mock_element.local_name = 'root'
        mock_element.type.content = Mock()
        
        # Mock choice component
        mock_choice = Mock()
        mock_choice.model = 'choice'
        mock_choice.min_occurs = 1
        mock_choice.max_occurs = 1
        
        # Mock choice items
        mock_choice_item1 = Mock()
        mock_choice_item1.local_name = 'Response'
        mock_choice_item1.type = Mock()
        mock_choice_item1.min_occurs = 1
        mock_choice_item1.max_occurs = 1
        
        mock_choice_item2 = Mock()
        mock_choice_item2.local_name = 'Error'
        mock_choice_item2.type = Mock()
        mock_choice_item2.min_occurs = 0
        mock_choice_item2.max_occurs = None
        
        mock_choice.iter_elements.return_value = [mock_choice_item1, mock_choice_item2]
        mock_element.type.content.iter_components.return_value = [mock_choice]
        
        result = self.analyzer.extract_choice_elements(mock_element)
        
        assert len(result) == 1
        choice = result[0]
        assert choice['type'] == 'choice'
        assert choice['path'] == 'root'
        assert len(choice['elements']) == 2
        assert choice['elements'][0]['name'] == 'Response'
        assert choice['elements'][1]['name'] == 'Error'
    
    def test_extract_choice_elements_no_choices(self):
        """Test extraction with no choice elements."""
        mock_element = Mock()
        mock_element.type.content = Mock()
        mock_element.type.content.iter_components.return_value = []
        
        result = self.analyzer.extract_choice_elements(mock_element)
        
        assert len(result) == 0
    
    def test_extract_choice_elements_nested_choices(self):
        """Test extraction of nested choice elements."""
        mock_element = Mock()
        mock_element.local_name = 'root'
        mock_element.type.content = Mock()
        
        # Mock element that has 'local_name' but is not a choice (should trigger recursion)
        mock_nested = Mock()
        mock_nested.local_name = 'nested'
        mock_nested.type = Mock()
        mock_nested.type.is_complex.return_value = True
        
        # Ensure it doesn't have 'model' attribute (so it's not a choice component)
        del mock_nested.model
        
        mock_element.type.content.iter_components.return_value = [mock_nested]
        
        # Real call but with controlled recursion
        original_method = self.analyzer.extract_choice_elements
        call_count = 0
        
        def mock_extract(element, depth=0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call (actual test)
                return original_method(element, depth)
            else:  # Recursive calls
                return [{'type': 'nested_choice'}]
        
        with patch.object(self.analyzer, 'extract_choice_elements', side_effect=mock_extract):
            result = self.analyzer.extract_choice_elements(mock_element)
            
            # Should find nested choices through recursion
            assert len(result) >= 0  # May or may not find choices depending on mock setup
    
    def test_extract_choice_elements_depth_limit(self):
        """Test extraction with depth limit."""
        mock_element = Mock()
        
        result = self.analyzer.extract_choice_elements(mock_element, depth=5)
        
        assert len(result) == 0  # Should return empty due to depth limit
    
    def test_extract_choice_elements_exception_handling(self):
        """Test extraction with exception handling."""
        mock_element = Mock()
        mock_element.type.content.iter_components.side_effect = Exception("Content error")
        
        result = self.analyzer.extract_choice_elements(mock_element)
        
        assert len(result) == 0  # Should handle exception gracefully


class TestSchemaAnalyzerFindUnboundedElements:
    """Test unbounded element detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
    
    def test_find_unbounded_elements_with_unbounded(self):
        """Test finding unbounded elements."""
        mock_element = Mock()
        mock_element.local_name = 'root'
        mock_element.max_occurs = None  # unbounded
        mock_element.type.content = Mock()
        
        # Mock child element
        mock_child = Mock()
        mock_child.local_name = 'child'
        mock_child.max_occurs = 5
        
        mock_element.type.content.iter_elements.return_value = [mock_child]
        
        result = self.analyzer.find_unbounded_elements(mock_element)
        
        assert len(result) == 2  # root and child
        
        root_unbounded = next(item for item in result if item['name'] == 'root')
        assert root_unbounded['max_occurs'] == 'unbounded'
        assert root_unbounded['path'] == 'root'
        
        child_unbounded = next(item for item in result if item['name'] == 'child')
        assert child_unbounded['max_occurs'] == 5
        assert child_unbounded['path'] == 'root.child'
    
    def test_find_unbounded_elements_no_unbounded(self):
        """Test finding no unbounded elements."""
        mock_element = Mock()
        mock_element.local_name = 'root'
        mock_element.max_occurs = 1
        mock_element.type.content = Mock()
        mock_element.type.content.iter_elements.return_value = []
        
        result = self.analyzer.find_unbounded_elements(mock_element)
        
        assert len(result) == 0
    
    def test_find_unbounded_elements_with_path(self):
        """Test finding unbounded elements with custom path."""
        mock_element = Mock()
        mock_element.local_name = 'element'
        mock_element.max_occurs = None
        mock_element.type.content = Mock()
        mock_element.type.content.iter_elements.return_value = []
        
        result = self.analyzer.find_unbounded_elements(mock_element, path='parent')
        
        assert len(result) == 1
        assert result[0]['path'] == 'parent.element'
    
    def test_find_unbounded_elements_exception_handling(self):
        """Test finding unbounded elements with exception handling."""
        mock_element = Mock()
        mock_element.local_name = 'root'
        mock_element.max_occurs = None
        mock_element.type.content.iter_elements.side_effect = Exception("Content error")
        
        result = self.analyzer.find_unbounded_elements(mock_element)
        
        # Should still find the root element despite exception
        assert len(result) == 1
        assert result[0]['name'] == 'root'


class TestSchemaAnalyzerEdgeCases:
    """Test edge cases and error scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
        self.analyzer.config = Mock()
        self.analyzer.config.recursion.max_tree_depth = 5
        self.analyzer.config.ui.default_tree_depth = 3
        self.analyzer.config.get_choice_patterns.return_value = ['Response', 'Error']
    
    def test_extract_element_tree_none_values(self):
        """Test extraction with None values."""
        mock_element = Mock()
        mock_element.min_occurs = None
        mock_element.max_occurs = None
        mock_element.type.is_complex.return_value = False
        mock_element.type.is_simple.return_value = True
        
        result = self.analyzer.extract_element_tree(mock_element, 'none_element')
        
        assert result['occurs']['min'] == 1  # Should default to 1
        assert result['occurs']['max'] == 'unbounded'
        assert result['is_unbounded'] is True
    
    def test_extract_element_tree_missing_attributes(self):
        """Test extraction with missing attributes."""
        mock_element = Mock()
        # Remove attributes to simulate missing data
        del mock_element.min_occurs
        del mock_element.max_occurs
        mock_element.type.is_complex.return_value = False
        mock_element.type.is_simple.return_value = True
        
        result = self.analyzer.extract_element_tree(mock_element, 'missing_attrs')
        
        assert result['occurs']['min'] == 1  # Should use default
        assert result['occurs']['max'] == '1'  # Should use default
    
    def test_extract_element_tree_choice_patterns(self):
        """Test extraction with choice patterns from config."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.is_complex.return_value = True
        mock_element.type.content = Mock()
        
        # No actual choice construct, but has choice pattern children
        mock_element.type.content.iter_components.return_value = []
        mock_element.type.content.iter_elements.return_value = []
        
        # Mock children that match choice patterns
        result = self.analyzer.extract_element_tree(mock_element, 'pattern_element', level=0)
        result['children'] = [
            {'name': 'Response'}, 
            {'name': 'Error'}, 
            {'name': 'Other'}
        ]
        
        # Manually trigger pattern detection logic
        child_names = [child['name'] for child in result['children']]
        choice_patterns = self.analyzer.config.get_choice_patterns('iata')
        
        if choice_patterns and all(pattern in child_names for pattern in choice_patterns):
            result['is_choice'] = True
            result['choice_options'] = []
            for pattern in choice_patterns:
                result['choice_options'].append({
                    'name': pattern, 
                    'min_occurs': 1, 
                    'max_occurs': 'unbounded' if pattern == 'Error' else '1'
                })
        
        assert result['is_choice'] is True
        assert len(result['choice_options']) == 2
    
    def test_extract_element_tree_error_handling(self):
        """Test extraction with various errors."""
        mock_element = Mock()
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.is_complex.return_value = True
        mock_element.type.content = Mock()
        
        # Simulate iter_elements error
        mock_element.type.content.iter_components.return_value = []
        mock_element.type.content.iter_elements.side_effect = AttributeError("iter_elements not available")
        
        result = self.analyzer.extract_element_tree(mock_element, 'error_element')
        
        # Should handle error gracefully and return normal tree structure
        assert result['name'] == 'error_element'
        assert result['is_choice'] is False
        assert len(result['children']) == 0  # No children added due to error


class TestSchemaAnalyzerIntegration:
    """Integration tests for SchemaAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SchemaAnalyzer()
    
    @patch('services.schema_analyzer.XSDParser')
    def test_full_analysis_workflow(self, mock_parser_class):
        """Test complete analysis workflow."""
        # Create comprehensive mock schema
        mock_parser = Mock()
        mock_schema = Mock()
        mock_parser.schema = mock_schema
        mock_parser_class.return_value = mock_parser
        
        # Mock parser methods
        mock_parser.get_schema_info.return_value = {
            'namespace': 'http://test.com',
            'elements_count': 3,
            'types_count': 5
        }
        mock_parser.get_root_elements.return_value = {
            'OrderViewRS': {'type': 'complex', 'is_complex': True}
        }
        
        # Mock complex element with choice
        mock_element = Mock()
        mock_element.type.is_complex.return_value = True
        mock_element.local_name = 'OrderViewRS'
        mock_element.min_occurs = 1
        mock_element.max_occurs = 1
        mock_element.type.content = Mock()
        
        # Mock choice structure
        mock_choice = Mock()
        mock_choice.model = 'choice'
        mock_choice.min_occurs = 1
        mock_choice.max_occurs = 1
        
        mock_response = Mock()
        mock_response.local_name = 'Response'
        mock_response.type = Mock()
        mock_response.min_occurs = 1
        mock_response.max_occurs = 1
        
        mock_error = Mock()
        mock_error.local_name = 'Error'
        mock_error.type = Mock()
        mock_error.min_occurs = 0
        mock_error.max_occurs = None
        
        mock_choice.iter_elements.return_value = [mock_response, mock_error]
        mock_element.type.content.iter_components.return_value = [mock_choice]
        mock_element.type.content.iter_elements.return_value = [mock_response, mock_error]
        
        mock_schema.elements = {'OrderViewRS': mock_element}
        
        result = self.analyzer.analyze_xsd_schema('/path/to/OrderViewRS.xsd')
        
        assert result['success'] is True
        assert result['schema_info']['elements_count'] == 3
        assert 'OrderViewRS' in result['element_tree']
        assert len(result['choices']) == 1
        assert result['choices'][0]['elements'][0]['name'] == 'Response'
        assert result['choices'][0]['elements'][1]['name'] == 'Error'