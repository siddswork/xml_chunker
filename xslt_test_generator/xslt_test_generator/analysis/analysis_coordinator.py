"""Analysis Coordinator - Orchestrates the complete XSLT analysis process."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from ..core.base import LoggerMixin
from ..database.connection import DatabaseManager
from .template_parser import XSLTTemplateParser
from .semantic_analyzer import SemanticAnalyzer
from .execution_path_analyzer import ExecutionPathAnalyzer


class AnalysisCoordinator(LoggerMixin):
    """Coordinates the complete XSLT analysis process."""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.template_parser = XSLTTemplateParser()
        self.semantic_analyzer = SemanticAnalyzer()
        self.execution_analyzer = ExecutionPathAnalyzer()
    
    def analyze_xslt_file(self, file_path: str, force_reanalysis: bool = False) -> Dict[str, Any]:
        """
        Perform complete XSLT analysis for a single file.
        
        Args:
            file_path: Path to XSLT file
            force_reanalysis: Force reanalysis even if already completed
            
        Returns:
            Dictionary containing complete analysis results
        """
        try:
            self.logger.info(f"Starting XSLT analysis for: {file_path}")
            
            # Check if analysis already exists and is current
            file_record = self.db.get_file_by_path(file_path)
            if (not force_reanalysis and file_record and 
                file_record['analysis_status'] == 'completed'):
                self.logger.info(f"Analysis already completed for {file_path}")
                return self._load_existing_analysis(file_record['id'])
            
            # Update status to analyzing
            if file_record:
                self.db.update_file_analysis_status(file_record['id'], 'analyzing')
            
            # Phase 1: Template Parsing
            self.logger.info("Phase 1: Parsing XSLT templates and variables")
            parse_results = self.template_parser.parse_xslt_file(file_path)
            
            if 'error' in parse_results:
                self._handle_analysis_error(file_record, f"Template parsing error: {parse_results['error']}")
                return parse_results
            
            templates = parse_results['templates']
            variables = parse_results['variables']
            
            # Phase 2: Semantic Analysis
            self.logger.info("Phase 2: Performing semantic analysis")
            semantic_results = self.semantic_analyzer.analyze_semantics(
                templates, variables, file_path
            )
            
            if 'error' in semantic_results:
                self._handle_analysis_error(file_record, f"Semantic analysis error: {semantic_results['error']}")
                return semantic_results
            
            # Phase 3: Execution Path Analysis
            self.logger.info("Phase 3: Analyzing execution paths")
            execution_results = self.execution_analyzer.analyze_execution_paths(
                templates, variables, semantic_results['semantic_patterns'], file_path
            )
            
            if 'error' in execution_results:
                self._handle_analysis_error(file_record, f"Execution analysis error: {execution_results['error']}")
                return execution_results
            
            # Phase 4: Store Results
            self.logger.info("Phase 4: Storing analysis results")
            analysis_id = self._store_analysis_results(
                file_record['id'], parse_results, semantic_results, execution_results
            )
            
            # Update status to completed
            self.db.update_file_analysis_status(file_record['id'], 'completed')
            
            # Compile complete results
            complete_results = {
                'analysis_id': analysis_id,
                'file_path': file_path,
                'template_analysis': parse_results,
                'semantic_analysis': semantic_results,
                'execution_analysis': execution_results,
                'analysis_timestamp': datetime.now().isoformat(),
                'summary': self._generate_complete_summary(parse_results, semantic_results, execution_results)
            }
            
            self.logger.info(f"XSLT analysis completed successfully for: {file_path}")
            return complete_results
            
        except Exception as e:
            self.logger.error(f"Unexpected error in XSLT analysis for {file_path}: {e}")
            if file_record:
                self._handle_analysis_error(file_record, f"Unexpected error: {str(e)}")
            return {'error': f"Analysis failed: {str(e)}"}
    
    def analyze_multiple_files(self, file_paths: List[str], 
                              force_reanalysis: bool = False) -> Dict[str, Any]:
        """
        Analyze multiple XSLT files and aggregate results.
        
        Args:
            file_paths: List of XSLT file paths
            force_reanalysis: Force reanalysis for all files
            
        Returns:
            Dictionary containing aggregated analysis results
        """
        self.logger.info(f"Starting batch analysis of {len(file_paths)} files")
        
        results = {}
        errors = {}
        successful_analyses = 0
        
        for file_path in file_paths:
            try:
                result = self.analyze_xslt_file(file_path, force_reanalysis)
                
                if 'error' in result:
                    errors[file_path] = result['error']
                else:
                    results[file_path] = result
                    successful_analyses += 1
                    
            except Exception as e:
                errors[file_path] = f"Analysis failed: {str(e)}"
        
        # Generate cross-file analysis
        cross_file_analysis = {}
        if successful_analyses > 1:
            cross_file_analysis = self._perform_cross_file_analysis(results)
        
        batch_results = {
            'batch_summary': {
                'total_files': len(file_paths),
                'successful_analyses': successful_analyses,
                'failed_analyses': len(errors),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'file_results': results,
            'errors': errors,
            'cross_file_analysis': cross_file_analysis,
            'aggregated_statistics': self._generate_aggregated_statistics(results)
        }
        
        self.logger.info(f"Batch analysis completed: {successful_analyses}/{len(file_paths)} files successful")
        return batch_results
    
    def get_analysis_recommendations(self, file_path: str) -> Dict[str, Any]:
        """
        Get analysis-based recommendations for test generation.
        
        Args:
            file_path: Path to analyzed XSLT file
            
        Returns:
            Dictionary containing recommendations
        """
        file_record = self.db.get_file_by_path(file_path)
        if not file_record or file_record['analysis_status'] != 'completed':
            return {'error': f"No completed analysis found for {file_path}"}
        
        try:
            # Load analysis results
            templates = self.db.get_templates_by_file(file_record['id'])
            
            # Generate recommendations
            recommendations = {
                'test_prioritization': self._recommend_test_prioritization(templates),
                'test_data_generation': self._recommend_test_data_generation(file_record['id']),
                'coverage_strategy': self._recommend_coverage_strategy(file_record['id']),
                'risk_assessment': self._assess_transformation_risks(templates),
                'optimization_suggestions': self._suggest_optimizations(templates)
            }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations for {file_path}: {e}")
            return {'error': f"Failed to generate recommendations: {str(e)}"}
    
    def _load_existing_analysis(self, file_id: int) -> Dict[str, Any]:
        """Load existing analysis results from database."""
        # This would load stored analysis results
        # For now, return a simplified version
        templates = self.db.get_templates_by_file(file_id)
        
        return {
            'analysis_id': f"existing_{file_id}",
            'file_id': file_id,
            'templates_count': len(templates),
            'status': 'loaded_from_cache',
            'note': 'Full analysis results would be loaded from database storage'
        }
    
    def _handle_analysis_error(self, file_record: Optional[Dict], error_message: str) -> None:
        """Handle analysis errors by updating database status."""
        if file_record:
            self.db.update_file_analysis_status(
                file_record['id'], 'error', error_message
            )
        self.logger.error(f"Analysis error: {error_message}")
    
    def _store_analysis_results(self, file_id: int, parse_results: Dict[str, Any],
                               semantic_results: Dict[str, Any], 
                               execution_results: Dict[str, Any]) -> str:
        """Store complete analysis results in database."""
        analysis_id = f"analysis_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store templates
        for template_name, template in parse_results['templates'].items():
            template_data = {
                'name': template.name,
                'match_pattern': template.match_pattern,
                'mode': template.mode,
                'priority': template.priority,
                'line_start': template.line_start,
                'line_end': template.line_end,
                'template_content': template.template_content,
                'calls_templates': template.calls_templates,
                'called_by_templates': template.called_by_templates,
                'uses_variables': template.uses_variables,
                'defines_variables': template.defines_variables,
                'xpath_expressions': template.xpath_expressions,
                'conditional_logic': template.conditional_logic,
                'output_elements': template.output_elements,
                'template_hash': template.template_hash,
                'complexity_score': template.complexity_score,
                'is_recursive': template.is_recursive
            }
            
            self.db.insert_xslt_template(file_id, template_data)
        
        # Store variables
        for var_name, variable in parse_results['variables'].items():
            variable_data = {
                'name': variable.name,
                'variable_type': variable.variable_type,
                'select_expression': variable.select_expression,
                'content': variable.content,
                'scope': variable.scope,
                'line_number': variable.line_number,
                'used_by_templates': variable.used_by_templates
            }
            
            self.db.insert_xslt_variable(file_id, variable_data)
        
        # Store execution paths (simplified - would need dedicated tables)
        for path in execution_results.get('execution_paths', []):
            path_data = {
                'path_id': path.path_id,
                'nodes': path.nodes,
                'conditions': path.conditions,
                'variables_used': list(path.variables_used),
                'templates_involved': list(path.templates_involved),
                'output_elements': list(path.output_elements),
                'path_probability': path.path_probability,
                'complexity_score': path.complexity_score,
                'test_data_requirements': path.test_data_requirements
            }
            
            self.db.insert_execution_path(file_id, path_data)
        
        return analysis_id
    
    def _generate_complete_summary(self, parse_results: Dict[str, Any],
                                  semantic_results: Dict[str, Any],
                                  execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete analysis summary."""
        return {
            'parsing_summary': parse_results.get('analysis_summary', {}),
            'semantic_summary': semantic_results.get('analysis_summary', {}),
            'execution_summary': execution_results.get('path_statistics', {}),
            'overall_complexity': self._calculate_overall_complexity(parse_results, semantic_results),
            'test_generation_priority': self._determine_test_priority(semantic_results, execution_results),
            'key_findings': self._extract_key_findings(semantic_results, execution_results)
        }
    
    def _perform_cross_file_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis across multiple files."""
        # Aggregate templates across files
        all_templates = {}
        all_patterns = []
        template_calls = {}
        
        for file_path, result in results.items():
            if 'template_analysis' in result:
                templates = result['template_analysis'].get('templates', {})
                all_templates[file_path] = templates
                
                # Collect template calls for cross-file analysis
                for template_name, template in templates.items():
                    for called_template in template.calls_templates:
                        if called_template not in template_calls:
                            template_calls[called_template] = []
                        template_calls[called_template].append({
                            'calling_file': file_path,
                            'calling_template': template_name
                        })
            
            if 'semantic_analysis' in result:
                patterns = result['semantic_analysis'].get('semantic_patterns', [])
                all_patterns.extend(patterns)
        
        # Identify cross-file dependencies
        cross_file_deps = []
        for called_template, callers in template_calls.items():
            if len(callers) > 1:  # Called from multiple places
                cross_file_deps.append({
                    'template': called_template,
                    'callers': callers,
                    'complexity': 'high' if len(callers) > 3 else 'medium'
                })
        
        return {
            'total_templates': sum(len(templates) for templates in all_templates.values()),
            'cross_file_dependencies': cross_file_deps,
            'common_patterns': self._identify_common_patterns(all_patterns),
            'integration_test_requirements': self._generate_integration_requirements(cross_file_deps)
        }
    
    def _generate_aggregated_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate aggregated statistics across all analyzed files."""
        total_templates = 0
        total_complexity = 0
        total_patterns = 0
        total_paths = 0
        
        for result in results.values():
            if 'template_analysis' in result:
                summary = result['template_analysis'].get('analysis_summary', {})
                total_templates += summary.get('total_templates', 0)
                
            if 'semantic_analysis' in result:
                summary = result['semantic_analysis'].get('analysis_summary', {})
                total_complexity += summary.get('transformation_complexity', 0)
                total_patterns += summary.get('total_patterns', 0)
                
            if 'execution_analysis' in result:
                stats = result['execution_analysis'].get('path_statistics', {})
                total_paths += stats.get('total_paths', 0)
        
        return {
            'total_templates': total_templates,
            'total_complexity_score': total_complexity,
            'total_semantic_patterns': total_patterns,
            'total_execution_paths': total_paths,
            'average_complexity_per_file': total_complexity / len(results) if results else 0,
            'analysis_completion_rate': len(results) / (len(results) + len(results)) * 100  # Simplified
        }
    
    def _recommend_test_prioritization(self, templates: List[Dict]) -> List[Dict[str, Any]]:
        """Recommend test prioritization based on analysis."""
        priorities = []
        
        for template in templates:
            priority_score = 0
            reasons = []
            
            complexity = template.get('complexity_score', 0)
            if complexity > 10:
                priority_score += 3
                reasons.append("High complexity")
            
            if template.get('is_recursive', False):
                priority_score += 3
                reasons.append("Recursive template")
            
            conditional_logic = template.get('conditional_logic', '[]')
            try:
                conditions = json.loads(conditional_logic) if isinstance(conditional_logic, str) else conditional_logic
                if len(conditions) > 2:
                    priority_score += 2
                    reasons.append("Complex conditional logic")
            except:
                pass
            
            if priority_score >= 5:
                priorities.append({
                    'template_name': template.get('name', 'unnamed'),
                    'priority': 'high' if priority_score >= 7 else 'medium',
                    'priority_score': priority_score,
                    'reasons': reasons
                })
        
        return sorted(priorities, key=lambda x: x['priority_score'], reverse=True)
    
    def _recommend_test_data_generation(self, file_id: int) -> Dict[str, Any]:
        """Recommend test data generation strategies."""
        # This would analyze execution paths and variable usage
        # to recommend specific test data generation approaches
        return {
            'data_generation_strategy': 'comprehensive',
            'required_data_types': ['xml_input', 'parameters', 'context_variables'],
            'complexity_factors': ['conditional_branches', 'recursive_processing'],
            'recommended_tools': ['xml_generator', 'parameter_matrix', 'edge_case_generator']
        }
    
    def _recommend_coverage_strategy(self, file_id: int) -> Dict[str, Any]:
        """Recommend test coverage strategy."""
        return {
            'coverage_targets': {
                'template_coverage': 100,
                'branch_coverage': 85,
                'path_coverage': 70
            },
            'coverage_priorities': [
                'Critical execution paths',
                'Error handling paths',
                'Conditional logic branches',
                'Recursive template calls'
            ],
            'coverage_tools': ['path_tracer', 'branch_analyzer', 'template_monitor']
        }
    
    def _assess_transformation_risks(self, templates: List[Dict]) -> List[Dict[str, Any]]:
        """Assess risks in the transformation."""
        risks = []
        
        # High complexity risk
        high_complexity = [t for t in templates if t.get('complexity_score', 0) > 15]
        if high_complexity:
            risks.append({
                'risk_type': 'high_complexity',
                'severity': 'high',
                'description': f"{len(high_complexity)} templates have very high complexity",
                'affected_templates': [t.get('name', 'unnamed') for t in high_complexity],
                'mitigation': 'Comprehensive testing with multiple scenarios'
            })
        
        # Recursion risk
        recursive = [t for t in templates if t.get('is_recursive', False)]
        if recursive:
            risks.append({
                'risk_type': 'recursion',
                'severity': 'medium',
                'description': f"{len(recursive)} recursive templates detected",
                'affected_templates': [t.get('name', 'unnamed') for t in recursive],
                'mitigation': 'Test recursion limits and termination conditions'
            })
        
        return risks
    
    def _suggest_optimizations(self, templates: List[Dict]) -> List[Dict[str, Any]]:
        """Suggest potential optimizations."""
        suggestions = []
        
        # Check for potentially unused templates
        called_templates = set()
        for template in templates:
            calls = template.get('calls_templates', '[]')
            try:
                if isinstance(calls, str):
                    calls = json.loads(calls)
                called_templates.update(calls)
            except:
                pass
        
        unused = []
        for template in templates:
            name = template.get('name')
            if name and name not in called_templates and not template.get('match_pattern'):
                unused.append(name)
        
        if unused:
            suggestions.append({
                'optimization_type': 'unused_templates',
                'description': f"Consider removing {len(unused)} potentially unused templates",
                'affected_templates': unused,
                'impact': 'code_cleanup'
            })
        
        return suggestions
    
    def _calculate_overall_complexity(self, parse_results: Dict, semantic_results: Dict) -> int:
        """Calculate overall transformation complexity."""
        base_complexity = parse_results.get('analysis_summary', {}).get('avg_complexity', 0)
        semantic_complexity = len(semantic_results.get('semantic_patterns', []))
        
        return int(base_complexity * 10 + semantic_complexity * 5)
    
    def _determine_test_priority(self, semantic_results: Dict, execution_results: Dict) -> str:
        """Determine overall test generation priority."""
        patterns = semantic_results.get('semantic_patterns', [])
        paths = execution_results.get('execution_paths', [])
        
        high_confidence_patterns = len([p for p in patterns if p.confidence_score > 0.8])
        complex_paths = len([p for p in paths if p.complexity_score > 10])
        
        if high_confidence_patterns > 3 or complex_paths > 5:
            return 'high'
        elif high_confidence_patterns > 1 or complex_paths > 2:
            return 'medium'
        else:
            return 'low'
    
    def _extract_key_findings(self, semantic_results: Dict, execution_results: Dict) -> List[str]:
        """Extract key findings from analysis."""
        findings = []
        
        patterns = semantic_results.get('semantic_patterns', [])
        if patterns:
            findings.append(f"Identified {len(patterns)} semantic patterns")
        
        paths = execution_results.get('execution_paths', [])
        if paths:
            max_complexity = max((p.complexity_score for p in paths), default=0)
            findings.append(f"Maximum execution path complexity: {max_complexity}")
        
        hotspots = semantic_results.get('transformation_hotspots', [])
        if hotspots:
            findings.append(f"Found {len(hotspots)} transformation hotspots")
        
        return findings
    
    def _identify_common_patterns(self, all_patterns: List) -> List[Dict[str, Any]]:
        """Identify common patterns across files."""
        pattern_counts = {}
        
        for pattern in all_patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in pattern_counts:
                pattern_counts[pattern_type] = 0
            pattern_counts[pattern_type] += 1
        
        common = []
        for pattern_type, count in pattern_counts.items():
            if count > 1:
                common.append({
                    'pattern_type': pattern_type,
                    'occurrences': count,
                    'commonality': 'high' if count > 3 else 'medium'
                })
        
        return common
    
    def _generate_integration_requirements(self, cross_file_deps: List) -> List[Dict[str, Any]]:
        """Generate integration test requirements."""
        requirements = []
        
        for dep in cross_file_deps:
            requirements.append({
                'requirement_type': 'cross_file_integration',
                'description': f"Test integration for template {dep['template']}",
                'involved_files': [caller['calling_file'] for caller in dep['callers']],
                'complexity': dep['complexity'],
                'test_scenarios': [
                    'Test template call from each file',
                    'Test parameter passing consistency',
                    'Test error propagation'
                ]
            })
        
        return requirements