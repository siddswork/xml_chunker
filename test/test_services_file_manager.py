"""
Unit tests for services.file_manager module.

Tests all FileManager functionality including file operations, temporary directory
management, XSD dependency resolution, and error handling scenarios.
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open
from services.file_manager import FileManager
from config import get_config


class TestFileManagerInit:
    """Test FileManager initialization."""
    
    def test_init_with_config(self):
        """Test FileManager initialization with config instance."""
        config = get_config()
        file_manager = FileManager(config)
        assert file_manager.config == config
    
    def test_init_without_config(self):
        """Test FileManager initialization without config (uses default)."""
        file_manager = FileManager()
        assert file_manager.config is not None


class TestFileManagerTempOperations:
    """Test temporary file and directory operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
    
    def test_create_temp_file_default(self):
        """Test creating temporary file with default parameters."""
        content = "<?xml version='1.0'?><test>content</test>"
        temp_path = self.file_manager.create_temp_file(content)
        
        try:
            assert os.path.exists(temp_path)
            assert temp_path.endswith('.xml')
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
        finally:
            self.file_manager.cleanup_temp_file(temp_path)
    
    def test_create_temp_file_custom_suffix(self):
        """Test creating temporary file with custom suffix."""
        content = "test content"
        temp_path = self.file_manager.create_temp_file(content, suffix='.xsd')
        
        try:
            assert os.path.exists(temp_path)
            assert temp_path.endswith('.xsd')
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
        finally:
            self.file_manager.cleanup_temp_file(temp_path)
    
    def test_create_temp_file_custom_encoding(self):
        """Test creating temporary file with custom encoding."""
        content = "test content with special chars: áéíóú"
        temp_path = self.file_manager.create_temp_file(content, encoding='utf-8')
        
        try:
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
        finally:
            self.file_manager.cleanup_temp_file(temp_path)
    
    def test_create_temp_directory(self):
        """Test creating temporary directory."""
        temp_dir = self.file_manager.create_temp_directory()
        
        try:
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)
        finally:
            self.file_manager.cleanup_temp_directory(temp_dir)
    
    def test_cleanup_temp_file_existing(self):
        """Test cleaning up existing temporary file."""
        content = "test content"
        temp_path = self.file_manager.create_temp_file(content)
        assert os.path.exists(temp_path)
        
        self.file_manager.cleanup_temp_file(temp_path)
        assert not os.path.exists(temp_path)
    
    def test_cleanup_temp_file_nonexistent(self):
        """Test cleaning up non-existent file (should not raise error)."""
        fake_path = "/nonexistent/file.xml"
        # Should not raise exception
        self.file_manager.cleanup_temp_file(fake_path)
    
    def test_cleanup_temp_directory_existing(self):
        """Test cleaning up existing temporary directory."""
        temp_dir = self.file_manager.create_temp_directory()
        
        # Create some files in the directory
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        assert os.path.exists(temp_dir)
        assert os.path.exists(test_file)
        
        self.file_manager.cleanup_temp_directory(temp_dir)
        assert not os.path.exists(temp_dir)
    
    def test_cleanup_temp_directory_nonexistent(self):
        """Test cleaning up non-existent directory (should not raise error)."""
        fake_dir = "/nonexistent/directory"
        # Should not raise exception
        self.file_manager.cleanup_temp_directory(fake_dir)


