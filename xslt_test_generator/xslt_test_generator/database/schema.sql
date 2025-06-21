-- ========================================
-- XSLT Test Generator v2.0 Database Schema
-- ========================================
-- This schema supports enterprise-scale XSLT analysis with
-- multi-file dependencies, execution path tracing, and 
-- comprehensive test specification generation.

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ========================================
-- CORE FILE MANAGEMENT
-- ========================================

-- Track all files in the transformation ecosystem
CREATE TABLE transformation_files (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('xslt', 'xsd', 'xml')),
    content_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    imports JSON, -- Array of imported file paths
    analysis_status TEXT DEFAULT 'pending' CHECK (
        analysis_status IN ('pending', 'analyzing', 'completed', 'error', 'skipped')
    ),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track dependencies between files (imports/includes)
CREATE TABLE file_dependencies (
    id INTEGER PRIMARY KEY,
    parent_file_id INTEGER NOT NULL,
    child_file_id INTEGER NOT NULL,
    import_type TEXT NOT NULL CHECK (
        import_type IN ('xsl:import', 'xsl:include', 'xs:import', 'xs:include')
    ),
    namespace TEXT,
    xpath_location TEXT, -- Where in parent file this import occurs
    href_attribute TEXT, -- Original href value
    resolved_path TEXT,  -- Actual resolved file path
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_file_id) REFERENCES transformation_files(id) ON DELETE CASCADE,
    FOREIGN KEY (child_file_id) REFERENCES transformation_files(id) ON DELETE CASCADE,
    UNIQUE(parent_file_id, child_file_id, import_type)
);

-- ========================================
-- XSLT STRUCTURAL ANALYSIS
-- ========================================

-- All templates across all XSLT files
CREATE TABLE xslt_templates (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    name TEXT, -- Named templates (can be NULL for match templates)
    match_pattern TEXT, -- Match templates (can be NULL for named templates)
    mode TEXT,
    priority INTEGER,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    template_content TEXT NOT NULL,
    calls_templates JSON, -- Array of template names/patterns this calls
    called_by_templates JSON, -- Array of template IDs that call this
    uses_variables JSON, -- Array of variable names referenced
    defines_variables JSON, -- Array of variable names defined
    xpath_expressions JSON, -- All XPath expressions found in template
    conditional_logic JSON, -- if/choose/when conditions with line numbers
    output_elements JSON, -- Elements this template outputs
    template_hash TEXT, -- Hash of template content for change detection
    complexity_score INTEGER DEFAULT 0,
    is_recursive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- Cross-file variable tracking
CREATE TABLE xslt_variables (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    scope TEXT NOT NULL CHECK (scope IN ('global', 'template', 'local')),
    xpath_expression TEXT,
    line_number INTEGER NOT NULL,
    defined_in_template_id INTEGER,
    data_type TEXT, -- Inferred type: 'string', 'number', 'boolean', 'node-set'
    sample_values JSON, -- Sample values if literal
    is_parameter BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE,
    FOREIGN KEY (defined_in_template_id) REFERENCES xslt_templates(id) ON DELETE CASCADE
);

-- Template call relationships
CREATE TABLE template_calls (
    id INTEGER PRIMARY KEY,
    caller_template_id INTEGER NOT NULL,
    called_template_name TEXT, -- Name or match pattern
    called_template_id INTEGER, -- NULL if not resolved yet
    call_type TEXT NOT NULL CHECK (call_type IN ('call-template', 'apply-templates')),
    line_number INTEGER NOT NULL,
    with_params JSON, -- Parameters passed to called template
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caller_template_id) REFERENCES xslt_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (called_template_id) REFERENCES xslt_templates(id) ON DELETE CASCADE
);

-- ========================================
-- XSD SCHEMA ANALYSIS
-- ========================================

-- Complete XSD schema model across all files
CREATE TABLE xsd_elements (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    namespace TEXT,
    qualified_name TEXT, -- namespace:name
    type_name TEXT,
    type_namespace TEXT,
    min_occurs INTEGER DEFAULT 1,
    max_occurs TEXT DEFAULT '1', -- Can be 'unbounded'
    is_root_element BOOLEAN DEFAULT FALSE,
    is_abstract BOOLEAN DEFAULT FALSE,
    is_nillable BOOLEAN DEFAULT FALSE,
    parent_element_id INTEGER,
    element_path TEXT, -- XPath from root
    line_number INTEGER,
    default_value TEXT,
    fixed_value TEXT,
    annotation TEXT, -- Documentation from xs:annotation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_element_id) REFERENCES xsd_elements(id) ON DELETE CASCADE
);

