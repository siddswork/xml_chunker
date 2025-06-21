"""Unit tests for FileDiscoveryEngine class."""

import pytest
from pathlib import Path
import hashlib
import time
from unittest.mock import patch, MagicMock

from xslt_test_generator.core.file_discovery import FileDiscoveryEngine, FileInfo


class TestFileDiscoveryEngine:
    """Test cases for FileDiscoveryEngine."""
    
    def test_initialization(self, db_manager):
        """Test file discovery engine initialization."""
        discovery = FileDiscoveryEngine(db_manager)
        
        assert discovery.db == db_manager
        assert discovery.discovered_files == {}
        assert discovery.dependency_graph == {}
        assert discovery.xslt_extensions == {'.xsl', '.xslt'}
        assert discovery.xsd_extensions == {'.xsd'}
        assert discovery.xml_extensions == {'.xml'}
    
    def test_determine_file_type(self, file_discovery, temp_dir):
        """Test file type determination."""
        # Test XSLT files
        xslt_file = temp_dir / "test.xsl"
        xslt_file.write_text("<?xml version='1.0'?><xsl:stylesheet/>")
        assert file_discovery._determine_file_type(xslt_file) == 'xslt'
        
        xslt_file2 = temp_dir / "test.xslt"
        xslt_file2.write_text("<?xml version='1.0'?><xsl:stylesheet/>")
        assert file_discovery._determine_file_type(xslt_file2) == 'xslt'
        
        # Test XSD files
        xsd_file = temp_dir / "test.xsd"
        xsd_file.write_text("<?xml version='1.0'?><xs:schema/>")
        assert file_discovery._determine_file_type(xsd_file) == 'xsd'
        
        # Test XML with schema indicators
        xml_schema = temp_dir / "schema.xml"
        xml_schema.write_text("<?xml version='1.0'?><xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema' targetNamespace='test'/>")
        assert file_discovery._determine_file_type(xml_schema) == 'xsd'
        
        # Test regular XML
        xml_file = temp_dir / "data.xml"
        xml_file.write_text("<?xml version='1.0'?><data><item>test</item></data>")
        assert file_discovery._determine_file_type(xml_file) == 'xml'
        
        # Test unknown file type
        txt_file = temp_dir / "readme.txt"
        txt_file.write_text("This is a text file")
        assert file_discovery._determine_file_type(txt_file) == 'unknown'
    
    def test_extract_xslt_imports(self, file_discovery, temp_dir, sample_xslt_content):
        """Test XSLT import extraction."""
        xslt_file = temp_dir / "main.xsl"
        xslt_file.write_text(sample_xslt_content)
        
        imports = file_discovery._extract_xslt_imports(str(xslt_file))
        
        expected_imports = ["common/utils.xsl", "templates/passenger.xsl"]
        assert imports == expected_imports
    
    def test_extract_xsd_imports(self, file_discovery, temp_dir, sample_xsd_content):
        """Test XSD import extraction."""
        xsd_file = temp_dir / "booking.xsd"
        xsd_file.write_text(sample_xsd_content)
        
        imports = file_discovery._extract_xsd_imports(str(xsd_file))
        
        expected_imports = ["common/CommonTypes.xsd"]
        assert imports == expected_imports
    
    def test_extract_imports_with_corrupted_xml(self, file_discovery, temp_dir, corrupted_xslt_content):
        """Test import extraction with corrupted XML."""
        corrupted_file = temp_dir / "corrupted.xsl"
        corrupted_file.write_text(corrupted_xslt_content)
        
        # Should handle corruption gracefully and return empty list
        imports = file_discovery._extract_xslt_imports(str(corrupted_file))
        assert imports == []
    
    def test_resolve_import_path(self, file_discovery, temp_dir):
        """Test import path resolution."""
        # Create directory structure
        main_dir = temp_dir / "project"
        common_dir = main_dir / "common"
        main_dir.mkdir()
        common_dir.mkdir()
        
        # Create files
        main_file = main_dir / "main.xsl"
        utils_file = common_dir / "utils.xsl"
        main_file.write_text("test")
        utils_file.write_text("test")
        
        # Test relative path resolution
        resolved = file_discovery._resolve_import_path("common/utils.xsl", str(main_file))
        assert resolved == str(utils_file.resolve())
        
        # Test absolute path (should return as-is if exists)
        absolute_path = str(utils_file.resolve())
        resolved_abs = file_discovery._resolve_import_path(absolute_path, str(main_file))
        assert resolved_abs == absolute_path
        
        # Test non-existent file
        resolved_none = file_discovery._resolve_import_path("nonexistent/file.xsl", str(main_file))
        assert resolved_none is None
    
    def test_analyze_file(self, file_discovery, temp_dir, sample_xslt_content):
        """Test single file analysis."""
        xslt_file = temp_dir / "test.xsl"
        xslt_file.write_text(sample_xslt_content)
        
        file_info = file_discovery._analyze_file(str(xslt_file))
        
        assert isinstance(file_info, FileInfo)
        assert file_info.path == str(xslt_file)
        assert file_info.file_type == 'xslt'
        assert file_info.size == len(sample_xslt_content.encode('utf-8'))
        assert file_info.content_hash == hashlib.sha256(sample_xslt_content.encode('utf-8')).hexdigest()
        assert file_info.imports == ["common/utils.xsl", "templates/passenger.xsl"]
        assert file_info.exists is True
    
    def test_discover_single_file(self, file_discovery, temp_dir, sample_xslt_content):
        """Test discovery of a single file with no dependencies."""
        # Create a simple XSLT with no imports
        simple_xslt = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output>Simple transform</output>
    </xsl:template>
