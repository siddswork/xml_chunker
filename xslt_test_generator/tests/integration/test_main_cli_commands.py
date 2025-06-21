"""Integration tests for main CLI commands."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import subprocess
import sys

from typer.testing import CliRunner

# Import the main CLI app
from main_v2 import app


class TestMainCLICommands:
    """Integration tests for main CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_xslt_file(self, temp_dir):
        """Create a sample XSLT file for testing."""
        xslt_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <body>
                <h1>Test Transformation</h1>
                <xsl:apply-templates select="order"/>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="order">
        <div class="order">
            <h2>Order: <xsl:value-of select="@id"/></h2>
            <xsl:if test="@type='premium'">
                <div class="premium-badge">Premium Order</div>
            </xsl:if>
            <xsl:apply-templates select="items"/>
        </div>
    </xsl:template>
    
    <xsl:template match="items">
        <ul>
            <xsl:for-each select="item">
                <li>
                    <xsl:value-of select="name"/> - $<xsl:value-of select="price"/>
                    <xsl:if test="price > 100">
                        <span class="expensive">Expensive Item</span>
                    </xsl:if>
                </li>
            </xsl:for-each>
        </ul>
    </xsl:template>
</xsl:stylesheet>'''
        
        xslt_file = Path(temp_dir) / "sample_transform.xslt"
        xslt_file.write_text(xslt_content)
        return str(xslt_file)
    
    def test_help_command(self, runner):
        """Test main help command."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "XSLT Test Generator v2.0" in result.stdout
        assert "analyze" in result.stdout
        assert "generate-tests" in result.stdout
        assert "analyze-only" in result.stdout
        assert "status" in result.stdout
        assert "clean" in result.stdout
    
    def test_generate_tests_help(self, runner):
        """Test generate-tests command help."""
        result = runner.invoke(app, ["generate-tests", "--help"])
        
        assert result.exit_code == 0
        assert "Generate intelligent test cases" in result.stdout
        assert "--output" in result.stdout
        assert "--format" in result.stdout
        assert "--force" in result.stdout
        assert "--verbose" in result.stdout
    
    def test_analyze_only_help(self, runner):
        """Test analyze-only command help."""
        result = runner.invoke(app, ["analyze-only", "--help"])
        
        assert result.exit_code == 0
        assert "Analyze XSLT transformation without generating tests" in result.stdout
        assert "--force" in result.stdout
    
    @patch('main_v2.TestGeneratorCLI')
    def test_generate_tests_command_success(self, mock_cli_class, runner, sample_xslt_file, temp_dir):
        """Test successful generate-tests command execution."""
        # Setup mock CLI instance
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        
        # Mock successful generation results
        mock_results = {
            'statistics': {
                'total_scenarios': 5,
                'output_formats': ['cucumber', 'pytest'],
                'coverage_metrics': {'template_coverage': '90.0%'}
            },
            'output_directory': temp_dir
        }
        mock_cli.generate_tests.return_value = mock_results
        
        # Execute command
        result = runner.invoke(app, [
            "generate-tests",
            sample_xslt_file,
            "--output", temp_dir,
            "--format", "cucumber",
            "--format", "pytest",
            "--verbose"
        ])
        
        # Verify success
        assert result.exit_code == 0
        assert "Test generation completed successfully" in result.stdout
        assert "Generated 5 test scenarios" in result.stdout
        
        # Verify CLI was called correctly
        mock_cli.generate_tests.assert_called_once()
        call_args = mock_cli.generate_tests.call_args[1]
        assert call_args['xslt_file'] == sample_xslt_file
        assert call_args['output_dir'] == temp_dir
        assert call_args['output_formats'] == ['cucumber', 'pytest']
        assert call_args['verbose'] is True
    
    @patch('main_v2.TestGeneratorCLI')
    def test_generate_tests_command_file_not_found(self, mock_cli_class, runner):
        """Test generate-tests with non-existent file."""
        result = runner.invoke(app, [
            "generate-tests",
            "/non/existent/file.xslt"
        ])
        
        assert result.exit_code == 1
        assert "XSLT file not found" in result.stdout
    
    @patch('main_v2.TestGeneratorCLI')
    def test_generate_tests_command_generation_error(self, mock_cli_class, runner, sample_xslt_file, temp_dir):
        """Test generate-tests with generation error."""
        # Setup mock to raise exception
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        mock_cli.generate_tests.side_effect = Exception("Generation failed")
        
        result = runner.invoke(app, [
            "generate-tests",
            sample_xslt_file,
            "--output", temp_dir
        ])
        
        assert result.exit_code == 1
        assert "Test generation failed" in result.stdout
    
    @patch('main_v2.TestGeneratorCLI')
    def test_analyze_only_command_success(self, mock_cli_class, runner, sample_xslt_file):
        """Test successful analyze-only command execution."""
        # Setup mock CLI instance
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        
        # Mock successful analysis results
        mock_results = {
            'analysis_id': 'test_analysis',
            'file_path': sample_xslt_file,
            'template_analysis': {'templates': {}},
            'semantic_analysis': {'patterns': []},
            'execution_analysis': {'paths': []}
        }
        mock_cli.analyze_only.return_value = mock_results
        
        # Execute command
        result = runner.invoke(app, [
            "analyze-only",
            sample_xslt_file,
            "--force"
        ])
        
        # Verify success
        assert result.exit_code == 0
        assert "Analysis completed successfully" in result.stdout
        
        # Verify CLI was called correctly
        mock_cli.analyze_only.assert_called_once_with(sample_xslt_file, force_reanalysis=True)
    
    @patch('main_v2.TestGeneratorCLI')
    def test_analyze_only_command_file_not_found(self, mock_cli_class, runner):
        """Test analyze-only with non-existent file."""
        result = runner.invoke(app, [
            "analyze-only",
            "/non/existent/file.xslt"
        ])
        
        assert result.exit_code == 1
        assert "XSLT file not found" in result.stdout
    
    @patch('main_v2.TestGeneratorCLI')
    def test_analyze_only_command_analysis_error(self, mock_cli_class, runner, sample_xslt_file):
        """Test analyze-only with analysis error."""
        # Setup mock to return error
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        mock_cli.analyze_only.return_value = {'error': 'Analysis failed'}
        
        result = runner.invoke(app, [
            "analyze-only",
            sample_xslt_file
        ])
        
        assert result.exit_code == 1
    
    @patch('main_v2.TestGeneratorCLI')
    def test_analyze_only_command_exception(self, mock_cli_class, runner, sample_xslt_file):
        """Test analyze-only with exception."""
        # Setup mock to raise exception
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        mock_cli.analyze_only.side_effect = Exception("Database error")
        
        result = runner.invoke(app, [
            "analyze-only",
            sample_xslt_file
        ])
        
        assert result.exit_code == 1
        assert "Analysis failed" in result.stdout
    
    @patch('main_v2.DatabaseManager')
    def test_status_command_success(self, mock_db_class, runner):
        """Test successful status command execution."""
        # Setup mock database manager
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.db_path = "/test/database.db"
        
        # Mock statistics
        mock_stats = {
            'files': {
                'xslt': {'count': 5, 'total_size': 1024000},
                'xsd': {'count': 3, 'total_size': 512000}
            },
            'templates': {
                'total_templates': 25,
                'named_templates': 15,
                'match_templates': 10,
                'avg_complexity': 7.5
            },
            'paths': {
                'total_paths': 50,
                'avg_path_complexity': 6.2,
                'recursive_paths': 5
            },
            'tests': {
                'total': 100,
                'by_category': {
                    'unit_tests': 60,
                    'integration_tests': 40
                }
            }
        }
        mock_db.get_analysis_statistics.return_value = mock_stats
        
        # Execute command
        result = runner.invoke(app, ["status"])
        
        # Verify success
        assert result.exit_code == 0
        assert "XSLT Test Generator v2.0 Status" in result.stdout
        assert "File Statistics" in result.stdout
        assert "Templates: 25" in result.stdout
        assert "Execution Paths: 50" in result.stdout
        assert "Test Cases: 100" in result.stdout
    
    @patch('main_v2.DatabaseManager')
    def test_status_command_error(self, mock_db_class, runner):
        """Test status command with database error."""
        # Setup mock to raise exception
        mock_db_class.side_effect = Exception("Database connection failed")
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 1
        assert "Error getting status" in result.stdout
    
    @patch('main_v2.DatabaseManager')
    @patch('typer.confirm')
    def test_clean_command_success(self, mock_confirm, mock_db_class, runner):
        """Test successful clean command execution."""
        # Setup mocks
        mock_confirm.return_value = True
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        # Execute command
        result = runner.invoke(app, [
            "clean",
            "--keep-files"
        ])
        
        # Verify success
        assert result.exit_code == 0
        assert "Analysis data cleaned successfully" in result.stdout
        
        # Verify database cleanup was called
        mock_db.cleanup_analysis.assert_called_once_with(keep_files=True)
    
    @patch('main_v2.DatabaseManager')
    @patch('typer.confirm')
    def test_clean_command_cancelled(self, mock_confirm, mock_db_class, runner):
        """Test clean command cancelled by user."""
        # Setup mock to return False (user cancels)
        mock_confirm.return_value = False
        
        result = runner.invoke(app, ["clean"])
        
        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout
    
    @patch('main_v2.DatabaseManager')
    @patch('typer.confirm')
    def test_clean_command_error(self, mock_confirm, mock_db_class, runner):
        """Test clean command with database error."""
        # Setup mocks
        mock_confirm.return_value = True
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.cleanup_analysis.side_effect = Exception("Cleanup failed")
        
        result = runner.invoke(app, ["clean"])
        
        assert result.exit_code == 1
        assert "Error cleaning database" in result.stdout
    
    def test_generate_tests_default_formats(self, runner, sample_xslt_file):
        """Test generate-tests command uses default formats when none specified."""
        with patch('main_v2.TestGeneratorCLI') as mock_cli_class:
            mock_cli = Mock()
            mock_cli_class.return_value = mock_cli
            mock_cli.generate_tests.return_value = {
                'statistics': {'total_scenarios': 3},
                'output_directory': '/test'
            }
            
            result = runner.invoke(app, [
                "generate-tests",
                sample_xslt_file
            ])
            
            # Should use default formats
            call_args = mock_cli.generate_tests.call_args[1]
            assert set(call_args['output_formats']) == {'cucumber', 'pytest', 'json'}
    
    def test_generate_tests_custom_formats(self, runner, sample_xslt_file):
        """Test generate-tests command with custom formats."""
        with patch('main_v2.TestGeneratorCLI') as mock_cli_class:
            mock_cli = Mock()
            mock_cli_class.return_value = mock_cli
            mock_cli.generate_tests.return_value = {
                'statistics': {'total_scenarios': 3},
                'output_directory': '/test'
            }
            
            result = runner.invoke(app, [
                "generate-tests",
                sample_xslt_file,
                "--format", "cucumber",
                "--format", "xml_unit"
            ])
            
            # Should use specified formats
            call_args = mock_cli.generate_tests.call_args[1]
            assert call_args['output_formats'] == ['cucumber', 'xml_unit']
    
    def test_logging_configuration(self, runner, sample_xslt_file):
        """Test that logging is properly configured."""
        with patch('main_v2.TestGeneratorCLI') as mock_cli_class, \
             patch('main_v2.setup_logging') as mock_setup_logging, \
             patch('main_v2.get_logger') as mock_get_logger:
            
            mock_cli = Mock()
            mock_cli_class.return_value = mock_cli
            mock_cli.generate_tests.return_value = {
                'statistics': {'total_scenarios': 3},
                'output_directory': '/test'
            }
            
            result = runner.invoke(app, [
                "generate-tests",
                sample_xslt_file,
                "--log-level", "DEBUG",
                "--no-log-to-file"
            ])
            
            # Verify logging setup was called with correct parameters
            mock_setup_logging.assert_called_once_with(
                log_level="DEBUG",
                log_to_file=False,
                log_dir="logs",
                enable_structured_logging=True
            )
            mock_get_logger.assert_called_once()
    
    def test_real_subprocess_execution(self, sample_xslt_file):
        """Test actual subprocess execution (integration test)."""
        # This test actually runs the CLI as a subprocess
        # Skip if we're in a testing environment that doesn't support this
        try:
            result = subprocess.run([
                sys.executable, "main_v2.py", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "XSLT Test Generator v2.0" in result.stdout
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Skip if subprocess execution fails (e.g., in some CI environments)
            pytest.skip("Subprocess execution not available")
    
    def test_command_argument_validation(self, runner):
        """Test command argument validation."""
        # Test generate-tests without required argument
        result = runner.invoke(app, ["generate-tests"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "Error" in result.stdout
        
        # Test analyze-only without required argument
        result = runner.invoke(app, ["analyze-only"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "Error" in result.stdout