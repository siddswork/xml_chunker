#!/usr/bin/env python3
"""
Enhanced Interactive XSLT PoC - Detailed Mapping Specification with Context Management

This enhanced version focuses on:
1. Extracting detailed mapping specifications (source→destination→transformation)
2. Progressive summarization with context reset
3. File-based understanding storage
4. Target: 20% chunk coverage for rapid validation
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import time
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not found")

import openai


@dataclass
class SimpleChunk:
    """Simple chunk structure for PoC"""
    id: str
    content: str
    description: str
    chunk_type: str
    templates_defined: List[str]
    template_calls: List[str]
    variables_defined: List[str]
    dependencies: List[str]
    line_start: int
    line_end: int
    token_count: int


class SmartXSLTChunker:
    """Smart XSLT chunker that breaks down large templates into logical sections"""
    
    def __init__(self):
        self.max_chunk_size = 100  # lines
        self.min_chunk_size = 10   # lines
    
    def chunk_xslt_file(self, file_path: str) -> List[SimpleChunk]:
        """Chunk XSLT file with smart splitting of large templates"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        chunks = []
        
        # Find template boundaries
        template_boundaries = self._find_template_boundaries(lines)
        
        # Process each template
        for i, (start, end, template_info) in enumerate(template_boundaries):
            template_size = end - start
            
            if template_size <= self.max_chunk_size:
                # Small template - keep as single chunk
                chunk = self._create_chunk(
                    chunk_id=f"chunk_{i:03d}",
                    lines=lines[start:end],
                    line_start=start + 1,
                    line_end=end,
                    template_info=template_info
                )
                chunks.append(chunk)
            else:
                # Large template - split into logical sub-chunks
                sub_chunks = self._split_large_template(
                    lines[start:end], 
                    start, 
                    template_info,
                    base_chunk_id=f"chunk_{i:03d}"
                )
                chunks.extend(sub_chunks)
        
        print(f"✅ Created {len(chunks)} chunks from XSLT file")
        return chunks
    
    def _find_template_boundaries(self, lines: List[str]) -> List[tuple]:
        """Find template start and end boundaries"""
        boundaries = []
        current_template = None
        
        for i, line in enumerate(lines):
            if '<xsl:template' in line:
                if current_template:
                    # End previous template
                    boundaries.append(current_template)
                
                # Start new template
                template_info = self._extract_template_info(line)
                current_template = [i, None, template_info]
            
            elif '</xsl:template>' in line and current_template:
                # End current template
                current_template[1] = i + 1
                boundaries.append(tuple(current_template))
                current_template = None
        
        # Handle last template
        if current_template:
            current_template[1] = len(lines)
            boundaries.append(tuple(current_template))
        
        return boundaries
    
    def _extract_template_info(self, line: str) -> Dict[str, Any]:
        """Extract template information from template declaration"""
        info = {"type": "template", "name": None, "match": None}
        
        # Extract name
        name_match = re.search(r'name="([^"]+)"', line)
        if name_match:
            info["name"] = name_match.group(1)
        
        # Extract match
        match_match = re.search(r'match="([^"]+)"', line)
        if match_match:
            info["match"] = match_match.group(1)
        
        # Determine type
        if info["name"] and "vmf:" in info["name"]:
            info["type"] = "helper"
        elif info["match"]:
            info["type"] = "main"
        
        return info
    
    def _split_large_template(self, template_lines: List[str], start_line: int, 
                            template_info: Dict[str, Any], base_chunk_id: str) -> List[SimpleChunk]:
        """Split large template into logical sub-chunks"""
        
        sub_chunks = []
        current_chunk_lines = []
        current_chunk_start = start_line
        chunk_counter = 0
        
        # Look for logical boundaries in the template
        for i, line in enumerate(template_lines):
            current_chunk_lines.append(line)
            
            # Check for logical boundaries
            if self._is_logical_boundary(line) and len(current_chunk_lines) >= self.min_chunk_size:
                # Create sub-chunk
                sub_chunk = self._create_chunk(
                    chunk_id=f"{base_chunk_id}_sub_{chunk_counter:03d}",
                    lines=current_chunk_lines,
                    line_start=current_chunk_start + 1,
                    line_end=current_chunk_start + len(current_chunk_lines),
                    template_info=template_info,
                    is_sub_chunk=True
                )
                sub_chunks.append(sub_chunk)
                
                # Reset for next chunk
                current_chunk_lines = []
                current_chunk_start = start_line + i + 1
                chunk_counter += 1
            
            # Force split if chunk gets too large
            elif len(current_chunk_lines) >= self.max_chunk_size:
                sub_chunk = self._create_chunk(
                    chunk_id=f"{base_chunk_id}_sub_{chunk_counter:03d}",
                    lines=current_chunk_lines,
                    line_start=current_chunk_start + 1,
                    line_end=current_chunk_start + len(current_chunk_lines),
                    template_info=template_info,
                    is_sub_chunk=True
                )
                sub_chunks.append(sub_chunk)
                
                current_chunk_lines = []
                current_chunk_start = start_line + i + 1
                chunk_counter += 1
        
        # Handle remaining lines
        if current_chunk_lines:
            sub_chunk = self._create_chunk(
                chunk_id=f"{base_chunk_id}_sub_{chunk_counter:03d}",
                lines=current_chunk_lines,
                line_start=current_chunk_start + 1,
                line_end=current_chunk_start + len(current_chunk_lines),
                template_info=template_info,
                is_sub_chunk=True
            )
            sub_chunks.append(sub_chunk)
        
        return sub_chunks
    
    def _is_logical_boundary(self, line: str) -> bool:
        """Check if line represents a logical boundary for splitting"""
        line_stripped = line.strip()
        
        # Major structural elements
        if any(tag in line_stripped for tag in [
            '</xsl:for-each>',
            '</xsl:choose>',
            '</xsl:if>',
            '</xsl:variable>',
            '</xsl:when>',
            '</xsl:otherwise>'
        ]):
            return True
        
        # Variable declarations
        if '<xsl:variable' in line_stripped:
            return True
        
        # Comments
        if line_stripped.startswith('<!--'):
            return True
        
        return False
    
    def _create_chunk(self, chunk_id: str, lines: List[str], line_start: int, 
                     line_end: int, template_info: Dict[str, Any], is_sub_chunk: bool = False) -> SimpleChunk:
        """Create a chunk from lines"""
        
        content = '\n'.join(lines)
        
        # Extract metadata
        templates_defined = []
        template_calls = []
        variables_defined = []
        
        if not is_sub_chunk:
            if template_info.get("name"):
                templates_defined.append(template_info["name"])
            if template_info.get("match"):
                templates_defined.append(f"match:{template_info['match']}")
        
        # Find template calls
        for line in lines:
            calls = re.findall(r'<xsl:call-template\s+name="([^"]+)"', line)
            template_calls.extend(calls)
        
        # Find variables
        for line in lines:
            vars_def = re.findall(r'<xsl:variable\s+name="([^"]+)"', line)
            variables_defined.extend(vars_def)
        
        # Generate description
        if is_sub_chunk:
            description = f"Sub-section of {template_info.get('name', 'template')} - {template_info.get('type', 'processing')} logic"
        else:
            if template_info.get("name"):
                description = f"Template: {template_info['name']} ({template_info.get('type', 'unknown')})"
            elif template_info.get("match"):
                description = f"Main template matching: {template_info['match']}"
            else:
                description = "XSLT template"
        
        # Estimate token count (rough approximation)
        token_count = len(content.split())
        
        return SimpleChunk(
            id=chunk_id,
            content=content,
            description=description,
            chunk_type=template_info.get("type", "unknown"),
            templates_defined=templates_defined,
            template_calls=template_calls,
            variables_defined=variables_defined,
            dependencies=template_calls,
            line_start=line_start,
            line_end=line_end,
            token_count=token_count
        )


