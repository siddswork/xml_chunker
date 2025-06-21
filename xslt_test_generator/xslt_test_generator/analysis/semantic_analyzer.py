"""Semantic Analysis Engine for XSLT transformations."""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re
from enum import Enum

from ..core.base import LoggerMixin
from .template_parser import XSLTTemplate, XSLTVariable


class DataFlowType(Enum):
    """Types of data flow in XSLT."""
    VARIABLE_ASSIGNMENT = "variable_assignment"
    PARAMETER_PASSING = "parameter_passing"
    TEMPLATE_CALL = "template_call"
    XPATH_SELECTION = "xpath_selection"
    CONDITIONAL_BRANCH = "conditional_branch"


@dataclass
class DataFlowNode:
    """Represents a node in the data flow graph."""
    node_id: str
    node_type: DataFlowType
    template_name: str
    line_number: int
    xpath_expression: Optional[str] = None
    variable_name: Optional[str] = None
    condition: Optional[str] = None
    predecessors: Set[str] = field(default_factory=set)
    successors: Set[str] = field(default_factory=set)


@dataclass
class SemanticPattern:
    """Represents a semantic pattern found in XSLT."""
    pattern_type: str
    description: str
    templates_involved: List[str]
    confidence_score: float
    test_implications: List[str] = field(default_factory=list)


