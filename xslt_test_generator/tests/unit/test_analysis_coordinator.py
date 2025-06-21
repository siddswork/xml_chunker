"""Unit tests for Analysis Coordinator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from xslt_test_generator.analysis.analysis_coordinator import AnalysisCoordinator
from xslt_test_generator.database.connection import DatabaseManager


class TestAnalysisCoordinator:
    """Test cases for Analysis Coordinator."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager."""
        mock_db = Mock(spec=DatabaseManager)
        mock_db.get_file_by_path.return_value = {
            'id': 1,
            'file_path': '/test/file.xsl',
            'analysis_status': 'pending'
        }
        mock_db.update_file_analysis_status.return_value = None
        mock_db.insert_xslt_template.return_value = 1
        mock_db.insert_xslt_variable.return_value = 1
        mock_db.insert_execution_path.return_value = 1
        mock_db.insert_semantic_pattern.return_value = 1
        mock_db.insert_transformation_hotspot.return_value = 1
        mock_db.get_templates_by_file.return_value = []
        return mock_db
    
    @pytest.fixture
    def coordinator(self, mock_db_manager):
        """Create analysis coordinator instance."""
        return AnalysisCoordinator(mock_db_manager)
    
    @pytest.fixture
    def sample_xslt_file(self, temp_dir):
        """Create sample XSLT file for testing."""
        xslt_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:variable name="title" select="'Test Document'"/>
    
    <xsl:template match="/">
        <html>
            <head><title><xsl:value-of select="$title"/></title></head>
            <body>
                <xsl:apply-templates select="//item"/>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="item">
        <div>
            <xsl:if test="@priority = 'high'">
                <span class="priority">HIGH</span>
            </xsl:if>
            <xsl:value-of select="@name"/>
        </div>
    </xsl:template>
