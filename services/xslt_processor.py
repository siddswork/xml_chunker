"""
XSLT Processing Service for XML Chunker.

This module handles XSLT transformations on XML content, including
batch processing, equivalence testing, and canonical comparison.
"""

import os
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from lxml import etree
from .file_manager import FileManager


class XSLTProcessor:
    """Handles XSLT transformations and equivalence testing."""
    
    def __init__(self, config_instance=None):
        """
        Initialize the XSLT processor.
        
        Args:
            config_instance: Configuration instance (uses global config if None)
        """
        self.file_manager = FileManager(config_instance)
    
    def transform_xml(
        self, 
        xml_content: str, 
        xslt_content: str,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Transform XML using XSLT stylesheet.
        
        Args:
            xml_content: XML content to transform
            xslt_content: XSLT stylesheet content
            parameters: Optional XSLT parameters
            
        Returns:
            Dictionary containing transformation results
        """
        try:
            # Parse XML and XSLT
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            xslt_doc = etree.fromstring(xslt_content.encode('utf-8'))
            
            # Create XSLT transformer
            transform = etree.XSLT(xslt_doc)
            
            # Apply transformation with parameters if provided
            if parameters:
                result = transform(xml_doc, **parameters)
            else:
                result = transform(xml_doc)
            
            # Convert result to string
            output_xml = etree.tostring(result, encoding='unicode', pretty_print=True)
            
            return {
                'success': True,
                'output_xml': output_xml,
                'errors': [],
                'warnings': []
            }
            
        except etree.XSLTParseError as e:
            return {
                'success': False,
                'error': f"XSLT Parse Error: {str(e)}",
                'error_type': 'xslt_parse',
                'line': getattr(e, 'lineno', None)
            }
        except etree.XMLSyntaxError as e:
            return {
                'success': False,
                'error': f"XML Syntax Error: {str(e)}",
                'error_type': 'xml_parse',
                'line': getattr(e, 'lineno', None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Transformation Error: {str(e)}",
                'error_type': 'transformation'
            }
    
    def validate_xslt(self, xslt_content: str) -> Dict[str, Any]:
        """
        Validate XSLT stylesheet syntax.
        
        Args:
            xslt_content: XSLT stylesheet content
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Parse XSLT to check for syntax errors
            xslt_doc = etree.fromstring(xslt_content.encode('utf-8'))
            transform = etree.XSLT(xslt_doc)
            
            return {
                'is_valid': True,
                'success': True,
                'message': "XSLT stylesheet is valid"
            }
            
        except etree.XSLTParseError as e:
            return {
                'is_valid': False,
                'success': False,
                'error': f"XSLT Parse Error: {str(e)}",
                'line': getattr(e, 'lineno', None)
            }
        except etree.XMLSyntaxError as e:
            return {
                'is_valid': False,
                'success': False,
                'error': f"XML Syntax Error: {str(e)}",
                'line': getattr(e, 'lineno', None)
            }
        except Exception as e:
            return {
                'is_valid': False,
                'success': False,
                'error': f"Validation Error: {str(e)}"
            }
    
    def batch_transform(
        self, 
        xml_inputs: List[str], 
        xslt_content: str,
        parameters: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply XSLT transformation to multiple XML inputs.
        
        Args:
            xml_inputs: List of XML content strings
            xslt_content: XSLT stylesheet content
            parameters: Optional XSLT parameters
            
        Returns:
            List of transformation results
        """
        results = []
        
        # First validate the XSLT
        validation_result = self.validate_xslt(xslt_content)
        if not validation_result['is_valid']:
            # Return error for all inputs if XSLT is invalid
            error_result = {
                'success': False,
                'error': validation_result['error'],
                'error_type': 'xslt_invalid'
            }
            return [error_result] * len(xml_inputs)
        
        # Transform each XML input
        for i, xml_content in enumerate(xml_inputs):
            result = self.transform_xml(xml_content, xslt_content, parameters)
            result['input_index'] = i
            results.append(result)
        
        return results
    
    def compare_xslt_outputs(
        self, 
        xml_content: str, 
        xslt1_content: str, 
        xslt2_content: str,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Compare outputs of two XSLT stylesheets on same XML input.
        
        Args:
            xml_content: XML content to transform
            xslt1_content: First XSLT stylesheet content
            xslt2_content: Second XSLT stylesheet content
            parameters: Optional XSLT parameters
            
        Returns:
            Dictionary containing comparison results
        """
        # Transform with first XSLT
        result1 = self.transform_xml(xml_content, xslt1_content, parameters)
        
        # Transform with second XSLT  
        result2 = self.transform_xml(xml_content, xslt2_content, parameters)
        
        # Check if both transformations succeeded
        if not result1['success'] or not result2['success']:
            return {
                'success': False,
                'equivalent': False,
                'xslt1_result': result1,
                'xslt2_result': result2,
                'error': "One or both transformations failed"
            }
        
        # Compare outputs canonically
        are_equivalent = self._compare_xml_canonically(
            result1['output_xml'], 
            result2['output_xml']
        )
        
        return {
            'success': True,
            'equivalent': are_equivalent,
            'xslt1_result': result1,
            'xslt2_result': result2,
            'canonical_comparison': are_equivalent
        }
    
    def test_xslt_equivalence(
        self, 
        xml_test_cases: List[str], 
        xslt1_content: str, 
        xslt2_content: str,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Test equivalence of two XSLT stylesheets across multiple XML inputs.
        
        Args:
            xml_test_cases: List of XML content strings for testing
            xslt1_content: First XSLT stylesheet content (reference)
            xslt2_content: Second XSLT stylesheet content (test)
            parameters: Optional XSLT parameters
            
        Returns:
            Dictionary containing comprehensive equivalence results
        """
        results = []
        equivalent_count = 0
        failed_transformations = 0
        
        for i, xml_content in enumerate(xml_test_cases):
            comparison = self.compare_xslt_outputs(
                xml_content, xslt1_content, xslt2_content, parameters
            )
            
            if comparison['success']:
                if comparison['equivalent']:
                    equivalent_count += 1
            else:
                failed_transformations += 1
            
            comparison['test_case_index'] = i
            results.append(comparison)
        
        total_tests = len(xml_test_cases)
        success_rate = (equivalent_count / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_test_cases': total_tests,
            'equivalent_outputs': equivalent_count,
            'failed_transformations': failed_transformations,
            'success_rate': success_rate,
            'overall_equivalent': equivalent_count == total_tests - failed_transformations,
            'detailed_results': results,
            'summary': f"{equivalent_count}/{total_tests} test cases passed ({success_rate:.1f}%)"
        }
    
    def _compare_xml_canonically(self, xml1: str, xml2: str) -> bool:
        """
        Compare two XML strings canonically (ignoring formatting differences).
        
        Args:
            xml1: First XML string
            xml2: Second XML string
            
        Returns:
            True if XML content is semantically equivalent
        """
        try:
            # Parse both XML strings
            doc1 = etree.fromstring(xml1.encode('utf-8'))
            doc2 = etree.fromstring(xml2.encode('utf-8'))
            
            # Canonicalize both documents
            canonical1 = etree.tostring(doc1, method='c14n', encoding='unicode')
            canonical2 = etree.tostring(doc2, method='c14n', encoding='unicode')
            
            # Compare canonical forms
            return canonical1 == canonical2
            
        except Exception:
            # If parsing fails, fall back to string comparison
            return xml1.strip() == xml2.strip()
    
    def get_transformation_statistics(self, xml_content: str, xslt_content: str) -> Dict[str, Any]:
        """
        Get statistics about XSLT transformation.
        
        Args:
            xml_content: XML content to analyze
            xslt_content: XSLT stylesheet content
            
        Returns:
            Dictionary containing transformation statistics
        """
        try:
            # Parse input XML
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            
            # Count input elements
            input_element_count = len(xml_doc.xpath('//*'))
            input_attribute_count = len(xml_doc.xpath('//@*'))
            
            # Transform XML
            result = self.transform_xml(xml_content, xslt_content)
            
            if not result['success']:
                return result
            
            # Parse output XML
            output_doc = etree.fromstring(result['output_xml'].encode('utf-8'))
            
            # Count output elements
            output_element_count = len(output_doc.xpath('//*'))
            output_attribute_count = len(output_doc.xpath('//@*'))
            
            return {
                'success': True,
                'input_statistics': {
                    'element_count': input_element_count,
                    'attribute_count': input_attribute_count
                },
                'output_statistics': {
                    'element_count': output_element_count,
                    'attribute_count': output_attribute_count
                },
                'transformation_ratio': {
                    'element_ratio': output_element_count / input_element_count if input_element_count > 0 else 0,
                    'attribute_ratio': output_attribute_count / input_attribute_count if input_attribute_count > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Statistics Error: {str(e)}"
            }