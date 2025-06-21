"""Integration tests for Phase 2 XSLT Analysis Engine."""

import pytest
from pathlib import Path
import tempfile
import json

from xslt_test_generator.database.connection import DatabaseManager
from xslt_test_generator.analysis.analysis_coordinator import AnalysisCoordinator


class TestPhase2Integration:
    """Integration tests for complete Phase 2 analysis workflow."""
    
    @pytest.fixture
    def complex_xslt_file(self, temp_dir):
        """Create complex XSLT file for comprehensive testing."""
        xslt_content = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Global variables and parameters -->
    <xsl:variable name="companyName" select="'ACME Corp'"/>
    <xsl:param name="reportMode" select="'detailed'"/>
    <xsl:param name="includeDebug" select="false()"/>
    
    <!-- Root template -->
    <xsl:template match="/">
        <html>
            <head>
                <title><xsl:value-of select="$companyName"/> - Report</title>
            </head>
            <body>
                <xsl:call-template name="generateHeader"/>
                <xsl:apply-templates select="//order"/>
                <xsl:call-template name="generateFooter"/>
            </body>
        </html>
    </xsl:template>
    
    <!-- Header template -->
    <xsl:template name="generateHeader">
        <header>
            <h1><xsl:value-of select="$companyName"/></h1>
            <xsl:if test="$includeDebug = true()">
                <div class="debug">Debug mode enabled</div>
            </xsl:if>
        </header>
    </xsl:template>
    
    <!-- Order processing with complex conditional logic -->
    <xsl:template match="order">
        <xsl:variable name="orderTotal" select="sum(item/@price * item/@quantity)"/>
        <xsl:variable name="customerType" select="customer/@type"/>
        
        <div class="order">
            <h2>Order <xsl:value-of select="@id"/></h2>
            
            <!-- Customer information -->
            <xsl:choose>
                <xsl:when test="$customerType = 'premium'">
                    <xsl:call-template name="processPremiumCustomer">
                        <xsl:with-param name="customer" select="customer"/>
                        <xsl:with-param name="orderTotal" select="$orderTotal"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="$customerType = 'standard'">
                    <xsl:call-template name="processStandardCustomer">
                        <xsl:with-param name="customer" select="customer"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                    <div class="customer-basic">
                        <p>Customer: <xsl:value-of select="customer/name"/></p>
                    </div>
                </xsl:otherwise>
            </xsl:choose>
            
            <!-- Order items with aggregation -->
            <div class="items">
                <h3>Items (<xsl:value-of select="count(item)"/> total)</h3>
                <xsl:for-each select="item">
                    <xsl:sort select="@priority" order="ascending"/>
                    <xsl:call-template name="processOrderItem">
                        <xsl:with-param name="item" select="."/>
                        <xsl:with-param name="position" select="position()"/>
                    </xsl:call-template>
                </xsl:for-each>
                
                <!-- Order summary with conditional pricing -->
                <div class="summary">
                    <p>Subtotal: <xsl:value-of select="format-number($orderTotal, '0.00')"/></p>
                    <xsl:choose>
                        <xsl:when test="$orderTotal >= 1000">
                            <p class="total">Total with discount: <xsl:value-of select="format-number($orderTotal * 0.9, '0.00')"/></p>
                        </xsl:when>
                        <xsl:when test="$orderTotal >= 500">
                            <p class="total">Total with discount: <xsl:value-of select="format-number($orderTotal * 0.95, '0.00')"/></p>
                        </xsl:when>
                        <xsl:otherwise>
                            <p class="total">Total: <xsl:value-of select="format-number($orderTotal, '0.00')"/></p>
                        </xsl:otherwise>
                    </xsl:choose>
                </div>
            </div>
        </div>
    </xsl:template>
    
    <!-- Premium customer processing -->
    <xsl:template name="processPremiumCustomer">
        <xsl:param name="customer"/>
        <xsl:param name="orderTotal"/>
        
        <div class="customer-premium">
            <h3>Premium Customer</h3>
            <p>Name: <xsl:value-of select="$customer/name"/></p>
            <p>Email: <xsl:value-of select="$customer/email"/></p>
            
            <xsl:if test="$orderTotal >= 2000">
                <div class="vip-benefits">
                    <p>VIP Benefits Applied</p>
                </div>
            </xsl:if>
            
            <xsl:variable name="loyaltyPoints" select="floor($orderTotal div 10)"/>
            <p>Loyalty Points Earned: <xsl:value-of select="$loyaltyPoints"/></p>
        </div>
    </xsl:template>
    
    <!-- Standard customer processing -->
    <xsl:template name="processStandardCustomer">
        <xsl:param name="customer"/>
        
        <div class="customer-standard">
            <h3>Standard Customer</h3>
            <p>Name: <xsl:value-of select="$customer/name"/></p>
            <p>Email: <xsl:value-of select="$customer/email"/></p>
        </div>
    </xsl:template>
    
    <!-- Order item processing -->
    <xsl:template name="processOrderItem">
        <xsl:param name="item"/>
        <xsl:param name="position"/>
        
        <div class="item">
            <xsl:variable name="itemTotal" select="@price * @quantity"/>
            
            <span class="position"><xsl:value-of select="$position"/>.</span>
            <span class="name"><xsl:value-of select="@name"/></span>
            <span class="quantity">Qty: <xsl:value-of select="@quantity"/></span>
            <span class="total">Total: <xsl:value-of select="format-number($itemTotal, '0.00')"/></span>
            
            <!-- Priority indicators -->
            <xsl:choose>
                <xsl:when test="@priority = 'urgent'">
                    <span class="priority urgent">URGENT</span>
                </xsl:when>
                <xsl:when test="@priority = 'high'">
                    <span class="priority high">HIGH</span>
                </xsl:when>
                <xsl:when test="@priority = 'normal'">
                    <span class="priority normal">NORMAL</span>
                </xsl:when>
                <xsl:otherwise>
                    <span class="priority low">LOW</span>
                </xsl:otherwise>
            </xsl:choose>
            
            <!-- Special handling for specific categories -->
            <xsl:if test="@category = 'electronics'">
                <div class="warranty">
                    <p>Electronics Warranty: 1 Year</p>
                </div>
            </xsl:if>
            
            <xsl:if test="@category = 'fragile'">
                <div class="handling">
                    <p>Special Handling Required</p>
                </div>
            </xsl:if>
        </div>
    </xsl:template>
    
    <!-- Recursive category processor -->
    <xsl:template name="processCategoryHierarchy">
        <xsl:param name="categories"/>
        <xsl:param name="level" select="1"/>
        
        <xsl:for-each select="$categories">
            <div class="category">
                <h3>Category: <xsl:value-of select="@name"/></h3>
                
                <xsl:if test="subcategory">
                    <xsl:call-template name="processCategoryHierarchy">
                        <xsl:with-param name="categories" select="subcategory"/>
                        <xsl:with-param name="level" select="$level + 1"/>
                    </xsl:call-template>
                </xsl:if>
            </div>
        </xsl:for-each>
    </xsl:template>
    
    <!-- Footer template -->
    <xsl:template name="generateFooter">
        <footer>
            <p>Report Mode: <xsl:value-of select="$reportMode"/></p>
            
            <xsl:if test="$includeDebug = true()">
                <div class="debug-info">
                    <h4>Debug Information</h4>
                    <p>Total Orders: <xsl:value-of select="count(//order)"/></p>
                    <p>Total Items: <xsl:value-of select="count(//item)"/></p>
                    <p>Grand Total: <xsl:value-of select="format-number(sum(//item/@price * //item/@quantity), '0.00')"/></p>
                </div>
            </xsl:if>
        </footer>
    </xsl:template>
    
    <!-- Error handling template -->
    <xsl:template name="handleError">
        <xsl:param name="errorMessage"/>
        <xsl:param name="errorCode"/>
        
        <div class="error">
            <h3>Error Occurred</h3>
            <p>Code: <xsl:value-of select="$errorCode"/></p>
            <p>Message: <xsl:value-of select="$errorMessage"/></p>
            <xsl:message terminate="no">
                Error <xsl:value-of select="$errorCode"/>: <xsl:value-of select="$errorMessage"/>
            </xsl:message>
        </div>
    </xsl:template>
    
