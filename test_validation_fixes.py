"""
Comprehensive test suite for validation error fixes.

Tests the pattern validation, enumeration, and length constraint fixes
implemented to resolve 1,150+ validation errors.
"""

import pytest
import re
from utils.type_generators import (
    StringTypeGenerator, 
    EnumerationTypeGenerator,
    TypeGeneratorFactory
)


class TestPatternValidationFixes:
    """Test pattern validation fixes for 1,034 errors."""
    
    def setup_method(self):
        """Setup test environment."""
        self.generator = StringTypeGenerator()
    
    def test_aviation_patterns_high_frequency(self):
        """Test the most common aviation patterns that caused 996+ errors."""
        patterns_to_test = [
            # Service and Reference Codes (highest frequency)
            ('[0-9A-Z]{1,3}', r'^[0-9A-Z]{1,3}$'),
            ('[0-9A-Z]{3}', r'^[0-9A-Z]{3}$'),
            ('[A-Z]{3}', r'^[A-Z]{3}$'),
            ('[A-Z]{2}', r'^[A-Z]{2}$'),
            
            # Numeric Codes
            ('[0-9]{1,4}', r'^[0-9]{1,4}$'),
            ('[0-9]{1,8}', r'^[0-9]{1,8}$'),
            ('[0-9]{2}', r'^[0-9]{2}$'),
            ('[0-9]{3}', r'^[0-9]{3}$'),
            ('[0-9]{4}', r'^[0-9]{4}$'),
            
            # Payment and Business Codes
            ('(IATAC|BLTRL)[A-Za-z0-9]{2}', r'^(IATAC|BLTRL)[A-Za-z0-9]{2}$'),
            
            # Mixed Alphanumeric
            ('[A-Za-z0-9]{2}', r'^[A-Za-z0-9]{2}$'),
            ('[A-Za-z0-9]{3}', r'^[A-Za-z0-9]{3}$'),
        ]
        
        for pattern, validation_pattern in patterns_to_test:
            # Test pattern generation
            value = self.generator.generate_pattern_value(pattern)
            assert re.match(validation_pattern, value), f"Pattern {pattern} failed with value {value}"
            
            # Test multiple generations for consistency
            for _ in range(5):
                test_value = self.generator.generate_pattern_value(pattern)
                assert re.match(validation_pattern, test_value), f"Pattern {pattern} inconsistent with value {test_value}"
    
    def test_pattern_validation_and_regeneration(self):
        """Test pattern validation and regeneration logic."""
        test_cases = [
            # (initial_value, pattern, should_change)
            ("ABC123", "[0-9A-Z]{1,3}", True),  # Should change to match pattern
            ("123", "[0-9]{1,4}", False),       # Should not change
            ("INVALID", "[A-Z]{2}", True),      # Should change to 2 chars
            ("AB", "[A-Z]{2}", False),          # Should not change
        ]
        
        for initial_value, pattern, should_change in test_cases:
            result = self.generator.validate_and_regenerate_pattern(initial_value, pattern)
            
            # Result should always match pattern
            assert re.match(f"^{pattern}$", result), f"Result '{result}' doesn't match pattern '{pattern}'"
            
            # Check if change occurred as expected
            if should_change:
                assert result != initial_value, f"Value should have changed from '{initial_value}'"
            else:
                assert result == initial_value, f"Value should not have changed from '{initial_value}'"
    
    def test_dynamic_pattern_generation(self):
        """Test dynamic pattern generation for unknown patterns."""
        dynamic_patterns = [
            '[0-9]{5,8}',    # Numeric range
            '[A-Z]{2,4}',    # Alpha range
            '[A-Za-z0-9]{1,5}'  # Mixed range
        ]
        
        for pattern in dynamic_patterns:
            value = self.generator.generate_dynamic_pattern_value(pattern)
            assert re.match(f"^{pattern}$", value), f"Dynamic pattern {pattern} failed with value {value}"
    
    def test_pattern_compliance_testing(self):
        """Test pattern compliance checking function."""
        test_cases = [
            ("123", "[0-9]{1,4}", True),
            ("ABC", "[A-Z]{3}", True),
            ("12A", "[0-9A-Z]{3}", True),
            ("invalid", "[A-Z]{3}", False),
            ("12345", "[0-9]{1,4}", False),  # Too long
        ]
        
        for value, pattern, expected in test_cases:
            result = self.generator.test_pattern_compliance(value, pattern)
            assert result == expected, f"Pattern compliance failed for '{value}' against '{pattern}'"


