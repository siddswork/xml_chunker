"""
File Analyzer Agent (o4-mini)

Systematic XSLT file analysis using progressive depth methodology.
Specialized for step-by-step reasoning and structured analysis patterns.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from ..core.base_agent import (
    ModelIntegratedAgent,
    ModelType,
    AgentCapability,
    ExecutionContext
)


class FileAnalyzerAgent(ModelIntegratedAgent):
    """
    File Analyzer Agent using o4-mini for systematic XSLT analysis.
    
    Responsibilities:
    - Progressive depth XSLT file analysis following proven methodology
    - Template structure analysis and documentation
    - Variable usage pattern identification
    - Business logic section mapping with precise line references
    """
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        capabilities = [
            AgentCapability(
                name="progressive_analysis",
                description="Progressive depth file analysis (5 patterns)",
                input_types=["xslt_file_path", "analysis_plan"],
                output_types=["structured_analysis", "template_mappings"],
                model_requirements=ModelType.O4_MINI
            ),
            AgentCapability(
                name="template_extraction",
                description="Extract and analyze XSLT templates",
                input_types=["xslt_content"],
                output_types=["template_catalog", "dependency_graph"],
                model_requirements=ModelType.O4_MINI
            ),
            AgentCapability(
                name="variable_analysis",
                description="Analyze variable usage patterns",
                input_types=["xslt_content"],
                output_types=["variable_catalog", "usage_patterns"],
                model_requirements=ModelType.O4_MINI
            )
        ]
        
        super().__init__(
            agent_id="file_analyzer",
            model_type=ModelType.O4_MINI,
            capabilities=capabilities,
            api_key=api_key,
            logger=logger
        )
    
    async def _process(self, context: ExecutionContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing logic for systematic XSLT analysis.
        
        Args:
            context: Execution context
            input_data: Input containing XSLT file path and analysis plan
            
        Returns:
            Comprehensive XSLT structure analysis
        """
        xslt_path = input_data.get("xslt_path")
        analysis_plan = input_data.get("analysis_plan", {})
        
        if not xslt_path or not Path(xslt_path).exists():
            raise ValueError(f"XSLT file not found: {xslt_path}")
        
        # Load XSLT content
        with open(xslt_path, 'r', encoding='utf-8') as f:
            xslt_content = f.read()
        
        # Perform progressive depth analysis
        analysis_results = await self._progressive_depth_analysis(xslt_content, analysis_plan)
        
        # Store analysis results in knowledge base
        await self.store_knowledge("xslt_structure_analysis", {
            "file_path": xslt_path,
            "analysis_results": analysis_results,
            "content_stats": self._get_content_statistics(xslt_content)
        })
        
        return analysis_results
    
    async def _progressive_depth_analysis(self, xslt_content: str, analysis_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform progressive depth analysis following the proven methodology.
        
        Implements the 5 analysis patterns from the manual methodology:
        1. Initial Assessment (≤50 lines)
        2. Structural Analysis (50-150 lines)  
        3. Deep Dive Analysis (150+ lines)
        4. Targeted Search + Focused Read
        5. Complex Logic Analysis (100+ lines)
        """
        
        # Split content into lines for analysis
        lines = xslt_content.split('\n')
        total_lines = len(lines)
        
        self.logger.info(f"Starting progressive analysis of {total_lines} lines")
        
        # Phase 1: Initial Assessment (lines 1-50)
        initial_assessment = await self._initial_assessment(lines[:50])
        
        # Phase 2: Helper Template Analysis (if applicable)
        helper_templates = await self._analyze_helper_templates(xslt_content)
        
        # Phase 3: Main Template Structure Analysis
        main_template_analysis = await self._analyze_main_template_structure(xslt_content)
        
        # Phase 4: Business Logic Pattern Recognition
        business_logic_patterns = await self._recognize_business_logic_patterns(xslt_content)
        
        # Phase 5: Variable and XPath Analysis
        variable_analysis = await self._analyze_variables_and_xpath(xslt_content)
        
        return {
            "analysis_summary": {
                "total_lines": total_lines,
                "analysis_phases_completed": 5,
                "templates_found": len(helper_templates.get("templates", {})) + (1 if main_template_analysis.get("main_template") else 0)
            },
            "initial_assessment": initial_assessment,
            "helper_templates": helper_templates,
            "main_template_analysis": main_template_analysis,
            "business_logic_patterns": business_logic_patterns,
            "variable_analysis": variable_analysis
        }
    
    async def _initial_assessment(self, first_50_lines: List[str]) -> Dict[str, Any]:
        """
        Phase 1: Initial Assessment (≤50 lines)
        
        Analysis focus:
        - File type identification
        - Template definitions discovery
        - Namespace declarations mapping
        - Generation tool detection
        """
        
        content_sample = '\n'.join(first_50_lines)
        
        reasoning_steps = [
            "Identify the file type and XSLT version from the XML declaration and root element",
            "Detect any code generation tool signatures or comments (e.g., MapForce, XMLSpy)",
            "Count and identify all template definitions (xsl:template elements)",
            "Map all namespace declarations and their prefixes",
            "Assess the overall file structure and organization approach"
        ]
        
        prompt = f"""
        Perform initial assessment of this XSLT file (first 50 lines):
        
        ```xml
        {content_sample}
        ```
        
        Provide systematic analysis following the methodology that successfully 
        generated 135+ test cases. Document findings for:
        
        1. File Type & Version Information
        2. Code Generation Tool Detection
        3. Template Definition Count and Names
        4. Namespace Declarations Mapping
        5. Overall Structure Assessment
        
        Be precise with line numbers and provide exact findings.
        """
        
        result = await self._execute_with_reasoning(prompt, reasoning_steps)
        
        # Parse structured findings
        assessment = self._parse_initial_assessment(result["content"])
        assessment["model_usage"] = result.get("usage", {})
        
        return assessment
    
    async def _analyze_helper_templates(self, xslt_content: str) -> Dict[str, Any]:
        """
        Phase 2: Helper Template Analysis
        
        Focus on named templates like vmf:vmf1_inputtoresult, vmf:vmf2_inputtoresult, etc.
        """
        
        # Extract helper template sections
        helper_templates = self._extract_helper_templates(xslt_content)
        
        if not helper_templates:
            return {"templates": {}, "analysis_summary": {"helper_templates_found": 0}}
        
        reasoning_steps = [
            "Identify each named template and its specific purpose",
            "Analyze input parameters and their expected types",
            "Map the transformation logic for each template",
            "Document output patterns and return values",
            "Identify relationships and dependencies between templates"
        ]
        
        prompt = f"""
        Analyze these helper templates from the XSLT file:
        
        {self._format_templates_for_analysis(helper_templates)}
        
        For each template, provide systematic analysis of:
        
        1. **Template Purpose**: What business function does it serve?
        2. **Input Parameters**: What inputs does it expect?
        3. **Transformation Logic**: How does it process the input?
        4. **Output Patterns**: What does it return?
        5. **Business Context**: What real-world scenario does this support?
        
        Reference the successful manual methodology that identified patterns like:
        - vmf:vmf1_inputtoresult: Maps 'P' and 'PT' inputs to 'VPT'
        - vmf:vmf2_inputtoresult: Maps 'V'→'VVI', 'R'→'VAEA', 'K'→'VCR'
        
        Provide precise line numbers and complete transformation mappings.
        """
        
        result = await self._execute_with_reasoning(prompt, reasoning_steps)
        
        analysis = self._parse_helper_template_analysis(result["content"], helper_templates)
        analysis["model_usage"] = result.get("usage", {})
        
        return analysis
    
    async def _analyze_main_template_structure(self, xslt_content: str) -> Dict[str, Any]:
        """
        Phase 3: Main Template Structure Analysis
        
        Analyze the main transformation template and its business flow.
        """
        
        # Extract main template
        main_template = self._extract_main_template(xslt_content)
        
        if not main_template:
            return {"main_template": None, "business_sections": []}
        
        reasoning_steps = [
            "Identify the main template and its match pattern",
            "Map major business sections and their purposes (Root Element, Version, POS, etc.)",
            "Catalog variable declarations and their usage scope",
            "Identify conditional logic structures (xsl:choose, xsl:when, xsl:if)",
            "Map business flow from input processing to output generation"
        ]
        
        prompt = f"""
        Analyze the main template structure (lines {main_template['line_start']}-{main_template['line_end']}):
        
        Following the successful methodology that identified sections like:
        - Root Element Creation (lines 68-69)
        - Version & Correlation (lines 70-79)  
        - Point of Sale (lines 82-91)
        - Travel Agency Sender (lines 95-180)
        - Order Query (lines 182-248)
        - Passenger Data (lines 249-767)
        - Contact Lists (lines 769-1227)
        - Metadata Generation (lines 1229-1863)
        
        Provide systematic analysis of:
        
        1. **Business Sections**: Identify and map major functional sections
        2. **Variable Usage**: Catalog key variables and their purposes
        3. **Conditional Logic**: Map decision points and branching logic
        4. **Data Flow**: Trace how input data flows to output generation
        5. **Line References**: Provide precise line numbers for each section
        
        Template content sample:
        ```xml
        {main_template['content'][:2000]}...
        ```
        """
        
        result = await self._execute_with_reasoning(prompt, reasoning_steps)
        
        analysis = self._parse_main_template_analysis(result["content"], main_template)
        analysis["model_usage"] = result.get("usage", {})
        
        return analysis
    
    async def _recognize_business_logic_patterns(self, xslt_content: str) -> Dict[str, Any]:
        """
        Phase 4: Business Logic Pattern Recognition
        
        Systematic identification of business rules and transformation patterns.
        """
        
        # Extract conditional logic patterns
        patterns = self._extract_conditional_patterns(xslt_content)
        
        reasoning_steps = [
            "Identify all xsl:choose, xsl:when, and xsl:if conditional structures",
            "Analyze target-specific processing logic (UA, UAD, other targets)",
            "Catalog XPath expressions and their business meanings",
            "Map data validation and transformation rules",
            "Identify complex business logic patterns and their purposes"
        ]
        
        prompt = f"""
        Analyze business logic patterns in this XSLT transformation:
        
        Key patterns found:
        {self._format_patterns_for_analysis(patterns)}
        
        Following the methodology that discovered patterns like:
        1. Target-Based Processing: UA vs UAD vs other targets
        2. Gender Mapping: Name/Type = 'Other' → 'Unspecified'
        3. Contact Type Processing: CTC contacts get special handling
        4. Phone Number Sanitization: Remove non-numeric characters
        5. Seat Number Parsing: Extract row number and column letter
        6. Address Concatenation: Complex address building
        
        Identify and document:
        
        1. **Conditional Logic Patterns**: All decision structures
        2. **Target-Specific Rules**: Airline-specific processing
        3. **Data Transformation Rules**: How data is modified
        4. **Validation Patterns**: Data quality and format rules
        5. **Business Context**: Real-world scenarios these patterns support
        
        Provide exact line references and complete transformation logic.
        """
        
        result = await self._execute_with_reasoning(prompt, reasoning_steps)
        
        pattern_analysis = self._parse_business_logic_patterns(result["content"], patterns)
        pattern_analysis["model_usage"] = result.get("usage", {})
        
        return pattern_analysis
    
    async def _analyze_variables_and_xpath(self, xslt_content: str) -> Dict[str, Any]:
        """
        Phase 5: Variable and XPath Analysis
        
        Comprehensive analysis of variable usage and XPath expressions.
        """
        
        # Extract variables and XPath expressions
        variables = self._extract_variables(xslt_content)
        xpath_expressions = self._extract_xpath_expressions(xslt_content)
        
        reasoning_steps = [
            "Catalog all variable declarations and their scope",
            "Analyze variable usage patterns and dependencies",
            "Extract and categorize all XPath expressions",
            "Map XPath expressions to business logic functions",
            "Identify complex expressions requiring special test coverage"
        ]
        
        prompt = f"""
        Analyze variables and XPath expressions in this XSLT:
        
        Variables found: {len(variables)}
        XPath expressions found: {len(xpath_expressions)}
        
        Sample analysis:
        ```
        Variables: {variables[:5] if variables else 'None found'}
        XPath samples: {xpath_expressions[:5] if xpath_expressions else 'None found'}
        ```
        
        Following the methodology that detected 280+ variables, provide:
        
        1. **Variable Catalog**: Complete list with purposes
        2. **Usage Patterns**: How variables are used and reused
        3. **XPath Expression Analysis**: Business meaning of each expression
        4. **Dependency Mapping**: Variable interdependencies
        5. **Test Implications**: Which variables/expressions need test coverage
        
        Focus on variables and expressions that affect business logic and 
        transformation outcomes.
        """
        
        result = await self._execute_with_reasoning(prompt, reasoning_steps)
        
        variable_analysis = self._parse_variable_analysis(result["content"], variables, xpath_expressions)
        variable_analysis["model_usage"] = result.get("usage", {})
        
        return variable_analysis
    
    def _extract_helper_templates(self, xslt_content: str) -> Dict[str, Dict[str, Any]]:
        """Extract helper templates (named templates) from XSLT."""
        templates = {}
        
        # Pattern to match named templates
        template_pattern = r'<xsl:template\s+name="([^"]+)"[^>]*>(.*?)</xsl:template>'
        
        for match in re.finditer(template_pattern, xslt_content, re.DOTALL):
            name = match.group(1)
            content = match.group(2)
            start_pos = match.start()
            
            # Calculate line numbers
            line_start = xslt_content[:start_pos].count('\n') + 1
            line_end = xslt_content[:match.end()].count('\n') + 1
            
            templates[name] = {
                "name": name,
                "content": content.strip(),
                "line_start": line_start,
                "line_end": line_end,
                "full_match": match.group(0)
            }
        
        return templates
    
    def _extract_main_template(self, xslt_content: str) -> Optional[Dict[str, Any]]:
        """Extract the main template (usually matches '/' or root element)."""
        # Pattern for main template (typically matches "/" or root element)
        main_patterns = [
            r'<xsl:template\s+match="/"[^>]*>(.*?)</xsl:template>',
            r'<xsl:template\s+match="[^"]*"[^>]*>\s*<[^/][^>]*>.*?</xsl:template>'
        ]
        
        for pattern in main_patterns:
            match = re.search(pattern, xslt_content, re.DOTALL)
            if match:
                start_pos = match.start()
                line_start = xslt_content[:start_pos].count('\n') + 1
                line_end = xslt_content[:match.end()].count('\n') + 1
                
                return {
                    "content": match.group(1).strip() if match.lastindex else match.group(0),
                    "line_start": line_start,
                    "line_end": line_end,
                    "full_match": match.group(0)
                }
        
        return None
    
    def _extract_conditional_patterns(self, xslt_content: str) -> List[Dict[str, Any]]:
        """Extract conditional logic patterns from XSLT."""
        patterns = []
        
        # Find xsl:choose blocks
        choose_pattern = r'<xsl:choose>(.*?)</xsl:choose>'
        for match in re.finditer(choose_pattern, xslt_content, re.DOTALL):
            start_pos = match.start()
            line_num = xslt_content[:start_pos].count('\n') + 1
            
            patterns.append({
                "type": "choose",
                "content": match.group(1).strip(),
                "line_number": line_num,
                "full_match": match.group(0)
            })
        
        # Find xsl:if statements
        if_pattern = r'<xsl:if\s+test="([^"]+)"[^>]*>(.*?)</xsl:if>'
        for match in re.finditer(if_pattern, xslt_content, re.DOTALL):
            start_pos = match.start()
            line_num = xslt_content[:start_pos].count('\n') + 1
            
            patterns.append({
                "type": "if",
                "test": match.group(1),
                "content": match.group(2).strip(),
                "line_number": line_num,
                "full_match": match.group(0)
            })
        
        return patterns
    
    def _extract_variables(self, xslt_content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from XSLT."""
        variables = []
        
        # Pattern for variable declarations
        var_pattern = r'<xsl:variable\s+name="([^"]+)"[^>]*(?:select="([^"]+)"|>(.*?)</xsl:variable>)'
        
        for match in re.finditer(var_pattern, xslt_content, re.DOTALL):
            start_pos = match.start()
            line_num = xslt_content[:start_pos].count('\n') + 1
            
            variables.append({
                "name": match.group(1),
                "select": match.group(2) if match.group(2) else None,
                "content": match.group(3) if match.group(3) else None,
                "line_number": line_num
            })
        
        return variables
    
    def _extract_xpath_expressions(self, xslt_content: str) -> List[str]:
        """Extract XPath expressions from XSLT."""
        xpath_expressions = []
        
        # Common XPath locations in XSLT
        xpath_patterns = [
            r'select="([^"]+)"',
            r'test="([^"]+)"',
            r'match="([^"]+)"'
        ]
        
        for pattern in xpath_patterns:
            for match in re.finditer(pattern, xslt_content):
                expr = match.group(1)
                if expr not in xpath_expressions:
                    xpath_expressions.append(expr)
        
        return xpath_expressions
    
    def _get_content_statistics(self, xslt_content: str) -> Dict[str, Any]:
        """Get basic statistics about the XSLT content."""
        lines = xslt_content.split('\n')
        
        return {
            "total_lines": len(lines),
            "total_characters": len(xslt_content),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "template_count": len(re.findall(r'<xsl:template', xslt_content)),
            "variable_count": len(re.findall(r'<xsl:variable', xslt_content)),
            "choose_count": len(re.findall(r'<xsl:choose', xslt_content)),
            "if_count": len(re.findall(r'<xsl:if', xslt_content))
        }
    
    def _format_templates_for_analysis(self, templates: Dict[str, Dict[str, Any]]) -> str:
        """Format templates for model analysis."""
        formatted = ""
        for name, template in templates.items():
            formatted += f"\n--- Template: {name} (lines {template['line_start']}-{template['line_end']}) ---\n"
            formatted += template['content'][:500] + ("..." if len(template['content']) > 500 else "")
            formatted += "\n"
        return formatted
    
    def _format_patterns_for_analysis(self, patterns: List[Dict[str, Any]]) -> str:
        """Format conditional patterns for model analysis."""
        formatted = ""
        for i, pattern in enumerate(patterns[:10]):  # Limit to first 10
            formatted += f"\n{i+1}. {pattern['type'].upper()} at line {pattern['line_number']}:\n"
            if pattern['type'] == 'if':
                formatted += f"   Test: {pattern['test']}\n"
            formatted += f"   Content: {pattern['content'][:200]}...\n"
        return formatted
    
    # Parsing methods for model responses (simplified for MVP)
    def _parse_initial_assessment(self, content: str) -> Dict[str, Any]:
        """Parse initial assessment from model response."""
        return {
            "file_type": "XSLT 1.0",  # Would parse from content
            "generation_tool": "Unknown",  # Would detect from content
            "template_count": 0,  # Would extract from content
            "namespace_declarations": {},  # Would parse from content
            "structure_assessment": "Complex",  # Would assess from content
            "raw_analysis": content
        }
    
    def _parse_helper_template_analysis(self, content: str, templates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Parse helper template analysis from model response."""
        return {
            "templates": templates,
            "analysis_summary": {
                "helper_templates_found": len(templates),
                "business_functions_identified": len(templates)
            },
            "transformation_mappings": {},  # Would parse from content
            "raw_analysis": content
        }
    
    def _parse_main_template_analysis(self, content: str, main_template: Dict[str, Any]) -> Dict[str, Any]:
        """Parse main template analysis from model response."""
        return {
            "main_template": main_template,
            "business_sections": [],  # Would parse from content
            "variable_usage": {},  # Would parse from content
            "conditional_logic": [],  # Would parse from content
            "raw_analysis": content
        }
    
    def _parse_business_logic_patterns(self, content: str, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse business logic patterns from model response."""
        return {
            "patterns": patterns,
            "pattern_summary": {
                "conditional_patterns": len([p for p in patterns if p['type'] in ['choose', 'if']]),
                "business_rules_identified": 0  # Would count from content
            },
            "target_specific_logic": {},  # Would parse from content
            "raw_analysis": content
        }
    
    def _parse_variable_analysis(self, content: str, variables: List[Dict[str, Any]], xpath_expressions: List[str]) -> Dict[str, Any]:
        """Parse variable and XPath analysis from model response."""
        return {
            "variables": variables,
            "xpath_expressions": xpath_expressions,
            "variable_summary": {
                "total_variables": len(variables),
                "total_xpath_expressions": len(xpath_expressions)
            },
            "usage_patterns": {},  # Would parse from content
            "raw_analysis": content
        }