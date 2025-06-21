"""Execution Path Analysis for XSLT transformations."""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from ..core.base import LoggerMixin
from .template_parser import XSLTTemplate, XSLTVariable
from .semantic_analyzer import SemanticPattern


class ExecutionNodeType(Enum):
    """Types of execution nodes."""
    TEMPLATE_START = "template_start"
    TEMPLATE_END = "template_end"
    CONDITION = "condition"
    LOOP = "loop"
    TEMPLATE_CALL = "template_call"
    VARIABLE_ASSIGNMENT = "variable_assignment"
    OUTPUT_GENERATION = "output_generation"


@dataclass
class ExecutionNode:
    """Represents a node in the execution path graph."""
    node_id: str
    node_type: ExecutionNodeType
    template_name: str
    line_number: int
    description: str
    
    # Execution characteristics
    condition: Optional[str] = None
    variables_read: Set[str] = field(default_factory=set)
    variables_written: Set[str] = field(default_factory=set)
    output_elements: Set[str] = field(default_factory=set)
    
    # Graph connections
    predecessors: Set[str] = field(default_factory=set)
    successors: Set[str] = field(default_factory=set)
    
    # Analysis metadata
    execution_probability: float = 1.0
    complexity_weight: int = 1


@dataclass 
class ExecutionPath:
    """Represents a complete execution path through the XSLT."""
    path_id: str
    nodes: List[str]
    conditions: List[str]
    variables_used: Set[str]
    templates_involved: Set[str]
    output_elements: Set[str]
    path_probability: float
    complexity_score: int
    test_data_requirements: List[Dict[str, Any]] = field(default_factory=list)