class TestEnumerationFixes:
    """Test enumeration mismatch fixes for 84 errors."""
    
    def setup_method(self):
        """Setup test environment."""
        self.generator = EnumerationTypeGenerator()
    
    def test_valid_enumeration_selection(self):
        """Test selection from valid enumeration lists."""
        test_cases = [
            (['USD', 'EUR', 'GBP'], 'CurrencyCode'),
            (['Y', 'N', 'Other'], 'BagRuleCode'),
            (['KGM', 'LBR'], 'WeightUnitOfMeasurement'),
            (['CMT', 'FOT', 'INH', 'MTR'], 'LengthUnitOfMeasurement'),
        ]
        
        for enum_values, element_name in test_cases:
            constraints = {'enum_values': enum_values}
            result = self.generator.generate(element_name, constraints)
            assert result in enum_values, f"Generated value '{result}' not in enum list {enum_values}"
    
    def test_empty_enumeration_fallbacks(self):
        """Test fallbacks when enumeration lists are empty or invalid."""
        test_cases = [
            ('CurrencyCode', 'USD'),
            ('CountryCode', 'US'),
            ('LanguageCode', 'EN'),
            ('BagRuleCode', 'Y'),
            ('WeightUnitOfMeasurement', 'KGM'),
            ('StatusCode', 'OK'),
            ('AirlineCode', 'AA'),
        ]
        
        for element_name, expected_fallback in test_cases:
            # Test with empty enum list
            result_empty = self.generator.generate(element_name, {'enum_values': []})
            assert result_empty == expected_fallback
            
            # Test with None/invalid enum list
            result_none = self.generator.generate(element_name, {'enum_values': ['None', '', None]})
            assert result_none == expected_fallback
    
    def test_enum_filtering_and_validation(self):
        """Test filtering of None/empty values from enum lists."""
        test_enum_list = ['USD', 'None', '', None, 'EUR', 'GBP']
        expected_valid = ['USD', 'EUR', 'GBP']
        
        result = self.generator.generate('CurrencyCode', {'enum_values': test_enum_list})
        assert result in expected_valid, f"Result '{result}' should be from valid enum values {expected_valid}"
    
    def test_enum_value_tracking_and_variety(self):
        """Test enum value usage tracking for variety."""
        enum_values = ['A', 'B', 'C']
        element_name = 'TestElement'
        
        # Reset tracker for clean test
        EnumerationTypeGenerator.reset_usage_tracker()
        
        # Generate multiple values and track usage
        results = []
        for _ in range(6):  # Generate twice as many as enum values
            result = self.generator.generate(element_name, {'enum_values': enum_values})
            results.append(result)
        
        # Check that all enum values were used
        unique_results = set(results)
        assert len(unique_results) >= 2, f"Should use multiple enum values for variety, got {unique_results}"
        
        # All results should be valid
        for result in results:
            assert result in enum_values, f"Result '{result}' not in valid enum values"


