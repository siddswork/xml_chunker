"""
Context Provider for Multi-Pass XSLT Analysis

This module provides intelligent context for XSLT analysis by:
1. Parsing full XSLT content to understand chunk relationships
2. Building dependency graphs between templates
3. Providing progressive context for multi-pass analysis
"""

import re
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class XSLTChunk:
    """Represents an XSLT template or chunk"""
    name: str
    content: str
    line_start: int
    line_end: int
    template_type: str  # 'named', 'match', 'helper'
    dependencies: List[str]
    dependent_templates: List[str]


@dataclass
class ContextLevel:
    """Different levels of context for multi-pass analysis"""
    level: str  # 'isolated', 'contextual', 'full_workflow'
    description: str
    content: str
    related_chunks: List[str]


class ContextProvider:
    """Provides progressive context for multi-pass XSLT analysis"""
    
    def __init__(self, xslt_content: str = None):
        """Initialize with full XSLT content"""
        self.xslt_content = xslt_content
        self.chunks: Dict[str, XSLTChunk] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        if xslt_content:
            self._parse_xslt_content()
            self._build_dependency_graph()
    
    def load_sample_xslt(self) -> str:
        """Load sample XSLT content for testing"""
        
        # Sample XSLT content representing the structure we're analyzing
        sample_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:vmf="http://www.example.com/vmf">

<!-- Helper Template: Document Type Transformations -->
<xsl:template name="vmf:vmf1_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'P'">VPT</xsl:when>
        <xsl:when test="$input = 'PT'">VPT</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template name="vmf:vmf2_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'V'">VVI</xsl:when>
        <xsl:when test="$input = 'R'">VAEA</xsl:when>
        <xsl:when test="$input = 'K'">VCR</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template name="vmf:vmf3_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'I'">VII</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- Main Processing Template -->
<xsl:template match="Passenger">
    <xsl:variable name="documentType">
        <xsl:choose>
            <xsl:when test="Document/@Type = 'P' or Document/@Type = 'PT'">
                <xsl:call-template name="vmf:vmf1_inputtoresult">
                    <xsl:with-param name="input" select="Document/@Type"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="Document/@Type = 'V' or Document/@Type = 'R' or Document/@Type = 'K'">
                <xsl:call-template name="vmf:vmf2_inputtoresult">
                    <xsl:with-param name="input" select="Document/@Type"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="Document/@Type = 'I'">
                <xsl:call-template name="vmf:vmf3_inputtoresult">
                    <xsl:with-param name="input" select="Document/@Type"/>
                </xsl:call-template>
            </xsl:when>
        </xsl:choose>
    </xsl:variable>
    
    <ProcessedPassenger>
        <DocumentType><xsl:value-of select="$documentType"/></DocumentType>
        <xsl:apply-templates select="Contact"/>
        <xsl:if test="@target = 'UA'">
            <xsl:call-template name="ua_specific_processing"/>
        </xsl:if>
    </ProcessedPassenger>
</xsl:template>

<!-- Target-Specific Processing -->
<xsl:template name="ua_specific_processing">
    <xsl:if test="count(../Passenger) > 1">
        <xsl:call-template name="multi_passenger_validation"/>
    </xsl:if>
    <ContactValidation>
        <xsl:apply-templates select="Contact" mode="ua_validation"/>
    </ContactValidation>
</xsl:template>

<!-- Contact Processing -->
<xsl:template match="Contact">
    <xsl:variable name="standardizedPhone">
        <xsl:call-template name="standardize_phone">
            <xsl:with-param name="phone" select="Phone"/>
            <xsl:with-param name="target" select="../@target"/>
        </xsl:call-template>
    </xsl:variable>
    
    <ProcessedContact>
        <Phone><xsl:value-of select="$standardizedPhone"/></Phone>
        <xsl:call-template name="process_address"/>
    </ProcessedContact>
</xsl:template>