</xsl:stylesheet>'''
        
        xslt_file = temp_dir / "simple.xsl"
        xslt_file.write_text(simple_xslt)
        
        discovered = file_discovery.discover_transformation_ecosystem(str(xslt_file))
        
        assert len(discovered) == 1
        assert str(xslt_file.resolve()) in discovered
        
        file_info = discovered[str(xslt_file.resolve())]
        assert file_info.file_type == 'xslt'
        assert file_info.imports == []
    
    def test_discover_multi_file_ecosystem(self, file_discovery, sample_files_structure):
        """Test discovery of multi-file ecosystem."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        discovered = file_discovery.discover_transformation_ecosystem(main_xslt_path)
        
        # Should discover main file + its dependencies
        assert len(discovered) >= 3  # main.xsl + utils.xsl + passenger.xsl
        
        # Verify main file is included
        main_path = str(Path(main_xslt_path).resolve())
        assert main_path in discovered
        
        # Verify dependencies were found
        discovered_paths = set(discovered.keys())
        utils_path = str(Path(sample_files_structure['utils_xslt']).resolve())
        passenger_path = str(Path(sample_files_structure['passenger_xslt']).resolve())
        
        assert utils_path in discovered_paths
        assert passenger_path in discovered_paths
        
        # Verify dependency graph was built
        main_deps = file_discovery.dependency_graph.get(main_path, set())
        assert utils_path in main_deps
        assert passenger_path in main_deps
    
    def test_circular_dependency_detection(self, file_discovery, temp_dir):
        """Test detection and handling of circular dependencies."""
        # Create files with circular dependencies
        file_a = temp_dir / "a.xsl"
        file_b = temp_dir / "b.xsl"
        
        content_a = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="b.xsl"/>
    <xsl:template match="/">A</xsl:template>
</xsl:stylesheet>'''
        
        content_b = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="a.xsl"/>
    <xsl:template match="/">B</xsl:template>