</xsl:stylesheet>'''
        
        xslt_file = temp_dir / "sample.xsl"
        xslt_file.write_text(xslt_content)
        return str(xslt_file)
    
    def test_coordinator_initialization(self, coordinator, mock_db_manager):
        """Test coordinator initialization."""
        assert coordinator.db == mock_db_manager
        assert coordinator.template_parser is not None
        assert coordinator.semantic_analyzer is not None
        assert coordinator.execution_analyzer is not None
    
    @patch('xslt_test_generator.analysis.analysis_coordinator.datetime')
    def test_analyze_xslt_file_success(self, mock_datetime, coordinator, sample_xslt_file):
        """Test successful XSLT file analysis."""
        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        result = coordinator.analyze_xslt_file(sample_xslt_file)
        
        # Check basic structure
        assert 'analysis_id' in result
        assert 'file_path' in result
        assert 'template_analysis' in result
        assert 'semantic_analysis' in result
        assert 'execution_analysis' in result
        assert 'analysis_timestamp' in result
        assert 'summary' in result
        assert 'error' not in result
        
        # Check that phases completed
        template_analysis = result['template_analysis']
        assert 'templates' in template_analysis
        assert 'variables' in template_analysis
        assert len(template_analysis['templates']) > 0
        
        semantic_analysis = result['semantic_analysis']
        assert 'semantic_patterns' in semantic_analysis
        assert 'data_flow_graph' in semantic_analysis
        
        execution_analysis = result['execution_analysis']
        assert 'execution_paths' in execution_analysis
        assert 'entry_points' in execution_analysis
        
        # Check database interactions
        coordinator.db.update_file_analysis_status.assert_called()
        coordinator.db.insert_xslt_template.assert_called()
        coordinator.db.insert_xslt_variable.assert_called()
    
    def test_analyze_xslt_file_already_completed(self, coordinator, sample_xslt_file):
        """Test analysis of already completed file."""
        # Mock file as already completed
        coordinator.db.get_file_by_path.return_value = {
            'id': 1,
            'file_path': sample_xslt_file,
            'analysis_status': 'completed'
        }
        
        result = coordinator.analyze_xslt_file(sample_xslt_file, force_reanalysis=False)
        
        # Should load existing analysis
        assert 'analysis_id' in result
        assert 'status' in result
        assert result['status'] == 'loaded_from_cache'
        
        # Should not call update_file_analysis_status for new analysis
        coordinator.db.update_file_analysis_status.assert_not_called()
    
    def test_analyze_xslt_file_force_reanalysis(self, coordinator, sample_xslt_file):
        """Test forced reanalysis of completed file."""
        # Mock file as already completed
        coordinator.db.get_file_by_path.return_value = {
            'id': 1,
            'file_path': sample_xslt_file,
            'analysis_status': 'completed'
        }
        
        result = coordinator.analyze_xslt_file(sample_xslt_file, force_reanalysis=True)
        
        # Should perform new analysis despite completion status
        assert 'template_analysis' in result
        assert 'semantic_analysis' in result
        assert 'execution_analysis' in result
        assert 'error' not in result
    
    def test_analyze_xslt_file_nonexistent(self, coordinator):
        """Test analysis of non-existent file."""
        result = coordinator.analyze_xslt_file("/nonexistent/file.xsl")
        
        assert 'error' in result
        assert 'No such file or directory' in result['error']
    
    def test_analyze_xslt_file_corrupted(self, coordinator, temp_dir):
        """Test analysis of corrupted XSLT file."""
        corrupted_content = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output>
            <unclosed-tag>
        </output>
    <!-- Missing closing tags -->'''
        
        corrupted_file = temp_dir / "corrupted.xsl"
        corrupted_file.write_text(corrupted_content)
        
        result = coordinator.analyze_xslt_file(str(corrupted_file))
        
        assert 'error' in result
        # Should update database with error status
        coordinator.db.update_file_analysis_status.assert_called_with(
            1, 'error', unittest.mock.ANY
        )
    
    def test_analyze_multiple_files(self, coordinator, temp_dir):
        """Test batch analysis of multiple files."""
        # Create multiple test files
        files = []
        for i in range(3):
            content = f'''<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output{i}>Test {i}</output{i}>
    </xsl:template>
</xsl:stylesheet>'''
            file_path = temp_dir / f"test_{i}.xsl"
            file_path.write_text(content)
            files.append(str(file_path))
        
        result = coordinator.analyze_multiple_files(files)
        
        # Check batch result structure
        assert 'batch_summary' in result
        assert 'file_results' in result
        assert 'errors' in result
        assert 'cross_file_analysis' in result
        assert 'aggregated_statistics' in result
        
        # Check batch summary
        batch_summary = result['batch_summary']
        assert batch_summary['total_files'] == 3
        assert batch_summary['successful_analyses'] > 0
        assert 'analysis_timestamp' in batch_summary
        
        # Check individual file results
        file_results = result['file_results']
        assert len(file_results) > 0
    
    def test_get_analysis_recommendations(self, coordinator, sample_xslt_file):
        """Test analysis recommendations generation."""
        # Mock completed analysis
        coordinator.db.get_file_by_path.return_value = {
            'id': 1,
            'file_path': sample_xslt_file,
            'analysis_status': 'completed'
        }
        
        # Mock template data
        coordinator.db.get_templates_by_file.return_value = [
            {
                'id': 1,
                'name': 'testTemplate',
                'complexity_score': 15,
                'is_recursive': False,
                'conditional_logic': '[{"type": "if", "condition": "test"}]'
            }
        ]
        
        result = coordinator.get_analysis_recommendations(sample_xslt_file)
        
        # Check recommendation structure
        assert 'test_prioritization' in result
        assert 'test_data_generation' in result
        assert 'coverage_strategy' in result
        assert 'risk_assessment' in result
        assert 'optimization_suggestions' in result
        assert 'error' not in result
        
        # Check test prioritization
        priorities = result['test_prioritization']
        assert len(priorities) >= 0
        
        if priorities:
            priority = priorities[0]
            assert 'template_name' in priority
            assert 'priority' in priority
            assert 'priority_score' in priority
            assert 'reasons' in priority
    
    def test_get_analysis_recommendations_no_analysis(self, coordinator):
        """Test recommendations for file without completed analysis."""
        coordinator.db.get_file_by_path.return_value = None
        
        result = coordinator.get_analysis_recommendations("/test/file.xsl")
        
        assert 'error' in result
        assert 'No completed analysis found' in result['error']
    
    def test_test_prioritization_recommendations(self, coordinator):
        """Test test prioritization logic."""
        # Mock high complexity templates
        templates = [
            {
                'name': 'highComplexity',
                'complexity_score': 20,
                'is_recursive': False,
                'conditional_logic': '[{"type": "if"}, {"type": "choose"}, {"type": "when"}]'  # 3 conditions > 2
            },
            {
                'name': 'recursiveTemplate',
                'complexity_score': 15,  # > 10 to get complexity bonus
                'is_recursive': True,
                'conditional_logic': '[{"type": "if"}, {"type": "choose"}, {"type": "when"}]'  # 3 conditions > 2
            },
            {
                'name': 'simpleTemplate',
                'complexity_score': 3,
                'is_recursive': False,
                'conditional_logic': '[]'
            }
        ]
        
        priorities = coordinator._recommend_test_prioritization(templates)
        
        # High complexity and recursive templates should be prioritized
        high_priority = [p for p in priorities if p['priority'] == 'high']
        assert len(high_priority) >= 1
        
        # Check that high complexity template is prioritized
        template_names = [p['template_name'] for p in high_priority]
        assert 'highComplexity' in template_names or 'recursiveTemplate' in template_names
    
    def test_risk_assessment(self, coordinator):
        """Test risk assessment generation."""
        templates = [
            {
                'name': 'veryHighComplexity',
                'complexity_score': 25,
                'is_recursive': False
            },
            {
                'name': 'recursiveTemplate',
                'complexity_score': 8,
                'is_recursive': True
            }
        ]
        
        risks = coordinator._assess_transformation_risks(templates)
        
        # Should identify risks
        assert len(risks) > 0
        
        # Check risk structure
        risk = risks[0]
        assert 'risk_type' in risk
        assert 'severity' in risk
        assert 'description' in risk
        assert 'affected_templates' in risk
        assert 'mitigation' in risk
        
        # Should identify high complexity risk
        risk_types = [r['risk_type'] for r in risks]
        assert 'high_complexity' in risk_types or 'recursion' in risk_types
    
    def test_cross_file_analysis(self, coordinator):
        """Test cross-file analysis logic."""
        # Mock results from multiple files
        results = {
            'file1.xsl': {
                'template_analysis': {
                    'templates': {
                        'template1': Mock(calls_templates=['sharedTemplate']),
                        'template2': Mock(calls_templates=[])
                    }
                },
                'semantic_analysis': {
                    'semantic_patterns': [
                        Mock(pattern_type='conditional_processing', confidence_score=0.9)
                    ]
                }
            },
            'file2.xsl': {
                'template_analysis': {
                    'templates': {
                        'template3': Mock(calls_templates=['sharedTemplate']),
                        'sharedTemplate': Mock(calls_templates=[])
                    }
                },
                'semantic_analysis': {
                    'semantic_patterns': [
                        Mock(pattern_type='conditional_processing', confidence_score=0.8)
                    ]
                }
            }
        }
        
        cross_analysis = coordinator._perform_cross_file_analysis(results)
        
        # Check cross-file analysis structure
        assert 'total_templates' in cross_analysis
        assert 'cross_file_dependencies' in cross_analysis
        assert 'common_patterns' in cross_analysis
        assert 'integration_test_requirements' in cross_analysis
        
        # Should identify shared templates
        dependencies = cross_analysis['cross_file_dependencies']
        assert len(dependencies) > 0
        
        # Should identify common patterns
        common_patterns = cross_analysis['common_patterns']
        assert len(common_patterns) > 0
    
    def test_aggregated_statistics(self, coordinator):
        """Test aggregated statistics generation."""
        results = {
            'file1.xsl': {
                'template_analysis': {
                    'analysis_summary': {
                        'total_templates': 5,
                        'avg_complexity': 8.0
                    }
                },
                'semantic_analysis': {
                    'analysis_summary': {
                        'transformation_complexity': 40,
                        'total_patterns': 3
                    }
                },
                'execution_analysis': {
                    'path_statistics': {
                        'total_paths': 7
                    }
                }
            },
            'file2.xsl': {
                'template_analysis': {
                    'analysis_summary': {
                        'total_templates': 3,
                        'avg_complexity': 6.0
                    }
                },
                'semantic_analysis': {
                    'analysis_summary': {
                        'transformation_complexity': 20,
                        'total_patterns': 2
                    }
                },
                'execution_analysis': {
                    'path_statistics': {
                        'total_paths': 4
                    }
                }
            }
        }
        
        stats = coordinator._generate_aggregated_statistics(results)
        
        # Check aggregated values
        assert stats['total_templates'] == 8  # 5 + 3
        assert stats['total_complexity_score'] == 60  # 40 + 20
        assert stats['total_semantic_patterns'] == 5  # 3 + 2
        assert stats['total_execution_paths'] == 11  # 7 + 4
        assert stats['average_complexity_per_file'] == 30  # 60 / 2
    
    def test_error_handling_in_storage(self, coordinator, sample_xslt_file):
        """Test error handling during result storage."""
        # Mock database error
        coordinator.db.insert_xslt_template.side_effect = Exception("Database error")
        
        result = coordinator.analyze_xslt_file(sample_xslt_file)
        
        # Should handle storage errors gracefully
        assert 'error' in result
        assert 'Database error' in result['error']
        
        # Should update status to error
        coordinator.db.update_file_analysis_status.assert_called_with(
            1, 'error', unittest.mock.ANY
        )
    
    def test_complete_summary_generation(self, coordinator):
        """Test complete analysis summary generation."""
        # Mock analysis results
        parse_results = {
            'analysis_summary': {
                'total_templates': 5,
                'avg_complexity': 8.0
            }
        }
        
        semantic_results = {
            'analysis_summary': {
                'total_patterns': 3,
                'transformation_complexity': 40
            },
            'semantic_patterns': [
                Mock(confidence_score=0.9),
                Mock(confidence_score=0.8),
                Mock(confidence_score=0.7)
            ],
            'transformation_hotspots': [
                Mock(template_name='hotspot1', hotspot_score=15)
            ]
        }
        
        execution_results = {
            'path_statistics': {
                'total_paths': 7,
                'avg_path_complexity': 5.0
            },
            'execution_paths': [
                Mock(complexity_score=10),
                Mock(complexity_score=8)
            ]
        }
        
        summary = coordinator._generate_complete_summary(
            parse_results, semantic_results, execution_results
        )
        
        # Check summary structure
        assert 'parsing_summary' in summary
        assert 'semantic_summary' in summary
        assert 'execution_summary' in summary
        assert 'overall_complexity' in summary
        assert 'test_generation_priority' in summary
        assert 'key_findings' in summary
        
        # Check calculated values
        assert summary['overall_complexity'] > 0
        assert summary['test_generation_priority'] in ['low', 'medium', 'high']
        assert len(summary['key_findings']) > 0
    
    @patch('xslt_test_generator.analysis.analysis_coordinator.datetime')
    def test_analysis_timestamp(self, mock_datetime, coordinator, sample_xslt_file):
        """Test analysis timestamp generation."""
        fixed_time = "2024-01-01T12:00:00"
        mock_datetime.now.return_value.isoformat.return_value = fixed_time
        
        result = coordinator.analyze_xslt_file(sample_xslt_file)
        
        assert result['analysis_timestamp'] == fixed_time
    
    def test_integration_requirements_generation(self, coordinator):
        """Test integration test requirements generation."""
        cross_file_deps = [
            {
                'template': 'sharedTemplate',
                'callers': [
                    {'calling_file': 'file1.xsl', 'calling_template': 'template1'},
                    {'calling_file': 'file2.xsl', 'calling_template': 'template2'}
                ],
                'complexity': 'high'
            }
        ]
        
        requirements = coordinator._generate_integration_requirements(cross_file_deps)
        
        # Should generate integration requirements
        assert len(requirements) > 0
        
        requirement = requirements[0]
        assert requirement['requirement_type'] == 'cross_file_integration'
        assert 'sharedTemplate' in requirement['description']
        assert len(requirement['involved_files']) == 2
        assert requirement['complexity'] == 'high'
        assert len(requirement['test_scenarios']) > 0


# Import for mock assertion
import unittest.mock