"""
XML Generator module for XML Chunker.

This module provides utilities for generating dummy XML files from XSD schemas.
"""

import os
import random
import string
import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Union, List
import xmlschema
from lxml import etree


class XMLGenerator:
    """Class for generating dummy XML files from XSD schemas."""
    
    def __init__(self, xsd_path: str):
        """
        Initialize the XML generator.
        
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
    
    def _generate_random_string(self, length: int = 8) -> str:
        """
        Generate a random string of specified length.
        
        Args:
            length: Length of the string to generate
            
        Returns:
            Random string
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_random_number(self, min_val: int = 1, max_val: int = 100) -> int:
        """
        Generate a random number between min_val and max_val.
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Random integer
        """
        return random.randint(min_val, max_val)
    
    def _generate_random_date(self) -> str:
        """
        Generate a random date in ISO format.
        
        Returns:
            Random date string in ISO format
        """
        year = random.randint(2000, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Simplified to avoid month-specific day ranges
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    def _generate_random_datetime(self) -> str:
        """
        Generate a random datetime in ISO format.
        
        Returns:
            Random datetime string in ISO format
        """
        date = self._generate_random_date()
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{date}T{hour:02d}:{minute:02d}:{second:02d}"
    
    def _generate_random_boolean(self) -> bool:
        """
        Generate a random boolean value.
        
        Returns:
            Random boolean
        """
        return random.choice([True, False])
    
    def _generate_value_for_type(self, type_name: str) -> Any:
        """
        Generate a random value based on the XSD type.
        
        Args:
            type_name: XSD type name
            
        Returns:
            Random value of appropriate type
        """
        if 'string' in type_name:
            return self._generate_random_string()
        elif 'int' in type_name or 'long' in type_name or 'short' in type_name:
            return self._generate_random_number()
        elif 'decimal' in type_name or 'float' in type_name or 'double' in type_name:
            return round(random.uniform(1.0, 100.0), 2)
        elif 'boolean' in type_name:
            return self._generate_random_boolean()
        elif 'date' in type_name and 'time' in type_name:
            return self._generate_random_datetime()
        elif 'date' in type_name:
            return self._generate_random_date()
        elif 'time' in type_name:
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            return self._generate_random_string()
    
    def _create_element_dict(self, element: xmlschema.validators.XsdElement) -> Dict[str, Any]:
        """
        Create a dictionary representation of an XSD element with random values.
        
        Args:
            element: XSD element
            
        Returns:
            Dictionary with element structure and random values
        """
        result = {}
        
        if element.type.is_complex() and element.type.attributes:
            for attr_name, attr in element.type.attributes.items():
                attr_type = str(attr.type)
                result[f'@{attr_name}'] = self._generate_value_for_type(attr_type)
        
        if element.type.is_complex() and hasattr(element.type, 'content'):
            for child in element.type.content.iter_elements():
                child_name = child.name
                
                if child.type.is_complex():
                    child_dict = self._create_element_dict(child)
                    
                    if child.max_occurs > 1:
                        num_items = random.randint(1, min(3, child.max_occurs))
                        result[child_name] = [child_dict for _ in range(num_items)]
                    else:
                        result[child_name] = child_dict
                else:
                    child_type = str(child.type)
                    
                    if child.max_occurs > 1:
                        num_items = random.randint(1, min(3, child.max_occurs))
                        result[child_name] = [self._generate_value_for_type(child_type) for _ in range(num_items)]
                    else:
                        result[child_name] = self._generate_value_for_type(child_type)
        
        elif element.type.is_simple():
            return self._generate_value_for_type(str(element.type))
        
        return result
    
    def generate_dummy_xml(self, output_path: Optional[str] = None) -> str:
        """
        Generate a dummy XML file based on the XSD schema.
        
        Args:
            output_path: Path where to save the generated XML file
            
        Returns:
            String containing the generated XML
        """
        if not self.schema:
            return '<?xml version="1.0" encoding="UTF-8"?><error>Failed to load schema</error>'
        
        try:
            root_elements = list(self.schema.elements.keys())
            if not root_elements:
                return '<?xml version="1.0" encoding="UTF-8"?><error>No root elements found in schema</error>'
            
            root_name = root_elements[0]
            root_element = self.schema.elements[root_name]
            
            xml_dict = self._create_element_dict(root_element)
            
            xml_element = self.schema.encode(xml_dict, path=root_name)
            xml_string = ET.tostring(xml_element, encoding='utf-8').decode('utf-8')
            
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
            
            return xml_content
            
        except Exception as e:
            error_xml = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<error>\n'
                f'  <message>Error generating XML: {str(e)}</message>\n'
                f'</error>'
            )
            return error_xml
