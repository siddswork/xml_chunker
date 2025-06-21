"""Unit tests for DatabaseManager class."""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

from xslt_test_generator.database.connection import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager."""
    
    def test_database_creation(self, temp_dir):
        """Test database creation and schema initialization."""
        db_path = str(temp_dir / "test_creation.db")
        
        # Database should not exist initially
        assert not Path(db_path).exists()
        
        # Create database manager
        db = DatabaseManager(db_path)
        
        # Database should now exist
        assert Path(db_path).exists()
        
        # Verify it's a valid SQLite database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
        # Check that key tables exist
        expected_tables = [
            'transformation_files', 'file_dependencies', 'xslt_templates',
            'xslt_variables', 'template_calls', 'xsd_elements', 'xsd_types',
            'execution_paths', 'test_specifications'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
    
    def test_database_reuse(self, temp_dir):
        """Test that existing database is reused correctly."""
        db_path = str(temp_dir / "test_reuse.db")
        
        # Create first database manager
        db1 = DatabaseManager(db_path)
        
        # Insert some test data
        file_id = db1.insert_file(
            file_path="/test/file.xsl",
            file_type="xslt",
            content_hash="abc123",
            file_size=1000,
            last_modified="2024-01-01 12:00:00"
        )
        
        # Create second database manager with same path
        db2 = DatabaseManager(db_path)
        
        # Verify data is still there
        file_record = db2.get_file_by_path("/test/file.xsl")
        assert file_record is not None
        assert file_record['id'] == file_id
        assert file_record['content_hash'] == "abc123"
    
    def test_insert_file(self, db_manager):
        """Test file insertion."""
        file_id = db_manager.insert_file(
            file_path="/path/to/transform.xsl",
            file_type="xslt",
            content_hash="hash123",
            file_size=5000,
            last_modified="2024-01-01 10:00:00",
            imports=["common/utils.xsl", "templates/main.xsl"]
        )
        
        assert isinstance(file_id, int)
        assert file_id > 0
        
        # Verify file was inserted correctly
        file_record = db_manager.get_file_by_path("/path/to/transform.xsl")
        assert file_record is not None
        assert file_record['file_type'] == "xslt"
        assert file_record['content_hash'] == "hash123"
        assert file_record['file_size'] == 5000
        assert file_record['analysis_status'] == "pending"
        
        # Verify imports were stored as JSON
        import json
        imports = json.loads(file_record['imports'])
        assert imports == ["common/utils.xsl", "templates/main.xsl"]
    
    def test_get_file_by_path(self, db_manager):
        """Test file retrieval by path."""
        # Insert test file
        db_manager.insert_file(
            file_path="/test/sample.xsl",
            file_type="xslt",
            content_hash="test_hash",
            file_size=2000,
            last_modified="2024-01-01 15:00:00"
        )
        
        # Test successful retrieval
        file_record = db_manager.get_file_by_path("/test/sample.xsl")
        assert file_record is not None
        assert file_record['file_path'] == "/test/sample.xsl"
        
        # Test non-existent file
        non_existent = db_manager.get_file_by_path("/does/not/exist.xsl")
        assert non_existent is None
    
    def test_update_file_analysis_status(self, db_manager):
        """Test updating file analysis status."""
        # Insert test file
        file_id = db_manager.insert_file(
            file_path="/test/status.xsl",
            file_type="xslt",
            content_hash="status_hash",
            file_size=1500,
            last_modified="2024-01-01 16:00:00"
        )
        
        # Update status to analyzing
        db_manager.update_file_analysis_status(file_id, "analyzing")
        
        file_record = db_manager.get_file_by_path("/test/status.xsl")
        assert file_record['analysis_status'] == "analyzing"
        assert file_record['error_message'] is None
        
        # Update status to error with message
        db_manager.update_file_analysis_status(file_id, "error", "Parse error on line 42")
        
        file_record = db_manager.get_file_by_path("/test/status.xsl")
        assert file_record['analysis_status'] == "error"
        assert file_record['error_message'] == "Parse error on line 42"
        
        # Update status to completed
        db_manager.update_file_analysis_status(file_id, "completed")
        
        file_record = db_manager.get_file_by_path("/test/status.xsl")
        assert file_record['analysis_status'] == "completed"
    
    def test_insert_file_dependency(self, db_manager):
        """Test file dependency insertion."""
        # Insert parent and child files
        parent_id = db_manager.insert_file(
            file_path="/parent.xsl",
            file_type="xslt",
            content_hash="parent_hash",
            file_size=3000,
            last_modified="2024-01-01 17:00:00"
        )
        
        child_id = db_manager.insert_file(
            file_path="/child.xsl", 
            file_type="xslt",
            content_hash="child_hash",
            file_size=1000,
            last_modified="2024-01-01 17:00:00"
        )
        
        # Insert dependency
        dep_id = db_manager.insert_file_dependency(
            parent_file_id=parent_id,
            child_file_id=child_id,
            import_type="xsl:import",
            namespace="http://example.com",
            xpath_location="line 5",
            href_attribute="child.xsl",
            resolved_path="/absolute/path/child.xsl"
        )
        
        assert isinstance(dep_id, int)
        assert dep_id > 0
        
        # Verify dependency was inserted
        dependencies = db_manager.get_file_dependencies(parent_id)
        assert len(dependencies) == 1
        
        dep = dependencies[0]
        assert dep['child_file_id'] == child_id
        assert dep['import_type'] == "xsl:import"
        assert dep['namespace'] == "http://example.com"
        assert dep['child_path'] == "/child.xsl"
    
    def test_get_file_dependencies(self, db_manager):
        """Test getting file dependencies."""
        # Insert files
        parent_id = db_manager.insert_file(
            file_path="/main.xsl",
            file_type="xslt",
            content_hash="main_hash",
            file_size=4000,
            last_modified="2024-01-01 18:00:00"
        )
        
        child1_id = db_manager.insert_file(
            file_path="/utils.xsl",
            file_type="xslt", 
            content_hash="utils_hash",
            file_size=1500,
            last_modified="2024-01-01 18:00:00"
        )
        
        child2_id = db_manager.insert_file(
            file_path="/templates.xsl",
            file_type="xslt",
            content_hash="templates_hash", 
            file_size=2000,
            last_modified="2024-01-01 18:00:00"
        )
        
        # Insert dependencies
        db_manager.insert_file_dependency(parent_id, child1_id, "xsl:import")
        db_manager.insert_file_dependency(parent_id, child2_id, "xsl:include")
        
        # Test retrieval
        dependencies = db_manager.get_file_dependencies(parent_id)
        assert len(dependencies) == 2
        
        dep_types = {dep['import_type'] for dep in dependencies}
        assert dep_types == {"xsl:import", "xsl:include"}
        
        dep_paths = {dep['child_path'] for dep in dependencies}
        assert dep_paths == {"/utils.xsl", "/templates.xsl"}
    
    def test_insert_xslt_template(self, db_manager):
        """Test XSLT template insertion."""
        # Insert file first
        file_id = db_manager.insert_file(
            file_path="/templates.xsl",
            file_type="xslt",
            content_hash="template_hash",
            file_size=2500,
            last_modified="2024-01-01 19:00:00"
        )
        
        # Insert template
        template_data = {
            'name': 'processPassenger',
            'match_pattern': 'passenger',
            'mode': 'process',
            'priority': 1,
            'line_start': 10,
            'line_end': 25,
            'template_content': '<xsl:template name="processPassenger">...</xsl:template>',
            'calls_templates': ['formatName', 'validateData'],
            'called_by_templates': [],
            'uses_variables': ['$passengerType', '$defaultValues'],
            'defines_variables': ['$processedName'],
            'xpath_expressions': ['@type', 'name/text()', '//booking'],
            'conditional_logic': [
                {'type': 'if', 'condition': '@type="adult"', 'line': 15}
            ],
            'output_elements': ['traveler', 'name', 'category'],
            'template_hash': 'template_content_hash',
            'complexity_score': 5,
            'is_recursive': False
        }
        
        template_id = db_manager.insert_xslt_template(file_id, template_data)
        assert isinstance(template_id, int)
        assert template_id > 0
        
        # Verify template was inserted
        templates = db_manager.get_templates_by_file(file_id)
        assert len(templates) == 1
        
        template = templates[0]
        assert template['name'] == 'processPassenger'
        assert template['match_pattern'] == 'passenger'
        assert template['complexity_score'] == 5
        
        # Verify JSON fields were stored correctly
        import json
        calls = json.loads(template['calls_templates'])
        assert calls == ['formatName', 'validateData']
        
        uses_vars = json.loads(template['uses_variables'])
        assert uses_vars == ['$passengerType', '$defaultValues']
    
    def test_get_all_files(self, db_manager):
        """Test getting all files."""
        # Initially should be empty
        files = db_manager.get_all_files()
        assert len(files) == 0
        
        # Insert some files
        db_manager.insert_file("/file1.xsl", "xslt", "hash1", 1000, "2024-01-01 10:00:00")
        db_manager.insert_file("/file2.xsd", "xsd", "hash2", 2000, "2024-01-01 11:00:00")
        db_manager.insert_file("/file3.xsl", "xslt", "hash3", 1500, "2024-01-01 12:00:00")
        
        # Test retrieval
        files = db_manager.get_all_files()
        assert len(files) == 3
        
        # Verify files are sorted by path
        paths = [f['file_path'] for f in files]
        assert paths == sorted(paths)
        
        # Verify file types
        types = [f['file_type'] for f in files]
        assert set(types) == {'xslt', 'xsd'}
    
    def test_get_analysis_statistics(self, db_manager):
        """Test analysis statistics generation."""
        # Insert test data
        file1_id = db_manager.insert_file("/test1.xsl", "xslt", "hash1", 1000, "2024-01-01 10:00:00")
        file2_id = db_manager.insert_file("/test2.xsd", "xsd", "hash2", 2000, "2024-01-01 11:00:00")
        file3_id = db_manager.insert_file("/test3.xsl", "xslt", "hash3", 1500, "2024-01-01 12:00:00")
        
        # Insert some templates
        template_data = {
            'name': 'test_template',
            'line_start': 1,
            'line_end': 10,
            'template_content': 'test content',
            'complexity_score': 3
        }
        db_manager.insert_xslt_template(file1_id, template_data)
        
        template_data['name'] = 'another_template'
        template_data['complexity_score'] = 7
        db_manager.insert_xslt_template(file3_id, template_data)
        
        # Get statistics
        stats = db_manager.get_analysis_statistics()
        
        # Verify file statistics
        assert 'files' in stats
        assert stats['files']['xslt']['count'] == 2
        assert stats['files']['xslt']['total_size'] == 2500  # 1000 + 1500
        assert stats['files']['xsd']['count'] == 1
        assert stats['files']['xsd']['total_size'] == 2000
        
        # Verify template statistics
        assert 'templates' in stats
        assert stats['templates']['total_templates'] == 2
        assert stats['templates']['named_templates'] == 2
        assert stats['templates']['match_templates'] == 0
        assert stats['templates']['avg_complexity'] == 5.0  # (3 + 7) / 2
    
    def test_cleanup_analysis(self, db_manager):
        """Test analysis data cleanup."""
        # Insert test data
        file_id = db_manager.insert_file("/test.xsl", "xslt", "hash", 1000, "2024-01-01 10:00:00")
        
        template_data = {
            'name': 'test_template',
            'line_start': 1,
            'line_end': 10,
            'template_content': 'test'
        }
        db_manager.insert_xslt_template(file_id, template_data)
        
        # Verify data exists
        files = db_manager.get_all_files()
        templates = db_manager.get_templates_by_file(file_id)
        assert len(files) == 1
        assert len(templates) == 1
        
        # Cleanup keeping files
        db_manager.cleanup_analysis(keep_files=True)
        
        # Files should still exist but templates should be gone
        files_after = db_manager.get_all_files()
        templates_after = db_manager.get_templates_by_file(file_id)
        assert len(files_after) == 1
        assert len(templates_after) == 0
        
        # Status should be reset to pending
        file_record = db_manager.get_file_by_path("/test.xsl")
        assert file_record['analysis_status'] == 'pending'
        
        # Cleanup removing everything
        db_manager.cleanup_analysis(keep_files=False)
        
        # Everything should be gone
        files_final = db_manager.get_all_files()
        assert len(files_final) == 0
    
    def test_database_error_handling(self, temp_dir):
        """Test database error handling."""
        # Test with invalid database path
        invalid_path = str(temp_dir / "nonexistent" / "test.db")
        
        # Should create directory and succeed
        db = DatabaseManager(invalid_path)
        assert Path(invalid_path).exists()
        
        # Test with read-only directory (if possible to simulate)
        # This test might be platform-specific
        
    def test_concurrent_database_access(self, test_db_path):
        """Test concurrent database access."""
        # Create two database managers
        db1 = DatabaseManager(test_db_path)
        db2 = DatabaseManager(test_db_path)
        
        # Insert from both
        file1_id = db1.insert_file("/file1.xsl", "xslt", "hash1", 1000, "2024-01-01 10:00:00")
        file2_id = db2.insert_file("/file2.xsl", "xslt", "hash2", 2000, "2024-01-01 11:00:00")
        
        # Both should see each other's data
        file1_from_db2 = db2.get_file_by_path("/file1.xsl")
        file2_from_db1 = db1.get_file_by_path("/file2.xsl")
        
        assert file1_from_db2 is not None
        assert file2_from_db1 is not None
        assert file1_from_db2['id'] == file1_id
        assert file2_from_db1['id'] == file2_id
    
    def test_unique_constraints(self, db_manager):
        """Test database unique constraints."""
        # Insert file
        db_manager.insert_file("/test.xsl", "xslt", "hash", 1000, "2024-01-01 10:00:00")
        
        # Try to insert same file path again - should raise error
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.insert_file("/test.xsl", "xslt", "different_hash", 2000, "2024-01-01 11:00:00")