<xsl:template match="Contact" mode="ua_validation">
    <xsl:if test="not(Phone) or not(Email)">
        <ValidationError>Missing required contact information for UA</ValidationError>
    </xsl:if>
</xsl:template>

<!-- Multi-passenger validation -->
<xsl:template name="multi_passenger_validation">
    <xsl:for-each select="../Passenger">
        <xsl:if test="not(Contact/Phone)">
            <ValidationError>Passenger <xsl:value-of select="position()"/> missing contact info</ValidationError>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<!-- Phone standardization -->
<xsl:template name="standardize_phone">
    <xsl:param name="phone"/>
    <xsl:param name="target"/>
    <xsl:choose>
        <xsl:when test="$target = 'UA'">
            <xsl:value-of select="translate($phone, '()-', '')"/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$phone"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- Address processing -->
<xsl:template name="process_address">
    <Address>
        <xsl:value-of select="normalize-space(concat(Address/Line1, ' ', Address/Line2, ' ', Address/City, ' ', Address/State))"/>
    </Address>
</xsl:template>

</xsl:stylesheet>'''
        
        self.xslt_content = sample_content
        self._parse_xslt_content()
        self._build_dependency_graph()
        return sample_content
    
    def _parse_xslt_content(self):
        """Parse XSLT content to extract templates and their relationships"""
        
        if not self.xslt_content:
            return
            
        lines = self.xslt_content.split('\n')
        current_template = None
        template_content = []
        template_start = 0
        
        for i, line in enumerate(lines):
            # Match template start
            template_match = re.search(r'<xsl:template\s+(?:name="([^"]+)"|match="([^"]+)")', line)
            if template_match:
                # Save previous template if exists
                if current_template:
                    self._save_template(current_template, template_content, template_start, i-1)
                
                # Start new template
                current_template = template_match.group(1) or template_match.group(2)
                template_content = [line]
                template_start = i
            elif current_template and line.strip():
                template_content.append(line)
            elif current_template and '</xsl:template>' in line:
                template_content.append(line)
                self._save_template(current_template, template_content, template_start, i)
                current_template = None
                template_content = []
        
        # Handle last template
        if current_template:
            self._save_template(current_template, template_content, template_start, len(lines)-1)
    
    def _save_template(self, name: str, content: List[str], start: int, end: int):
        """Save parsed template as XSLTChunk"""
        
        content_str = '\n'.join(content)
        
        # Determine template type
        if 'name=' in content_str:
            template_type = 'helper' if 'vmf:' in name else 'named'
        elif 'match=' in content_str:
            template_type = 'match'
        else:
            template_type = 'unknown'
        
        # Find dependencies (templates this one calls)
        dependencies = self._extract_dependencies(content_str)
        
        self.chunks[name] = XSLTChunk(
            name=name,
            content=content_str,
            line_start=start,
            line_end=end,
            template_type=template_type,
            dependencies=dependencies,
            dependent_templates=[]  # Will be populated later
        )
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract template dependencies from content"""
        
        dependencies = []
        
        # Find call-template references
        call_matches = re.findall(r'<xsl:call-template\s+name="([^"]+)"', content)
        dependencies.extend(call_matches)
        
        # Find apply-templates with mode (indicates dependency)
        apply_matches = re.findall(r'<xsl:apply-templates[^>]+mode="([^"]+)"', content)
        dependencies.extend(apply_matches)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _build_dependency_graph(self):
        """Build dependency relationships between templates"""
        
        # Initialize dependency graph
        for chunk_name in self.chunks:
            self.dependency_graph[chunk_name] = set()
        
        # Build forward dependencies
        for chunk_name, chunk in self.chunks.items():
            for dep in chunk.dependencies:
                if dep in self.chunks:
                    self.dependency_graph[chunk_name].add(dep)
                    # Also populate dependent_templates (reverse dependency)
                    self.chunks[dep].dependent_templates.append(chunk_name)
    
    def get_chunk_by_name(self, name: str) -> Optional[XSLTChunk]:
        """Get specific chunk by name"""
        return self.chunks.get(name)
    
    def get_related_chunks(self, chunk_name: str) -> List[str]:
        """Get chunks that are directly related to the given chunk"""
        
        if chunk_name not in self.chunks:
            return []
        
        chunk = self.chunks[chunk_name]
        related = set()
        
        # Add direct dependencies
        related.update(chunk.dependencies)
        
        # Add templates that depend on this one
        related.update(chunk.dependent_templates)
        
        return list(related)
    
    def get_dependency_chain(self, chunk_name: str, depth: int = 2) -> List[str]:
        """Get dependency chain for a chunk up to specified depth"""
        
        if chunk_name not in self.chunks:
            return []
        
        visited = set()
        chain = []
        
        def collect_dependencies(current_chunk: str, current_depth: int):
            if current_depth <= 0 or current_chunk in visited:
                return
            
            visited.add(current_chunk)
            if current_chunk in self.chunks:
                chain.append(current_chunk)
                
                # Add dependencies
                for dep in self.chunks[current_chunk].dependencies:
                    collect_dependencies(dep, current_depth - 1)
                
                # Add dependents
                for dep in self.chunks[current_chunk].dependent_templates:
                    collect_dependencies(dep, current_depth - 1)
        
        collect_dependencies(chunk_name, depth)
        return chain
    
    def get_context_levels(self, chunk_name: str) -> List[ContextLevel]:
        """Get progressive context levels for multi-pass analysis"""
        
        if chunk_name not in self.chunks:
            return []
        
        chunk = self.chunks[chunk_name]
        levels = []
        
        # Level 1: Isolated chunk
        levels.append(ContextLevel(
            level="isolated",
            description=f"Analysis of {chunk_name} in isolation",
            content=chunk.content,
            related_chunks=[]
        ))
        
        # Level 2: Contextual (immediate dependencies)
        related_chunks = self.get_related_chunks(chunk_name)
        contextual_content = chunk.content
        
        if related_chunks:
            contextual_content += "\n\n<!-- RELATED TEMPLATES -->\n"
            for related in related_chunks:
                if related in self.chunks:
                    contextual_content += f"\n<!-- {related} -->\n"
                    contextual_content += self.chunks[related].content
        
        levels.append(ContextLevel(
            level="contextual",
            description=f"Analysis of {chunk_name} with immediate dependencies",
            content=contextual_content,
            related_chunks=related_chunks
        ))
        
        # Level 3: Full workflow context
        workflow_chunks = self.get_dependency_chain(chunk_name, depth=3)
        workflow_content = chunk.content
        
        if workflow_chunks:
            workflow_content += "\n\n<!-- FULL WORKFLOW CONTEXT -->\n"
            for workflow_chunk in workflow_chunks:
                if workflow_chunk != chunk_name and workflow_chunk in self.chunks:
                    workflow_content += f"\n<!-- {workflow_chunk} -->\n"
                    workflow_content += self.chunks[workflow_chunk].content
        
        levels.append(ContextLevel(
            level="full_workflow",
            description=f"Analysis of {chunk_name} with complete workflow context",
            content=workflow_content,
            related_chunks=workflow_chunks
        ))
        
        return levels
    
    def get_business_workflow_context(self, chunk_name: str) -> str:
        """Get business workflow explanation for the chunk"""
        
        if chunk_name not in self.chunks:
            return ""
        
        chunk = self.chunks[chunk_name]
        
        # Generate business workflow explanation
        workflow_explanation = f"""
BUSINESS WORKFLOW CONTEXT FOR {chunk_name}:

Template Type: {chunk.template_type}
Role in Workflow: {self._get_template_role(chunk)}

Dependencies (What this template needs):
{self._format_dependencies(chunk.dependencies)}

Dependent Templates (What depends on this template):
{self._format_dependencies(chunk.dependent_templates)}

Integration Points:
{self._get_integration_points(chunk_name)}

Business Data Flow:
{self._get_business_data_flow(chunk_name)}
"""
        
        return workflow_explanation
    
    def _get_template_role(self, chunk: XSLTChunk) -> str:
        """Determine the business role of a template"""
        
        if chunk.template_type == 'helper':
            return "Helper template - provides data transformation services"
        elif chunk.template_type == 'match':
            return "Main processing template - handles specific XML elements"
        elif 'validation' in chunk.name.lower():
            return "Validation template - ensures data quality and compliance"
        elif 'processing' in chunk.name.lower():
            return "Processing template - applies business rules"
        else:
            return "Business logic template - implements specific business requirements"
    
    def _format_dependencies(self, deps: List[str]) -> str:
        """Format dependencies for readable output"""
        
        if not deps:
            return "  - None"
        
        formatted = []
        for dep in deps:
            if dep in self.chunks:
                role = self._get_template_role(self.chunks[dep])
                formatted.append(f"  - {dep}: {role}")
            else:
                formatted.append(f"  - {dep}: External dependency")
        
        return '\n'.join(formatted)
    
    def _get_integration_points(self, chunk_name: str) -> str:
        """Get integration points for a chunk"""
        
        if chunk_name not in self.chunks:
            return "  - None identified"
        
        chunk = self.chunks[chunk_name]
        integration_points = []
        
        # Check for common integration patterns
        if 'call-template' in chunk.content:
            integration_points.append("  - Calls other templates for processing")
        
        if 'apply-templates' in chunk.content:
            integration_points.append("  - Applies templates to child elements")
        
        if 'variable' in chunk.content:
            integration_points.append("  - Uses variables for data passing")
        
        if '@target' in chunk.content:
            integration_points.append("  - Target-specific processing logic")
        
        return '\n'.join(integration_points) if integration_points else "  - None identified"
    
    def _get_business_data_flow(self, chunk_name: str) -> str:
        """Get business data flow explanation"""
        
        if chunk_name not in self.chunks:
            return "  - Flow not identified"
        
        chunk = self.chunks[chunk_name]
        
        # Analyze data flow patterns
        if 'vmf1' in chunk_name:
            return "  - Input: Document type codes (P, PT) → Output: NDC-compliant codes (VPT)"
        elif 'vmf2' in chunk_name:
            return "  - Input: Visa type codes (V, R, K) → Output: NDC-compliant codes (VVI, VAEA, VCR)"
        elif 'vmf3' in chunk_name:
            return "  - Input: Identity document codes (I) → Output: NDC-compliant codes (VII)"
        elif 'Passenger' in chunk_name:
            return "  - Input: Passenger XML → Output: Processed passenger with document validation"
        elif 'Contact' in chunk_name:
            return "  - Input: Contact information → Output: Validated and standardized contact data"
        elif 'phone' in chunk_name.lower():
            return "  - Input: Phone number → Output: Target-specific formatted phone number"
        elif 'address' in chunk_name.lower():
            return "  - Input: Address components → Output: Concatenated standardized address"
        else:
            return "  - Data flow pattern not identified"


# Test function
if __name__ == "__main__":
    # Test the context provider
    provider = ContextProvider()
    provider.load_sample_xslt()
    
    # Test context levels for vmf1
    levels = provider.get_context_levels("vmf:vmf1_inputtoresult")
    
    print("Context Levels for vmf1:")
    for level in levels:
        print(f"\n{level.level.upper()}:")
        print(f"Description: {level.description}")
        print(f"Related chunks: {level.related_chunks}")
        print(f"Content preview: {level.content[:200]}...")
    
    # Test business workflow context
    workflow_context = provider.get_business_workflow_context("vmf:vmf1_inputtoresult")
    print(f"\nBusiness Workflow Context:\n{workflow_context}")