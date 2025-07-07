"""
XSLT Chunker for Intelligent File Sectioning

This module provides intelligent chunking of XSLT files based on template boundaries,
maintaining semantic coherence while respecting token limits for LLM processing.

Regex Pattern Examples:
======================

Template Boundaries:
- Start: '<xsl:template name="vmf:vmf1_inputtoresult">' or '<xsl:template match="/">'
- End: '</xsl:template>'

Helper Templates (vmf namespace functions):
- 'vmf:vmf1_inputtoresult', 'vmf:vmf2_inputtoresult', 'vmf3_helper', 'vmf4_transform'

Variable References:
- '$target', '$var196_nested', '$input', '$globalVar'

Template Calls:
- '<xsl:call-template name="vmf:vmf1_inputtoresult">'
- '<xsl:call-template name="helper_function">'

Choose Blocks:
- '<xsl:choose>' ... '</xsl:choose>'

Variable Declarations:
- '<xsl:variable name="target" select="//Target"/>'
- '<xsl:variable name="var196_nested" select="."/>'

XPath Expressions:
- '//Target', '@value', '/root/element[1]', './/child::*', 'ancestor::node()'

Function Calls:
- 'fn:count($items)', 'xs:string(@value)', 'custom:format(.)'

Import/Include:
- '<xsl:import href="common_templates.xsl"/>'
- '<xsl:include href="helper_functions.xslt"/>'
"""

import re
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.streaming_file_reader import StreamingFileReader
from ..utils.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class ChunkType(Enum):
    """Types of XSLT chunks"""
    HELPER_TEMPLATE = "helper_template"
    MAIN_TEMPLATE = "main_template"
    VARIABLE_SECTION = "variable_section"
    IMPORT_SECTION = "import_section"
    NAMESPACE_SECTION = "namespace_section"
    CHOOSE_BLOCK = "choose_block"
    UNKNOWN = "unknown"


@dataclass
class ChunkInfo:
    """Information about an XSLT chunk"""
    chunk_id: str
    chunk_type: ChunkType
    name: Optional[str]
    start_line: int
    end_line: int
    lines: List[str]
    estimated_tokens: int
    dependencies: List[str]
    metadata: Dict[str, Any]
    
    @property
    def text(self) -> str:
        """Get chunk text"""
        return '\n'.join(self.lines)
    
    @property
    def line_count(self) -> int:
        """Get number of lines in chunk"""
        return len(self.lines)


# Default helper patterns for different XSLT generators
DEFAULT_HELPER_PATTERNS = {
    'mapforce': r'(?:vmf:)?vmf\d+',           # MapForce generated helpers (vmf:vmf1_inputtoresult)
    'saxon': r'(?:f:)?func\d+',               # Saxon helper functions (f:func1, func2)
    'custom': r'(?:util:)?helper[\w_]*',      # Custom helper patterns (util:helper_name)
    'generic': r'(?:\w+:)?(?:helper|util|fn)\w*'  # Generic helper detection
}