class ExecutionPathAnalyzer(LoggerMixin):
    """Analyzes execution paths through XSLT transformations."""
    
    def __init__(self):
        super().__init__()
        self.templates: Dict[str, XSLTTemplate] = {}
        self.variables: Dict[str, XSLTVariable] = {}
        self.execution_graph: Dict[str, ExecutionNode] = {}
        self.execution_paths: List[ExecutionPath] = []
        self.entry_points: List[str] = []
        self.file_path: Optional[str] = None
    
    def analyze_execution_paths(self, templates: Dict[str, XSLTTemplate], 
                               variables: Dict[str, XSLTVariable],
                               semantic_patterns: List[SemanticPattern],
                               file_path: str) -> Dict[str, Any]:
        """
        Analyze execution paths through XSLT transformation.
        
        Args:
            templates: Parsed XSLT templates
            variables: Parsed XSLT variables
            semantic_patterns: Identified semantic patterns
            file_path: Path to XSLT file
            
        Returns:
            Dictionary containing execution path analysis
        """
        self.templates = templates
        self.variables = variables
        self.file_path = file_path
        self.execution_graph.clear()
        self.execution_paths.clear()
        self.entry_points.clear()
        
        try:
            # Build execution graph
            self._build_execution_graph()
            
            # Identify entry points
            self._identify_entry_points()
            
            # Discover execution paths
            self._discover_execution_paths()
            
            # Analyze path characteristics
            self._analyze_path_characteristics()
            
            # Generate test data requirements
            self._generate_test_data_requirements()
            
            # Create coverage analysis
            coverage_analysis = self._analyze_coverage_requirements()
            
            self.logger.info(f"Execution path analysis complete for {file_path}: "
                           f"{len(self.execution_paths)} paths discovered")
            
            return {
                'execution_graph': self.execution_graph,
                'execution_paths': self.execution_paths,
                'entry_points': self.entry_points,
                'coverage_analysis': coverage_analysis,
                'path_statistics': self._generate_path_statistics(),
                'test_scenarios': self._generate_test_scenarios()
            }
            
        except Exception as e:
            self.logger.error(f"Error in execution path analysis: {e}")
            return {'error': str(e)}
    
    def _build_execution_graph(self) -> None:
        """Build execution graph from templates."""
        node_counter = 0
        
        for template_name, template in self.templates.items():
            # Template start node
            start_node_id = f"start_{template_name}_{node_counter}"
            node_counter += 1
            
            start_node = ExecutionNode(
                node_id=start_node_id,
                node_type=ExecutionNodeType.TEMPLATE_START,
                template_name=template_name,
                line_number=template.line_start,
                description=f"Start of template {template_name}"
            )
            self.execution_graph[start_node_id] = start_node
            
            # Process template content
            current_node_id = start_node_id
            
            # Variable assignments
            for var_name in template.defines_variables:
                var_node_id = f"var_{template_name}_{var_name}_{node_counter}"
                node_counter += 1
                
                var_node = ExecutionNode(
                    node_id=var_node_id,
                    node_type=ExecutionNodeType.VARIABLE_ASSIGNMENT,
                    template_name=template_name,
                    line_number=template.line_start,
                    description=f"Assign variable {var_name}",
                    variables_written={var_name}
                )
                
                # Connect to previous node
                var_node.predecessors.add(current_node_id)
                self.execution_graph[current_node_id].successors.add(var_node_id)
                
                self.execution_graph[var_node_id] = var_node
                current_node_id = var_node_id
            
            # Conditional logic
            for i, condition_info in enumerate(template.conditional_logic):
                cond_node_id = f"cond_{template_name}_{i}_{node_counter}"
                node_counter += 1
                
                condition = condition_info.get('condition', '')
                cond_node = ExecutionNode(
                    node_id=cond_node_id,
                    node_type=ExecutionNodeType.CONDITION,
                    template_name=template_name,
                    line_number=condition_info.get('line', template.line_start),
                    description=f"Condition: {condition}",
                    condition=condition,
                    variables_read=self._extract_variables_from_expression(condition)
                )
                
                # Connect to previous node
                cond_node.predecessors.add(current_node_id)
                self.execution_graph[current_node_id].successors.add(cond_node_id)
                
                self.execution_graph[cond_node_id] = cond_node
                current_node_id = cond_node_id
            
            # Template calls
            for called_template in template.calls_templates:
                call_node_id = f"call_{template_name}_{called_template}_{node_counter}"
                node_counter += 1
                
                call_node = ExecutionNode(
                    node_id=call_node_id,
                    node_type=ExecutionNodeType.TEMPLATE_CALL,
                    template_name=template_name,
                    line_number=template.line_start,
                    description=f"Call template {called_template}"
                )
                
                # Connect to previous node
                call_node.predecessors.add(current_node_id)
                self.execution_graph[current_node_id].successors.add(call_node_id)
                
                self.execution_graph[call_node_id] = call_node
                current_node_id = call_node_id
            
            # Output generation
            if template.output_elements:
                output_node_id = f"output_{template_name}_{node_counter}"
                node_counter += 1
                
                output_node = ExecutionNode(
                    node_id=output_node_id,
                    node_type=ExecutionNodeType.OUTPUT_GENERATION,
                    template_name=template_name,
                    line_number=template.line_end,
                    description=f"Generate output elements",
                    output_elements=set(template.output_elements)
                )
                
                # Connect to previous node
                output_node.predecessors.add(current_node_id)
                self.execution_graph[current_node_id].successors.add(output_node_id)
                
                self.execution_graph[output_node_id] = output_node
                current_node_id = output_node_id
            
            # Template end node
            end_node_id = f"end_{template_name}_{node_counter}"
            node_counter += 1
            
            end_node = ExecutionNode(
                node_id=end_node_id,
                node_type=ExecutionNodeType.TEMPLATE_END,
                template_name=template_name,
                line_number=template.line_end,
                description=f"End of template {template_name}"
            )
            
            # Connect to previous node
            end_node.predecessors.add(current_node_id)
            self.execution_graph[current_node_id].successors.add(end_node_id)
            
            self.execution_graph[end_node_id] = end_node
    
    def _identify_entry_points(self) -> None:
        """Identify entry points for execution path analysis."""
        # Match templates are natural entry points
        for template_name, template in self.templates.items():
            if template.match_pattern:
                self.entry_points.append(template_name)
        
        # If no match templates, look for root template or main template
        if not self.entry_points:
            for template_name in self.templates:
                if template_name.lower() in ['root', 'main', 'transform']:
                    self.entry_points.append(template_name)
        
        # If still no entry points, use templates not called by others
        if not self.entry_points:
            called_templates = set()
            for template in self.templates.values():
                called_templates.update(template.calls_templates)
            
            for template_name in self.templates:
                if template_name not in called_templates:
                    self.entry_points.append(template_name)
        
        self.logger.info(f"Identified {len(self.entry_points)} entry points: {self.entry_points}")
    
    def _discover_execution_paths(self) -> None:
        """Discover all possible execution paths."""
        path_counter = 0
        
        for entry_point in self.entry_points:
            # Find start nodes for this template
            start_nodes = [
                node_id for node_id, node in self.execution_graph.items()
                if (node.template_name == entry_point and 
                    node.node_type == ExecutionNodeType.TEMPLATE_START)
            ]
            
            for start_node_id in start_nodes:
                paths = self._explore_paths_from_node(start_node_id, set(), [])
                
                for path_nodes in paths:
                    path = ExecutionPath(
                        path_id=f"path_{path_counter}",
                        nodes=path_nodes,
                        conditions=[],
                        variables_used=set(),
                        templates_involved=set(),
                        output_elements=set(),
                        path_probability=1.0,
                        complexity_score=0
                    )
                    
                    # Populate path details
                    self._populate_path_details(path)
                    
                    self.execution_paths.append(path)
                    path_counter += 1
    
    def _explore_paths_from_node(self, node_id: str, visited: Set[str], 
                                current_path: List[str]) -> List[List[str]]:
        """Recursively explore paths from a given node."""
        if node_id in visited:
            return [current_path + [node_id]]  # Cycle detected, end path
        
        visited_copy = visited.copy()
        visited_copy.add(node_id)
        path_copy = current_path + [node_id]
        
        node = self.execution_graph.get(node_id)
        if not node or not node.successors:
            return [path_copy]  # End of path
        
        all_paths = []
        for successor_id in node.successors:
            successor_paths = self._explore_paths_from_node(
                successor_id, visited_copy, path_copy
            )
            all_paths.extend(successor_paths)
        
        return all_paths
    
    def _populate_path_details(self, path: ExecutionPath) -> None:
        """Populate details for an execution path."""
        for node_id in path.nodes:
            node = self.execution_graph.get(node_id)
            if not node:
                continue
            
            # Collect conditions
            if node.condition:
                path.conditions.append(node.condition)
            
            # Collect variables
            path.variables_used.update(node.variables_read)
            path.variables_used.update(node.variables_written)
            
            # Collect templates
            path.templates_involved.add(node.template_name)
            
            # Collect output elements
            path.output_elements.update(node.output_elements)
            
            # Add to complexity score
            path.complexity_score += node.complexity_weight
        
        # Calculate path probability (simplified)
        path.path_probability = 1.0 / (len(path.conditions) + 1)
    
    def _analyze_path_characteristics(self) -> None:
        """Analyze characteristics of discovered paths."""
        for path in self.execution_paths:
            # Identify critical paths (high complexity or many conditions)
            if path.complexity_score > 10 or len(path.conditions) > 3:
                path.test_data_requirements.append({
                    'requirement_type': 'critical_path',
                    'description': 'High complexity execution path',
                    'priority': 'high'
                })
            
            # Identify paths with many variable dependencies
            if len(path.variables_used) > 5:
                path.test_data_requirements.append({
                    'requirement_type': 'variable_heavy',
                    'description': 'Path uses many variables',
                    'priority': 'medium'
                })
            
            # Identify paths with complex conditions
            complex_conditions = [c for c in path.conditions if len(c) > 30]
            if complex_conditions:
                path.test_data_requirements.append({
                    'requirement_type': 'complex_conditions',
                    'description': 'Path has complex conditional logic',
                    'priority': 'high'
                })
    
    def _generate_test_data_requirements(self) -> None:
        """Generate test data requirements for each path."""
        for path in self.execution_paths:
            # Basic input data requirements
            if path.variables_used:
                path.test_data_requirements.append({
                    'requirement_type': 'input_variables',
                    'variables': list(path.variables_used),
                    'description': 'Input data for path variables',
                    'priority': 'high'
                })
            
            # Condition-specific requirements
            for condition in path.conditions:
                path.test_data_requirements.append({
                    'requirement_type': 'condition_data',
                    'condition': condition,
                    'description': f'Data to satisfy condition: {condition}',
                    'priority': 'high'
                })
            
            # Output verification requirements
            if path.output_elements:
                path.test_data_requirements.append({
                    'requirement_type': 'output_verification',
                    'output_elements': list(path.output_elements),
                    'description': 'Expected output elements verification',
                    'priority': 'medium'
                })
    
    def _analyze_coverage_requirements(self) -> Dict[str, Any]:
        """Analyze test coverage requirements."""
        total_nodes = len(self.execution_graph)
        total_templates = len(self.templates)
        
        covered_nodes = set()
        covered_templates = set()
        
        for path in self.execution_paths:
            covered_nodes.update(path.nodes)
            covered_templates.update(path.templates_involved)
        
        node_coverage = len(covered_nodes) / total_nodes if total_nodes > 0 else 0
        template_coverage = len(covered_templates) / total_templates if total_templates > 0 else 0
        
        # Identify uncovered elements
        uncovered_nodes = set(self.execution_graph.keys()) - covered_nodes
        uncovered_templates = set(self.templates.keys()) - covered_templates
        
        return {
            'node_coverage_percentage': round(node_coverage * 100, 2),
            'template_coverage_percentage': round(template_coverage * 100, 2),
            'total_execution_nodes': total_nodes,
            'covered_nodes': len(covered_nodes),
            'uncovered_nodes': len(uncovered_nodes),
            'uncovered_node_list': list(uncovered_nodes),
            'uncovered_templates': list(uncovered_templates),
            'coverage_gaps': self._identify_coverage_gaps()
        }
    
    def _generate_path_statistics(self) -> Dict[str, Any]:
        """Generate statistics about execution paths."""
        if not self.execution_paths:
            return {}
        
        complexities = [path.complexity_score for path in self.execution_paths]
        path_lengths = [len(path.nodes) for path in self.execution_paths]
        condition_counts = [len(path.conditions) for path in self.execution_paths]
        
        return {
            'total_paths': len(self.execution_paths),
            'avg_path_complexity': sum(complexities) / len(complexities),
            'max_path_complexity': max(complexities),
            'avg_path_length': sum(path_lengths) / len(path_lengths),
            'max_path_length': max(path_lengths),
            'avg_conditions_per_path': sum(condition_counts) / len(condition_counts),
            'paths_with_conditions': len([p for p in self.execution_paths if p.conditions]),
            'most_complex_path': max(self.execution_paths, key=lambda p: p.complexity_score).path_id
        }
    
    def _generate_test_scenarios(self) -> List[Dict[str, Any]]:
        """Generate test scenarios based on execution paths."""
        scenarios = []
        
        # Group paths by characteristics
        critical_paths = [p for p in self.execution_paths if p.complexity_score > 10]
        conditional_paths = [p for p in self.execution_paths if len(p.conditions) > 0]
        simple_paths = [p for p in self.execution_paths if p.complexity_score <= 5]
        
        # Critical path scenarios
        for path in critical_paths[:5]:  # Limit to top 5
            scenarios.append({
                'scenario_type': 'critical_path',
                'path_id': path.path_id,
                'description': f'Test critical execution path with complexity {path.complexity_score}',
                'templates_involved': list(path.templates_involved),
                'test_requirements': path.test_data_requirements,
                'priority': 'high'
            })
        
        # Conditional logic scenarios
        for path in conditional_paths[:3]:  # Limit to top 3
            scenarios.append({
                'scenario_type': 'conditional_logic',
                'path_id': path.path_id,
                'description': f'Test conditional logic path with {len(path.conditions)} conditions',
                'conditions': path.conditions,
                'test_requirements': path.test_data_requirements,
                'priority': 'high'
            })
        
        # Happy path scenarios
        for path in simple_paths[:2]:  # Limit to 2
            scenarios.append({
                'scenario_type': 'happy_path',
                'path_id': path.path_id,
                'description': 'Test simple/happy path execution',
                'templates_involved': list(path.templates_involved),
                'test_requirements': path.test_data_requirements,
                'priority': 'medium'
            })
        
        return scenarios
    
    def _extract_variables_from_expression(self, expression: str) -> Set[str]:
        """Extract variable references from XPath/XSLT expression."""
        import re
        variables = set()
        
        # Find $variable references
        var_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_-]*)'
        matches = re.findall(var_pattern, expression)
        variables.update(matches)
        
        return variables
    
    def _identify_coverage_gaps(self) -> List[Dict[str, Any]]:
        """Identify test coverage gaps."""
        gaps = []
        
        # Templates never executed
        executed_templates = set()
        for path in self.execution_paths:
            executed_templates.update(path.templates_involved)
        
        unexecuted = set(self.templates.keys()) - executed_templates
        if unexecuted:
            gaps.append({
                'gap_type': 'unexecuted_templates',
                'description': 'Templates never executed in any path',
                'affected_elements': list(unexecuted),
                'impact': 'high'
            })
        
        # Conditions never tested
        all_conditions = set()
        for template in self.templates.values():
            for cond_info in template.conditional_logic:
                condition = cond_info.get('condition')
                if condition:
                    all_conditions.add(condition)
        
        tested_conditions = set()
        for path in self.execution_paths:
            tested_conditions.update(path.conditions)
        
        untested_conditions = all_conditions - tested_conditions
        if untested_conditions:
            gaps.append({
                'gap_type': 'untested_conditions',
                'description': 'Conditional logic never tested',
                'affected_elements': list(untested_conditions),
                'impact': 'medium'
            })
        
        return gaps