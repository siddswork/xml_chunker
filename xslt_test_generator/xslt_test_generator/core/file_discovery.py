"""File discovery and management for XSLT Test Generator v2.0."""

import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

from xslt_test_generator.config.logging_config import LoggerMixin
from xslt_test_generator.database.connection import DatabaseManager


@dataclass
class FileInfo:
    """Information about a discovered file."""
    path: str
    file_type: str  # 'xslt', 'xsd', 'xml'
    size: int
    modified_time: float
    content_hash: str
    imports: List[str]
    exists: bool = True


class FileDiscoveryEngine(LoggerMixin):
    """Discovers and manages files in XSLT transformation ecosystems."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize file discovery engine.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.discovered_files: Dict[str, FileInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Supported file extensions
        self.xslt_extensions = {'.xsl', '.xslt'}
        self.xsd_extensions = {'.xsd'}
        self.xml_extensions = {'.xml'}
        
        self.logger.info("File discovery engine initialized")
    
    def discover_transformation_ecosystem(self, entry_file_path: str) -> Dict[str, FileInfo]:
        """
        Discover complete transformation ecosystem starting from entry file.
        
        Args:
            entry_file_path: Path to the main XSLT or XSD file
            
        Returns:
            Dictionary mapping file paths to FileInfo objects
        """
        self.logger.info(f"Starting ecosystem discovery from: {entry_file_path}")
        
        entry_path = Path(entry_file_path).resolve()
        if not entry_path.exists():
            raise FileNotFoundError(f"Entry file not found: {entry_file_path}")
        
        # Clear previous discovery
        self.discovered_files.clear()
        self.dependency_graph.clear()
        
        # Start recursive discovery
        self._discover_file_recursive(str(entry_path))
        
        self.logger.info(f"Discovery completed. Found {len(self.discovered_files)} files")
        return self.discovered_files.copy()
    
    def _discover_file_recursive(self, file_path: str, visited: Set[str] = None) -> FileInfo:
        """
        Recursively discover a file and its dependencies.
        
        Args:
            file_path: Path to file to discover
            visited: Set of already visited paths (for cycle detection)
            
        Returns:
            FileInfo object for the discovered file
        """
        if visited is None:
            visited = set()
        
        # Resolve to absolute path
        abs_path = str(Path(file_path).resolve())
        
        # Check for circular dependencies
        if abs_path in visited:
            self.logger.warning(f"Circular dependency detected: {abs_path}")
            return self.discovered_files.get(abs_path)
        
        # Skip if already discovered
        if abs_path in self.discovered_files:
            return self.discovered_files[abs_path]
        
        visited.add(abs_path)
        
        try:
            # Gather file information
            file_info = self._analyze_file(abs_path)
            self.discovered_files[abs_path] = file_info
            
            # Initialize dependency tracking
            self.dependency_graph[abs_path] = set()
            
            # Discover dependencies
            for import_path in file_info.imports:
                resolved_import = self._resolve_import_path(import_path, abs_path)
                if resolved_import and Path(resolved_import).exists():
                    self.dependency_graph[abs_path].add(resolved_import)
                    # Recursively discover imported file
                    self._discover_file_recursive(resolved_import, visited.copy())
                else:
                    self.logger.warning(f"Could not resolve import: {import_path} from {abs_path}")
            
            self.logger.debug(f"Discovered file: {abs_path} with {len(file_info.imports)} imports")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Error discovering file {abs_path}: {e}")
            # Create error file info
            error_info = FileInfo(
                path=abs_path,
                file_type='unknown',
                size=0,
                modified_time=0,
                content_hash='',
                imports=[],
                exists=False
            )
            self.discovered_files[abs_path] = error_info
            return error_info
        finally:
            visited.discard(abs_path)
    
    def _analyze_file(self, file_path: str) -> FileInfo:
        """
        Analyze a single file and extract information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object with file details
        """
        path_obj = Path(file_path)
        
        # Get file stats
        stat = path_obj.stat()
        file_size = stat.st_size
        modified_time = stat.st_mtime
        
        # Determine file type
        file_type = self._determine_file_type(path_obj)
        
        # Read and hash content
        with open(file_path, 'rb') as f:
            content = f.read()
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Extract imports
        imports = self._extract_imports(file_path, file_type)
        
        return FileInfo(
            path=file_path,
            file_type=file_type,
            size=file_size,
            modified_time=modified_time,
            content_hash=content_hash,
            imports=imports
        )
    
    def _determine_file_type(self, path: Path) -> str:
        """
        Determine file type from extension and content.
        
        Args:
            path: Path object
            
        Returns:
            File type string
        """
        suffix = path.suffix.lower()
        
        if suffix in self.xslt_extensions:
            return 'xslt'
        elif suffix in self.xsd_extensions:
            return 'xsd'
        elif suffix in self.xml_extensions:
            # Could be sample XML or could be schema - check content
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1KB
                    if 'xmlns:xs=' in content or 'targetNamespace=' in content:
                        return 'xsd'
                    else:
                        return 'xml'
            except:
                return 'xml'
        
        return 'unknown'
    
    def _extract_imports(self, file_path: str, file_type: str) -> List[str]:
        """
        Extract import/include statements from file.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('xslt', 'xsd', 'xml')
            
        Returns:
            List of imported file paths
        """
        imports = []
        
        try:
            if file_type == 'xslt':
                imports = self._extract_xslt_imports(file_path)
            elif file_type == 'xsd':
                imports = self._extract_xsd_imports(file_path)
            # XML files typically don't have imports, but could have schema references
                
        except Exception as e:
            self.logger.warning(f"Error extracting imports from {file_path}: {e}")
        
        return imports
    
    def _extract_xslt_imports(self, file_path: str) -> List[str]:
        """
        Extract imports and includes from XSLT file.
        
        Args:
            file_path: Path to XSLT file
            
        Returns:
            List of imported file paths
        """
        imports = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find xsl:import and xsl:include elements
            namespaces = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
            
            for import_elem in root.findall('.//xsl:import', namespaces):
                href = import_elem.get('href')
                if href:
                    imports.append(href)
            
            for include_elem in root.findall('.//xsl:include', namespaces):
                href = include_elem.get('href')
                if href:
                    imports.append(href)
                    
        except ET.ParseError as e:
            self.logger.warning(f"XML parsing error in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing XSLT {file_path}: {e}")
        
        return imports
    
    def _extract_xsd_imports(self, file_path: str) -> List[str]:
        """
        Extract imports and includes from XSD file.
        
        Args:
            file_path: Path to XSD file
            
        Returns:
            List of imported file paths
        """
        imports = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find xs:import and xs:include elements
            namespaces = {'xs': 'http://www.w3.org/2001/XMLSchema'}
            
            for import_elem in root.findall('.//xs:import', namespaces):
                schema_location = import_elem.get('schemaLocation')
                if schema_location:
                    imports.append(schema_location)
            
            for include_elem in root.findall('.//xs:include', namespaces):
                schema_location = include_elem.get('schemaLocation')
                if schema_location:
                    imports.append(schema_location)
                    
        except ET.ParseError as e:
            self.logger.warning(f"XML parsing error in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing XSD {file_path}: {e}")
        
        return imports
    
    def _resolve_import_path(self, import_path: str, source_file: str) -> Optional[str]:
        """
        Resolve relative import path to absolute path.
        
        Args:
            import_path: Import path from file
            source_file: Path to file containing the import
            
        Returns:
            Resolved absolute path or None if cannot resolve
        """
        try:
            # Handle absolute paths
            if Path(import_path).is_absolute():
                return str(Path(import_path).resolve())
            
            # Handle relative paths
            source_dir = Path(source_file).parent
            resolved_path = source_dir / import_path
            
            if resolved_path.exists():
                return str(resolved_path.resolve())
            
            # Try some common patterns
            common_locations = [
                source_dir / 'common' / import_path,
                source_dir / 'include' / import_path,
                source_dir / 'imports' / import_path,
                source_dir.parent / import_path,
                source_dir.parent / 'common' / import_path
            ]
            
            for location in common_locations:
                if location.exists():
                    return str(location.resolve())
            
            self.logger.debug(f"Could not resolve import path: {import_path}")
            return None
            
        except Exception as e:
            self.logger.warning(f"Error resolving import path {import_path}: {e}")
            return None
    
    def store_discovered_files(self) -> Dict[str, int]:
        """
        Store discovered files in database.
        
        Returns:
            Dictionary mapping file paths to database IDs
        """
        self.logger.info("Storing discovered files in database")
        
        file_id_map = {}
        
        for file_path, file_info in self.discovered_files.items():
            try:
                # Check if file already exists in database
                existing_file = self.db.get_file_by_path(file_path)
                
                if existing_file:
                    # Check if file has changed
                    if existing_file['content_hash'] != file_info.content_hash:
                        self.logger.info(f"File changed, updating: {file_path}")
                        # Update existing record
                        self.db.execute_update("""
                            UPDATE transformation_files 
                            SET content_hash = ?, file_size = ?, last_modified = ?, 
                                imports = ?, analysis_status = 'pending', updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            file_info.content_hash, file_info.size, 
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info.modified_time)),
                            str(file_info.imports), existing_file['id']
                        ))
                        file_id_map[file_path] = existing_file['id']
                    else:
                        # File unchanged
                        file_id_map[file_path] = existing_file['id']
                else:
                    # Insert new file
                    file_id = self.db.insert_file(
                        file_path=file_path,
                        file_type=file_info.file_type,
                        content_hash=file_info.content_hash,
                        file_size=file_info.size,
                        last_modified=time.strftime('%Y-%m-%d %H:%M:%S', 
                                                   time.localtime(file_info.modified_time)),
                        imports=file_info.imports
                    )
                    file_id_map[file_path] = file_id
                    self.logger.debug(f"Stored new file: {file_path} with ID {file_id}")
                    
            except Exception as e:
                self.logger.error(f"Error storing file {file_path}: {e}")
        
        # Store dependencies
        self._store_dependencies(file_id_map)
        
        self.logger.info(f"Stored {len(file_id_map)} files in database")
        return file_id_map
    
    def _store_dependencies(self, file_id_map: Dict[str, int]):
        """
        Store file dependencies in database.
        
        Args:
            file_id_map: Dictionary mapping file paths to database IDs
        """
        self.logger.info("Storing file dependencies")
        
        for parent_path, dependencies in self.dependency_graph.items():
            parent_id = file_id_map.get(parent_path)
            if not parent_id:
                continue
            
            for dep_path in dependencies:
                child_id = file_id_map.get(dep_path)
                if not child_id:
                    continue
                
                try:
                    # Determine import type based on file types
                    parent_type = self.discovered_files[parent_path].file_type
                    child_type = self.discovered_files[dep_path].file_type
                    
                    if parent_type == 'xslt' and child_type == 'xslt':
                        import_type = 'xsl:import'  # Could also be xsl:include, would need to parse
                    elif parent_type == 'xsd' and child_type == 'xsd':
                        import_type = 'xs:import'   # Could also be xs:include
                    else:
                        import_type = 'unknown'
                    
                    # Check if dependency already exists
                    existing = self.db.execute_query("""
                        SELECT id FROM file_dependencies 
                        WHERE parent_file_id = ? AND child_file_id = ? AND import_type = ?
                    """, (parent_id, child_id, import_type))
                    
                    if not existing:
                        self.db.insert_file_dependency(
                            parent_file_id=parent_id,
                            child_file_id=child_id,
                            import_type=import_type,
                            resolved_path=dep_path
                        )
                        
                except Exception as e:
                    self.logger.error(f"Error storing dependency {parent_path} -> {dep_path}: {e}")
    
    def get_dependency_order(self) -> List[str]:
        """
        Get files in dependency order (dependencies first).
        
        Returns:
            List of file paths in processing order
        """
        # Topological sort of dependency graph
        # dependency_graph maps parent -> set of dependencies
        # We need to process dependencies before parents
        
        in_degree = {file_path: 0 for file_path in self.discovered_files}
        
        # Calculate in-degrees: count how many files depend on each file
        for parent_file, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[parent_file] += 1
        
        # Start with files that have no incoming dependencies
        queue = [path for path, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Process files that depend on current file
            for parent_file, dependencies in self.dependency_graph.items():
                if current in dependencies:
                    in_degree[parent_file] -= 1
                    if in_degree[parent_file] == 0:
                        queue.append(parent_file)
        
        # Check for circular dependencies
        if len(result) != len(self.discovered_files):
            remaining = set(self.discovered_files.keys()) - set(result)
            self.logger.warning(f"Circular dependencies detected in files: {remaining}")
            result.extend(remaining)  # Add remaining files anyway
        
        return result
    
    def detect_changed_files(self) -> List[str]:
        """
        Detect files that have changed since last analysis.
        
        Returns:
            List of file paths that have changed
        """
        changed_files = []
        
        for file_path, file_info in self.discovered_files.items():
            existing_file = self.db.get_file_by_path(file_path)
            
            if not existing_file:
                changed_files.append(file_path)
            elif existing_file['content_hash'] != file_info.content_hash:
                changed_files.append(file_path)
            elif existing_file['analysis_status'] in ['pending', 'error']:
                changed_files.append(file_path)
        
        self.logger.info(f"Detected {len(changed_files)} changed files")
        return changed_files