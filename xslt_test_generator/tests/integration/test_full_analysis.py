"""Integration tests for complete analysis workflow."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path

from xslt_test_generator.database.connection import DatabaseManager
from xslt_test_generator.core.file_discovery import FileDiscoveryEngine


class TestFullAnalysisWorkflow:
    """Test complete analysis workflows end-to-end."""
    
    def test_single_file_analysis_workflow(self, temp_dir, sample_xslt_content):
        """Test complete workflow with single XSLT file."""
        # Create test file
        xslt_file = temp_dir / "transform.xsl"
        xslt_file.write_text(sample_xslt_content)
        
        # Create database
        db_path = str(temp_dir / "analysis.db")
        db = DatabaseManager(db_path)
        
        # Initialize file discovery
        discovery = FileDiscoveryEngine(db)
        
        # Step 1: Discovery
        discovered_files = discovery.discover_transformation_ecosystem(str(xslt_file))
        
        assert len(discovered_files) >= 1
        assert str(xslt_file.resolve()) in discovered_files
        
        # Step 2: Storage
        file_id_map = discovery.store_discovered_files()
        
        assert len(file_id_map) == len(discovered_files)
        
        # Step 3: Verify database state
        all_files = db.get_all_files()
        assert len(all_files) == len(discovered_files)
        
        for file_record in all_files:
            assert file_record['analysis_status'] == 'pending'
            assert file_record['file_type'] in ['xslt', 'xsd', 'xml']
        
        # Step 4: Change detection
        changed_files = discovery.detect_changed_files()
        assert len(changed_files) == len(discovered_files)  # All files are new
        
        # Step 5: Mark as analyzed
        for file_path in changed_files:
            file_record = db.get_file_by_path(file_path)
            db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Step 6: Verify no changes needed
        changed_after_analysis = discovery.detect_changed_files()
        assert len(changed_after_analysis) == 0
        
        # Step 7: Statistics
        stats = db.get_analysis_statistics()
        assert stats['files']['xslt']['count'] >= 1
    
    def test_multi_file_analysis_workflow(self, sample_files_structure, temp_dir):
        """Test complete workflow with multi-file ecosystem."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        # Create database
        db_path = str(temp_dir / "multi_analysis.db")
        db = DatabaseManager(db_path)
        
        # Initialize discovery
        discovery = FileDiscoveryEngine(db)
        
        # Full workflow
        discovered_files = discovery.discover_transformation_ecosystem(main_xslt_path)
        file_id_map = discovery.store_discovered_files()
        changed_files = discovery.detect_changed_files()
        
        # Verify multi-file discovery
        assert len(discovered_files) >= 3  # main + dependencies
        assert len(file_id_map) == len(discovered_files)
        assert len(changed_files) == len(discovered_files)
        
        # Verify dependency relationships
        dependencies_count = 0
        for file_id in file_id_map.values():
            deps = db.get_file_dependencies(file_id)
            dependencies_count += len(deps)
        
        assert dependencies_count >= 2  # At least main->utils and main->passenger
        
        # Process files in dependency order
        processing_order = discovery.get_dependency_order()
        
        for file_path in processing_order:
            file_record = db.get_file_by_path(file_path)
            assert file_record is not None
            
            # Simulate analysis
            db.update_file_analysis_status(file_record['id'], 'analyzing')
            # ... analysis would happen here ...
            db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Verify all files are completed
        final_files = db.get_all_files()
        for file_record in final_files:
            assert file_record['analysis_status'] == 'completed'
        
        # Verify no more changes needed
        final_changes = discovery.detect_changed_files()
        assert len(final_changes) == 0
    
    def test_incremental_analysis_after_file_modification(self, sample_files_structure, temp_dir):
        """Test incremental analysis after file modifications."""
        main_xslt_path = sample_files_structure['main_xslt']
        utils_xslt_path = sample_files_structure['utils_xslt']
        
        db_path = str(temp_dir / "incremental.db")
        db = DatabaseManager(db_path)
        discovery = FileDiscoveryEngine(db)
        
        # Initial analysis
        discovery.discover_transformation_ecosystem(main_xslt_path)
        discovery.store_discovered_files()
        initial_changed = discovery.detect_changed_files()
        
        # Mark all as completed
        for file_path in initial_changed:
            file_record = db.get_file_by_path(file_path)
            db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Verify no changes
        no_changes = discovery.detect_changed_files()
        assert len(no_changes) == 0
        
        # Modify a dependency file
        utils_file = Path(utils_xslt_path)
        original_content = utils_file.read_text()
        modified_content = original_content + "\n<!-- Incremental change -->"
        utils_file.write_text(modified_content)
        
        # Re-discover and check changes
        discovery.discover_transformation_ecosystem(main_xslt_path)
        discovery.store_discovered_files()
        incremental_changed = discovery.detect_changed_files()
        
        # Only the modified file should need reanalysis
        assert len(incremental_changed) == 1
        assert str(utils_file.resolve()) in incremental_changed
        
        # Verify other files are still marked as completed
        main_file_record = db.get_file_by_path(str(Path(main_xslt_path).resolve()))
        assert main_file_record['analysis_status'] == 'completed'
        
        # Restore original content
        utils_file.write_text(original_content)
    
    def test_error_recovery_workflow(self, sample_files_structure, temp_dir):
        """Test workflow with error conditions and recovery."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        db_path = str(temp_dir / "error_recovery.db")
        db = DatabaseManager(db_path)
        discovery = FileDiscoveryEngine(db)
        
        # Initial discovery
        discovery.discover_transformation_ecosystem(main_xslt_path)
        discovery.store_discovered_files()
        changed_files = discovery.detect_changed_files()
        
        # Simulate analysis with some errors
        processed_count = 0
        for file_path in changed_files:
            file_record = db.get_file_by_path(file_path)
            
            if processed_count < 2:
                # First two files succeed
                db.update_file_analysis_status(file_record['id'], 'completed')
            else:
                # Remaining files have errors
                db.update_file_analysis_status(
                    file_record['id'], 
                    'error', 
                    'Simulated analysis error'
                )
            processed_count += 1
        
        # Check that error files are detected as needing reanalysis
        retry_files = discovery.detect_changed_files()
        
        # Only error files should need retry
        error_files = []
        for file_path in changed_files:
            file_record = db.get_file_by_path(file_path)
            if file_record['analysis_status'] == 'error':
                error_files.append(file_path)
        
        assert set(retry_files) == set(error_files)
        
        # Simulate retry (successful this time)
        for file_path in retry_files:
            file_record = db.get_file_by_path(file_path)
            db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Verify all files are now completed
        final_retry = discovery.detect_changed_files()
        assert len(final_retry) == 0
    
    def test_database_persistence_across_sessions(self, sample_files_structure, temp_dir):
        """Test that analysis persists across database sessions."""
        main_xslt_path = sample_files_structure['main_xslt']
        db_path = str(temp_dir / "persistence.db")
        
        # Session 1: Initial analysis
        db1 = DatabaseManager(db_path)
        discovery1 = FileDiscoveryEngine(db1)
        
        discovered1 = discovery1.discover_transformation_ecosystem(main_xslt_path)
        file_id_map1 = discovery1.store_discovered_files()
        
        # Mark some files as completed
        changed1 = discovery1.detect_changed_files()
        for i, file_path in enumerate(changed1):
            if i < len(changed1) // 2:  # Complete half the files
                file_record = db1.get_file_by_path(file_path)
                db1.update_file_analysis_status(file_record['id'], 'completed')
        
        session1_stats = db1.get_analysis_statistics()
        
        # Session 2: New database manager, same database
        db2 = DatabaseManager(db_path)
        discovery2 = FileDiscoveryEngine(db2)
        
        # Re-discover (should use existing data)
        discovered2 = discovery2.discover_transformation_ecosystem(main_xslt_path)
        file_id_map2 = discovery2.store_discovered_files()
        changed2 = discovery2.detect_changed_files()
        
        # Verify persistence
        assert len(discovered2) == len(discovered1)
        assert file_id_map2 == file_id_map1  # Same file IDs
        
        # Only incomplete files should need analysis
        assert len(changed2) < len(changed1)
        
        session2_stats = db2.get_analysis_statistics()
        assert session2_stats == session1_stats
    
    def test_concurrent_discovery_sessions(self, sample_files_structure, temp_dir):
        """Test concurrent file discovery sessions."""
        main_xslt_path = sample_files_structure['main_xslt']
        db_path = str(temp_dir / "concurrent.db")
        
        # Create two concurrent sessions
        db1 = DatabaseManager(db_path)
        db2 = DatabaseManager(db_path)
        
        discovery1 = FileDiscoveryEngine(db1)
        discovery2 = FileDiscoveryEngine(db2)
        
        # Both discover the same ecosystem
        discovered1 = discovery1.discover_transformation_ecosystem(main_xslt_path)
        discovered2 = discovery2.discover_transformation_ecosystem(main_xslt_path)
        
        # Both should discover the same files
        assert len(discovered1) == len(discovered2)
        assert set(discovered1.keys()) == set(discovered2.keys())
        
        # Store from both sessions
        file_id_map1 = discovery1.store_discovered_files()
        file_id_map2 = discovery2.store_discovered_files()
        
        # File IDs should be consistent
        assert file_id_map1 == file_id_map2
        
        # Both should see same changed files
        changed1 = discovery1.detect_changed_files()
        changed2 = discovery2.detect_changed_files()
        
        assert set(changed1) == set(changed2)
    
    def test_large_ecosystem_performance(self, temp_dir, large_xslt_content):
        """Test performance with larger file ecosystem."""
        # Create a larger ecosystem
        main_dir = temp_dir / "large_project"
        main_dir.mkdir()
        
        # Create main file
        main_file = main_dir / "main.xsl"
        main_file.write_text(large_xslt_content)
        
        # Create multiple dependency files
        deps_dir = main_dir / "dependencies"
        deps_dir.mkdir()
        
        dependency_files = []
        for i in range(10):  # 10 dependency files
            dep_content = f'''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="template_{i}">
        <element_{i}>Dependency {i}</element_{i}>
    </xsl:template>
</xsl:stylesheet>'''
            dep_file = deps_dir / f"dep_{i}.xsl"
            dep_file.write_text(dep_content)
            dependency_files.append(str(dep_file))
        
        # Measure performance
        import time
        start_time = time.time()
        
        db_path = str(temp_dir / "large_perf.db")
        db = DatabaseManager(db_path)
        discovery = FileDiscoveryEngine(db)
        
        # Full workflow
        discovered = discovery.discover_transformation_ecosystem(str(main_file))
        file_id_map = discovery.store_discovered_files()
        changed = discovery.detect_changed_files()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert len(discovered) >= 1  # At least the main file
        assert len(file_id_map) == len(discovered)
        assert len(changed) == len(discovered)
        
        # Verify database operations were efficient
        stats = db.get_analysis_statistics()
        assert stats['files']['xslt']['count'] >= 1