@dataclass
class MappingSpecification:
    """Detailed mapping specification for XSLT transformation"""
    id: str
    source_path: str
    destination_path: str
    transformation_type: str  # direct_mapping, conditional_mapping, function_call, etc.
    transformation_logic: Dict[str, Any]  # Enhanced with natural language description
    conditions: List[str]
    validation_rules: List[str]
    template_name: str
    chunk_source: str


@dataclass
class TemplateAnalysis:
    """Deep analysis of an XSLT template"""
    name: str
    purpose: str
    input_parameters: List[str]
    output_structure: str
    dependencies: List[str]
    complexity: str
    mappings: List[MappingSpecification]


class EnhancedXSLTExplorer:
    """Enhanced XSLT explorer with detailed mapping extraction and context management"""
    
    def __init__(self, openai_api_key: str, xslt_file_path: str, target_coverage: float = 1.0):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.xslt_file_path = xslt_file_path
        self.target_coverage = target_coverage
        
        # Initialize chunker and create chunks
        print("🔍 Chunking XSLT file...")
        chunker = SmartXSLTChunker()
        self.chunks = chunker.chunk_xslt_file(xslt_file_path)
        self.target_chunks = int(len(self.chunks) * target_coverage)
        
        print(f"✅ Created {len(self.chunks)} chunks, targeting {self.target_chunks} chunks ({target_coverage:.0%})")
        
        # Create indexes
        self.chunk_index = {chunk.id: chunk for chunk in self.chunks}
        
        # Exploration state
        self.chunks_explored = set()
        self.current_chunk_index = 0
        self.conversation_turns = 0
        self.context_resets = 0
        
        # Understanding storage (file-based)
        self.results_dir = Path("poc_results/enhanced_exploration")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.mapping_specs: List[MappingSpecification] = []
        self.template_analyses: List[TemplateAnalysis] = []
        
        # Cost tracking
        self.cost_tracker = {
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "cumulative_cost_usd": 0.0,
            "cost_per_phase": []
        }
        
        # Validation metrics to prove understanding is building
        self.validation_metrics = {
            "mappings_per_chunk": [],
            "understanding_depth_scores": [],
            "cross_references_found": [],
            "template_connections_discovered": [],
            "insights_quality_trend": [],
            "evolution_milestones": []
        }
        
        # LLM understanding storage
        self.llm_insights = []
        self.understanding_evolution = []
        
        # Available functions
        self.available_functions = {
            "get_current_chunk": self.get_current_chunk,
            "get_next_chunk": self.get_next_chunk,
            "analyze_chunk_mappings": self.analyze_chunk_mappings,
            "save_template_analysis": self.save_template_analysis,
            "get_understanding_summary": self.get_understanding_summary,
            "search_related_chunks": self.search_related_chunks,
            "save_llm_insights": self.save_llm_insights,
            "record_understanding_evolution": self.record_understanding_evolution,
            "get_validation_metrics": self.get_validation_metrics
        }
    
    def get_current_chunk(self) -> Dict[str, Any]:
        """Get the current chunk being analyzed"""
        if self.current_chunk_index < len(self.chunks):
            chunk = self.chunks[self.current_chunk_index]
            self.chunks_explored.add(chunk.id)
            
            return {
                "success": True,
                "chunk": asdict(chunk),
                "progress": f"{len(self.chunks_explored)}/{self.target_chunks}",
                "message": f"Current chunk: {chunk.id}"
            }
        
        return {"success": False, "message": "No more chunks to explore"}
    
    def get_next_chunk(self) -> Dict[str, Any]:
        """Move to the next chunk"""
        self.current_chunk_index += 1
        
        if self.current_chunk_index < len(self.chunks) and len(self.chunks_explored) < self.target_chunks:
            return self.get_current_chunk()
        else:
            return {
                "success": False,
                "message": f"Target coverage reached: {len(self.chunks_explored)}/{self.target_chunks} chunks explored"
            }
    
    def analyze_chunk_mappings(self, mapping_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Save detailed mapping analysis for current chunk"""
        
        if not mapping_analysis or not isinstance(mapping_analysis, dict):
            return {"success": False, "message": "Invalid mapping analysis provided"}
        
        # Extract mappings from analysis
        if "mappings" in mapping_analysis:
            for mapping_data in mapping_analysis["mappings"]:
                try:
                    # Handle both old string format and new enhanced format
                    transformation_logic = mapping_data.get("transformation_logic", "")
                    if isinstance(transformation_logic, str):
                        # Convert old string format to enhanced format
                        transformation_logic = {
                            "natural_language": transformation_logic,
                            "original_xslt": transformation_logic,
                            "rules": [],
                            "transformation_type": mapping_data.get("transformation_type", "unknown")
                        }
                    
                    mapping_spec = MappingSpecification(
                        id=f"mapping_{len(self.mapping_specs):03d}",
                        source_path=mapping_data.get("source_path", ""),
                        destination_path=mapping_data.get("destination_path", ""),
                        transformation_type=mapping_data.get("transformation_type", "unknown"),
                        transformation_logic=transformation_logic,
                        conditions=mapping_data.get("conditions", []),
                        validation_rules=mapping_data.get("validation_rules", []),
                        template_name=mapping_data.get("template_name", ""),
                        chunk_source=self.chunks[self.current_chunk_index].id if self.current_chunk_index < len(self.chunks) else ""
                    )
                    self.mapping_specs.append(mapping_spec)
                except Exception as e:
                    print(f"⚠️  Error creating mapping spec: {e}")
        
        # Save to file
        self._save_current_understanding()
        
        return {
            "success": True,
            "message": f"Saved {len(mapping_analysis.get('mappings', []))} mapping specifications",
            "total_mappings": len(self.mapping_specs)
        }
    
    def save_template_analysis(self, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Save detailed template analysis"""
        
        if not template_analysis or not isinstance(template_analysis, dict):
            return {"success": False, "message": "Invalid template analysis provided"}
        
        try:
            # Create template analysis
            analysis = TemplateAnalysis(
                name=template_analysis.get("name", ""),
                purpose=template_analysis.get("purpose", ""),
                input_parameters=template_analysis.get("input_parameters", []),
                output_structure=template_analysis.get("output_structure", ""),
                dependencies=template_analysis.get("dependencies", []),
                complexity=template_analysis.get("complexity", "unknown"),
                mappings=[]  # Mappings are handled separately
            )
            
            self.template_analyses.append(analysis)
            self._save_current_understanding()
            
            return {
                "success": True,
                "message": f"Saved template analysis for '{analysis.name}'",
                "total_templates": len(self.template_analyses)
            }
        
        except Exception as e:
            return {"success": False, "message": f"Error saving template analysis: {e}"}
    
    def get_understanding_summary(self) -> Dict[str, Any]:
        """Get current understanding summary"""
        
        return {
            "success": True,
            "summary": {
                "chunks_explored": len(self.chunks_explored),
                "target_chunks": self.target_chunks,
                "progress_percentage": (len(self.chunks_explored) / self.target_chunks) * 100,
                "mapping_specifications": len(self.mapping_specs),
                "template_analyses": len(self.template_analyses),
                "context_resets": self.context_resets,
                "conversation_turns": self.conversation_turns
            }
        }
    
    def search_related_chunks(self, search_pattern: str) -> Dict[str, Any]:
        """Search for chunks containing specific patterns"""
        
        matches = []
        for chunk in self.chunks:
            if re.search(search_pattern, chunk.content, re.IGNORECASE):
                matches.append({
                    "id": chunk.id,
                    "description": chunk.description,
                    "templates_defined": chunk.templates_defined
                })
        
        return {
            "success": True,
            "matches": matches[:5],  # Limit to 5 results
            "total_matches": len(matches),
            "message": f"Found {len(matches)} chunks matching '{search_pattern}'"
        }
    
    def save_llm_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Save LLM's understanding insights and observations"""
        
        if not insights or not isinstance(insights, dict):
            return {"success": False, "message": "Invalid insights provided"}
        
        # Add metadata
        insight_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "chunk_context": self.chunks[self.current_chunk_index].id if self.current_chunk_index < len(self.chunks) else "",
            "chunks_explored_so_far": len(self.chunks_explored),
            "insights": insights
        }
        
        self.llm_insights.append(insight_record)
        self._save_current_understanding()
        
        return {
            "success": True,
            "message": f"Saved LLM insights - total insights: {len(self.llm_insights)}",
            "total_insights": len(self.llm_insights)
        }
    
    def record_understanding_evolution(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record how LLM's understanding is evolving over time"""
        
        if not evolution_data or not isinstance(evolution_data, dict):
            return {"success": False, "message": "Invalid evolution data provided"}
        
        # Add metadata
        evolution_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "chunks_explored": len(self.chunks_explored),
            "progress_percentage": (len(self.chunks_explored) / self.target_chunks) * 100,
            "conversation_turn": self.conversation_turns,
            "evolution_data": evolution_data
        }
        
        self.understanding_evolution.append(evolution_record)
        self._calculate_validation_metrics()
        self._save_current_understanding()
        
        return {
            "success": True,
            "message": f"Recorded understanding evolution - total records: {len(self.understanding_evolution)}",
            "total_evolution_records": len(self.understanding_evolution)
        }
    
    def _calculate_validation_metrics(self):
        """Calculate validation metrics to prove understanding is building"""
        
        # Track mappings per chunk
        if len(self.chunks_explored) > 0:
            mappings_per_chunk = len(self.mapping_specs) / len(self.chunks_explored)
            self.validation_metrics["mappings_per_chunk"].append(mappings_per_chunk)
        
        # Calculate understanding depth score based on recent insights
        if self.llm_insights:
            recent_insights = self.llm_insights[-5:]  # Last 5 insights
            depth_score = sum(len(str(insight.get("insights", {}))) for insight in recent_insights) / len(recent_insights)
            self.validation_metrics["understanding_depth_scores"].append(depth_score)
        
        # Track cross-references found
        cross_refs = 0
        for spec in self.mapping_specs:
            if hasattr(spec, 'dependencies') and spec.dependencies:
                cross_refs += len(spec.dependencies)
        self.validation_metrics["cross_references_found"].append(cross_refs)
        
        # Track template connections discovered
        template_connections = len(set(spec.template_name for spec in self.mapping_specs if spec.template_name))
        self.validation_metrics["template_connections_discovered"].append(template_connections)
        
        # Track insights quality trend (based on length and detail)
        if self.llm_insights:
            last_insight = self.llm_insights[-1]
            quality_score = len(str(last_insight.get("insights", {}))) / 100  # Rough quality metric
            self.validation_metrics["insights_quality_trend"].append(quality_score)
        
        # Track evolution milestones
        if self.understanding_evolution:
            milestone = {
                "chunks_explored": len(self.chunks_explored),
                "mappings_extracted": len(self.mapping_specs),
                "insights_recorded": len(self.llm_insights),
                "understanding_breadth": len(set(chunk.chunk_type for chunk in self.chunks if chunk.id in self.chunks_explored))
            }
            self.validation_metrics["evolution_milestones"].append(milestone)
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics to prove understanding is building"""
        
        # Calculate trends
        mapping_trend = "increasing" if len(self.validation_metrics["mappings_per_chunk"]) > 1 and \
                       self.validation_metrics["mappings_per_chunk"][-1] > self.validation_metrics["mappings_per_chunk"][0] else "stable"
        
        understanding_trend = "deepening" if len(self.validation_metrics["understanding_depth_scores"]) > 1 and \
                             self.validation_metrics["understanding_depth_scores"][-1] > self.validation_metrics["understanding_depth_scores"][0] else "stable"
        
        return {
            "success": True,
            "metrics": {
                "mappings_per_chunk": self.validation_metrics["mappings_per_chunk"][-5:],  # Last 5 values
                "understanding_depth_scores": self.validation_metrics["understanding_depth_scores"][-5:],
                "cross_references_found": self.validation_metrics["cross_references_found"][-5:],
                "template_connections_discovered": self.validation_metrics["template_connections_discovered"][-5:],
                "insights_quality_trend": self.validation_metrics["insights_quality_trend"][-5:],
                "evolution_milestones": self.validation_metrics["evolution_milestones"][-3:]  # Last 3 milestones
            },
            "trends": {
                "mapping_extraction": mapping_trend,
                "understanding_depth": understanding_trend,
                "overall_progress": f"{len(self.chunks_explored)}/{self.target_chunks} chunks explored"
            },
            "validation_summary": {
                "total_mappings": len(self.mapping_specs),
                "total_insights": len(self.llm_insights),
                "total_evolution_records": len(self.understanding_evolution),
                "understanding_building": len(self.validation_metrics["evolution_milestones"]) > 0
            }
        }
    
    def _save_current_understanding(self):
        """Save current understanding to files"""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save mapping specifications
        mappings_file = self.results_dir / f"mapping_specifications_{timestamp}.json"
        with open(mappings_file, 'w') as f:
            json.dump([asdict(spec) for spec in self.mapping_specs], f, indent=2)
        
        # Save template analyses
        templates_file = self.results_dir / f"template_analyses_{timestamp}.json"
        with open(templates_file, 'w') as f:
            json.dump([asdict(analysis) for analysis in self.template_analyses], f, indent=2)
        
        # Save LLM insights
        insights_file = self.results_dir / f"llm_insights_{timestamp}.json"
        with open(insights_file, 'w') as f:
            json.dump(self.llm_insights, f, indent=2)
        
        # Save understanding evolution
        evolution_file = self.results_dir / f"understanding_evolution_{timestamp}.json"
        with open(evolution_file, 'w') as f:
            json.dump(self.understanding_evolution, f, indent=2)
        
        # Save validation metrics
        validation_file = self.results_dir / f"validation_metrics_{timestamp}.json"
        with open(validation_file, 'w') as f:
            json.dump(self.validation_metrics, f, indent=2)
        
        # Save exploration summary
        summary_file = self.results_dir / f"exploration_summary_{timestamp}.json"
        summary = {
            "timestamp": timestamp,
            "chunks_explored": list(self.chunks_explored),
            "progress": {
                "chunks_explored": len(self.chunks_explored),
                "target_chunks": self.target_chunks,
                "progress_percentage": (len(self.chunks_explored) / self.target_chunks) * 100
            },
            "statistics": {
                "mapping_specifications": len(self.mapping_specs),
                "template_analyses": len(self.template_analyses),
                "llm_insights": len(self.llm_insights),
                "understanding_evolution_records": len(self.understanding_evolution),
                "context_resets": self.context_resets,
                "conversation_turns": self.conversation_turns
            },
            "cost_tracking": self.cost_tracker,
            "validation_metrics": self.validation_metrics
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 UNDERSTANDING SAVED:")
        print(f"   📁 Directory: {self.results_dir}")
        print(f"   📄 Mappings: {len(self.mapping_specs)} specifications")
        print(f"   📋 Templates: {len(self.template_analyses)} analyses")
        print(f"   🧠 LLM Insights: {len(self.llm_insights)} records")
        print(f"   📈 Evolution: {len(self.understanding_evolution)} records")
        print(f"   📊 Validation Metrics: {len(self.validation_metrics.get('evolution_milestones', []))} milestones")
        print(f"{'~'*60}")
    
    def _should_reset_context(self) -> bool:
        """Determine if context should be reset"""
        return self.conversation_turns >= 15  # Reset every 15 turns
    
    def _reset_context(self) -> str:
        """Reset conversation context and return summary"""
        
        self.context_resets += 1
        self.conversation_turns = 0
        
        # Create progressive summary
        summary = f"""