class SemanticAnalyzer(LoggerMixin):
    """Analyzes semantic patterns and data flow in XSLT transformations."""
    
    def __init__(self):
        super().__init__()
        self.templates: Dict[str, XSLTTemplate] = {}
        self.variables: Dict[str, XSLTVariable] = {}
        self.data_flow_graph: Dict[str, DataFlowNode] = {}
        self.semantic_patterns: List[SemanticPattern] = []
        self.file_path: Optional[str] = None
    
    def analyze_semantics(self, templates: Dict[str, XSLTTemplate], 
                         variables: Dict[str, XSLTVariable],
                         file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis.
        
        Args:
            templates: Parsed XSLT templates
            variables: Parsed XSLT variables
            file_path: Path to XSLT file
            
        Returns:
            Dictionary containing semantic analysis results
        """
        self.templates = templates
        self.variables = variables
        self.file_path = file_path
        self.data_flow_graph.clear()
        self.semantic_patterns.clear()
        
        try:
            # Build data flow graph
            self._build_data_flow_graph()
            
            # Identify semantic patterns
            self._identify_semantic_patterns()
            
            # Analyze variable scoping and lifecycle
            variable_analysis = self._analyze_variable_scoping()
            
            # Analyze template interaction patterns
            interaction_analysis = self._analyze_template_interactions()
            
            # Identify potential transformation hotspots
            hotspots = self._identify_transformation_hotspots()
            
            # Generate test implications
            test_implications = self._generate_test_implications()
            
            self.logger.info(f"Semantic analysis complete for {file_path}: "
                           f"{len(self.semantic_patterns)} patterns identified")
            
            return {
                'data_flow_graph': self.data_flow_graph,
                'semantic_patterns': self.semantic_patterns,
                'variable_analysis': variable_analysis,
                'interaction_analysis': interaction_analysis,
                'transformation_hotspots': hotspots,
                'test_implications': test_implications,
                'analysis_summary': self._generate_semantic_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {e}")
            return {'error': str(e)}
    
    def _build_data_flow_graph(self) -> None:
        """Build data flow graph from templates and variables."""
        node_counter = 0
        
        for template_name, template in self.templates.items():
            # Create nodes for variable assignments
            for var_name in template.defines_variables:
                node_id = f"var_assign_{node_counter}"
                node_counter += 1
                
                node = DataFlowNode(
                    node_id=node_id,
                    node_type=DataFlowType.VARIABLE_ASSIGNMENT,
                    template_name=template_name,
                    line_number=template.line_start,
                    variable_name=var_name
                )
                self.data_flow_graph[node_id] = node
            
            # Create nodes for template calls
            for call in template.calls_templates:
                node_id = f"template_call_{node_counter}"
                node_counter += 1
                
                node = DataFlowNode(
                    node_id=node_id,
                    node_type=DataFlowType.TEMPLATE_CALL,
                    template_name=template_name,
                    line_number=template.line_start
                )
                self.data_flow_graph[node_id] = node
            
            # Create nodes for conditional logic
            for condition_info in template.conditional_logic:
                node_id = f"condition_{node_counter}"
                node_counter += 1
                
                node = DataFlowNode(
                    node_id=node_id,
                    node_type=DataFlowType.CONDITIONAL_BRANCH,
                    template_name=template_name,
                    line_number=condition_info.get('line', template.line_start),
                    condition=condition_info.get('condition')
                )
                self.data_flow_graph[node_id] = node
            
            # Create nodes for XPath selections
            for xpath in template.xpath_expressions:
                node_id = f"xpath_{node_counter}"
                node_counter += 1
                
                node = DataFlowNode(
                    node_id=node_id,
                    node_type=DataFlowType.XPATH_SELECTION,
                    template_name=template_name,
                    line_number=template.line_start,
                    xpath_expression=xpath
                )
                self.data_flow_graph[node_id] = node
        
        # Build relationships between nodes
        self._build_data_flow_relationships()
    
    def _build_data_flow_relationships(self) -> None:
        """Build relationships between data flow nodes."""
        # This is a simplified implementation
        # In practice, would need more sophisticated analysis
        for node_id, node in self.data_flow_graph.items():
            # Connect variable assignments to their usage
            if node.node_type == DataFlowType.VARIABLE_ASSIGNMENT:
                var_name = node.variable_name
                template = self.templates.get(node.template_name)
                
                if template and var_name in template.uses_variables:
                    # Find subsequent nodes that use this variable
                    for other_id, other_node in self.data_flow_graph.items():
                        if (other_id != node_id and 
                            other_node.template_name == node.template_name):
                            node.successors.add(other_id)
                            other_node.predecessors.add(node_id)
    
    def _identify_semantic_patterns(self) -> None:
        """Identify common semantic patterns in XSLT."""
        # Pattern 1: Data Transformation Pipeline
        self._detect_transformation_pipeline()
        
        # Pattern 2: Conditional Processing
        self._detect_conditional_processing()
        
        # Pattern 3: Recursive Processing
        self._detect_recursive_processing()
        
        # Pattern 4: Data Aggregation
        self._detect_data_aggregation()
        
        # Pattern 5: Template Orchestration
        self._detect_template_orchestration()
        
        # Pattern 6: Error Handling Patterns
        self._detect_error_handling()
    
    def _detect_transformation_pipeline(self) -> None:
        """Detect data transformation pipeline patterns."""
        # Look for sequences of templates that transform data step by step
        pipeline_templates = []
        
        for template_name, template in self.templates.items():
            if (len(template.calls_templates) > 0 and 
                len(template.output_elements) > 0):
                pipeline_templates.append(template_name)
        
        if len(pipeline_templates) >= 2:
            pattern = SemanticPattern(
                pattern_type="transformation_pipeline",
                description=f"Data transformation pipeline with {len(pipeline_templates)} stages",
                templates_involved=pipeline_templates,
                confidence_score=0.8,
                test_implications=[
                    "Test each pipeline stage independently",
                    "Test complete pipeline with various data inputs",
                    "Verify data integrity through pipeline stages"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _detect_conditional_processing(self) -> None:
        """Detect conditional processing patterns."""
        conditional_templates = []
        
        for template_name, template in self.templates.items():
            if len(template.conditional_logic) > 0:
                conditional_templates.append(template_name)
        
        if conditional_templates:
            pattern = SemanticPattern(
                pattern_type="conditional_processing",
                description=f"Conditional processing in {len(conditional_templates)} templates",
                templates_involved=conditional_templates,
                confidence_score=0.9,
                test_implications=[
                    "Test all conditional branches",
                    "Test edge cases for conditional expressions",
                    "Verify default/fallback behavior"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _detect_recursive_processing(self) -> None:
        """Detect recursive processing patterns."""
        recursive_templates = [
            name for name, template in self.templates.items() 
            if template.is_recursive
        ]
        
        if recursive_templates:
            pattern = SemanticPattern(
                pattern_type="recursive_processing",
                description=f"Recursive processing in templates: {', '.join(recursive_templates)}",
                templates_involved=recursive_templates,
                confidence_score=1.0,
                test_implications=[
                    "Test recursion base cases",
                    "Test recursion termination conditions",
                    "Test recursive depth limits",
                    "Verify recursive data structure handling"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _detect_data_aggregation(self) -> None:
        """Detect data aggregation patterns."""
        aggregation_keywords = ['sum', 'count', 'avg', 'max', 'min', 'distinct-values']
        aggregation_templates = []
        
        for template_name, template in self.templates.items():
            for xpath in template.xpath_expressions:
                if any(keyword in xpath.lower() for keyword in aggregation_keywords):
                    aggregation_templates.append(template_name)
                    break
        
        if aggregation_templates:
            pattern = SemanticPattern(
                pattern_type="data_aggregation",
                description=f"Data aggregation in templates: {', '.join(aggregation_templates)}",
                templates_involved=aggregation_templates,
                confidence_score=0.85,
                test_implications=[
                    "Test with empty data sets",
                    "Test with single and multiple data items",
                    "Verify aggregation accuracy",
                    "Test boundary conditions"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _detect_template_orchestration(self) -> None:
        """Detect template orchestration patterns."""
        orchestrator_templates = []
        
        for template_name, template in self.templates.items():
            if len(template.calls_templates) >= 2:  # Calls multiple templates
                orchestrator_templates.append(template_name)
        
        if orchestrator_templates:
            pattern = SemanticPattern(
                pattern_type="template_orchestration",
                description=f"Template orchestration in: {', '.join(orchestrator_templates)}",
                templates_involved=orchestrator_templates,
                confidence_score=0.7,
                test_implications=[
                    "Test template call sequences",
                    "Verify parameter passing between templates",
                    "Test orchestration error handling"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _detect_error_handling(self) -> None:
        """Detect error handling patterns."""
        error_keywords = ['error', 'exception', 'fallback', 'default', 'fail']
        error_handling_templates = []
        
        for template_name, template in self.templates.items():
            content_lower = template.template_content.lower()
            if any(keyword in content_lower for keyword in error_keywords):
                error_handling_templates.append(template_name)
        
        if error_handling_templates:
            pattern = SemanticPattern(
                pattern_type="error_handling",
                description=f"Error handling in templates: {', '.join(error_handling_templates)}",
                templates_involved=error_handling_templates,
                confidence_score=0.6,
                test_implications=[
                    "Test error conditions and edge cases",
                    "Verify error message content",
                    "Test fallback mechanisms"
                ]
            )
            self.semantic_patterns.append(pattern)
    
    def _analyze_variable_scoping(self) -> Dict[str, Any]:
        """Analyze variable scoping and lifecycle."""
        global_vars = []
        template_vars = []
        local_vars = []
        
        for var_name, variable in self.variables.items():
            if variable.scope == 'global':
                global_vars.append(var_name)
            elif variable.scope == 'template':
                template_vars.append(var_name)
            else:
                local_vars.append(var_name)
        
        return {
            'global_variables': global_vars,
            'template_variables': template_vars,
            'local_variables': local_vars,
            'variable_conflicts': self._detect_variable_conflicts(),
            'unused_variables': self._detect_unused_variables()
        }
    
    def _analyze_template_interactions(self) -> Dict[str, Any]:
        """Analyze template interaction patterns."""
        call_graph = {}
        for template_name, template in self.templates.items():
            call_graph[template_name] = template.calls_templates
        
        return {
            'call_graph': call_graph,
            'template_dependencies': self._build_template_dependencies(),
            'circular_dependencies': self._detect_circular_template_calls(),
            'orphaned_templates': self._detect_orphaned_templates()
        }
    
    def _identify_transformation_hotspots(self) -> List[Dict[str, Any]]:
        """Identify potential transformation hotspots."""
        hotspots = []
        
        for template_name, template in self.templates.items():
            hotspot_score = 0
            reasons = []
            
            # High complexity
            if template.complexity_score > 10:
                hotspot_score += 3
                reasons.append("High complexity score")
            
            # Many conditional branches
            if len(template.conditional_logic) > 3:
                hotspot_score += 2
                reasons.append("Many conditional branches")
            
            # Recursive template
            if template.is_recursive:
                hotspot_score += 3
                reasons.append("Recursive processing")
            
            # Many template calls
            if len(template.calls_templates) > 5:
                hotspot_score += 2
                reasons.append("Many template calls")
            
            # Complex XPath expressions
            complex_xpath = [x for x in template.xpath_expressions if len(x) > 50]
            if complex_xpath:
                hotspot_score += 2
                reasons.append("Complex XPath expressions")
            
            if hotspot_score >= 5:
                hotspots.append({
                    'template_name': template_name,
                    'hotspot_score': hotspot_score,
                    'reasons': reasons,
                    'risk_level': 'high' if hotspot_score >= 8 else 'medium'
                })
        
        return sorted(hotspots, key=lambda x: x['hotspot_score'], reverse=True)
    
    def _generate_test_implications(self) -> List[Dict[str, Any]]:
        """Generate test implications from semantic analysis."""
        implications = []
        
        for pattern in self.semantic_patterns:
            for implication in pattern.test_implications:
                implications.append({
                    'pattern_type': pattern.pattern_type,
                    'templates': pattern.templates_involved,
                    'test_requirement': implication,
                    'priority': 'high' if pattern.confidence_score > 0.8 else 'medium'
                })
        
        return implications
    
    def _detect_variable_conflicts(self) -> List[str]:
        """Detect potential variable naming conflicts."""
        conflicts = []
        var_names = {}
        
        for var_key, variable in self.variables.items():
            name = variable.name
            if name in var_names:
                conflicts.append(f"Variable '{name}' defined in multiple scopes")
            else:
                var_names[name] = var_key
        
        return conflicts
    
    def _detect_unused_variables(self) -> List[str]:
        """Detect potentially unused variables."""
        unused = []
        
        for var_name, variable in self.variables.items():
            if not variable.used_by_templates:
                unused.append(var_name)
        
        return unused
    
    def _build_template_dependencies(self) -> Dict[str, List[str]]:
        """Build template dependency graph."""
        dependencies = {}
        
        for template_name, template in self.templates.items():
            dependencies[template_name] = template.called_by_templates
        
        return dependencies
    
    def _detect_circular_template_calls(self) -> List[List[str]]:
        """Detect circular template call patterns."""
        # Simplified circular dependency detection
        visited = set()
        cycles = []
        
        def dfs(template_name, path):
            if template_name in path:
                cycle_start = path.index(template_name)
                cycles.append(path[cycle_start:] + [template_name])
                return
            
            if template_name in visited:
                return
            
            visited.add(template_name)
            template = self.templates.get(template_name)
            if template:
                for called_template in template.calls_templates:
                    if called_template in self.templates:
                        dfs(called_template, path + [template_name])
        
        for template_name in self.templates:
            if template_name not in visited:
                dfs(template_name, [])
        
        return cycles
    
    def _detect_orphaned_templates(self) -> List[str]:
        """Detect templates that are never called."""
        called_templates = set()
        
        for template in self.templates.values():
            called_templates.update(template.calls_templates)
        
        orphaned = []
        for template_name, template in self.templates.items():
            if (template_name not in called_templates and 
                not template.match_pattern):  # Named templates that aren't called
                orphaned.append(template_name)
        
        return orphaned
    
    def _generate_semantic_summary(self) -> Dict[str, Any]:
        """Generate summary of semantic analysis."""
        return {
            'total_patterns': len(self.semantic_patterns),
            'pattern_types': list(set(p.pattern_type for p in self.semantic_patterns)),
            'high_confidence_patterns': len([p for p in self.semantic_patterns if p.confidence_score > 0.8]),
            'data_flow_nodes': len(self.data_flow_graph),
            'transformation_complexity': sum(t.complexity_score for t in self.templates.values()),
            'test_implications_count': sum(len(p.test_implications) for p in self.semantic_patterns)
        }