</xsl:stylesheet>"""
        
        xslt_file = temp_dir / "complex_analysis.xsl"
        xslt_file.write_text(xslt_content)
        return str(xslt_file)
    
    def test_complete_analysis_workflow(self, temp_dir, complex_xslt_file):
        """Test complete Phase 2 analysis workflow."""
        # Create database
        db_path = str(temp_dir / "analysis_integration.db")
        db = DatabaseManager(db_path)
        
        # Create analysis coordinator
        coordinator = AnalysisCoordinator(db)
        
        # Perform complete analysis
        result = coordinator.analyze_xslt_file(complex_xslt_file, force_reanalysis=True)
        
        # Verify no errors
        assert 'error' not in result
        
        # Verify all analysis phases completed
        assert 'template_analysis' in result
        assert 'semantic_analysis' in result
        assert 'execution_analysis' in result
        assert 'summary' in result
        
        # Verify template analysis results
        template_analysis = result['template_analysis']
        templates = template_analysis['templates']
        variables = template_analysis['variables']
        
        # Should parse all templates
        assert len(templates) >= 8  # All defined templates
        assert len(variables) >= 3  # Global variables/parameters
        
        # Check specific templates were found
        template_names = [t.name for t in templates.values() if t.name]
        expected_names = [
            'generateHeader', 'processPremiumCustomer', 'processStandardCustomer',
            'processOrderItem', 'processCategoryHierarchy', 'generateFooter', 'handleError'
        ]
        for name in expected_names:
            assert name in template_names
        
        # Check match templates
        match_templates = [t for t in templates.values() if t.match_pattern]
        assert len(match_templates) >= 2  # Root and order templates
        
        # Verify semantic analysis results
        semantic_analysis = result['semantic_analysis']
        patterns = semantic_analysis['semantic_patterns']
        hotspots = semantic_analysis['transformation_hotspots']
        
        # Should identify multiple semantic patterns
        assert len(patterns) >= 3
        
        # Check specific pattern types
        pattern_types = [p.pattern_type for p in patterns]
        assert 'conditional_processing' in pattern_types
        assert 'template_orchestration' in pattern_types
        assert 'data_aggregation' in pattern_types
        
        # Should identify transformation hotspots
        assert len(hotspots) > 0
        
        # Verify execution analysis results
        execution_analysis = result['execution_analysis']
        paths = execution_analysis['execution_paths']
        entry_points = execution_analysis['entry_points']
        
        # Should discover execution paths
        assert len(paths) > 0
        assert len(entry_points) > 0
        
        # Entry points should include match templates
        assert '/' in entry_points
        assert 'order' in entry_points
        
        # Verify analysis summary
        summary = result['summary']
        assert 'overall_complexity' in summary
        assert 'test_generation_priority' in summary
        assert summary['overall_complexity'] > 50  # Complex XSLT should have high complexity
    
    def test_database_persistence_verification(self, temp_dir, complex_xslt_file):
        """Test that analysis results are properly persisted in database."""
        db_path = str(temp_dir / "persistence_test.db")
        db = DatabaseManager(db_path)
        coordinator = AnalysisCoordinator(db)
        
        # Perform analysis
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        # Verify database contains analysis results
        file_record = db.get_file_by_path(complex_xslt_file)
        assert file_record is not None
        assert file_record['analysis_status'] == 'completed'
        
        # Check templates were stored
        templates = db.get_templates_by_file(file_record['id'])
        assert len(templates) >= 8
        
        # Check template details
        root_template = next((t for t in templates if t.get('match_pattern') == '/'), None)
        assert root_template is not None
        assert root_template['complexity_score'] > 0
        
        # Check variables were stored (they should be in xslt_variables table)
        # Note: Would need to add get_variables_by_file method to fully test
        
        # Check semantic patterns were stored
        patterns = db.get_semantic_patterns_by_file(file_record['id'])
        assert len(patterns) > 0
        
        # Check pattern details
        pattern = patterns[0]
        assert 'pattern_type' in pattern
        assert 'confidence_score' in pattern
        assert 'templates_involved' in pattern
        
        # Check hotspots were stored
        hotspots = db.get_transformation_hotspots_by_file(file_record['id'])
        assert len(hotspots) > 0
        
        # Check hotspot details
        hotspot = hotspots[0]
        assert 'template_name' in hotspot
        assert 'hotspot_score' in hotspot
        assert 'risk_level' in hotspot
    
    def test_incremental_analysis_detection(self, temp_dir, complex_xslt_file):
        """Test incremental analysis behavior."""
        db_path = str(temp_dir / "incremental_test.db")
        db = DatabaseManager(db_path)
        coordinator = AnalysisCoordinator(db)
        
        # First analysis
        result1 = coordinator.analyze_xslt_file(complex_xslt_file)
        assert 'error' not in result1
        
        # Second analysis without force - should use cached results
        result2 = coordinator.analyze_xslt_file(complex_xslt_file, force_reanalysis=False)
        assert 'status' in result2
        assert result2['status'] == 'loaded_from_cache'
        
        # Third analysis with force - should reanalyze
        result3 = coordinator.analyze_xslt_file(complex_xslt_file, force_reanalysis=True)
        assert 'template_analysis' in result3
        assert 'error' not in result3
    
    def test_complex_conditional_logic_analysis(self, temp_dir, complex_xslt_file):
        """Test analysis of complex conditional logic."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        # Check conditional processing pattern was detected
        semantic_analysis = result['semantic_analysis']
        patterns = semantic_analysis['semantic_patterns']
        
        conditional_patterns = [p for p in patterns if p.pattern_type == 'conditional_processing']
        assert len(conditional_patterns) > 0
        
        conditional_pattern = conditional_patterns[0]
        assert conditional_pattern.confidence_score >= 0.8
        
        # Check test implications include conditional testing
        test_implications = conditional_pattern.test_implications
        assert any('conditional' in impl.lower() for impl in test_implications)
        assert any('branch' in impl.lower() for impl in test_implications)
    
    def test_data_aggregation_pattern_detection(self, temp_dir, complex_xslt_file):
        """Test detection of data aggregation patterns."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        # Should detect data aggregation due to sum(), count(), format-number() functions
        semantic_analysis = result['semantic_analysis']
        patterns = semantic_analysis['semantic_patterns']
        
        aggregation_patterns = [p for p in patterns if p.pattern_type == 'data_aggregation']
        assert len(aggregation_patterns) > 0
        
        # Check templates involved in aggregation
        aggregation_pattern = aggregation_patterns[0]
        assert len(aggregation_pattern.templates_involved) > 0
    
    def test_recursive_template_analysis(self, temp_dir):
        """Test analysis of recursive templates."""
        # Create XSLT with recursive template
        recursive_xslt = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <result>
            <xsl:call-template name="processTree">
                <xsl:with-param name="nodes" select="//node"/>
                <xsl:with-param name="depth" select="0"/>
            </xsl:call-template>
        </result>
    </xsl:template>
    
    <xsl:template name="processTree">
        <xsl:param name="nodes"/>
        <xsl:param name="depth"/>
        
        <xsl:for-each select="$nodes">
            <item level="{$depth}">
                <xsl:value-of select="@name"/>
                
                <xsl:if test="child::node and $depth < 10">
                    <xsl:call-template name="processTree">
                        <xsl:with-param name="nodes" select="child::node"/>
                        <xsl:with-param name="depth" select="$depth + 1"/>
                    </xsl:call-template>
                </xsl:if>
            </item>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>"""
        
        recursive_file = temp_dir / "recursive.xsl"
        recursive_file.write_text(recursive_xslt)
        
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(str(recursive_file))
        
        # Should detect recursive processing pattern
        semantic_analysis = result['semantic_analysis']
        patterns = semantic_analysis['semantic_patterns']
        
        recursive_patterns = [p for p in patterns if p.pattern_type == 'recursive_processing']
        assert len(recursive_patterns) > 0
        
        recursive_pattern = recursive_patterns[0]
        assert recursive_pattern.confidence_score == 1.0  # Perfect confidence for recursion
        assert 'processTree' in recursive_pattern.templates_involved
        
        # Check test implications for recursion
        test_implications = recursive_pattern.test_implications
        assert any('recursion' in impl.lower() for impl in test_implications)
        assert any('termination' in impl.lower() for impl in test_implications)
    
    def test_template_orchestration_analysis(self, temp_dir, complex_xslt_file):
        """Test analysis of template orchestration patterns."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        # Should detect orchestration due to templates calling multiple others
        semantic_analysis = result['semantic_analysis']
        patterns = semantic_analysis['semantic_patterns']
        
        orchestration_patterns = [p for p in patterns if p.pattern_type == 'template_orchestration']
        assert len(orchestration_patterns) > 0
        
        # Root template and order template should be orchestrators
        orchestration_pattern = orchestration_patterns[0]
        orchestrating_templates = orchestration_pattern.templates_involved
        
        # Should include templates that call multiple others
        template_analysis = result['template_analysis']
        templates = template_analysis['templates']
        
        # Find templates with multiple calls
        multi_call_templates = [
            name for name, template in templates.items() 
            if len(template.calls_templates) >= 3
        ]
        
        # At least one orchestrating template should be a multi-call template
        assert len(multi_call_templates) > 0
    
    def test_transformation_hotspot_identification(self, temp_dir, complex_xslt_file):
        """Test identification of transformation hotspots."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        semantic_analysis = result['semantic_analysis']
        hotspots = semantic_analysis['transformation_hotspots']
        
        # Should identify hotspots
        assert len(hotspots) > 0
        
        # Check hotspot structure and scoring
        for hotspot in hotspots:
            assert hotspot['hotspot_score'] >= 5  # Threshold for hotspot identification
            assert hotspot['risk_level'] in ['low', 'medium', 'high', 'critical']
            assert len(hotspot['reasons']) > 0
            
            # High complexity templates should be hotspots
            if hotspot['hotspot_score'] >= 8:
                assert hotspot['risk_level'] in ['medium', 'high', 'critical']
    
    def test_execution_path_coverage(self, temp_dir, complex_xslt_file):
        """Test execution path coverage analysis."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        execution_analysis = result['execution_analysis']
        coverage = execution_analysis['coverage_analysis']
        
        # Check coverage metrics
        assert 'node_coverage_percentage' in coverage
        assert 'template_coverage_percentage' in coverage
        assert 'coverage_gaps' in coverage
        
        # Coverage should be reasonable for complex XSLT
        assert coverage['node_coverage_percentage'] > 0
        assert coverage['template_coverage_percentage'] > 0
        
        # Should identify coverage gaps
        gaps = coverage['coverage_gaps']
        for gap in gaps:
            assert 'gap_type' in gap
            assert 'description' in gap
            assert 'impact' in gap
    
    def test_test_scenario_generation(self, temp_dir, complex_xslt_file):
        """Test generation of test scenarios."""
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        
        execution_analysis = result['execution_analysis']
        scenarios = execution_analysis['test_scenarios']
        
        # Should generate test scenarios
        assert len(scenarios) > 0
        
        # Check scenario types
        scenario_types = set(s['scenario_type'] for s in scenarios)
        expected_types = {'critical_path', 'conditional_logic', 'happy_path'}
        assert scenario_types.intersection(expected_types)
        
        # Check scenario structure
        for scenario in scenarios:
            assert 'scenario_type' in scenario
            assert 'description' in scenario
            assert 'test_requirements' in scenario
            assert 'priority' in scenario
            assert scenario['priority'] in ['low', 'medium', 'high']
    
    def test_analysis_recommendations(self, temp_dir, complex_xslt_file):
        """Test analysis-based recommendations."""
        db_path = str(temp_dir / "recommendations_test.db")
        db = DatabaseManager(db_path)
        coordinator = AnalysisCoordinator(db)
        
        # Perform analysis
        result = coordinator.analyze_xslt_file(complex_xslt_file)
        assert 'error' not in result
        
        # Get recommendations
        recommendations = coordinator.get_analysis_recommendations(complex_xslt_file)
        assert 'error' not in recommendations
        
        # Check recommendation structure
        assert 'test_prioritization' in recommendations
        assert 'test_data_generation' in recommendations
        assert 'coverage_strategy' in recommendations
        assert 'risk_assessment' in recommendations
        assert 'optimization_suggestions' in recommendations
        
        # Check test prioritization
        priorities = recommendations['test_prioritization']
        if priorities:  # May be empty if no high-priority templates
            for priority in priorities:
                assert 'template_name' in priority
                assert 'priority' in priority
                assert 'priority_score' in priority
                assert 'reasons' in priority
        
        # Check risk assessment
        risks = recommendations['risk_assessment']
        if risks:  # May be empty if no significant risks
            for risk in risks:
                assert 'risk_type' in risk
                assert 'severity' in risk
                assert 'description' in risk
                assert 'mitigation' in risk
    
    def test_performance_with_large_xslt(self, temp_dir):
        """Test performance with large XSLT files."""
        import time
        
        # Generate a large XSLT file
        large_xslt_parts = [
            """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:variable name="largeVar" select="'Large Document Processing'"/>
    
    <xsl:template match="/">
        <html>
            <body>
                <xsl:apply-templates select="//record"/>
            </body>
        </html>
    </xsl:template>"""
        ]
        
        # Add many templates
        for i in range(50):
            template = f"""
    <xsl:template match="record[@type='type_{i}']">
        <div class="record-{i}">
            <h3>Record Type {i}</h3>
            <xsl:if test="@priority = 'high'">
                <span class="priority">HIGH PRIORITY</span>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="@status = 'active'">
                    <div class="active">Active Record</div>
                </xsl:when>
                <xsl:when test="@status = 'inactive'">
                    <div class="inactive">Inactive Record</div>
                </xsl:when>
                <xsl:otherwise>
                    <div class="unknown">Unknown Status</div>
                </xsl:otherwise>
            </xsl:choose>
            <p><xsl:value-of select="description"/></p>
        </div>
    </xsl:template>"""
            large_xslt_parts.append(template)
        
        large_xslt_parts.append('</xsl:stylesheet>')
        large_xslt_content = ''.join(large_xslt_parts)
        
        large_file = temp_dir / "large_performance_test.xsl"
        large_file.write_text(large_xslt_content)
        
        db = DatabaseManager()
        coordinator = AnalysisCoordinator(db)
        
        # Measure analysis time
        start_time = time.time()
        result = coordinator.analyze_xslt_file(str(large_file))
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert analysis_time < 30.0  # 30 seconds max for large file
        
        # Should still produce valid results
        assert 'error' not in result
        assert len(result['template_analysis']['templates']) >= 50
        
        # Should identify patterns even in large files
        patterns = result['semantic_analysis']['semantic_patterns']
        assert len(patterns) > 0