class XSLTChunker:
    """Intelligent XSLT file chunker"""
    
    def __init__(self, max_tokens_per_chunk: int = 15000, overlap_tokens: int = 500, 
                 helper_patterns: Optional[List[str]] = None, 
                 main_template_split_threshold: int = 10000):
        """
        Initialize XSLT chunker
        
        Args:
            max_tokens_per_chunk: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            helper_patterns: List of regex patterns to identify helper templates.
                           If None, defaults to MapForce patterns for backward compatibility.
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap_tokens = overlap_tokens
        self.main_template_split_threshold = main_template_split_threshold
        
        # Set helper patterns - default to MapForce for backward compatibility
        if helper_patterns is None:
            self.helper_patterns = [DEFAULT_HELPER_PATTERNS['mapforce']]
        else:
            self.helper_patterns = helper_patterns
        
        self.file_reader = StreamingFileReader()
        self.token_counter = TokenCounter()
        
        # XSLT patterns for identifying boundaries with real examples
        self.xslt_patterns = {
            # Template start patterns
            # Examples: <xsl:template name="vmf:vmf1_inputtoresult">
            #          <xsl:template match="/">
            #          <xsl:template name="helper_function">
            'template_start': r'<xsl:template\s+(?:name|match)=',
            
            # Template end pattern
            # Example: </xsl:template>
            'template_end': r'</xsl:template>',
            
            # Variable declarations
            # Examples: <xsl:variable name="target" select="//Target"/>
            #          <xsl:variable name="var196_nested" select="."/>
            #          <xsl:variable name="globalVar" select="'test'"/>
            'variable_declaration': r'<xsl:variable\s+name=',
            
            # Import/Include statements
            # Examples: <xsl:import href="common_templates.xsl"/>
            #          <xsl:include href="helper_functions.xslt"/>
            'import_include': r'<xsl:(?:import|include)\s+href=',
            
            # Choose block start
            # Example: <xsl:choose>
            'choose_start': r'<xsl:choose>',
            
            # Choose block end
            # Example: </xsl:choose>
            'choose_end': r'</xsl:choose>',
            
            # Function definitions (XSLT 2.0+)
            # Examples: <xsl:function name="my:custom-function">
            #          <xsl:function name="util:format-date">
            'function_start': r'<xsl:function\s+name=',
            
            # Function end
            # Example: </xsl:function>
            'function_end': r'</xsl:function>',
            
            # Helper template patterns - now configurable via self.helper_patterns
            # Examples depend on the patterns provided:
            # MapForce: vmf:vmf1_inputtoresult, vmf:vmf2_inputtoresult, vmf1_helper
            # Saxon: f:func1, func2_helper
            # Custom: util:helper_name, helper_function
            # Note: Helper detection is now handled by _is_helper_template() method
            
            # Namespace declarations
            # Examples: xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
            #          xmlns:vmf="http://mapforce.altova.com/"
            #          xmlns:fn="http://www.w3.org/2005/xpath-functions"
            'namespace_declaration': r'xmlns:\w+='
        }
    
    def chunk_file(self, file_path: Path) -> List[ChunkInfo]:
        """
        Chunk an XSLT file into manageable pieces
        
        Args:
            file_path: Path to XSLT file
            
        Returns:
            List of ChunkInfo objects
        """
        logger.info(f"Starting to chunk XSLT file: {file_path}")
        
        # Get file metadata
        file_metadata = self.file_reader.get_file_metadata(file_path)
        logger.info(f"File info: {file_metadata.line_count} lines, {file_metadata.size_bytes / 1024 / 1024:.1f} MB")
        
        # Read all lines for analysis
        all_lines = self.file_reader.read_lines(file_path)
        
        # Identify structural boundaries
        boundaries = self._identify_boundaries(all_lines)
        
        # Create initial chunks based on boundaries
        structural_chunks = self._create_structural_chunks(all_lines, boundaries)
        
        # Split large chunks if they exceed token limits
        final_chunks = self._split_oversized_chunks(structural_chunks)
        
        # Add dependencies and metadata
        self._enrich_chunks_with_metadata(final_chunks)
        
        logger.info(f"Created {len(final_chunks)} chunks from {file_path}")
        return final_chunks
    
    def _identify_boundaries(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Identify structural boundaries in XSLT file
        
        Args:
            lines: All lines from the file
            
        Returns:
            List of boundary information
        """
        boundaries = []
        
        for line_num, line in enumerate(lines, 1):
            # Check for template boundaries
            if re.search(self.xslt_patterns['template_start'], line):
                template_name = self._extract_template_name(line)
                template_type = self._classify_template_type(template_name, line)
                
                boundaries.append({
                    'type': 'template_start',
                    'line': line_num,
                    'name': template_name,
                    'template_type': template_type,
                    'content': line.strip()
                })
            
            elif re.search(self.xslt_patterns['template_end'], line):
                boundaries.append({
                    'type': 'template_end',
                    'line': line_num,
                    'content': line.strip()
                })
            
            # Check for variable declarations
            elif re.search(self.xslt_patterns['variable_declaration'], line):
                var_name = self._extract_variable_name(line)
                boundaries.append({
                    'type': 'variable_declaration',
                    'line': line_num,
                    'name': var_name,
                    'content': line.strip()
                })
            
            # Check for imports/includes
            elif re.search(self.xslt_patterns['import_include'], line):
                href = self._extract_href(line)
                boundaries.append({
                    'type': 'import_include',
                    'line': line_num,
                    'href': href,
                    'content': line.strip()
                })
            
            # Check for choose blocks
            elif re.search(self.xslt_patterns['choose_start'], line):
                boundaries.append({
                    'type': 'choose_start',
                    'line': line_num,
                    'content': line.strip()
                })
            
            elif re.search(self.xslt_patterns['choose_end'], line):
                boundaries.append({
                    'type': 'choose_end',
                    'line': line_num,
                    'content': line.strip()
                })
        
        return boundaries
    
    def _create_structural_chunks(self, lines: List[str], boundaries: List[Dict[str, Any]]) -> List[ChunkInfo]:
        """
        Create chunks based on structural boundaries
        
        Args:
            lines: All lines from file
            boundaries: Identified boundaries
            
        Returns:
            List of initial chunks
        """
        chunks = []
        current_chunk_start = 1
        template_stack = []  # Track nested templates
        
        for i, boundary in enumerate(boundaries):
            if boundary['type'] == 'template_start':
                # End previous chunk if it exists
                if current_chunk_start < boundary['line']:
                    chunk = self._create_chunk(
                        lines, current_chunk_start, boundary['line'] - 1,
                        ChunkType.UNKNOWN, None, len(chunks)
                    )
                    if chunk.lines:  # Only add non-empty chunks
                        chunks.append(chunk)
                
                template_stack.append(boundary)
                current_chunk_start = boundary['line']
            
            elif boundary['type'] == 'template_end':
                if template_stack:
                    template_start = template_stack.pop()
                    
                    # Create template chunk
                    chunk = self._create_chunk(
                        lines, template_start['line'], boundary['line'],
                        template_start['template_type'], 
                        template_start['name'], len(chunks)
                    )
                    chunks.append(chunk)
                    current_chunk_start = boundary['line'] + 1
        
        # Handle remaining lines
        if current_chunk_start <= len(lines):
            chunk = self._create_chunk(
                lines, current_chunk_start, len(lines),
                ChunkType.UNKNOWN, None, len(chunks)
            )
            if chunk.lines:
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, lines: List[str], start_line: int, end_line: int, 
                     chunk_type: ChunkType, name: Optional[str], chunk_id: int) -> ChunkInfo:
        """
        Create a chunk from line range
        
        Args:
            lines: All file lines
            start_line: Starting line (1-based)
            end_line: Ending line (1-based, inclusive)
            chunk_type: Type of chunk
            name: Name of the chunk (e.g., template name)
            chunk_id: Unique chunk identifier
            
        Returns:
            ChunkInfo object
        """
        chunk_lines = lines[start_line - 1:end_line]
        chunk_text = '\n'.join(chunk_lines)
        estimated_tokens = self.token_counter.estimate_tokens(chunk_text)
        
        return ChunkInfo(
            chunk_id=f"chunk_{chunk_id:03d}",
            chunk_type=chunk_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            lines=chunk_lines,
            estimated_tokens=estimated_tokens,
            dependencies=[],
            metadata={}
        )
    
    def _split_oversized_chunks(self, chunks: List[ChunkInfo]) -> List[ChunkInfo]:
        """
        Split chunks that exceed token limits
        
        Args:
            chunks: Initial chunks
            
        Returns:
            Chunks with size limits enforced
        """
        final_chunks = []
        
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.MAIN_TEMPLATE and chunk.estimated_tokens > self.main_template_split_threshold:
                # NEW: Use semantic sub-chunking for large main templates
                sub_chunks = self._split_large_main_template(chunk)
                final_chunks.extend(sub_chunks)
            elif chunk.estimated_tokens <= self.max_tokens_per_chunk:
                final_chunks.append(chunk)
            else:
                # Existing logic for other oversized chunks
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    def _split_large_chunk(self, chunk: ChunkInfo) -> List[ChunkInfo]:
        """
        Split a large chunk into smaller pieces
        
        Args:
            chunk: Large chunk to split
            
        Returns:
            List of smaller chunks
        """
        sub_chunks = []
        lines = chunk.lines
        current_lines = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.token_counter.estimate_tokens(line)
            
            # Check if adding this line would exceed limit
            if current_tokens + line_tokens > self.max_tokens_per_chunk and current_lines:
                # Create sub-chunk
                sub_chunk = ChunkInfo(
                    chunk_id=f"{chunk.chunk_id}_sub_{len(sub_chunks)}",
                    chunk_type=chunk.chunk_type,
                    name=f"{chunk.name}_part_{len(sub_chunks)}" if chunk.name else None,
                    start_line=chunk.start_line,  # Approximate
                    end_line=chunk.start_line + len(current_lines),
                    lines=current_lines.copy(),
                    estimated_tokens=current_tokens,
                    dependencies=chunk.dependencies.copy(),
                    metadata=chunk.metadata.copy()
                )
                sub_chunks.append(sub_chunk)
                
                # Start new sub-chunk with overlap
                overlap_lines = self._get_overlap_lines(current_lines)
                current_lines = overlap_lines + [line]
                current_tokens = sum(self.token_counter.estimate_tokens(l) for l in current_lines)
            else:
                current_lines.append(line)
                current_tokens += line_tokens
        
        # Add final sub-chunk
        if current_lines:
            sub_chunk = ChunkInfo(
                chunk_id=f"{chunk.chunk_id}_sub_{len(sub_chunks)}",
                chunk_type=chunk.chunk_type,
                name=f"{chunk.name}_part_{len(sub_chunks)}" if chunk.name else None,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                lines=current_lines,
                estimated_tokens=current_tokens,
                dependencies=chunk.dependencies.copy(),
                metadata=chunk.metadata.copy()
            )
            sub_chunks.append(sub_chunk)
        
        return sub_chunks
    
    def _get_overlap_lines(self, lines: List[str]) -> List[str]:
        """Get lines for overlap between chunks"""
        overlap_lines = []
        current_tokens = 0
        
        # Start from the end and work backwards
        for line in reversed(lines):
            line_tokens = self.token_counter.estimate_tokens(line)
            if current_tokens + line_tokens > self.overlap_tokens:
                break
            overlap_lines.insert(0, line)
            current_tokens += line_tokens
        
        return overlap_lines
    
    def _enrich_chunks_with_metadata(self, chunks: List[ChunkInfo]):
        """
        Add dependencies and metadata to chunks
        
        Args:
            chunks: Chunks to enrich
        """
        for chunk in chunks:
            # Extract dependencies (variables, templates referenced)
            chunk.dependencies = self._extract_dependencies(chunk.text)
            
            # Add metadata
            chunk.metadata.update({
                'has_choose_blocks': bool(re.search(self.xslt_patterns['choose_start'], chunk.text)),
                'has_variables': bool(re.search(self.xslt_patterns['variable_declaration'], chunk.text)),
                # XPath expressions detection
                # Examples: //Target, @value, /root/element[1], .//child::*, ancestor::node()
                'has_xpath': bool(re.search(r'(//|@\w+|\.\./|\./)[\w\[\]\/\.\(\):@-]*|@\w+|select="[^"]*[/@]', chunk.text)),
                'complexity_score': self._calculate_complexity_score(chunk.text)
            })
    
    def _extract_template_name(self, line: str) -> Optional[str]:
        """Extract template name from template declaration"""
        name_match = re.search(r'name="([^"]+)"', line)
        if name_match:
            return name_match.group(1)
        
        match_match = re.search(r'match="([^"]+)"', line)
        if match_match:
            return f"match:{match_match.group(1)}"
        
        return None
    
    def _is_helper_template(self, name: str) -> bool:
        """Check if a template name matches any helper pattern"""
        for pattern in self.helper_patterns:
            if re.search(pattern, name):
                return True
        return False
    
    def _classify_template_type(self, name: Optional[str], line: str) -> ChunkType:
        """Classify template type based on name and content"""
        if name and self._is_helper_template(name):
            return ChunkType.HELPER_TEMPLATE
        elif name and name.startswith('match:'):
            return ChunkType.MAIN_TEMPLATE
        else:
            return ChunkType.MAIN_TEMPLATE
    
    def _extract_variable_name(self, line: str) -> Optional[str]:
        """Extract variable name from variable declaration"""
        match = re.search(r'name="([^"]+)"', line)
        return match.group(1) if match else None
    
    def _extract_href(self, line: str) -> Optional[str]:
        """Extract href from import/include statement"""
        match = re.search(r'href="([^"]+)"', line)
        return match.group(1) if match else None
    
    def _extract_dependencies(self, text: str) -> List[str]:
        """
        Extract dependencies from chunk text
        
        Finds variable references, template calls, and function calls that indicate
        dependencies between chunks or external resources.
        """
        dependencies = []
        
        # Extract variable references
        # Examples: $target, $var196_nested, $input, $globalVar
        # Pattern matches: <xsl:value-of select="$target"/>
        #                 <xsl:when test="$input='P'">
        #                 <xsl:with-param name="input" select="$var196_nested"/>
        var_refs = re.findall(r'\$(\w+)', text)
        dependencies.extend([f"var:{var}" for var in var_refs])
        
        # Extract template calls
        # Examples: vmf:vmf1_inputtoresult, helper_function, format_date
        # Pattern matches: <xsl:call-template name="vmf:vmf1_inputtoresult">
        #                 <xsl:call-template name="helper_function">
        template_calls = re.findall(r'call-template\s+name="([^"]+)"', text)
        dependencies.extend([f"template:{template}" for template in template_calls])
        
        # Extract function calls (XSLT 2.0+ and extension functions)
        # Examples: fn:count(), xs:string(), custom:format()
        # Pattern matches: fn:count($items), xs:string(@value), custom:format(.)
        function_calls = re.findall(r'(\w+:\w+)\s*\(', text)
        dependencies.extend([f"function:{func}" for func in function_calls])
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score for chunk"""
        base_score = 1.0
        
        # Count different XSLT constructs
        choose_count = len(re.findall(self.xslt_patterns['choose_start'], text))
        variable_count = len(re.findall(self.xslt_patterns['variable_declaration'], text))
        xpath_count = len(re.findall(r'(//|@\w+|\.\./|\./)[\w\[\]\/\.\(\):@-]*|@\w+|select="[^"]*[/@]', text))
        
        # Calculate complexity
        base_score += choose_count * 0.5
        base_score += variable_count * 0.2
        base_score += xpath_count * 0.1
        
        # Normalize by text length
        if len(text) > 0:
            base_score = base_score * (len(text) / 1000)  # Per 1000 characters
        
        return min(base_score, 10.0)  # Cap at 10.0

    def _identify_main_template_logical_sections(self, lines: List[str], start_line: int) -> List[Dict]:
        """
        Identify logical sections within large main templates - GENERIC approach
        
        This method identifies semantic boundaries that work across different XSLT files:
        1. Major output element boundaries (most generic)
        2. Top-level for-each loops (universal XSLT pattern)  
        3. Variable declaration clusters (common pattern)
        4. Choose block boundaries (universal conditional logic)
        5. Comment-based sections (if present)
        
        Args:
            lines: All lines from the template
            start_line: Starting line number of the template
            
        Returns:
            List of logical section boundaries
        """
        sections = []
        
        # Find major output elements - these are the most reliable boundaries
        major_elements = self._find_major_output_elements(lines)
        sections.extend(major_elements)
        
        # Find top-level for-each loops - universal XSLT pattern
        for_each_loops = self._find_top_level_for_each_loops(lines, start_line)
        sections.extend(for_each_loops)
        
        # Find variable declaration clusters
        variable_clusters = self._find_variable_declaration_clusters(lines)
        sections.extend(variable_clusters)
        
        # Find major choose blocks
        choose_blocks = self._find_major_choose_blocks(lines)
        sections.extend(choose_blocks)
        
        # Sort by line number and remove duplicates
        sections = sorted(sections, key=lambda x: x['line'])
        
        # Remove duplicates (keep the first occurrence)
        unique_sections = []
        seen_lines = set()
        for section in sections:
            if section['line'] not in seen_lines:
                unique_sections.append(section)
                seen_lines.add(section['line'])
        
        return unique_sections

    def _find_major_output_elements(self, lines: List[str]) -> List[Dict]:
        """
        Find major output XML elements - universal pattern
        Look for elements like <Party>, <Query>, <Individual>, <IdentityDocument>
        Pattern: <(?!xsl:|/)([A-Z][a-zA-Z]{3,})
        """
        elements = []
        
        for line_num, line in enumerate(lines, 1):
            # Look for major output elements (capitalized, not XSLT, not closing)
            # Examples: <Party>, <Query>, <Individual>, <IdentityDocument>
            match = re.search(r'<(?!xsl:|/)([A-Z][a-zA-Z]{3,})', line.strip())
            if match:
                element_name = match.group(1)
                # Skip common attributes and short elements
                if element_name not in ['XML', 'HTTP', 'URI', 'URL', 'ID']:
                    elements.append({
                        'type': 'major_output_element',
                        'line': line_num,
                        'element_name': element_name,
                        'content': line.strip()
                    })
        
        return elements

    def _find_top_level_for_each_loops(self, lines: List[str], template_start: int) -> List[Dict]:
        """
        Find top-level for-each loops - universal XSLT pattern
        Only consider loops at base indentation level (not deeply nested)
        Track: select attribute, indentation level, line position
        """
        loops = []
        base_indent = None
        
        for line_num, line in enumerate(lines, 1):
            # Find for-each loops
            if re.search(r'<xsl:for-each\s+select=', line):
                # Determine indentation level
                indent = len(line) - len(line.lstrip())
                
                # Set base indentation from first for-each we find
                if base_indent is None:
                    base_indent = indent
                
                # Only consider loops at base indentation level (top-level)
                if indent <= base_indent + 4:  # Allow slight variation
                    select_match = re.search(r'select="([^"]+)"', line)
                    select_path = select_match.group(1) if select_match else 'unknown'
                    
                    loops.append({
                        'type': 'top_level_for_each',
                        'line': line_num,
                        'select_path': select_path,
                        'indent_level': indent,
                        'content': line.strip()
                    })
        
        return loops

    def _find_variable_declaration_clusters(self, lines: List[str]) -> List[Dict]:
        """
        Find clusters of variable declarations
        Group related variables that should stay together
        """
        clusters = []
        current_cluster = []
        
        for line_num, line in enumerate(lines, 1):
            if re.search(self.xslt_patterns['variable_declaration'], line):
                current_cluster.append({
                    'line': line_num,
                    'content': line.strip()
                })
            else:
                # If we have a cluster and hit a non-variable line, close the cluster
                if current_cluster and len(current_cluster) >= 2:
                    clusters.append({
                        'type': 'variable_cluster',
                        'line': current_cluster[0]['line'],
                        'cluster_size': len(current_cluster),
                        'content': f"Variable cluster ({len(current_cluster)} variables)"
                    })
                current_cluster = []
        
        # Handle final cluster
        if current_cluster and len(current_cluster) >= 2:
            clusters.append({
                'type': 'variable_cluster',
                'line': current_cluster[0]['line'],
                'cluster_size': len(current_cluster),
                'content': f"Variable cluster ({len(current_cluster)} variables)"
            })
        
        return clusters

    def _find_major_choose_blocks(self, lines: List[str]) -> List[Dict]:
        """
        Find major choose blocks that can serve as boundaries
        Must handle nested choose blocks correctly
        """
        blocks = []
        choose_stack = []
        
        for line_num, line in enumerate(lines, 1):
            if re.search(self.xslt_patterns['choose_start'], line):
                choose_stack.append({
                    'start_line': line_num,
                    'indent': len(line) - len(line.lstrip())
                })
            elif re.search(self.xslt_patterns['choose_end'], line):
                if choose_stack:
                    choose_info = choose_stack.pop()
                    # Only consider top-level choose blocks (not deeply nested)
                    if len(choose_stack) == 0:  # Top-level choose block
                        blocks.append({
                            'type': 'major_choose_block',
                            'line': choose_info['start_line'],
                            'end_line': line_num,
                            'content': f"Choose block ({choose_info['start_line']}-{line_num})"
                        })
        
        return blocks

    def _split_large_main_template(self, chunk: ChunkInfo) -> List[ChunkInfo]:
        """
        Entry point for main template decomposition
        Calls _identify_main_template_logical_sections and _create_semantic_sub_chunks
        Only triggers for MAIN_TEMPLATE chunks > 20,000 tokens
        """
        logger.info(f"Splitting large main template: {chunk.chunk_id} ({chunk.estimated_tokens} tokens)")
        
        # Identify logical sections within the main template
        sections = self._identify_main_template_logical_sections(chunk.lines, chunk.start_line)
        
        # Create semantic sub-chunks based on the identified sections
        sub_chunks = self._create_semantic_sub_chunks(chunk, sections)
        
        logger.info(f"Split main template into {len(sub_chunks)} sub-chunks")
        return sub_chunks

    def _create_semantic_sub_chunks(self, chunk: ChunkInfo, sections: List[Dict]) -> List[ChunkInfo]:
        """
        Split oversized main template into logical sub-chunks
        Target size: 3,000-5,000 tokens per sub-chunk
        Minimum size: 1,000 tokens (avoid tiny fragments)
        Overlap: 200-500 tokens with variable declarations and context
        """
        sub_chunks = []
        lines = chunk.lines
        
        # If no sections found, fall back to simple splitting
        if not sections:
            logger.warning(f"No logical sections found in {chunk.chunk_id}, using simple split")
            return self._split_large_chunk(chunk)
        
        # Create boundaries for sub-chunks
        boundaries = [0]  # Start with first line
        current_tokens = 0
        min_chunk_tokens = 1000
        target_chunk_tokens = 4000
        max_chunk_tokens = 6000
        
        for section in sections:
            # Calculate tokens up to this section
            section_line_idx = section['line'] - 1  # Convert to 0-based index
            if section_line_idx < len(lines):
                tokens_to_section = sum(
                    self.token_counter.estimate_tokens(lines[i]) 
                    for i in range(boundaries[-1], min(section_line_idx, len(lines)))
                )
                
                # If adding this section would create a good-sized chunk
                if (current_tokens + tokens_to_section >= target_chunk_tokens or 
                    current_tokens + tokens_to_section >= max_chunk_tokens):
                    
                    # Only create boundary if we have minimum tokens
                    if current_tokens >= min_chunk_tokens:
                        boundaries.append(section_line_idx)
                        current_tokens = 0
                    else:
                        current_tokens += tokens_to_section
                else:
                    current_tokens += tokens_to_section
        
        # Ensure we end with the last line
        if boundaries[-1] < len(lines):
            boundaries.append(len(lines))
        
        # Create sub-chunks with overlap
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            
            # Add overlap from previous chunk (except for first chunk)
            if i > 0:
                overlap_start = max(0, start_idx - self._calculate_overlap_lines(lines, start_idx))
                chunk_lines = lines[overlap_start:end_idx]
                actual_start_line = chunk.start_line + overlap_start
            else:
                chunk_lines = lines[start_idx:end_idx]
                actual_start_line = chunk.start_line + start_idx
            
            # Create sub-chunk
            sub_chunk = ChunkInfo(
                chunk_id=f"{chunk.chunk_id}_sub_{i:02d}",
                chunk_type=ChunkType.MAIN_TEMPLATE,
                name=f"{chunk.name}_section_{i+1}" if chunk.name else f"main_template_section_{i+1}",
                start_line=actual_start_line,
                end_line=chunk.start_line + end_idx - 1,
                lines=chunk_lines,
                estimated_tokens=sum(self.token_counter.estimate_tokens(line) for line in chunk_lines),
                dependencies=chunk.dependencies.copy(),
                metadata=chunk.metadata.copy()
            )
            
            # Add section-specific metadata
            sub_chunk.metadata.update({
                'is_sub_chunk': True,
                'parent_chunk_id': chunk.chunk_id,
                'sub_chunk_index': i,
                'logical_sections': [s for s in sections if start_idx <= s['line'] - 1 < end_idx]
            })
            
            sub_chunks.append(sub_chunk)
        
        return sub_chunks

    def _calculate_overlap_lines(self, lines: List[str], start_idx: int) -> int:
        """
        Calculate number of lines to include as overlap
        Focus on minimal context - just essential variable declarations and structure
        """
        overlap_lines = 0
        overlap_tokens = 0
        target_overlap_tokens = min(self.overlap_tokens // 4, 100)  # Much smaller overlap - max 100 tokens
        max_overlap_lines = 10  # Hard limit to prevent excessive overlap
        
        # Look backwards from start_idx to find essential context only
        for i in range(start_idx - 1, max(0, start_idx - max_overlap_lines - 1), -1):
            if i < len(lines):
                line = lines[i]
                line_tokens = self.token_counter.estimate_tokens(line)
                
                # Only include essential context: variable declarations and immediate structure
                is_essential = (
                    re.search(self.xslt_patterns['variable_declaration'], line) or
                    re.search(r'<xsl:for-each', line) or
                    line.strip().startswith('</') or  # Closing tags for context
                    line.strip() == '' or  # Empty lines for readability
                    (overlap_lines < 3 and overlap_tokens + line_tokens <= target_overlap_tokens)  # First few lines
                )
                
                if is_essential and overlap_tokens + line_tokens <= target_overlap_tokens:
                    overlap_lines += 1
                    overlap_tokens += line_tokens
                else:
                    # Stop if we have enough context or hit non-essential content
                    break
        
        return min(overlap_lines, max_overlap_lines)  # Enforce hard limit


# Utility functions
def quick_chunk_file(file_path: str, max_tokens: int = 15000) -> List[Dict[str, Any]]:
    """Quick utility to chunk an XSLT file"""
    chunker = XSLTChunker(max_tokens_per_chunk=max_tokens)
    chunks = chunker.chunk_file(Path(file_path))
    
    return [
        {
            'id': chunk.chunk_id,
            'type': chunk.chunk_type.value,
            'name': chunk.name,
            'start_line': chunk.start_line,
            'end_line': chunk.end_line,
            'line_count': chunk.line_count,
            'estimated_tokens': chunk.estimated_tokens,
            'dependencies': chunk.dependencies
        }
        for chunk in chunks
    ]