PROGRESSIVE UNDERSTANDING SUMMARY (Reset #{self.context_resets}):

EXPLORATION PROGRESS:
- Chunks explored: {len(self.chunks_explored)}/{self.target_chunks} ({(len(self.chunks_explored)/self.target_chunks)*100:.1f}%)
- Mapping specifications extracted: {len(self.mapping_specs)}
- Template analyses completed: {len(self.template_analyses)}

RECENT MAPPINGS (last 5):
{json.dumps([asdict(spec) for spec in self.mapping_specs[-5:]], indent=2) if self.mapping_specs else "None yet"}

NEXT GOAL: Continue systematic chunk exploration and mapping extraction.
"""
        
        print(f"\n🔄 CONTEXT RESET #{self.context_resets}")
        print(f"📊 Progress: {len(self.chunks_explored)}/{self.target_chunks} chunks explored")
        print(f"💾 Understanding preserved in files")
        print(f"🔄 Starting fresh conversation context")
        print(f"{'█'*60}\n")
        return summary
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for GPT-4o-mini"""
        input_cost = (input_tokens / 1000) * 0.000150
        output_cost = (output_tokens / 1000) * 0.000600
        return input_cost + output_cost
    
    def _update_cost_tracking(self, input_tokens: int, output_tokens: int):
        """Update cost tracking"""
        
        call_cost = self._calculate_cost(input_tokens, output_tokens)
        
        self.cost_tracker["total_calls"] += 1
        self.cost_tracker["total_input_tokens"] += input_tokens
        self.cost_tracker["total_output_tokens"] += output_tokens
        self.cost_tracker["cumulative_cost_usd"] += call_cost
        
        print(f"\n💰 COST TRACKING:")
        print(f"   Call #{self.cost_tracker['total_calls']}: ${call_cost:.6f} | Total: ${self.cost_tracker['cumulative_cost_usd']:.6f}")
        print(f"   Tokens: {input_tokens:,} in, {output_tokens:,} out | Context turns: {self.conversation_turns}")
        print(f"{'-'*60}")
    
    async def start_enhanced_exploration(self) -> str:
        """Start enhanced exploration with detailed mapping extraction"""
        
        print(f"🚀 Starting Enhanced XSLT Exploration")
        print(f"📊 Target: {self.target_chunks} chunks ({self.target_coverage:.0%} coverage)")
        
        initial_prompt = f"""You are an expert XSLT analyst extracting detailed mapping specifications.

GOAL: Extract detailed source→destination→transformation mappings from XSLT chunks.

TARGET: Explore {self.target_chunks} chunks systematically and extract comprehensive mapping specifications.

AVAILABLE FUNCTIONS:
- get_current_chunk(): Get current chunk for analysis
- get_next_chunk(): Move to next chunk
- analyze_chunk_mappings(mapping_analysis): Save detailed mapping specifications
- save_template_analysis(template_analysis): Save template analysis
- get_understanding_summary(): Check progress
- search_related_chunks(pattern): Find related chunks
- save_llm_insights(insights): Save your understanding insights and observations
- record_understanding_evolution(evolution_data): Record how your understanding evolves
- get_validation_metrics(): Get metrics proving your understanding is building

IMPORTANT: Use save_llm_insights() to document your understanding and observations as you explore. Use record_understanding_evolution() to track how your understanding of the XSLT transforms over time. Use get_validation_metrics() periodically to verify your understanding is building.

REQUIRED OUTPUT FORMAT for analyze_chunk_mappings():
{{
  "mappings": [
    {{
      "source_path": "xpath/to/source/element",
      "destination_path": "xpath/to/destination/element", 
      "transformation_type": "direct_mapping|conditional_mapping|function_call|text_manipulation",
      "transformation_logic": {{
        "natural_language": "Clear description of what transformation does in plain English",
        "transformation_type": "conditional_lookup|direct_copy|computed_value|text_manipulation",
        "rules": [
          {{"condition": "input condition", "output": "result value"}},
          {{"condition": "default", "output": "fallback value"}}
        ],
        "original_xslt": "actual XSLT code snippet"
      }},
      "conditions": ["condition1", "condition2"],
      "validation_rules": ["rule1", "rule2"],
      "template_name": "template name"
    }}
  ]
}}

EXAMPLE of good transformation_logic:
{{
  "natural_language": "If input document type is 'P' or 'PT' (passport), convert to standardized code 'VPT'. Otherwise return empty.",
  "transformation_type": "conditional_lookup", 
  "rules": [
    {{"condition": "input = 'P'", "output": "VPT"}},
    {{"condition": "input = 'PT'", "output": "VPT"}},
    {{"condition": "default", "output": ""}}
  ],
  "original_xslt": "<xsl:choose><xsl:when test=\"$input='P'\">..."
}}

EXPLORATION STRATEGY:
1. get_current_chunk() to see current chunk
2. Extract ALL source→destination mappings from the chunk
3. Document transformation logic and conditions
4. Call analyze_chunk_mappings() with detailed analysis
5. Call save_llm_insights() with your observations
6. Call record_understanding_evolution() to track learning
7. get_next_chunk() and repeat
8. Continue until target coverage reached

FUNCTION CALL EXAMPLES:
- get_current_chunk() - No parameters needed
- analyze_chunk_mappings(mapping_analysis: object with mappings array)
- save_llm_insights(insights: object with observations and understanding)
- record_understanding_evolution(evolution_data: object with milestone and understanding_level)

Start by getting the current chunk and analyzing its mappings in detail."""
        
        # Start exploration
        result = await self._call_llm_with_functions(initial_prompt)
        
        # Save final results
        self._save_current_understanding()
        
        return result
    
    async def _call_llm_with_functions(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """Enhanced LLM calling with context management"""
        
        # Initialize or manage conversation history
        if conversation_history is None:
            conversation_history = [{"role": "user", "content": prompt}]
        elif self._should_reset_context():
            # Reset context with progressive summary
            summary = self._reset_context()
            conversation_history = [{"role": "user", "content": summary + "\n\n" + prompt}]
        
        # Check completion
        if len(self.chunks_explored) >= self.target_chunks:
            return f"✅ Target coverage reached: {len(self.chunks_explored)}/{self.target_chunks} chunks explored"
        
        # Safety limit - increased for complete exploration
        if self.conversation_turns > 200:
            return f"⚠️ Safety limit reached: {self.conversation_turns} turns"
        
        # Define function schemas
        functions = [
            {
                "name": "get_current_chunk",
                "description": "Get the current chunk for analysis",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_next_chunk", 
                "description": "Move to the next chunk",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "analyze_chunk_mappings",
                "description": "Save detailed mapping specifications for current chunk",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mapping_analysis": {
                            "type": "object",
                            "description": "Detailed mapping analysis with source→destination→transformation"
                        }
                    },
                    "required": ["mapping_analysis"]
                }
            },
            {
                "name": "save_template_analysis",
                "description": "Save detailed template analysis",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "template_analysis": {
                            "type": "object",
                            "description": "Detailed template analysis"
                        }
                    },
                    "required": ["template_analysis"]
                }
            },
            {
                "name": "get_understanding_summary",
                "description": "Get current exploration progress",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "search_related_chunks",
                "description": "Search for chunks containing specific patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_pattern": {"type": "string"}
                    },
                    "required": ["search_pattern"]
                }
            },
            {
                "name": "save_llm_insights",
                "description": "Save LLM's understanding insights and observations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "insights": {
                            "type": "object",
                            "description": "LLM's insights, observations, and understanding"
                        }
                    },
                    "required": ["insights"]
                }
            },
            {
                "name": "record_understanding_evolution",
                "description": "Record how LLM's understanding is evolving over time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "evolution_data": {
                            "type": "object",
                            "description": "Data about how understanding has evolved"
                        }
                    },
                    "required": ["evolution_data"]
                }
            },
            {
                "name": "get_validation_metrics",
                "description": "Get validation metrics to prove understanding is building over time",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
        
        try:
            tools = [{"type": "function", "function": func} for func in functions]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history,
                tools=tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=2000
            )
            
            message = response.choices[0].message
            self.conversation_turns += 1
            
            # Track costs
            usage = response.usage
            self._update_cost_tracking(usage.prompt_tokens, usage.completion_tokens)
            
            if message.tool_calls:
                # Add assistant message to conversation
                conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message.tool_calls
                    ]
                })
                
                # Execute function calls
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"\n{'='*60}")
                    print(f"🔧 FUNCTION CALL: {function_name}({list(function_args.keys())})")
                    print(f"{'='*60}")
                    
                    try:
                        if function_name in self.available_functions:
                            # Handle cases where LLM passes arrays instead of objects
                            if isinstance(function_args, list):
                                function_result = {"success": False, "message": f"Function {function_name} expects object parameters, got array"}
                            elif function_name in ['get_current_chunk', 'get_next_chunk', 'get_understanding_summary', 'get_validation_metrics']:
                                # Functions that take no parameters
                                function_result = self.available_functions[function_name]()
                            else:
                                function_result = self.available_functions[function_name](**function_args)
                        else:
                            function_result = {"success": False, "message": f"Unknown function: {function_name}"}
                    except Exception as e:
                        function_result = {"success": False, "message": f"Function error: {str(e)}"}
                    
                    # Add function result to conversation
                    conversation_history.append({
                        "role": "tool",
                        "content": json.dumps(function_result, indent=2),
                        "tool_call_id": tool_call.id
                    })
                    
                    print(f"✅ RESULT: {function_result.get('success', 'unknown')}")
                    if 'message' in function_result:
                        print(f"📝 MESSAGE: {function_result['message']}")
                    print(f"{'='*60}\n")
                
                # Continue exploration
                continue_prompt = f"Continue systematic exploration. Progress: {len(self.chunks_explored)}/{self.target_chunks} chunks."
                return await self._call_llm_with_functions(continue_prompt, conversation_history)
            
            return message.content or "Exploration completed"
            
        except Exception as e:
            print(f"❌ Error during exploration: {str(e)}")
            return f"Error during exploration: {str(e)}"