class TestFileManagerXSDDependencies:
    """Test XSD dependency resolution functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        self.test_dir = tempfile.mkdtemp()
        self.resource_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.resource_dir, ignore_errors=True)
    
    def test_setup_temp_directory_with_dependencies_success(self):
        """Test successful XSD dependency setup."""
        file_manager = FileManager()
        
        # Create source XSD files in resource directory (simulating original location)
        source_files = ['IATA_OrderViewRS.xsd', 'IATA_OffersAndOrdersCommonTypes.xsd']
        for filename in source_files:
            source_path = os.path.join(self.resource_dir, filename)
            with open(source_path, 'w') as f:
                f.write(f'<schema>{filename}</schema>')
        
        # Create target XSD file in resource directory too (simulating user upload)
        target_file = 'TestSchema.xsd'
        source_target_path = os.path.join(self.resource_dir, target_file)
        with open(source_target_path, 'w') as f:
            f.write('<schema>TestSchema</schema>')
        
        # Create target XSD file in temp directory (simulating temp processing)
        temp_target_path = os.path.join(self.test_dir, target_file)
        with open(temp_target_path, 'w') as f:
            f.write('<schema>TestSchema</schema>')
        
        # Test dependency setup with source path
        file_manager.setup_temp_directory_with_dependencies(temp_target_path, target_file, source_target_path)
        
        # Verify dependencies were copied (excluding the target file itself)
        for filename in source_files:
            if filename != target_file:
                dest_path = os.path.join(self.test_dir, filename)
                assert os.path.exists(dest_path)
                
                with open(dest_path, 'r') as f:
                    content = f.read()
                    assert f'<schema>{filename}</schema>' in content
    
    def test_setup_temp_directory_missing_source_dir(self):
        """Test dependency setup with missing source directory."""
        file_manager = FileManager()
        
        target_path = os.path.join(self.test_dir, 'test.xsd')
        with open(target_path, 'w') as f:
            f.write('<schema>test</schema>')
        
        # Should not raise exception, should handle gracefully
        file_manager.setup_temp_directory_with_dependencies(target_path, 'test.xsd', '/nonexistent/directory/test.xsd')
    
    def test_setup_temp_directory_missing_temp_dir(self):
        """Test dependency setup with missing temp directory."""
        file_manager = FileManager()
        
        # Use non-existent temp directory
        fake_path = '/nonexistent/directory/test.xsd'
        
        # Should not raise exception, should handle gracefully
        file_manager.setup_temp_directory_with_dependencies(fake_path, 'test.xsd')
    
    def test_setup_temp_directory_file_copy_error(self):
        """Test dependency setup with file copy error."""
        file_manager = FileManager()
        
        # Create a directory instead of file to cause copy error
        problem_dir = os.path.join(self.resource_dir, 'NotAFile.xsd')
        os.makedirs(problem_dir)
        
        # Create source XSD file  
        source_target_path = os.path.join(self.resource_dir, 'test.xsd')
        with open(source_target_path, 'w') as f:
            f.write('<schema>test</schema>')
        
        target_path = os.path.join(self.test_dir, 'test.xsd')
        with open(target_path, 'w') as f:
            f.write('<schema>test</schema>')
        
        # Should handle copy error gracefully
        file_manager.setup_temp_directory_with_dependencies(target_path, 'test.xsd', source_target_path)


class TestFileManagerXSDWithDependencies:
    """Test write_temp_xsd_with_dependencies functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
    
    @patch.object(FileManager, 'setup_temp_directory_with_dependencies')
    @patch.object(FileManager, 'create_temp_directory')
    def test_write_temp_xsd_with_dependencies(self, mock_create_dir, mock_setup_deps):
        """Test writing XSD with dependencies."""
        # Mock temp directory creation
        test_dir = '/tmp/test_dir'
        mock_create_dir.return_value = test_dir
        
        xsd_content = '<?xml version="1.0"?><schema>test</schema>'
        xsd_filename = 'test.xsd'
        
        with patch('builtins.open', mock_open()) as mock_file:
            result_path, result_dir = self.file_manager.write_temp_xsd_with_dependencies(
                xsd_content, xsd_filename
            )
            
            # Verify results
            expected_path = os.path.join(test_dir, xsd_filename)
            assert result_path == expected_path
            assert result_dir == test_dir
            
            # Verify file operations
            mock_file.assert_called_once_with(expected_path, 'w', encoding='utf-8')
            mock_file().write.assert_called_once_with(xsd_content)
            
            # Verify dependency setup was called
            mock_setup_deps.assert_called_once_with(expected_path, xsd_filename, None)


class TestFileManagerErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
    
    @patch('tempfile.NamedTemporaryFile')
    def test_create_temp_file_permission_error(self, mock_temp_file):
        """Test create_temp_file with permission error."""
        mock_temp_file.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(PermissionError):
            self.file_manager.create_temp_file("content")
    
    @patch('tempfile.mkdtemp')
    def test_create_temp_directory_permission_error(self, mock_mkdtemp):
        """Test create_temp_directory with permission error."""
        mock_mkdtemp.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(PermissionError):
            self.file_manager.create_temp_directory()
    
    @patch('os.unlink')
    def test_cleanup_temp_file_permission_error(self, mock_unlink):
        """Test cleanup_temp_file with permission error (should handle gracefully)."""
        mock_unlink.side_effect = PermissionError("Permission denied")
        
        # Should not raise exception
        self.file_manager.cleanup_temp_file('/some/file.xml')
    
    @patch('shutil.rmtree')
    def test_cleanup_temp_directory_permission_error(self, mock_rmtree):
        """Test cleanup_temp_directory with permission error (should handle gracefully)."""
        mock_rmtree.side_effect = PermissionError("Permission denied")
        
        # Should not raise exception
        self.file_manager.cleanup_temp_directory('/some/directory')


class TestFileManagerIntegration:
    """Integration tests for FileManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
    
    def test_full_workflow_temp_file(self):
        """Test complete workflow: create -> use -> cleanup temp file."""
        content = "<?xml version='1.0'?><test><element>value</element></test>"
        
        # Create temp file
        temp_path = self.file_manager.create_temp_file(content, suffix='.xml')
        
        try:
            # Verify file exists and has correct content
            assert os.path.exists(temp_path)
            assert temp_path.endswith('.xml')
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
            
            # Modify file
            additional_content = "\n<!-- Added content -->"
            with open(temp_path, 'a', encoding='utf-8') as f:
                f.write(additional_content)
            
            # Verify modification
            with open(temp_path, 'r', encoding='utf-8') as f:
                assert f.read() == content + additional_content
        
        finally:
            # Cleanup
            self.file_manager.cleanup_temp_file(temp_path)
            assert not os.path.exists(temp_path)
    
    def test_full_workflow_temp_directory(self):
        """Test complete workflow: create -> use -> cleanup temp directory."""
        # Create temp directory
        temp_dir = self.file_manager.create_temp_directory()
        
        try:
            # Verify directory exists
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)
            
            # Create files in directory
            test_files = ['file1.xml', 'file2.xsd', 'subdir/file3.txt']
            for file_path in test_files:
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w') as f:
                    f.write(f"Content of {file_path}")
                
                assert os.path.exists(full_path)
        
        finally:
            # Cleanup
            self.file_manager.cleanup_temp_directory(temp_dir)
            assert not os.path.exists(temp_dir)