"""
XSD Parser module for XML Chunker.

This module provides utilities for parsing XSD schema files.
"""

import os
import xmlschema
from typing import Dict, Any, Optional


class XSDParser:
    """Class for parsing XSD schema files."""
    
    def __init__(self, xsd_path: str):
        """
        Initialize the XSD parser.
        
        Args:
            xsd_path: Path to the XSD schema file
        """
        self.xsd_path = xsd_path
        self.schema = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the XSD schema from the file."""
        try:
            self.schema = xmlschema.XMLSchema(self.xsd_path)
        except Exception as e:
            raise ValueError(f"Failed to load XSD schema: {e}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get basic information about the schema.
        
        Returns:
            Dictionary containing schema information
        """
        if not self.schema:
            return {}
        
        return {
            'filepath': self.xsd_path,
            'filename': os.path.basename(self.xsd_path),
            'target_namespace': self.schema.target_namespace,
            'elements_count': len(self.schema.elements),
            'types_count': len(self.schema.types),
            'attributes_count': len(self.schema.attributes)
        }
    
    def get_root_elements(self) -> Dict[str, Any]:
        """
        Get the root elements defined in the schema.
        
        Returns:
            Dictionary of root element names and their types
        """
        if not self.schema:
            return {}
        
        root_elements = {}
        for name, element in self.schema.elements.items():
            root_elements[name] = {
                'type': str(element.type),
                'is_complex': element.type.is_complex()
            }
        
        return root_elements
    
    def validate_xml(self, xml_path: str) -> bool:
        """
        Validate an XML file against this schema.
        
        Args:
            xml_path: Path to the XML file to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.schema:
            return False
        
        try:
            return self.schema.is_valid(xml_path)
        except Exception:
            return False