-- XSD type definitions
CREATE TABLE xsd_types (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    namespace TEXT,
    qualified_name TEXT, -- namespace:name
    type_category TEXT NOT NULL CHECK (
        type_category IN ('simple', 'complex', 'restriction', 'extension', 'union', 'list')
    ),
    base_type TEXT,
    base_namespace TEXT,
    restriction_pattern TEXT,
    enumeration_values JSON,
    min_length INTEGER,
    max_length INTEGER,
    min_inclusive TEXT,
    max_inclusive TEXT,
    min_exclusive TEXT,
    max_exclusive TEXT,
    content_model TEXT, -- 'sequence', 'choice', 'all', 'group'
    is_mixed BOOLEAN DEFAULT FALSE,
    annotation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- XSD attributes
CREATE TABLE xsd_attributes (
    id INTEGER PRIMARY KEY,
    element_id INTEGER,
    type_id INTEGER,
    name TEXT NOT NULL,
    namespace TEXT,
    type_name TEXT,
    type_namespace TEXT,
    use_type TEXT DEFAULT 'optional' CHECK (use_type IN ('required', 'optional', 'prohibited')),
    default_value TEXT,
    fixed_value TEXT,
    annotation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (element_id) REFERENCES xsd_elements(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES xsd_types(id) ON DELETE CASCADE
);

-- ========================================
-- EXECUTION PATH ANALYSIS
-- ========================================

-- Discovered execution paths through XSLT
CREATE TABLE execution_paths (
    id INTEGER PRIMARY KEY,
    path_name TEXT NOT NULL,
    entry_template_id INTEGER NOT NULL,
    path_hash TEXT UNIQUE NOT NULL, -- Hash of template sequence for deduplication
    template_sequence JSON NOT NULL, -- Ordered array of template IDs
    decision_points JSON, -- Conditions that determine this path
    required_input_structure JSON, -- Input XML structure requirements
    expected_output_structure JSON, -- Expected output XML structure
    path_complexity_score INTEGER DEFAULT 0,
    covers_templates JSON, -- Array of template IDs covered by this path
    covers_conditions JSON, -- Array of condition hashes covered
    estimated_frequency TEXT DEFAULT 'unknown' CHECK (
        estimated_frequency IN ('common', 'edge_case', 'error', 'boundary', 'unknown')
    ),
    execution_depth INTEGER DEFAULT 0, -- How deep the call stack goes
    has_recursion BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_template_id) REFERENCES xslt_templates(id) ON DELETE CASCADE
);

-- Conditions that determine specific paths
CREATE TABLE path_conditions (
    id INTEGER PRIMARY KEY,
    path_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    condition_xpath TEXT NOT NULL,
    condition_type TEXT NOT NULL CHECK (
        condition_type IN ('if', 'choose', 'when', 'for-each', 'test')
    ),
    condition_branch TEXT NOT NULL, -- 'true', 'false', 'otherwise', 'each'
    required_input_values JSON, -- Input values needed for this condition
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (path_id) REFERENCES execution_paths(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES xslt_templates(id) ON DELETE CASCADE
);

-- ========================================
-- SEMANTIC ANALYSIS
-- ========================================

-- Semantic patterns identified in XSLT transformations
CREATE TABLE semantic_patterns (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL CHECK (
        pattern_type IN ('transformation_pipeline', 'conditional_processing', 'recursive_processing', 
                        'data_aggregation', 'template_orchestration', 'error_handling')
    ),
    description TEXT NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    templates_involved JSON NOT NULL, -- Array of template names
    test_implications JSON, -- Array of test requirement descriptions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- Data flow analysis results
CREATE TABLE data_flow_nodes (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL CHECK (
        node_type IN ('variable_assignment', 'parameter_passing', 'template_call', 
                     'xpath_selection', 'conditional_branch')
    ),
    template_name TEXT NOT NULL,
    line_number INTEGER,
    xpath_expression TEXT,
    variable_name TEXT,
    condition_expr TEXT,
    predecessors JSON, -- Array of predecessor node IDs
    successors JSON,   -- Array of successor node IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- Variable scoping and lifecycle analysis
CREATE TABLE variable_analysis (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    scope_type TEXT NOT NULL CHECK (scope_type IN ('global', 'template', 'local')),
    definition_line INTEGER,
    usage_count INTEGER DEFAULT 0,
    is_conflicted BOOLEAN DEFAULT FALSE,
    is_unused BOOLEAN DEFAULT FALSE,
    used_by_templates JSON, -- Array of template names that use this variable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- Transformation hotspots (high-risk areas)
CREATE TABLE transformation_hotspots (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    template_name TEXT NOT NULL,
    hotspot_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    reasons JSON NOT NULL, -- Array of reasons for hotspot classification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES transformation_files(id) ON DELETE CASCADE
);

-- ========================================
-- TEST SPECIFICATIONS
-- ========================================

-- Comprehensive test specifications generated from paths
CREATE TABLE test_specifications (
    id INTEGER PRIMARY KEY,
    execution_path_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    test_description TEXT,
    test_category TEXT DEFAULT 'functional' CHECK (
        test_category IN ('happy_path', 'edge_case', 'error_scenario', 'boundary', 'integration', 'performance')
    ),
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10), -- 1=highest, 10=lowest
    
    -- Input requirements
    input_xml_template JSON, -- XML structure template with placeholders
    input_data_constraints JSON, -- Specific value requirements and constraints
    input_generation_rules JSON, -- Rules for generating test data
    required_namespaces JSON, -- Namespaces that must be present
    
    -- Expected output
    expected_output_template JSON, -- Expected XML structure template
    xpath_assertions JSON, -- Array of XPath assertion objects
    output_validation_rules JSON, -- Validation criteria for output
    expected_errors JSON, -- Expected errors for negative test cases
    
    -- Test execution metadata
    estimated_execution_time INTEGER, -- Estimated milliseconds
    test_complexity_score INTEGER DEFAULT 0,
    depends_on_tests JSON, -- Array of test IDs this depends on
    tags JSON, -- Array of tags for test organization
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_path_id) REFERENCES execution_paths(id) ON DELETE CASCADE
);

-- Detailed test data requirements for input generation
CREATE TABLE test_data_requirements (
    id INTEGER PRIMARY KEY,
    test_spec_id INTEGER NOT NULL,
    element_path TEXT NOT NULL, -- XPath to element in input XML
    element_name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    required_value TEXT, -- Specific value if fixed
    value_constraints JSON, -- Min/max, pattern, enum values, etc.
    generation_strategy TEXT DEFAULT 'random' CHECK (
        generation_strategy IN ('fixed', 'random', 'sequential', 'pattern', 'derived')
    ),
    sample_values JSON, -- Array of sample valid values
    invalid_values JSON, -- Array of sample invalid values for negative tests
    relationship_rules JSON, -- Rules for relationships with other elements
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_spec_id) REFERENCES test_specifications(id) ON DELETE CASCADE
);

-- ========================================
-- ANALYSIS METADATA & REPORTING
-- ========================================

-- Analysis session tracking
CREATE TABLE analysis_sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT,
    entry_file_path TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'running' CHECK (
        status IN ('running', 'completed', 'failed', 'cancelled')
    ),
    files_analyzed INTEGER DEFAULT 0,
    templates_found INTEGER DEFAULT 0,
    paths_discovered INTEGER DEFAULT 0,
    tests_generated INTEGER DEFAULT 0,
    error_log TEXT,
    configuration JSON -- Analysis parameters used
);

-- Coverage tracking
CREATE TABLE coverage_analysis (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    total_templates INTEGER DEFAULT 0,
    covered_templates INTEGER DEFAULT 0,
    total_conditions INTEGER DEFAULT 0,
    covered_conditions INTEGER DEFAULT 0,
    total_variables INTEGER DEFAULT 0,
    referenced_variables INTEGER DEFAULT 0,
    template_coverage_percentage REAL DEFAULT 0.0,
    condition_coverage_percentage REAL DEFAULT 0.0,
    variable_coverage_percentage REAL DEFAULT 0.0,
    uncovered_templates JSON, -- Array of template IDs not covered
    uncovered_conditions JSON, -- Array of condition hashes not covered
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES analysis_sessions(id) ON DELETE CASCADE
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- File management indexes
CREATE INDEX idx_transformation_files_type ON transformation_files(file_type);
CREATE INDEX idx_transformation_files_status ON transformation_files(analysis_status);
CREATE INDEX idx_transformation_files_hash ON transformation_files(content_hash);
CREATE INDEX idx_file_dependencies_parent ON file_dependencies(parent_file_id);
CREATE INDEX idx_file_dependencies_child ON file_dependencies(child_file_id);

-- XSLT analysis indexes
CREATE INDEX idx_xslt_templates_file ON xslt_templates(file_id);
CREATE INDEX idx_xslt_templates_name ON xslt_templates(name);
CREATE INDEX idx_xslt_templates_match ON xslt_templates(match_pattern);
CREATE INDEX idx_xslt_variables_file ON xslt_variables(file_id);
CREATE INDEX idx_xslt_variables_name ON xslt_variables(name);
CREATE INDEX idx_template_calls_caller ON template_calls(caller_template_id);
CREATE INDEX idx_template_calls_called ON template_calls(called_template_id);

-- XSD analysis indexes
CREATE INDEX idx_xsd_elements_file ON xsd_elements(file_id);
CREATE INDEX idx_xsd_elements_name ON xsd_elements(name);
CREATE INDEX idx_xsd_elements_parent ON xsd_elements(parent_element_id);
CREATE INDEX idx_xsd_types_file ON xsd_types(file_id);
CREATE INDEX idx_xsd_types_name ON xsd_types(name);

-- Execution path indexes
CREATE INDEX idx_execution_paths_entry ON execution_paths(entry_template_id);
CREATE INDEX idx_execution_paths_hash ON execution_paths(path_hash);
CREATE INDEX idx_path_conditions_path ON path_conditions(path_id);
CREATE INDEX idx_path_conditions_template ON path_conditions(template_id);

-- Test specification indexes
CREATE INDEX idx_test_specs_path ON test_specifications(execution_path_id);
CREATE INDEX idx_test_specs_category ON test_specifications(test_category);
CREATE INDEX idx_test_specs_priority ON test_specifications(priority);
CREATE INDEX idx_test_data_reqs_spec ON test_data_requirements(test_spec_id);

-- ========================================
-- VIEWS FOR COMMON QUERIES
-- ========================================

-- View: Complete file dependency graph
CREATE VIEW v_file_dependency_graph AS
SELECT 
    p.file_path as parent_file,
    p.file_type as parent_type,
    c.file_path as child_file,
    c.file_type as child_type,
    d.import_type,
    d.namespace
FROM file_dependencies d
JOIN transformation_files p ON d.parent_file_id = p.id
JOIN transformation_files c ON d.child_file_id = c.id;

-- View: Template call relationships with file context
CREATE VIEW v_template_call_graph AS
SELECT 
    tf1.file_path as caller_file,
    t1.name as caller_template,
    t1.match_pattern as caller_match,
    tc.called_template_name,
    tf2.file_path as called_file,
    t2.name as called_template,
    t2.match_pattern as called_match,
    tc.call_type,
    tc.line_number
FROM template_calls tc
JOIN xslt_templates t1 ON tc.caller_template_id = t1.id
JOIN transformation_files tf1 ON t1.file_id = tf1.id
LEFT JOIN xslt_templates t2 ON tc.called_template_id = t2.id
LEFT JOIN transformation_files tf2 ON t2.file_id = tf2.id;

-- View: Test coverage summary
CREATE VIEW v_test_coverage_summary AS
SELECT 
    COUNT(DISTINCT t.id) as total_templates,
    COUNT(DISTINCT ep.entry_template_id) as entry_point_templates,
    COUNT(DISTINCT ep.id) as total_paths,
    COUNT(DISTINCT ts.id) as total_tests,
    AVG(ep.path_complexity_score) as avg_path_complexity,
    COUNT(DISTINCT CASE WHEN ts.test_category = 'happy_path' THEN ts.id END) as happy_path_tests,
    COUNT(DISTINCT CASE WHEN ts.test_category = 'edge_case' THEN ts.id END) as edge_case_tests,
    COUNT(DISTINCT CASE WHEN ts.test_category = 'error_scenario' THEN ts.id END) as error_tests
FROM xslt_templates t
LEFT JOIN execution_paths ep ON t.id = ep.entry_template_id
LEFT JOIN test_specifications ts ON ep.id = ts.execution_path_id;

-- ========================================
-- TRIGGERS FOR DATA INTEGRITY
-- ========================================

-- Update timestamp trigger for transformation_files
CREATE TRIGGER update_transformation_files_timestamp 
AFTER UPDATE ON transformation_files
BEGIN
    UPDATE transformation_files 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Update timestamp trigger for test_specifications
CREATE TRIGGER update_test_specifications_timestamp 
AFTER UPDATE ON test_specifications
BEGIN
    UPDATE test_specifications 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- ========================================
-- INITIAL DATA AND CONFIGURATION
-- ========================================

-- Insert schema version for migration tracking
CREATE TABLE schema_metadata (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_metadata (version, description) 
VALUES ('2.0.0', 'Initial schema for XSLT Test Generator v2.0 with multi-file support');