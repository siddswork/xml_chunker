"""Tests for TestGeneratorCLI component."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from xslt_test_generator.cli.test_generator_cli import TestGeneratorCLI
from xslt_test_generator.agents.intelligent_test_generator import TestSuite, TestScenario
from xslt_test_generator.agents.test_case_formatter import FormattedTestCase


class TestTestGeneratorCLI:
    """Test TestGeneratorCLI functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_cli(self):
        """Create CLI instance with mocked dependencies."""
        with patch('xslt_test_generator.cli.test_generator_cli.DatabaseManager'), \
             patch('xslt_test_generator.cli.test_generator_cli.AnalysisCoordinator'), \
             patch('xslt_test_generator.cli.test_generator_cli.IntelligentTestGenerator'), \
             patch('xslt_test_generator.cli.test_generator_cli.TestCaseFormatter'):
            
            cli = TestGeneratorCLI()
            return cli
    
    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results."""
        return {
            'analysis_id': 'test_analysis_1',
            'file_path': '/test/sample.xslt',
            'template_analysis': {
                'templates': {'formatOrder': Mock()},
                'analysis_summary': {'total_templates': 1}
            },
            'semantic_analysis': {
                'semantic_patterns': [Mock()],
                'transformation_hotspots': [Mock()],
                'analysis_summary': {'total_patterns': 1}
            },
            'execution_analysis': {
                'execution_paths': [Mock()],
                'entry_points': ['formatOrder'],
                'path_statistics': {'total_paths': 1}
            },
            'summary': {
                'key_findings': ['Complex transformation detected'],
                'overall_complexity': 25,
                'test_generation_priority': 'high'
            }
        }
    
    @pytest.fixture
    def sample_test_suite(self):
        """Sample test suite."""
        scenarios = [
            TestScenario(
                scenario_id="test_1",
                scenario_type="complexity_hotspot",
                description="Test high complexity scenario",
                priority="high",
                input_requirements={"xml": "<test/>"},
                expected_outputs={"xml": "<result/>"},
                test_conditions=["Verify complex processing"],
                source_templates=["formatOrder"],
                semantic_patterns=["complex_pattern"],
                execution_paths=["path_1"]
            ),
            TestScenario(
                scenario_id="test_2",
                scenario_type="pattern_test",
                description="Test pattern scenario",
                priority="medium",
                input_requirements={"xml": "<test2/>"},
                expected_outputs={"xml": "<result2/>"},
                test_conditions=["Verify pattern"],
                source_templates=["processOrder"],
                semantic_patterns=["pattern_1"],
                execution_paths=["path_2"]
            )
        ]
        
        return TestSuite(
            xslt_file="/test/sample.xslt",
            total_scenarios=2,
            scenarios_by_priority={"high": 1, "medium": 1, "low": 0},
            scenarios_by_type={"complexity_hotspot": 1, "pattern_test": 1},
            scenarios=scenarios,
            template_coverage=0.85,
            path_coverage=0.75,
            pattern_coverage=1.0,
            estimated_execution_time="4s"
        )
    
    @pytest.fixture
    def sample_formatted_tests(self):
        """Sample formatted test cases."""
        return {
            'cucumber': [
                FormattedTestCase(
                    test_id="feature_complexity_hotspot",
                    format_type="cucumber",
                    content="Feature: Complexity Hotspot Tests\n  Scenario: Test high complexity scenario\n    Given input XML\n    When transformation executed\n    Then verify result",
                    file_name="complexity_hotspot_tests.feature",
                    metadata={"scenario_count": 1}
                )
            ],
            'pytest': [
                FormattedTestCase(
                    test_id="pytest_suite",
                    format_type="pytest",
                    content="import pytest\n\ndef test_high_complexity():\n    pass",
                    file_name="test_sample.py",
                    metadata={"total_tests": 2}
                )
            ],
            'json': [
                FormattedTestCase(
                    test_id="json_specification",
                    format_type="json",
                    content='{"test_suite": "data"}',
                    file_name="sample_test_specification.json",
                    metadata={"total_scenarios": 2}
                )
            ]
        }
    
    def test_generate_tests_success(self, mock_cli, temp_dir, sample_analysis_results, 
                                   sample_test_suite, sample_formatted_tests):
        """Test successful test generation."""
        # Setup mocks
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli.test_generator.generate_test_suite.return_value = sample_test_suite
        mock_cli.test_formatter.format_test_suite.return_value = sample_formatted_tests
        
        # Execute
        result = mock_cli.generate_tests(
            xslt_file="/test/sample.xslt",
            output_dir=temp_dir,
            output_formats=['cucumber', 'pytest', 'json'],
            force_reanalysis=False,
            verbose=False
        )
        
        # Verify method calls
        mock_cli.analysis_coordinator.analyze_xslt_file.assert_called_once_with(
            "/test/sample.xslt", False
        )
        mock_cli.test_generator.generate_test_suite.assert_called_once_with(sample_analysis_results)
        mock_cli.test_formatter.format_test_suite.assert_called_once_with(
            sample_test_suite, ['cucumber', 'pytest', 'json']
        )
        
        # Verify result structure
        assert result['xslt_file'] == "/test/sample.xslt"
        assert result['analysis_results'] == sample_analysis_results
        assert result['test_suite'] == sample_test_suite
        assert 'generated_files' in result
        assert result['output_directory'] == temp_dir
        assert 'statistics' in result
        
        # Verify statistics
        stats = result['statistics']
        assert stats['total_scenarios'] == 2
        assert stats['scenarios_by_priority'] == {"high": 1, "medium": 1, "low": 0}
        assert stats['output_formats'] == ['cucumber', 'pytest', 'json']
        assert stats['coverage_metrics']['template_coverage'] == "85.0%"
    
    def test_generate_tests_with_verbose(self, mock_cli, temp_dir, sample_analysis_results,
                                        sample_test_suite, sample_formatted_tests):
        """Test test generation with verbose output."""
        # Setup mocks
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli.test_generator.generate_test_suite.return_value = sample_test_suite
        mock_cli.test_formatter.format_test_suite.return_value = sample_formatted_tests
        
        # Mock the display methods to avoid rich output in tests
        mock_cli._display_detailed_results = Mock()
        
        # Execute with verbose
        result = mock_cli.generate_tests(
            xslt_file="/test/sample.xslt",
            output_dir=temp_dir,
            verbose=True
        )
        
        # Verify detailed results display was called
        mock_cli._display_detailed_results.assert_called_once()
        
        # Result should still be valid
        assert result['statistics']['total_scenarios'] == 2
    
    def test_generate_tests_analysis_error(self, mock_cli, temp_dir):
        """Test handling of analysis errors."""
        # Mock analysis failure
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = {
            'error': 'Analysis failed: File not found'
        }
        
        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            mock_cli.generate_tests(
                xslt_file="/test/nonexistent.xslt",
                output_dir=temp_dir
            )
        
        assert "Analysis failed" in str(exc_info.value)
    
    def test_save_test_files(self, mock_cli, temp_dir, sample_formatted_tests):
        """Test saving formatted test files."""
        output_path = Path(temp_dir)
        
        saved_files = mock_cli._save_test_files(sample_formatted_tests, output_path)
        
        # Verify files were created
        assert len(saved_files) == 3  # cucumber, pytest, json
        
        # Check cucumber file
        cucumber_dir = output_path / 'cucumber'
        assert cucumber_dir.exists()
        cucumber_file = cucumber_dir / 'complexity_hotspot_tests.feature'
        assert cucumber_file.exists()
        
        # Check pytest file
        pytest_dir = output_path / 'pytest'
        assert pytest_dir.exists()
        pytest_file = pytest_dir / 'test_sample.py'
        assert pytest_file.exists()
        
        # Check JSON file
        json_dir = output_path / 'json'
        assert json_dir.exists()
        json_file = json_dir / 'sample_test_specification.json'
        assert json_file.exists()
        
        # Verify saved files metadata
        for file_info in saved_files:
            assert 'format' in file_info
            assert 'file_path' in file_info
            assert 'file_name' in file_info
            assert 'test_id' in file_info
            assert 'metadata' in file_info
            
            # File should actually exist
            assert Path(file_info['file_path']).exists()
    
    def test_generate_statistics(self, mock_cli, sample_test_suite, sample_formatted_tests):
        """Test statistics generation."""
        stats = mock_cli._generate_statistics(sample_test_suite, sample_formatted_tests)
        
        # Check required fields
        assert stats['total_scenarios'] == 2
        assert stats['scenarios_by_priority'] == {"high": 1, "medium": 1, "low": 0}
        assert stats['scenarios_by_type'] == {"complexity_hotspot": 1, "pattern_test": 1}
        
        # Check coverage metrics formatting
        coverage = stats['coverage_metrics']
        assert coverage['template_coverage'] == "85.0%"
        assert coverage['path_coverage'] == "75.0%"
        assert coverage['pattern_coverage'] == "100.0%"
        
        # Check output formats
        assert set(stats['output_formats']) == {'cucumber', 'pytest', 'json'}
        assert stats['total_files_generated'] == 3
        assert stats['estimated_execution_time'] == "4s"
    
    def test_analyze_only_success(self, mock_cli, sample_analysis_results):
        """Test analysis-only operation."""
        # Setup mock
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli._display_analysis_results = Mock()
        
        # Execute
        result = mock_cli.analyze_only("/test/sample.xslt", force_reanalysis=True)
        
        # Verify
        mock_cli.analysis_coordinator.analyze_xslt_file.assert_called_once_with(
            "/test/sample.xslt", True
        )
        mock_cli._display_analysis_results.assert_called_once_with(sample_analysis_results)
        
        assert result == sample_analysis_results
    
    def test_analyze_only_error(self, mock_cli):
        """Test analysis-only with error."""
        error_result = {'error': 'Analysis failed'}
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = error_result
        
        result = mock_cli.analyze_only("/test/sample.xslt")
        
        assert result == error_result
    
    def test_display_summary(self, mock_cli, temp_dir):
        """Test summary display."""
        # Create sample results
        results = {
            'xslt_file': '/test/sample.xslt',
            'output_directory': temp_dir,
            'generated_files': [
                {'format': 'cucumber', 'file_name': 'test.feature'},
                {'format': 'pytest', 'file_name': 'test.py'}
            ],
            'statistics': {
                'total_scenarios': 5,
                'scenarios_by_priority': {'high': 2, 'medium': 2, 'low': 1},
                'coverage_metrics': {
                    'template_coverage': '90.0%',
                    'path_coverage': '85.0%',
                    'pattern_coverage': '100.0%'
                },
                'output_formats': ['cucumber', 'pytest'],
                'estimated_execution_time': '10s'
            }
        }
        
        # Mock console to avoid actual output during tests
        with patch('xslt_test_generator.cli.test_generator_cli.rprint'), \
             patch('xslt_test_generator.cli.test_generator_cli.console'):
            
            # Should not raise exception
            mock_cli._display_summary(results)
    
    def test_display_detailed_results(self, mock_cli, temp_dir, sample_test_suite):
        """Test detailed results display."""
        results = {
            'xslt_file': '/test/sample.xslt',
            'output_directory': temp_dir,
            'generated_files': [],
            'analysis_results': {
                'summary': {
                    'key_findings': ['Complex transformation', 'Multiple patterns'],
                    'overall_complexity': 35,
                    'test_generation_priority': 'high'
                }
            },
            'test_suite': sample_test_suite,
            'statistics': {
                'total_scenarios': 2,
                'scenarios_by_priority': {'high': 1, 'medium': 1},
                'coverage_metrics': {'template_coverage': '85.0%'},
                'output_formats': ['cucumber'],
                'estimated_execution_time': '4s'
            }
        }
        
        # Mock display methods and console output
        mock_cli._display_summary = Mock()
        
        with patch('xslt_test_generator.cli.test_generator_cli.rprint'), \
             patch('xslt_test_generator.cli.test_generator_cli.console'):
            
            mock_cli._display_detailed_results(results)
            
        # Should call summary display
        mock_cli._display_summary.assert_called_once_with(results)
    
    def test_display_analysis_results(self, mock_cli, sample_analysis_results):
        """Test analysis results display."""
        with patch('xslt_test_generator.cli.test_generator_cli.rprint'), \
             patch('xslt_test_generator.cli.test_generator_cli.console'):
            
            # Should not raise exception
            mock_cli._display_analysis_results(sample_analysis_results)
    
    def test_default_output_formats(self, mock_cli, temp_dir, sample_analysis_results,
                                   sample_test_suite):
        """Test default output formats when none specified."""
        # Setup minimal mocks
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli.test_generator.generate_test_suite.return_value = sample_test_suite
        mock_cli.test_formatter.format_test_suite.return_value = {
            'cucumber': [FormattedTestCase(
                test_id="test_cucumber",
                format_type="cucumber",
                content="Feature: Test",
                file_name="test.feature",
                metadata={}
            )], 
            'pytest': [FormattedTestCase(
                test_id="test_pytest",
                format_type="pytest", 
                content="def test_something(): pass",
                file_name="test.py",
                metadata={}
            )], 
            'json': [FormattedTestCase(
                test_id="test_json",
                format_type="json",
                content="{}",
                file_name="test.json",
                metadata={}
            )]
        }
        
        # Call without specifying formats (should use defaults)
        result = mock_cli.generate_tests(
            xslt_file="/test/sample.xslt",
            output_dir=temp_dir
        )
        
        # Should use default formats
        expected_formats = ['cucumber', 'pytest', 'json']
        mock_cli.test_formatter.format_test_suite.assert_called_once_with(
            sample_test_suite, expected_formats
        )
    
    def test_force_reanalysis_parameter(self, mock_cli, temp_dir, sample_analysis_results,
                                       sample_test_suite, sample_formatted_tests):
        """Test force_reanalysis parameter is passed through."""
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli.test_generator.generate_test_suite.return_value = sample_test_suite
        mock_cli.test_formatter.format_test_suite.return_value = sample_formatted_tests
        
        # Test with force_reanalysis=True
        mock_cli.generate_tests(
            xslt_file="/test/sample.xslt",
            output_dir=temp_dir,
            force_reanalysis=True
        )
        
        # Verify force parameter was passed
        mock_cli.analysis_coordinator.analyze_xslt_file.assert_called_with(
            "/test/sample.xslt", True
        )
    
    def test_output_directory_creation(self, mock_cli, sample_analysis_results,
                                      sample_test_suite, sample_formatted_tests):
        """Test output directory is created if it doesn't exist."""
        # Use a non-existent directory
        output_dir = "/tmp/test_nonexistent_dir_12345"
        
        mock_cli.analysis_coordinator.analyze_xslt_file.return_value = sample_analysis_results
        mock_cli.test_generator.generate_test_suite.return_value = sample_test_suite
        mock_cli.test_formatter.format_test_suite.return_value = sample_formatted_tests
        
        try:
            result = mock_cli.generate_tests(
                xslt_file="/test/sample.xslt",
                output_dir=output_dir
            )
            
            # Directory should have been created
            assert Path(output_dir).exists()
            assert result['output_directory'] == output_dir
            
        finally:
            # Cleanup
            if Path(output_dir).exists():
                shutil.rmtree(output_dir)
    
    def test_exception_handling(self, mock_cli, temp_dir):
        """Test exception handling in generate_tests."""
        # Mock to raise exception
        mock_cli.analysis_coordinator.analyze_xslt_file.side_effect = Exception("Database error")
        
        # Should re-raise the exception
        with pytest.raises(Exception) as exc_info:
            mock_cli.generate_tests(
                xslt_file="/test/sample.xslt",
                output_dir=temp_dir
            )
        
        assert "Database error" in str(exc_info.value)