"""
Token Counter for Chunk Size Management

This module provides utilities for counting tokens in text to manage chunk sizes
for LLM processing within context limits.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Information about token count in text"""
    text: str
    character_count: int
    word_count: int
    estimated_tokens: int
    actual_tokens: Optional[int] = None


class TokenCounter:
    """Token counter for managing chunk sizes"""
    
    def __init__(self):
        """Initialize token counter with estimation rules"""
        # Token estimation rules (approximations for GPT-style tokenization)
        self.chars_per_token = 4  # Average characters per token
        self.words_per_token = 0.75  # Average words per token
        
        # XML/XSLT specific patterns that affect tokenization
        self.xml_patterns = {
            'xml_tags': r'<[^>]+>',
            'xml_attributes': r'\w+="[^"]*"',
            'xpath_expressions': r'(//|@\w+|\.\./|\./)[\w\[\]\/\.\(\):@-]*|@\w+|select="[^"]*[/@]',
            'xsl_functions': r'xsl:\w+',
            'namespaces': r'\w+:\w+',
            'xml_comments': r'<!--.*?-->',
        }
    
    def estimate_tokens(self, text: str, method: str = 'xml_aware') -> int:
        """
        Estimate token count using different methods
        
        Args:
            text: Text to analyze
            method: Estimation method ('chars', 'words', 'hybrid', 'xml_aware')
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
            
        if method == 'chars':
            return self._estimate_by_chars(text)
        elif method == 'words':
            return self._estimate_by_words(text)
        elif method == 'hybrid':
            return self._estimate_hybrid(text)
        elif method == 'xml_aware':
            return self._estimate_xml_aware(text)
        else:
            raise ValueError(f"Unknown estimation method: {method}")
    
    def get_token_info(self, text: str) -> TokenInfo:
        """
        Get comprehensive token information for text
        
        Args:
            text: Text to analyze
            
        Returns:
            TokenInfo object with detailed analysis
        """
        char_count = len(text)
        word_count = len(text.split())
        estimated_tokens = self.estimate_tokens(text, method='xml_aware')
        
        return TokenInfo(
            text=text[:100] + "..." if len(text) > 100 else text,  # Truncate for display
            character_count=char_count,
            word_count=word_count,
            estimated_tokens=estimated_tokens
        )
    
    def _estimate_by_chars(self, text: str) -> int:
        """Estimate tokens by character count"""
        return max(1, len(text) // self.chars_per_token)
    
    def _estimate_by_words(self, text: str) -> int:
        """Estimate tokens by word count"""
        words = len(text.split())
        return max(1, int(words / self.words_per_token))
    
    def _estimate_hybrid(self, text: str) -> int:
        """Estimate tokens using hybrid approach"""
        char_estimate = self._estimate_by_chars(text)
        word_estimate = self._estimate_by_words(text)
        
        # Use average of both methods
        return (char_estimate + word_estimate) // 2
    
    def _estimate_xml_aware(self, text: str) -> int:
        """Estimate tokens with XML/XSLT awareness"""
        base_estimate = self._estimate_hybrid(text)
        
        # Adjust for XML complexity
        xml_tag_count = len(re.findall(r'<[^>]+>', text))
        xpath_count = len(re.findall(r'(//|@\w+|\.\./|\./)[\w\[\]\/\.\(\):@-]*|@\w+|select="[^"]*[/@]', text))
        
        # XML tags and XPath expressions tend to tokenize differently
        xml_adjustment = (xml_tag_count * 0.5) + (xpath_count * 0.3)
        
        return max(1, int(base_estimate + xml_adjustment))


# Utility functions
def quick_token_count(text: str) -> int:
    """Quick utility to get token count"""
    counter = TokenCounter()
    return counter.estimate_tokens(text, method='xml_aware')