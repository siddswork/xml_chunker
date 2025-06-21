"""Database connection and management for XSLT Test Generator v2.0."""

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
from xslt_test_generator.config.logging_config import LoggerMixin


class DatabaseManager(LoggerMixin):
    """Manages database connections and operations for XSLT analysis."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = os.path.join(os.getcwd(), "xslt_analysis.db")
        
        self.db_path = Path(db_path)
        self.logger.info(f"Initializing database manager with path: {self.db_path}")
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema if needed
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema if it doesn't exist."""
        if not self.db_path.exists():
            self.logger.info("Creating new database with schema")
            self._create_schema()
        else:
            self.logger.info("Using existing database")
            self._verify_schema()
    
    def _create_schema(self):
        """Create database schema from SQL file."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            # Use executescript for multiple statements
            try:
                conn.executescript(schema_sql)
                conn.commit()
            except sqlite3.Error as e:
                self.logger.error(f"Error executing schema: {e}")
                raise
        
        self.logger.info("Database schema created successfully")
    
    def _verify_schema(self):
        """Verify that existing database has correct schema."""
        with self.get_connection() as conn:
            # Check if key tables exist
            required_tables = [
                'transformation_files', 'file_dependencies', 'xslt_templates',
                'xslt_variables', 'template_calls', 'xsd_elements', 'xsd_types',
                'execution_paths', 'test_specifications'
            ]
            
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(required_tables) - existing_tables
            if missing_tables:
                self.logger.warning(f"Missing tables in database: {missing_tables}")
                # Could implement migration logic here
            else:
                self.logger.info("Database schema verification passed")
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection with proper error handling.
        
        Yields:
            sqlite3.Connection: Database connection with JSON support
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,  # 30 second timeout
                check_same_thread=False
            )
            
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Set row factory for easier data access
            conn.row_factory = sqlite3.Row
            
            yield conn
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def insert_file(self, file_path: str, file_type: str, content_hash: str, 
                   file_size: int, last_modified: str, imports: List[str] = None) -> int:
        """
        Insert a new transformation file record.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('xslt', 'xsd', 'xml')
            content_hash: Hash of file content
            file_size: Size of file in bytes
            last_modified: Last modification timestamp
            imports: List of imported file paths
            
        Returns:
            ID of inserted record
        """
        query = """
            INSERT INTO transformation_files 
            (file_path, file_type, content_hash, file_size, last_modified, imports)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        imports_json = json.dumps(imports or [])
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                file_path, file_type, content_hash, file_size, last_modified, imports_json
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_file_by_path(self, file_path: str) -> Optional[sqlite3.Row]:
        """
        Get file record by path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File record or None if not found
        """
        query = "SELECT * FROM transformation_files WHERE file_path = ?"
        results = self.execute_query(query, (file_path,))
        return results[0] if results else None
    
    def get_file_by_id(self, file_id: int) -> Optional[sqlite3.Row]:
        """
        Get file record by ID.
        
        Args:
            file_id: ID of the file
            
        Returns:
            File record or None if not found
        """
        query = "SELECT * FROM transformation_files WHERE id = ?"
        results = self.execute_query(query, (file_id,))
        return results[0] if results else None
    
    def get_variables_by_file(self, file_id: int) -> List[sqlite3.Row]:
        """
        Get all variables for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of variable records
        """
        query = "SELECT * FROM xslt_variables WHERE file_id = ?"
        return self.execute_query(query, (file_id,))
    
    def get_execution_paths_by_file(self, file_id: int) -> List[sqlite3.Row]:
        """
        Get all execution paths for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of execution path records
        """
        query = "SELECT * FROM execution_paths WHERE entry_template_id IN (SELECT id FROM xslt_templates WHERE file_id = ?)"
        return self.execute_query(query, (file_id,))
    
    def update_file_analysis_status(self, file_id: int, status: str, error_message: str = None):
        """
        Update the analysis status of a file.
        
        Args:
            file_id: ID of the file
            status: New status ('pending', 'analyzing', 'completed', 'error', 'skipped')
            error_message: Error message if status is 'error'
        """
        query = """
            UPDATE transformation_files 
            SET analysis_status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.execute_update(query, (status, error_message, file_id))
    
    def insert_file_dependency(self, parent_file_id: int, child_file_id: int, 
                              import_type: str, namespace: str = None, 
                              xpath_location: str = None, href_attribute: str = None,
                              resolved_path: str = None) -> int:
        """
        Insert a file dependency relationship.
        
        Args:
            parent_file_id: ID of parent file
            child_file_id: ID of child file
            import_type: Type of import ('xsl:import', 'xsl:include', etc.)
            namespace: Namespace if applicable
            xpath_location: XPath location of import in parent
            href_attribute: Original href attribute value
            resolved_path: Resolved file path
            
        Returns:
            ID of inserted record
        """
        query = """
            INSERT INTO file_dependencies 
            (parent_file_id, child_file_id, import_type, namespace, 
             xpath_location, href_attribute, resolved_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                parent_file_id, child_file_id, import_type, namespace,
                xpath_location, href_attribute, resolved_path
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_file_dependencies(self, file_id: int) -> List[sqlite3.Row]:
        """
        Get all dependencies for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of dependency records
        """
        query = """
            SELECT d.*, cf.file_path as child_path, cf.file_type as child_type
            FROM file_dependencies d
            JOIN transformation_files cf ON d.child_file_id = cf.id
            WHERE d.parent_file_id = ?
        """
        return self.execute_query(query, (file_id,))
    
    def insert_xslt_template(self, file_id: int, template_data: Dict[str, Any]) -> int:
        """
        Insert an XSLT template record.
        
        Args:
            file_id: ID of the file containing the template
            template_data: Dictionary with template information
            
        Returns:
            ID of inserted record
        """
        query = """
            INSERT INTO xslt_templates 
            (file_id, name, match_pattern, mode, priority, line_start, line_end,
             template_content, calls_templates, called_by_templates, uses_variables,
             defines_variables, xpath_expressions, conditional_logic, output_elements,
             template_hash, complexity_score, is_recursive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Convert lists/dicts to JSON
        json_fields = [
            'calls_templates', 'called_by_templates', 'uses_variables',
            'defines_variables', 'xpath_expressions', 'conditional_logic', 'output_elements'
        ]
        
        params = [file_id]
        for field in ['name', 'match_pattern', 'mode', 'priority', 'line_start', 'line_end',
                     'template_content']:
            params.append(template_data.get(field))
        
        for field in json_fields:
            params.append(json.dumps(template_data.get(field, [])))
        
        params.extend([
            template_data.get('template_hash'),
            template_data.get('complexity_score', 0),
            template_data.get('is_recursive', False)
        ])
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def get_templates_by_file(self, file_id: int) -> List[sqlite3.Row]:
        """
        Get all templates for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of template records
        """
        query = "SELECT * FROM xslt_templates WHERE file_id = ?"
        return self.execute_query(query, (file_id,))
    
    def get_all_files(self) -> List[sqlite3.Row]:
        """Get all transformation files."""
        return self.execute_query("SELECT * FROM transformation_files ORDER BY file_path")
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        Get analysis statistics.
        
        Returns:
            Dictionary with analysis statistics
        """
        stats = {}
        
        # File statistics
        file_stats = self.execute_query("""
            SELECT 
                file_type,
                COUNT(*) as count,
                SUM(file_size) as total_size
            FROM transformation_files 
            GROUP BY file_type
        """)
        
        stats['files'] = {row['file_type']: {
            'count': row['count'], 
            'total_size': row['total_size']
        } for row in file_stats}
        
        # Template statistics
        template_stats = self.execute_query("""
            SELECT 
                COUNT(*) as total_templates,
                COUNT(CASE WHEN name IS NOT NULL THEN 1 END) as named_templates,
                COUNT(CASE WHEN match_pattern IS NOT NULL THEN 1 END) as match_templates,
                AVG(complexity_score) as avg_complexity
            FROM xslt_templates
        """)
        
        if template_stats:
            stats['templates'] = dict(template_stats[0])
        
        # Path statistics
        path_stats = self.execute_query("""
            SELECT 
                COUNT(*) as total_paths,
                AVG(path_complexity_score) as avg_path_complexity,
                COUNT(CASE WHEN has_recursion THEN 1 END) as recursive_paths
            FROM execution_paths
        """)
        
        if path_stats:
            stats['paths'] = dict(path_stats[0])
        
        # Test statistics
        test_stats = self.execute_query("""
            SELECT 
                COUNT(*) as total_tests,
                test_category,
                COUNT(*) as category_count
            FROM test_specifications
            GROUP BY test_category
        """)
        
        stats['tests'] = {
            'total': sum(row['category_count'] for row in test_stats),
            'by_category': {row['test_category']: row['category_count'] for row in test_stats}
        }
        
        return stats
    
    def insert_xslt_variable(self, file_id: int, variable_data: Dict[str, Any]) -> int:
        """Insert XSLT variable or parameter."""
        query = """
        INSERT INTO xslt_variables (
            file_id, name, scope, xpath_expression, line_number, 
            is_parameter, usage_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            file_id,
            variable_data['name'],
            variable_data.get('scope', 'template'),
            variable_data.get('select_expression'),
            variable_data.get('line_number', 0),
            variable_data.get('variable_type') == 'parameter',
            len(variable_data.get('used_by_templates', []))
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def insert_execution_path(self, file_id: int, path_data: Dict[str, Any]) -> int:
        """Insert execution path."""
        query = """
        INSERT INTO execution_paths (
            path_name, entry_template_id, path_hash, template_sequence,
            decision_points, path_complexity_score, covers_templates, 
            estimated_frequency, execution_depth, has_recursion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Get entry template ID (simplified - assume first template)
        entry_template_id = 1  # Default fallback
        if path_data.get('templates_involved'):
            templates = list(path_data['templates_involved'])
            if templates:
                with self.get_connection() as conn:
                    template_records = conn.execute(
                        "SELECT id FROM xslt_templates WHERE file_id = ? AND name = ?",
                        (file_id, templates[0])
                    ).fetchone()
                if template_records:
                    entry_template_id = template_records[0]
        
        # Generate a simple hash for the path
        import hashlib
        path_content = str(path_data.get('nodes', []))
        path_hash = hashlib.md5(path_content.encode()).hexdigest()[:16]
        
        values = (
            path_data.get('path_id', 'unknown'),
            entry_template_id,
            path_hash,
            json.dumps(path_data.get('nodes', [])),
            json.dumps(path_data.get('conditions', [])),
            path_data.get('complexity_score', 0),
            json.dumps(list(path_data.get('templates_involved', set()))),
            'unknown',
            len(path_data.get('nodes', [])),
            False  # has_recursion - would need more sophisticated detection
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def insert_semantic_pattern(self, file_id: int, pattern_data: Dict[str, Any]) -> int:
        """Insert semantic pattern analysis result."""
        query = """
        INSERT INTO semantic_patterns (
            file_id, pattern_type, description, confidence_score, 
            templates_involved, test_implications
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        values = (
            file_id,
            pattern_data['pattern_type'],
            pattern_data['description'],
            pattern_data['confidence_score'],
            json.dumps(pattern_data.get('templates_involved', [])),
            json.dumps(pattern_data.get('test_implications', []))
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def insert_data_flow_node(self, file_id: int, node_data: Dict[str, Any]) -> int:
        """Insert data flow node."""
        query = """
        INSERT INTO data_flow_nodes (
            file_id, node_id, node_type, template_name, line_number,
            xpath_expression, variable_name, condition_expr, predecessors, successors
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            file_id,
            node_data['node_id'],
            node_data['node_type'],
            node_data['template_name'],
            node_data.get('line_number'),
            node_data.get('xpath_expression'),
            node_data.get('variable_name'),
            node_data.get('condition_expr'),
            json.dumps(list(node_data.get('predecessors', set()))),
            json.dumps(list(node_data.get('successors', set())))
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def insert_variable_analysis(self, file_id: int, var_data: Dict[str, Any]) -> int:
        """Insert variable analysis result."""
        query = """
        INSERT INTO variable_analysis (
            file_id, variable_name, scope_type, definition_line, usage_count,
            is_conflicted, is_unused, used_by_templates
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            file_id,
            var_data['variable_name'],
            var_data['scope_type'],
            var_data.get('definition_line'),
            var_data.get('usage_count', 0),
            var_data.get('is_conflicted', False),
            var_data.get('is_unused', False),
            json.dumps(var_data.get('used_by_templates', []))
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def insert_transformation_hotspot(self, file_id: int, hotspot_data: Dict[str, Any]) -> int:
        """Insert transformation hotspot."""
        query = """
        INSERT INTO transformation_hotspots (
            file_id, template_name, hotspot_score, risk_level, reasons
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        values = (
            file_id,
            hotspot_data['template_name'],
            hotspot_data['hotspot_score'],
            hotspot_data['risk_level'],
            json.dumps(hotspot_data.get('reasons', []))
        )
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.lastrowid
    
    def get_semantic_patterns_by_file(self, file_id: int) -> List[Dict[str, Any]]:
        """Get all semantic patterns for a file."""
        query = """
        SELECT * FROM semantic_patterns WHERE file_id = ? ORDER BY confidence_score DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (file_id,))
            columns = [desc[0] for desc in cursor.description]
            
            patterns = []
            for row in cursor.fetchall():
                pattern = dict(zip(columns, row))
                # Parse JSON fields
                pattern['templates_involved'] = json.loads(pattern['templates_involved'])
                pattern['test_implications'] = json.loads(pattern['test_implications'])
                patterns.append(pattern)
            
            return patterns
    
    def get_transformation_hotspots_by_file(self, file_id: int) -> List[Dict[str, Any]]:
        """Get all transformation hotspots for a file."""
        query = """
        SELECT * FROM transformation_hotspots WHERE file_id = ? ORDER BY hotspot_score DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (file_id,))
            columns = [desc[0] for desc in cursor.description]
            
            hotspots = []
            for row in cursor.fetchall():
                hotspot = dict(zip(columns, row))
                # Parse JSON fields
                hotspot['reasons'] = json.loads(hotspot['reasons'])
                hotspots.append(hotspot)
            
            return hotspots
    
    def cleanup_analysis(self, keep_files: bool = True):
        """
        Clean up analysis data, optionally keeping file records.
        
        Args:
            keep_files: If True, keep transformation_files and file_dependencies
        """
        tables_to_clear = [
            'test_data_requirements',
            'test_specifications', 
            'path_conditions',
            'execution_paths',
            'template_calls',
            'xslt_variables',
            'xslt_templates',
            'xsd_attributes',
            'xsd_types',
            'xsd_elements',
            'coverage_analysis',
            'analysis_sessions',
            'transformation_hotspots',
            'variable_analysis',
            'data_flow_nodes',
            'semantic_patterns'
        ]
        
        if not keep_files:
            tables_to_clear.extend(['file_dependencies', 'transformation_files'])
        
        with self.get_connection() as conn:
            # Get list of existing tables
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            # Only delete from tables that actually exist
            deleted_count = 0
            for table in tables_to_clear:
                if table in existing_tables:
                    try:
                        cursor = conn.execute(f"DELETE FROM {table}")
                        rows_deleted = cursor.rowcount
                        if rows_deleted > 0:
                            self.logger.info(f"Deleted {rows_deleted} records from {table}")
                        deleted_count += rows_deleted
                    except sqlite3.Error as e:
                        self.logger.warning(f"Could not delete from {table}: {e}")
                else:
                    self.logger.debug(f"Table {table} does not exist, skipping")
            
            if keep_files and 'transformation_files' in existing_tables:
                # Reset analysis status for files
                try:
                    cursor = conn.execute("""
                        UPDATE transformation_files 
                        SET analysis_status = 'pending', error_message = NULL
                    """)
                    updated_count = cursor.rowcount
                    if updated_count > 0:
                        self.logger.info(f"Reset analysis status for {updated_count} files")
                except sqlite3.Error as e:
                    self.logger.warning(f"Could not reset file status: {e}")
            
            conn.commit()
        
        self.logger.info(f"Cleaned up analysis data, keep_files={keep_files}, total records deleted: {deleted_count}")