</xsl:stylesheet>'''
        
        file_a.write_text(content_a)
        file_b.write_text(content_b)
        
        # Should handle circular dependency gracefully
        discovered = file_discovery.discover_transformation_ecosystem(str(file_a))
        
        # Both files should be discovered despite circular dependency
        assert len(discovered) == 2
        file_a_path = str(file_a.resolve())
        file_b_path = str(file_b.resolve())
        assert file_a_path in discovered
        assert file_b_path in discovered
    
    def test_missing_dependency_handling(self, file_discovery, temp_dir):
        """Test handling of missing dependency files."""
        xslt_with_missing_import = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="nonexistent.xsl"/>
    <xsl:template match="/">Test</xsl:template>
</xsl:stylesheet>'''
        
        main_file = temp_dir / "main.xsl"
        main_file.write_text(xslt_with_missing_import)
        
        # Should discover main file but warn about missing dependency
        discovered = file_discovery.discover_transformation_ecosystem(str(main_file))
        
        assert len(discovered) == 1
        main_path = str(main_file.resolve())
        assert main_path in discovered
        
        # Missing file should not be in discovered files
        missing_path = str((temp_dir / "nonexistent.xsl").resolve())
        assert missing_path not in discovered
    
    def test_store_discovered_files(self, file_discovery, sample_files_structure):
        """Test storing discovered files in database."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        # Discover files
        discovered = file_discovery.discover_transformation_ecosystem(main_xslt_path)
        
        # Store in database
        file_id_map = file_discovery.store_discovered_files()
        
        # Verify all discovered files were stored
        assert len(file_id_map) == len(discovered)
        
        # Verify files can be retrieved from database
        for file_path in discovered.keys():
            file_record = file_discovery.db.get_file_by_path(file_path)
            assert file_record is not None
            assert file_record['file_path'] == file_path
            assert file_record['analysis_status'] == 'pending'
    
    def test_detect_changed_files(self, file_discovery, sample_files_structure):
        """Test detection of changed files."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        # Initial discovery and storage
        file_discovery.discover_transformation_ecosystem(main_xslt_path)
        file_discovery.store_discovered_files()
        
        # Initially, all files should be detected as changed (new)
        changed = file_discovery.detect_changed_files()
        assert len(changed) > 0
        
        # Mark files as completed
        for file_path in changed:
            file_record = file_discovery.db.get_file_by_path(file_path)
            file_discovery.db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Now no files should be detected as changed
        changed_after = file_discovery.detect_changed_files()
        assert len(changed_after) == 0
        
        # Modify a file
        main_file = Path(main_xslt_path)
        original_content = main_file.read_text()
        modified_content = original_content + "\n<!-- Modified -->"
        main_file.write_text(modified_content)
        
        # Rediscover (to update internal state)
        file_discovery.discover_transformation_ecosystem(main_xslt_path)
        
        # Should detect the modified file
        changed_final = file_discovery.detect_changed_files()
        assert len(changed_final) >= 1
        assert str(main_file.resolve()) in changed_final
        
        # Restore original content
        main_file.write_text(original_content)
    
    def test_get_dependency_order(self, file_discovery, sample_files_structure):
        """Test dependency order calculation."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        # Discover files to build dependency graph
        file_discovery.discover_transformation_ecosystem(main_xslt_path)
        
        # Get processing order
        order = file_discovery.get_dependency_order()
        
        # Dependencies should come before files that depend on them
        main_path = str(Path(main_xslt_path).resolve())
        utils_path = str(Path(sample_files_structure['utils_xslt']).resolve())
        passenger_path = str(Path(sample_files_structure['passenger_xslt']).resolve())
        
        main_index = order.index(main_path)
        utils_index = order.index(utils_path)
        passenger_index = order.index(passenger_path)
        
        # Utils and passenger should come before main (since main depends on them)
        assert utils_index < main_index
        assert passenger_index < main_index
    
    def test_performance_with_large_file(self, file_discovery, temp_dir, large_xslt_content):
        """Test performance with large XSLT file."""
        large_file = temp_dir / "large.xsl"
        large_file.write_text(large_xslt_content)
        
        start_time = time.time()
        
        # Discover large file
        discovered = file_discovery.discover_transformation_ecosystem(str(large_file))
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds max
        
        # Should successfully discover the file
        assert len(discovered) == 1
        
        large_path = str(large_file.resolve())
        assert large_path in discovered
        
        # Verify file info is correct
        file_info = discovered[large_path]
        assert file_info.file_type == 'xslt'
        assert file_info.size > 50000  # Should be a substantial file
    
    def test_error_handling_nonexistent_entry_file(self, file_discovery, temp_dir):
        """Test error handling for non-existent entry file."""
        nonexistent_path = str(temp_dir / "does_not_exist.xsl")
        
        with pytest.raises(FileNotFoundError):
            file_discovery.discover_transformation_ecosystem(nonexistent_path)
    
    def test_incremental_analysis_workflow(self, file_discovery, sample_files_structure):
        """Test complete incremental analysis workflow."""
        main_xslt_path = sample_files_structure['main_xslt']
        
        # First analysis
        discovered1 = file_discovery.discover_transformation_ecosystem(main_xslt_path)
        file_id_map1 = file_discovery.store_discovered_files()
        changed1 = file_discovery.detect_changed_files()
        
        # All files should be new
        assert len(changed1) == len(discovered1)
        
        # Mark as completed
        for file_path in changed1:
            file_record = file_discovery.db.get_file_by_path(file_path)
            file_discovery.db.update_file_analysis_status(file_record['id'], 'completed')
        
        # Second analysis (no changes)
        discovered2 = file_discovery.discover_transformation_ecosystem(main_xslt_path)
        file_id_map2 = file_discovery.store_discovered_files()
        changed2 = file_discovery.detect_changed_files()
        
        # No files should need reanalysis
        assert len(changed2) == 0
        assert file_id_map1 == file_id_map2  # Same file IDs
        
        # Modify a file
        utils_file = Path(sample_files_structure['utils_xslt'])
        original_content = utils_file.read_text()
        utils_file.write_text(original_content + "\n<!-- Modified -->")
        
        # Third analysis (with changes)
        discovered3 = file_discovery.discover_transformation_ecosystem(main_xslt_path)
        file_id_map3 = file_discovery.store_discovered_files()
        changed3 = file_discovery.detect_changed_files()
        
        # Only modified file should need reanalysis
        assert len(changed3) == 1
        assert str(utils_file.resolve()) in changed3
        
        # Restore original content
        utils_file.write_text(original_content)