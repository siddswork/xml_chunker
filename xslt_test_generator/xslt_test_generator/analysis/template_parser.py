"""XSLT Template Parser for extracting and analyzing XSLT templates."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import hashlib
import re

from ..core.base import LoggerMixin


@dataclass
class XSLTTemplate:
    """Represents an analyzed XSLT template."""
    name: Optional[str] = None
    match_pattern: Optional[str] = None
    mode: Optional[str] = None
    priority: Optional[float] = None
    line_start: int = 0
    line_end: int = 0
    template_content: str = ""
    
    # Dependencies and relationships
    calls_templates: List[str] = field(default_factory=list)
    called_by_templates: List[str] = field(default_factory=list)
    uses_variables: List[str] = field(default_factory=list)
    defines_variables: List[str] = field(default_factory=list)
    
    # XPath and logic analysis
    xpath_expressions: List[str] = field(default_factory=list)
    conditional_logic: List[Dict[str, Any]] = field(default_factory=list)
    output_elements: List[str] = field(default_factory=list)
    
    # Metadata
    template_hash: str = ""
    complexity_score: int = 0
    is_recursive: bool = False
    
    def __post_init__(self):
        """Calculate hash if not provided."""
        if not self.template_hash and self.template_content:
            self.template_hash = hashlib.sha256(
                self.template_content.encode('utf-8')
            ).hexdigest()[:16]


@dataclass
class XSLTVariable:
    """Represents an XSLT variable or parameter."""
    name: str
    variable_type: str  # 'variable' or 'parameter'
    select_expression: Optional[str] = None
    content: str = ""
    scope: str = "template"  # 'global', 'template', 'local'
    line_number: int = 0
    used_by_templates: List[str] = field(default_factory=list)


class XSLTTemplateParser(LoggerMixin):
    """Parser for extracting and analyzing XSLT templates."""
    
    def __init__(self):
        super().__init__()
        self.namespaces = {
            'xsl': 'http://www.w3.org/1999/XSL/Transform',
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'fn': 'http://www.w3.org/2005/xpath-functions'
        }
        self.templates: Dict[str, XSLTTemplate] = {}
        self.variables: Dict[str, XSLTVariable] = {}
        self.file_path: Optional[str] = None
    
    def parse_xslt_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse XSLT file and extract all templates and variables.
        
        Args:
            file_path: Path to XSLT file
            
        Returns:
            Dictionary containing parsed templates and variables
        """
        self.file_path = file_path
        self.templates.clear()
        self.variables.clear()
        
        try:
            # Read file content with line numbers for accurate tracking
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract all templates
            self._extract_templates(root, lines)
            
            # Extract all variables and parameters
            self._extract_variables(root, lines)
            
            # Analyze template relationships
            self._analyze_template_relationships()
            
            # Calculate complexity scores
            self._calculate_complexity_scores()
            
            self.logger.info(f"Parsed {len(self.templates)} templates and {len(self.variables)} variables from {file_path}")
            
            return {
                'templates': self.templates,
                'variables': self.variables,
                'file_path': file_path,
                'analysis_summary': self._generate_analysis_summary()
            }
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in {file_path}: {e}")
            return {'error': f"XML parsing error: {e}"}
        except Exception as e:
            self.logger.error(f"Unexpected error parsing {file_path}: {e}")
            return {'error': f"Unexpected error: {e}"}
    
    def _extract_templates(self, root: ET.Element, lines: List[str]) -> None:
        """Extract all templates from XSLT root."""
        template_elements = root.findall('.//xsl:template', self.namespaces)
        
        for template_elem in template_elements:
            template = self._parse_template_element(template_elem, lines)
            
            # Use name or match pattern as key
            key = template.name or template.match_pattern or f"anonymous_{len(self.templates)}"
            self.templates[key] = template
    
    def _parse_template_element(self, template_elem: ET.Element, lines: List[str]) -> XSLTTemplate:
        """Parse individual template element."""
        template = XSLTTemplate()
        
        # Basic attributes
        template.name = template_elem.get('name')
        template.match_pattern = template_elem.get('match')
        template.mode = template_elem.get('mode')
        
        priority_str = template_elem.get('priority')
        if priority_str:
            try:
                template.priority = float(priority_str)
            except ValueError:
                pass
        
        # Get template content and line numbers
        template.template_content = ET.tostring(template_elem, encoding='unicode')
        template.line_start, template.line_end = self._find_element_lines(
            template_elem, lines
        )
        
        # Extract template calls
        template.calls_templates = self._extract_template_calls(template_elem)
        
        # Extract variable usage
        template.uses_variables = self._extract_variable_usage(template_elem)
        template.defines_variables = self._extract_variable_definitions(template_elem)
        
        # Extract XPath expressions
        template.xpath_expressions = self._extract_xpath_expressions(template_elem)
        
        # Extract conditional logic
        template.conditional_logic = self._extract_conditional_logic(template_elem)
        
        # Extract output elements
        template.output_elements = self._extract_output_elements(template_elem)
        
        # Generate hash after content is set
        if template.template_content and not template.template_hash:
            template.template_hash = hashlib.sha256(
                template.template_content.encode('utf-8')
            ).hexdigest()[:16]
        
        return template
    
    def _extract_variables(self, root: ET.Element, lines: List[str]) -> None:
        """Extract all variables and parameters."""
        # Global variables
        for var_elem in root.findall('./xsl:variable', self.namespaces):
            variable = self._parse_variable_element(var_elem, lines, 'global')
            self.variables[variable.name] = variable
        
        # Global parameters
        for param_elem in root.findall('./xsl:param', self.namespaces):
            variable = self._parse_variable_element(param_elem, lines, 'global')
            variable.variable_type = 'parameter'
            self.variables[variable.name] = variable
        
        # Template-level variables and parameters
        for template_elem in root.findall('.//xsl:template', self.namespaces):
            for var_elem in template_elem.findall('.//xsl:variable', self.namespaces):
                variable = self._parse_variable_element(var_elem, lines, 'template')
                var_key = f"{variable.name}_{variable.line_number}"
                self.variables[var_key] = variable
            
            for param_elem in template_elem.findall('.//xsl:param', self.namespaces):
                variable = self._parse_variable_element(param_elem, lines, 'template')
                variable.variable_type = 'parameter'
                var_key = f"{variable.name}_{variable.line_number}"
                self.variables[var_key] = variable
    
    def _parse_variable_element(self, var_elem: ET.Element, lines: List[str], scope: str) -> XSLTVariable:
        """Parse individual variable or parameter element."""
        variable = XSLTVariable(
            name=var_elem.get('name', ''),
            variable_type='variable',
            select_expression=var_elem.get('select'),
            scope=scope
        )
        
        # Get line number
        variable.line_number = self._find_element_lines(var_elem, lines)[0]
        
        # Get content if no select attribute
        if not variable.select_expression and var_elem.text:
            variable.content = var_elem.text.strip()
        
        return variable
    
    def _extract_template_calls(self, template_elem: ET.Element) -> List[str]:
        """Extract template calls from template element."""
        calls = []
        
        # xsl:call-template
        for call_elem in template_elem.findall('.//xsl:call-template', self.namespaces):
            name = call_elem.get('name')
            if name:
                calls.append(name)
        
        # xsl:apply-templates (mode-based calls)
        for apply_elem in template_elem.findall('.//xsl:apply-templates', self.namespaces):
            mode = apply_elem.get('mode')
            select = apply_elem.get('select')
            if mode:
                calls.append(f"mode:{mode}")
            elif select:
                calls.append(f"select:{select}")
        
        return list(set(calls))  # Remove duplicates
    
    def _extract_variable_usage(self, template_elem: ET.Element) -> List[str]:
        """Extract variable usage from template content."""
        variables = []
        content = ET.tostring(template_elem, encoding='unicode')
        
        # Find $variable references
        var_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_-]*)'
        matches = re.findall(var_pattern, content)
        variables.extend(matches)
        
        return list(set(variables))
    
    def _extract_variable_definitions(self, template_elem: ET.Element) -> List[str]:
        """Extract variable definitions within template."""
        definitions = []
        
        for var_elem in template_elem.findall('.//xsl:variable', self.namespaces):
            name = var_elem.get('name')
            if name:
                definitions.append(name)
        
        for param_elem in template_elem.findall('.//xsl:param', self.namespaces):
            name = param_elem.get('name')
            if name:
                definitions.append(name)
        
        return definitions
    
    def _extract_xpath_expressions(self, template_elem: ET.Element) -> List[str]:
        """Extract XPath expressions from template."""
        expressions = []
        
        # Check common XPath attributes
        xpath_attrs = ['select', 'test', 'match']
        
        for elem in template_elem.iter():
            for attr in xpath_attrs:
                value = elem.get(attr)
                if value:
                    expressions.append(value)
        
        return list(set(expressions))
    
    def _extract_conditional_logic(self, template_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract conditional logic structures."""
        conditionals = []
        
        # xsl:if elements
        for if_elem in template_elem.findall('.//xsl:if', self.namespaces):
            test = if_elem.get('test')
            if test:
                conditionals.append({
                    'type': 'if',
                    'condition': test,
                    'line': self._find_element_lines(if_elem, [])[0]
                })
        
        # xsl:choose/when/otherwise
        for choose_elem in template_elem.findall('.//xsl:choose', self.namespaces):
            choose_info = {
                'type': 'choose',
                'conditions': [],
                'line': self._find_element_lines(choose_elem, [])[0]
            }
            
            for when_elem in choose_elem.findall('./xsl:when', self.namespaces):
                test = when_elem.get('test')
                if test:
                    choose_info['conditions'].append(test)
            
            conditionals.append(choose_info)
        
        return conditionals
    
    def _extract_output_elements(self, template_elem: ET.Element) -> List[str]:
        """Extract output elements created by template."""
        outputs = []
        
        # Look for literal result elements (non-xsl elements)
        for elem in template_elem.iter():
            if elem.tag and not elem.tag.startswith('{http://www.w3.org/1999/XSL/Transform}'):
                # Remove namespace prefix for readability
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                outputs.append(tag_name)
        
        # xsl:element
        for element_elem in template_elem.findall('.//xsl:element', self.namespaces):
            name = element_elem.get('name')
            if name:
                outputs.append(name)
        
        return list(set(outputs))
    
    def _analyze_template_relationships(self) -> None:
        """Analyze relationships between templates."""
        # Build called_by_templates relationships
        for template_name, template in self.templates.items():
            for called_template in template.calls_templates:
                if called_template in self.templates:
                    self.templates[called_template].called_by_templates.append(template_name)
        
        # Check for recursive templates
        for template_name, template in self.templates.items():
            if template_name in template.calls_templates:
                template.is_recursive = True
                self.logger.info(f"Detected recursive template: {template_name}")
    
    def _calculate_complexity_scores(self) -> None:
        """Calculate complexity scores for templates."""
        for template in self.templates.values():
            score = 0
            
            # Base complexity
            score += 1
            
            # Conditional logic complexity
            score += len(template.conditional_logic) * 2
            
            # Variable usage complexity
            score += len(template.uses_variables)
            
            # XPath expression complexity
            score += len(template.xpath_expressions)
            
            # Template call complexity
            score += len(template.calls_templates)
            
            # Recursive template penalty
            if template.is_recursive:
                score += 5
            
            # Content length factor
            if len(template.template_content) > 1000:
                score += 2
            elif len(template.template_content) > 500:
                score += 1
            
            template.complexity_score = score
    
    def _find_element_lines(self, element: ET.Element, lines: List[str]) -> Tuple[int, int]:
        """Find line numbers for XML element (simplified approach)."""
        # This is a simplified implementation
        # For production, would need more sophisticated line tracking
        return (1, 1)
    
    def _generate_analysis_summary(self) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        total_templates = len(self.templates)
        named_templates = len([t for t in self.templates.values() if t.name])
        match_templates = len([t for t in self.templates.values() if t.match_pattern])
        recursive_templates = len([t for t in self.templates.values() if t.is_recursive])
        
        avg_complexity = 0
        if total_templates > 0:
            avg_complexity = sum(t.complexity_score for t in self.templates.values()) / total_templates
        
        return {
            'total_templates': total_templates,
            'named_templates': named_templates,
            'match_templates': match_templates,
            'recursive_templates': recursive_templates,
            'total_variables': len(self.variables),
            'avg_complexity': round(avg_complexity, 2),
            'most_complex_template': max(
                self.templates.keys(),
                key=lambda k: self.templates[k].complexity_score,
                default=None
            )
        }