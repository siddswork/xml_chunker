"""
XML Validation Service for XML Chunker.

This module handles XML validation against XSD schemas, including
error categorization and detailed validation reporting.
"""

import os
import tempfile
from typing import Dict, Any, Optional, List
from utils.xsd_parser import XSDParser
from .file_manager import FileManager


class XMLValidator:
    """Handles XML validation against XSD schemas."""
    
    def __init__(self, config_instance=None):
        """
        Initialize the XML validator.
        
        Args:
            config_instance: Configuration instance (uses global config if None)
        """
        self.file_manager = FileManager(config_instance)
    
    def validate_xml_against_schema(
        self, 
        xml_content: str, 
        xsd_file_path: str, 
        uploaded_file_name: Optional[str] = None, 
        uploaded_file_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate generated XML against the XSD schema.
        
        Args:
            xml_content: XML content to validate
            xsd_file_path: Path to the XSD schema file (may not exist)
            uploaded_file_name: Original uploaded file name
            uploaded_file_content: Original uploaded file content
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Create a temporary XML file for validation
            temp_xml_path = self.file_manager.create_temp_file(xml_content, '.xml')
            
            # Create temporary XSD file if the original path doesn't exist
            temp_xsd_path = xsd_file_path
            temp_xsd_cleanup = False
            
            if not os.path.exists(xsd_file_path) and uploaded_file_content and uploaded_file_name:
                # Recreate the temp XSD file and dependencies
                temp_xsd_path, temp_dir = self.file_manager.write_temp_xsd_with_dependencies(
                    uploaded_file_content, uploaded_file_name
                )
                temp_xsd_cleanup = True
            
            try:
                # Load the schema and validate
                parser = XSDParser(temp_xsd_path)
                
                # Get detailed validation results using xmlschema
                import xmlschema
                errors = list(parser.schema.iter_errors(temp_xml_path))
                
                # Categorize validation errors for better reporting
                categorized_errors = self._categorize_errors(errors)
                
                # Basic validation result
                is_valid = parser.validate_xml(temp_xml_path)
                
                return {
                    'is_valid': is_valid,
                    'total_errors': len(errors),
                    'error_breakdown': {
                        'enumeration_errors': len(categorized_errors['enumeration_errors']),
                        'boolean_errors': len(categorized_errors['boolean_errors']),
                        'pattern_errors': len(categorized_errors['pattern_errors']),
                        'structural_errors': len(categorized_errors['structural_errors'])
                    },
                    'categorized_errors': categorized_errors,
                    'detailed_errors': errors[:10],  # First 10 errors for display
                    'success': True
                }
                
            finally:
                # Cleanup temporary XML file
                self.file_manager.cleanup_temp_file(temp_xml_path)
                
                # Cleanup temporary XSD directory if we created it
                if temp_xsd_cleanup and 'temp_dir' in locals():
                    self.file_manager.cleanup_temp_directory(temp_dir)
                    
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'success': False
            }
    
    def _categorize_errors(self, errors: List) -> Dict[str, List]:
        """
        Categorize validation errors for better reporting.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Dictionary with categorized errors
        """
        enumeration_errors = [e for e in errors if 'XsdEnumerationFacets' in str(e.message)]
        boolean_errors = [e for e in errors if "with XsdAtomicBuiltin(name='xs:boolean')" in str(e.message)]
        pattern_errors = [e for e in errors if 'pattern' in str(e.message).lower()]
        structural_errors = [e for e in errors if e not in enumeration_errors + boolean_errors + pattern_errors]
        
        return {
            'enumeration_errors': enumeration_errors,
            'boolean_errors': boolean_errors,
            'pattern_errors': pattern_errors,
            'structural_errors': structural_errors
        }
    
    def format_validation_error(self, error) -> Dict[str, Any]:
        """
        Format a validation error for display.
        
        Args:
            error: xmlschema validation error object
            
        Returns:
            Dictionary with formatted error information
        """
        try:
            # Extract path information
            path = getattr(error, 'path', 'Unknown path')
            
            # Clean up the error message
            message = str(error.message)
            
            # Extract element name from path if possible
            element_name = 'Unknown'
            if path and isinstance(path, str):
                if '/' in path:
                    element_name = path.split('/')[-1]
                    # Remove namespace prefixes and array indices
                    if ':' in element_name:
                        element_name = element_name.split(':')[-1]
                    element_name = element_name.split('[')[0]  # Remove array indices like [1]
            
            return {
                'message': message,
                'path': path,
                'element_name': element_name,
                'line': getattr(error, 'lineno', None)
            }
        except Exception:
            return {
                'message': str(error),
                'path': 'Unknown',
                'element_name': 'Unknown',
                'line': None
            }