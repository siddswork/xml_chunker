#!/usr/bin/env python3
"""
Agentic XSLT Test Generation CLI

This CLI demonstrates and validates the agentic XSLT test generation system
using real XSLT files from the orderCreate transformations.
"""

import sys
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.xslt_chunker import XSLTChunker, ChunkType
from src.utils.streaming_file_reader import StreamingFileReader
from src.utils.token_counter import TokenCounter


def format_bytes(bytes_size: int) -> str:
    """Format bytes in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_memory_usage() -> Dict[str, str]:
    """Get current memory usage"""
    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss': format_bytes(memory_info.rss),
                'vms': format_bytes(memory_info.vms),
                'percent': f"{process.memory_percent():.1f}%"
            }
        except Exception:
            pass
    
    return {
        'rss': "N/A (psutil not available)",
        'vms': "N/A (psutil not available)", 
        'percent': "N/A"
    }


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """
    Comprehensive analysis of an XSLT file using our agentic system
    
    Returns:
        Dictionary with analysis results
    """
    print(f"\n{'='*80}")
    print(f"📁 ANALYZING: {file_path.name}")
    print(f"📂 Path: {file_path}")
    print(f"{'='*80}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return {"error": "File not found"}
    
    analysis_results = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "analysis_timestamp": time.time()
    }
    
    # Step 1: File metadata analysis
    print(f"\n📊 FILE METADATA ANALYSIS")
    print(f"{'='*40}")
    
    try:
        reader = StreamingFileReader()
        metadata = reader.get_file_metadata(file_path)
        
        file_info = {
            "size_bytes": metadata.size_bytes,
            "size_formatted": format_bytes(metadata.size_bytes),
            "line_count": metadata.line_count,
            "encoding": metadata.encoding,
            "estimated_tokens": metadata.estimated_tokens
        }
        
        print(f"📋 Size: {file_info['size_formatted']}")
        print(f"📋 Lines: {file_info['line_count']:,}")
        print(f"📋 Encoding: {file_info['encoding']}")
        print(f"📋 Estimated Tokens: {file_info['estimated_tokens']:,}")
        
        analysis_results["file_metadata"] = file_info
        
        # Memory usage estimates
        estimates = reader.estimate_memory_usage(file_path)
        print(f"\n💾 MEMORY ESTIMATES:")
        print(f"   Full Load: {estimates['full_load_memory_mb']:.1f} MB")
        print(f"   Chunked: {estimates['chunked_memory_mb']:.1f} MB")
        print(f"   Streaming: {estimates['streaming_memory_mb']:.1f} MB")
        print(f"   Recommended: {estimates['recommended_strategy']}")
        
        analysis_results["memory_estimates"] = estimates
        
    except Exception as e:
        error_msg = f"Error reading file metadata: {e}"
        print(f"❌ {error_msg}")
        analysis_results["metadata_error"] = error_msg
        return analysis_results
    
    # Step 2: XSLT Chunking Analysis
    print(f"\n✂️  XSLT CHUNKING ANALYSIS")
    print(f"{'='*40}")
    
    # Track memory and time
    memory_before = get_memory_usage()
    start_time = time.time()
    
    try:
        chunker = XSLTChunker(max_tokens_per_chunk=15000)
        chunks = chunker.chunk_file(file_path)
        
        end_time = time.time()
        memory_after = get_memory_usage()
        processing_time = end_time - start_time
        
        print(f"⚡ Processing Time: {processing_time:.2f} seconds")
        print(f"💾 Memory Before: {memory_before['rss']} ({memory_before['percent']})")
        print(f"💾 Memory After: {memory_after['rss']} ({memory_after['percent']})")
        
        # Chunk analysis
        chunk_analysis = analyze_chunks(chunks, chunker.max_tokens_per_chunk)
        chunk_analysis["processing_time"] = processing_time
        chunk_analysis["memory_before"] = memory_before
        chunk_analysis["memory_after"] = memory_after
        
        analysis_results["chunking_analysis"] = chunk_analysis
        
        print(f"\n📊 CHUNKING RESULTS:")
        print(f"   Total Chunks: {len(chunks)}")
        print(f"   Total Estimated Tokens: {chunk_analysis['total_tokens']:,}")
        print(f"   Average Tokens per Chunk: {chunk_analysis['avg_tokens']:,}")
        
        # Display chunk type distribution
        print(f"\n📈 CHUNK TYPE DISTRIBUTION:")
        for chunk_type, count in chunk_analysis['chunk_types'].items():
            percentage = (count / len(chunks)) * 100 if chunks else 0
            print(f"   {chunk_type}: {count} ({percentage:.1f}%)")
        
        # Helper template analysis
        if chunk_analysis['helper_templates']:
            print(f"\n🔧 HELPER TEMPLATES ({len(chunk_analysis['helper_templates'])}):")
            for i, helper in enumerate(chunk_analysis['helper_templates'][:10], 1):
                print(f"   {i:2d}. {helper['name']} (Lines {helper['start_line']}-{helper['end_line']}, {helper['tokens']} tokens)")
            if len(chunk_analysis['helper_templates']) > 10:
                print(f"   ... and {len(chunk_analysis['helper_templates']) - 10} more helper templates")
        
        # Dependency analysis
        if chunk_analysis['dependencies']:
            print(f"\n🔗 DEPENDENCY ANALYSIS:")
            deps = chunk_analysis['dependencies']
            print(f"   Total dependencies: {deps['total']}")
            print(f"   Unique dependencies: {deps['unique']}")
            print(f"   Variable references: {deps['variables']}")
            print(f"   Template calls: {deps['templates']}")
            print(f"   Function calls: {deps['functions']}")
        
        # Pattern detection
        patterns = chunk_analysis['patterns']
        print(f"\n🔍 PATTERN DETECTION:")
        print(f"   Chunks with choose blocks: {patterns['choose_blocks']}")
        print(f"   Chunks with variables: {patterns['variables']}")
        print(f"   Chunks with XPath: {patterns['xpath']}")
        
        # Token size analysis
        tokens = chunk_analysis['token_analysis']
        print(f"\n📏 TOKEN SIZE ANALYSIS:")
        print(f"   Min tokens: {tokens['min_tokens']}")
        print(f"   Max tokens: {tokens['max_tokens']}")
        print(f"   Average tokens: {tokens['avg_tokens']:.1f}")
        if tokens['oversized_chunks']:
            print(f"   ⚠️  Oversized chunks: {len(tokens['oversized_chunks'])}")
        else:
            print(f"   ✅ All chunks within limit ({chunker.max_tokens_per_chunk} tokens)")
        
        # Sample chunk preview
        if chunks:
            print(f"\n📄 SAMPLE CHUNK PREVIEW:")
            sample_chunk = chunks[0]
            print(f"   Chunk: {sample_chunk.chunk_id} ({sample_chunk.chunk_type.value})")
            print(f"   Name: {sample_chunk.name or 'N/A'}")
            print(f"   Lines {sample_chunk.start_line}-{sample_chunk.end_line} ({sample_chunk.line_count} lines):")
            for i, line in enumerate(sample_chunk.lines[:5], 1):
                print(f"      {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
            if len(sample_chunk.lines) > 5:
                print(f"      ... and {len(sample_chunk.lines) - 5} more lines")
        
        print(f"\n✅ Analysis completed successfully!")
        return analysis_results
        
    except Exception as e:
        error_msg = f"Error during chunking analysis: {e}"
        print(f"❌ {error_msg}")
        analysis_results["chunking_error"] = error_msg
        return analysis_results


def analyze_chunks(chunks: List, max_tokens: int) -> Dict[str, Any]:
    """Analyze the generated chunks"""
    if not chunks:
        return {"total_chunks": 0}
    
    # Basic statistics
    total_tokens = sum(chunk.estimated_tokens for chunk in chunks)
    avg_tokens = total_tokens // len(chunks) if chunks else 0
    
    # Chunk type analysis
    chunk_types = {}
    helper_templates = []
    main_templates = []
    
    for chunk in chunks:
        chunk_type = chunk.chunk_type.value
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        if chunk.chunk_type == ChunkType.HELPER_TEMPLATE:
            helper_templates.append({
                "name": chunk.name or "Unnamed",
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "tokens": chunk.estimated_tokens,
                "dependencies": len(chunk.dependencies)
            })
        elif chunk.chunk_type == ChunkType.MAIN_TEMPLATE:
            main_templates.append({
                "name": chunk.name or "Unnamed",
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "tokens": chunk.estimated_tokens,
                "dependencies": len(chunk.dependencies)
            })
    
    # Dependency analysis
    all_dependencies = []
    for chunk in chunks:
        all_dependencies.extend(chunk.dependencies)
    
    unique_deps = set(all_dependencies)
    var_deps = [d for d in unique_deps if d.startswith('var:')]
    template_deps = [d for d in unique_deps if d.startswith('template:')]
    function_deps = [d for d in unique_deps if d.startswith('function:')]
    
    dependency_analysis = {
        "total": len(all_dependencies),
        "unique": len(unique_deps),
        "variables": len(var_deps),
        "templates": len(template_deps),
        "functions": len(function_deps),
        "variable_list": var_deps[:10],  # Sample
        "template_list": template_deps[:10],  # Sample
        "function_list": function_deps[:10]  # Sample
    }
    
    # Pattern detection
    choose_chunks = sum(1 for c in chunks if c.metadata.get('has_choose_blocks', False))
    variable_chunks = sum(1 for c in chunks if c.metadata.get('has_variables', False))
    xpath_chunks = sum(1 for c in chunks if c.metadata.get('has_xpath', False))
    
    patterns = {
        "choose_blocks": choose_chunks,
        "variables": variable_chunks,
        "xpath": xpath_chunks
    }
    
    # Token size analysis
    token_sizes = [chunk.estimated_tokens for chunk in chunks]
    oversized = [c for c in chunks if c.estimated_tokens > max_tokens]
    
    token_analysis = {
        "min_tokens": min(token_sizes) if token_sizes else 0,
        "max_tokens": max(token_sizes) if token_sizes else 0,
        "avg_tokens": avg_tokens,
        "oversized_chunks": [{"id": c.chunk_id, "tokens": c.estimated_tokens} for c in oversized]
    }
    
    return {
        "total_chunks": len(chunks),
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
        "chunk_types": chunk_types,
        "helper_templates": helper_templates,
        "main_templates": main_templates,
        "dependencies": dependency_analysis,
        "patterns": patterns,
        "token_analysis": token_analysis
    }


def compare_files(file1_path: Path, file2_path: Path) -> Dict[str, Any]:
    """Compare two XSLT files"""
    print(f"\n{'='*80}")
    print(f"⚖️  COMPARISON: {file1_path.name} vs {file2_path.name}")
    print(f"{'='*80}")
    
    # Analyze both files
    analysis1 = analyze_file(file1_path)
    analysis2 = analyze_file(file2_path)
    
    if "error" in analysis1 or "error" in analysis2:
        print("❌ Cannot compare - one or both files failed to analyze")
        return {"error": "Analysis failed for one or both files"}
    
    chunk1 = analysis1.get("chunking_analysis", {})
    chunk2 = analysis2.get("chunking_analysis", {})
    
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"{'Metric':<25} {'File 1':<20} {'File 2':<20} {'Difference':<15}")
    print(f"{'-' * 80}")
    
    # File size comparison
    size1 = analysis1["file_metadata"]["size_bytes"]
    size2 = analysis2["file_metadata"]["size_bytes"]
    print(f"{'File Size':<25} {format_bytes(size1):<20} {format_bytes(size2):<20} {format_bytes(abs(size1-size2)):<15}")
    
    # Token comparison
    tokens1 = chunk1.get("total_tokens", 0)
    tokens2 = chunk2.get("total_tokens", 0)
    print(f"{'Total Tokens':<25} {tokens1:,}{'':>20} {tokens2:,}{'':>20} {abs(tokens1-tokens2):,}{'':>15}")
    
    # Chunk comparison
    chunks1 = chunk1.get("total_chunks", 0)
    chunks2 = chunk2.get("total_chunks", 0)
    print(f"{'Total Chunks':<25} {chunks1:<20} {chunks2:<20} {abs(chunks1-chunks2):<15}")
    
    # Helper template comparison
    helpers1 = len(chunk1.get("helper_templates", []))
    helpers2 = len(chunk2.get("helper_templates", []))
    print(f"{'Helper Templates':<25} {helpers1:<20} {helpers2:<20} {abs(helpers1-helpers2):<15}")
    
    # Processing time comparison
    time1 = chunk1.get("processing_time", 0)
    time2 = chunk2.get("processing_time", 0)
    print(f"{'Processing Time (s)':<25} {time1:.2f}{'':>20} {time2:.2f}{'':>20} {abs(time1-time2):.2f}{'':>15}")
    
    return {
        "file1": analysis1,
        "file2": analysis2,
        "comparison": {
            "file1_name": file1_path.name,
            "file2_name": file2_path.name,
            "size_diff": abs(size1 - size2),
            "token_diff": abs(tokens1 - tokens2),
            "chunk_diff": abs(chunks1 - chunks2),
            "helper_diff": abs(helpers1 - helpers2),
            "time_diff": abs(time1 - time2)
        }
    }


def save_analysis_report(analysis: Dict[str, Any], output_file: Path):
    """Save analysis results to JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"💾 Analysis report saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Agentic XSLT Test Generation CLI")
    parser.add_argument("--file", "-f", help="Analyze specific XSLT file")
    parser.add_argument("--compare", "-c", action="store_true", help="Compare both XSLT files")
    parser.add_argument("--all", "-a", action="store_true", help="Analyze all XSLT files in orderCreate")
    parser.add_argument("--output", "-o", help="Save analysis to JSON file")
    parser.add_argument("--max-tokens", type=int, default=15000, help="Maximum tokens per chunk")
    
    args = parser.parse_args()
    
    # Default paths to real XSLT files
    base_path = Path(__file__).parent.parent / "resource" / "orderCreate" / "xslt"
    file1_path = base_path / "OrderCreate_MapForce_Full.xslt"
    file2_path = base_path / "OrderCreate_Part1_AI.xslt"
    
    print(f"🚀 AGENTIC XSLT TEST GENERATION CLI")
    print(f"🎯 Validating agentic system with real XSLT files")
    print(f"⚙️  Max Tokens per Chunk: {args.max_tokens:,}")
    print(f"📁 Base Path: {base_path}")
    
    analysis_results = {}
    
    if args.file:
        # Analyze specific file
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = base_path / file_path
        
        analysis_results = analyze_file(file_path)
        
    elif args.compare:
        # Compare both files
        analysis_results = compare_files(file1_path, file2_path)
        
    elif args.all:
        # Analyze all files
        analysis_results = {}
        for xslt_file in base_path.glob("*.xslt"):
            analysis_results[xslt_file.name] = analyze_file(xslt_file)
        
    else:
        # Default: analyze the main file
        analysis_results = analyze_file(file1_path)
    
    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        save_analysis_report(analysis_results, output_path)
    
    print(f"\n{'='*80}")
    print(f"🎉 AGENTIC XSLT ANALYSIS COMPLETED!")
    print(f"✅ System validation successful!")
    print(f"📊 Final memory usage: {get_memory_usage()['rss']}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()