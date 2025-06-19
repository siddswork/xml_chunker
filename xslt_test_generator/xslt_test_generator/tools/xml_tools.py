"""XML and XSD parsing utilities."""

from lxml import etree
from typing import Dict, List, Any, Optional

class XSLTAnalyzer:
    """Analyze XSLT files for transformation patterns."""
    
    def __init__(self, xslt_content: str):
        """Initialize with XSLT content."""
        self.content = xslt_content
        self.doc = etree.fromstring(xslt_content.encode('utf-8'))
        self.namespaces = {
            'xsl': 'http://www.w3.org/1999/XSL/Transform'
        }
    
    def extract_templates(self) -> List[Dict[str, Any]]:
        """Extract template information from XSLT."""
        templates = []
        template_elements = self.doc.xpath('//xsl:template', namespaces=self.namespaces)
        
        for template in template_elements:
            template_info = {
                'match': template.get('match'),
                'name': template.get('name'),
                'mode': template.get('mode'),
                'has_conditions': len(template.xpath('.//xsl:choose | .//xsl:when | .//xsl:if', namespaces=self.namespaces)) > 0,
                'xpath_expressions': self.extract_xpath_from_element(template)
            }
            templates.append(template_info)
        
        return templates
    
    def extract_conditional_logic(self) -> List[Dict[str, Any]]:
        """Extract conditional logic patterns."""
        conditions = []
        
        # Find choose/when structures
        choose_elements = self.doc.xpath('//xsl:choose', namespaces=self.namespaces)
        for choose in choose_elements:
            when_elements = choose.xpath('./xsl:when', namespaces=self.namespaces)
            condition_group = {
                'type': 'choose',
                'conditions': [when.get('test') for when in when_elements if when.get('test')],
                'has_otherwise': len(choose.xpath('./xsl:otherwise', namespaces=self.namespaces)) > 0
            }
            conditions.append(condition_group)
        
        # Find if statements
        if_elements = self.doc.xpath('//xsl:if', namespaces=self.namespaces)
        for if_elem in if_elements:
            condition = {
                'type': 'if',
                'test': if_elem.get('test')
            }
            conditions.append(condition)
        
        return conditions
    
    def extract_xpath_from_element(self, element) -> List[str]:
        """Extract XPath expressions from an element."""
        xpath_expressions = []
        
        # Look for select attributes
        select_attrs = element.xpath('.//@select')
        xpath_expressions.extend([attr for attr in select_attrs if attr])
        
        # Look for test attributes in conditions
        test_attrs = element.xpath('.//@test')
        xpath_expressions.extend([attr for attr in test_attrs if attr])
        
        return list(set(xpath_expressions))  # Remove duplicates
    
    def extract_value_mappings(self) -> List[Dict[str, Any]]:
        """Extract value mapping patterns."""
        mappings = []
        
        # Look for named templates that seem to do value mapping
        named_templates = self.doc.xpath('//xsl:template[@name]', namespaces=self.namespaces)
        for template in named_templates:
            name = template.get('name')
            if 'map' in name.lower() or 'convert' in name.lower() or 'transform' in name.lower():
                choose_elements = template.xpath('.//xsl:choose', namespaces=self.namespaces)
                for choose in choose_elements:
                    when_elements = choose.xpath('./xsl:when', namespaces=self.namespaces)
                    mapping = {
                        'template_name': name,
                        'mappings': []
                    }
                    for when in when_elements:
                        test = when.get('test')
                        value = when.text or ''
                        value_of = when.xpath('./xsl:value-of/@select', namespaces=self.namespaces)
                        if value_of:
                            value = value_of[0]
                        mapping['mappings'].append({
                            'condition': test,
                            'output': value
                        })
                    mappings.append(mapping)
        
        return mappings

class XSDAnalyzer:
    """Analyze XSD files for schema structure."""
    
    def __init__(self, xsd_content: str):
        """Initialize with XSD content."""
        self.content = xsd_content
        self.doc = etree.fromstring(xsd_content.encode('utf-8'))
        self.namespaces = {
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
    
    def extract_root_elements(self) -> List[Dict[str, Any]]:
        """Extract root element definitions."""
        elements = []
        root_elements = self.doc.xpath('//xs:element[@name]', namespaces=self.namespaces)
        
        for element in root_elements:
            element_info = {
                'name': element.get('name'),
                'type': element.get('type'),
                'min_occurs': element.get('minOccurs', '1'),
                'max_occurs': element.get('maxOccurs', '1'),
                'nillable': element.get('nillable', 'false') == 'true'
            }
            elements.append(element_info)
        
        return elements
    
    def extract_complex_types(self) -> List[Dict[str, Any]]:
        """Extract complex type definitions."""
        types = []
        complex_types = self.doc.xpath('//xs:complexType[@name]', namespaces=self.namespaces)
        
        for complex_type in complex_types:
            type_info = {
                'name': complex_type.get('name'),
                'mixed': complex_type.get('mixed', 'false') == 'true',
                'elements': self.extract_elements_from_type(complex_type),
                'attributes': self.extract_attributes_from_type(complex_type),
                'has_choice': len(complex_type.xpath('.//xs:choice', namespaces=self.namespaces)) > 0
            }
            types.append(type_info)
        
        return types
    
    def extract_elements_from_type(self, type_element) -> List[Dict[str, Any]]:
        """Extract elements from a complex type."""
        elements = []
        element_defs = type_element.xpath('.//xs:element', namespaces=self.namespaces)
        
        for element in element_defs:
            element_info = {
                'name': element.get('name'),
                'type': element.get('type'),
                'min_occurs': element.get('minOccurs', '1'),
                'max_occurs': element.get('maxOccurs', '1'),
                'ref': element.get('ref')
            }
            elements.append(element_info)
        
        return elements
    
    def extract_attributes_from_type(self, type_element) -> List[Dict[str, Any]]:
        """Extract attributes from a complex type."""
        attributes = []
        attr_defs = type_element.xpath('.//xs:attribute', namespaces=self.namespaces)
        
        for attr in attr_defs:
            attr_info = {
                'name': attr.get('name'),
                'type': attr.get('type'),
                'use': attr.get('use', 'optional'),
                'ref': attr.get('ref')
            }
            attributes.append(attr_info)
        
        return attributes
    
    def extract_choice_elements(self) -> List[Dict[str, Any]]:
        """Extract choice element definitions."""
        choices = []
        choice_elements = self.doc.xpath('//xs:choice', namespaces=self.namespaces)
        
        for choice in choice_elements:
            choice_info = {
                'min_occurs': choice.get('minOccurs', '1'),
                'max_occurs': choice.get('maxOccurs', '1'),
                'options': []
            }
            
            # Get choice options
            options = choice.xpath('./xs:element', namespaces=self.namespaces)
            for option in options:
                option_info = {
                    'name': option.get('name'),
                    'type': option.get('type'),
                    'ref': option.get('ref')
                }
                choice_info['options'].append(option_info)
            
            choices.append(choice_info)
        
        return choices