class TestLengthConstraintFixes:
    """Test length constraint fixes for 104 errors."""
    
    def setup_method(self):
        """Setup test environment."""
        self.generator = StringTypeGenerator()
    
    def test_exact_length_constraints(self):
        """Test exact length constraint handling."""
        test_cases = [
            ('test', 3, 'tes'),      # Truncate
            ('hi', 5, 'hiXXX'),      # Pad
            ('exact', 5, 'exact'),   # No change needed
        ]
        
        for initial_value, exact_length, expected in test_cases:
            result = self.generator.adjust_to_exact_length(initial_value, exact_length)
            assert len(result) == exact_length, f"Result length {len(result)} != expected {exact_length}"
            assert result == expected, f"Expected '{expected}', got '{result}'"
    
    def test_min_max_length_constraints(self):
        """Test min/max length constraint handling."""
        test_cases = [
            # (value, min_len, max_len, expected_len_range)
            ('hi', 5, 10, (5, 10)),      # Should pad to meet min
            ('verylongstring', 3, 8, (3, 8)),  # Should truncate to meet max
            ('perfect', 5, 10, (7, 7)),  # Should stay same
        ]
        
        for value, min_len, max_len, expected_range in test_cases:
            constraints = {'min_length': min_len, 'max_length': max_len}
            result = self.generator.validate_length_constraints(value, constraints)
            
            result_len = len(result)
            min_expected, max_expected = expected_range
            assert min_expected <= result_len <= max_expected, \
                f"Result length {result_len} not in range {expected_range}"
    
    def test_smart_padding_strategies(self):
        """Test intelligent padding based on content type."""
        test_cases = [
            ('123', 6, '123000'),     # Numeric - pad with zeros
            ('ABC', 6, 'ABCXXX'),     # Alpha - pad with X
            ('A1B', 6, 'A1BXXX'),     # Mixed - pad with X
        ]
        
        for value, target_length, expected in test_cases:
            result = self.generator.smart_pad(value, target_length)
            assert len(result) == target_length
            assert result == expected, f"Expected '{expected}', got '{result}'"
    
    def test_smart_truncation_strategies(self):
        """Test intelligent truncation preserving meaning."""
        test_cases = [
            ('verylongstring', 8, 'verylong'),   # Normal truncation
            ('abc', 2, 'ab'),                    # Truncate to 2
            ('a', 0, ''),                        # Edge case
        ]
        
        for value, max_length, expected in test_cases:
            result = self.generator.smart_truncate(value, max_length)
            assert len(result) == max_length or len(result) == len(value)
            assert result == expected, f"Expected '{expected}', got '{result}'"


class TestIntegratedConstraintHandling:
    """Test combined constraint handling (length + pattern)."""
    
    def setup_method(self):
        """Setup test environment."""
        self.generator = StringTypeGenerator()
    
    def test_pattern_with_length_constraints(self):
        """Test handling of both pattern and length constraints together."""
        # Pattern should take precedence and generate compliant value
        constraints = {
            'pattern': '[0-9A-Z]{3}',
            'max_length': 5,
            'min_length': 2
        }
        
        result = self.generator.validate_constraints('invalidvalue', constraints)
        
        # Should match pattern
        assert re.match(r'^[0-9A-Z]{3}$', result), f"Result '{result}' doesn't match pattern"
        
        # Should meet length constraints (pattern ensures this)
        assert 2 <= len(result) <= 5, f"Result length {len(result)} outside constraint range"
    
    def test_length_then_pattern_application(self):
        """Test that length constraints are applied before pattern constraints."""
        constraints = {
            'min_length': 10,
            'pattern': '[A-Z]{3}'
        }
        
        result = self.generator.validate_constraints('AB', constraints)
        
        # Pattern should override length padding
        assert re.match(r'^[A-Z]{3}$', result), f"Pattern should override length constraint"


class TestTypeGeneratorFactory:
    """Test type generator factory for creating appropriate generators."""
    
    def setup_method(self):
        """Setup test environment."""
        self.factory = TypeGeneratorFactory()
    
    def test_enumeration_type_detection(self):
        """Test that enumeration constraints create enumeration generators."""
        constraints = {'enum_values': ['A', 'B', 'C']}
        generator = self.factory.create_generator('string', constraints)
        
        assert isinstance(generator, EnumerationTypeGenerator)
        assert generator.enum_values == ['A', 'B', 'C']
    
    def test_string_type_fallback(self):
        """Test that unknown types fall back to string generator."""
        generator = self.factory.create_generator('unknown_type')
        assert isinstance(generator, StringTypeGenerator)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])