async def main():
    """Main enhanced PoC execution"""
    
    print("🚀 Enhanced Interactive XSLT Exploration PoC")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        return False
    
    # Set up paths
    xslt_path = "/home/sidd/dev/xml_wizard/resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    
    if not Path(xslt_path).exists():
        print(f"❌ ERROR: XSLT file not found: {xslt_path}")
        return False
    
    try:
        # Initialize enhanced explorer (100% coverage for complete scanning)
        explorer = EnhancedXSLTExplorer(api_key, xslt_path, target_coverage=1.0)
        
        # Start exploration
        result = await explorer.start_enhanced_exploration()
        
        print(f"\n🎯 ENHANCED EXPLORATION RESULT:")
        print(f"=" * 60)
        print(result)
        
        # Final assessment
        final_summary = explorer.get_understanding_summary()["summary"]
        
        print(f"\n📊 FINAL ASSESSMENT:")
        print(f"   • Chunks Explored: {final_summary['chunks_explored']}/{final_summary['target_chunks']} ({final_summary['progress_percentage']:.1f}%)")
        print(f"   • Mapping Specifications: {final_summary['mapping_specifications']}")
        print(f"   • Template Analyses: {final_summary['template_analyses']}")
        print(f"   • Context Resets: {final_summary['context_resets']}")
        print(f"   • Total Cost: ${explorer.cost_tracker['cumulative_cost_usd']:.6f}")
        
        # Validate success
        success = (
            final_summary['progress_percentage'] >= 80 and  # Reached most of target
            final_summary['mapping_specifications'] > 0 and  # Extracted mappings
            explorer.cost_tracker['cumulative_cost_usd'] < 1.0  # Reasonable cost
        )
        
        if success:
            print(f"\n🎉 ENHANCED PoC SUCCESS!")
            print(f"✨ Detailed mapping specifications extracted with context management")
            print(f"📁 Results saved to: {explorer.results_dir}")
        else:
            print(f"\n⚠️ ENHANCED PoC NEEDS IMPROVEMENT")
            print(f"🔧 Check mapping extraction quality and coverage")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)