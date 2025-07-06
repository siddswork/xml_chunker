"""
Streaming File Reader for Memory-Efficient File Processing

This module provides memory-efficient file reading capabilities for large XSLT files,
supporting streaming, buffered reading, and memory-mapped access.
"""

import os
import mmap
import logging
from pathlib import Path
from typing import Iterator, Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Metadata about a file"""
    path: Path
    size_bytes: int
    encoding: str
    line_count: int
    estimated_tokens: int


class StreamingFileReader:
    """Memory-efficient file reader for large XSLT files"""
    
    def __init__(self, buffer_size: int = 8192, encoding: str = 'utf-8'):
        """
        Initialize the streaming file reader
        
        Args:
            buffer_size: Size of read buffer in bytes
            encoding: File encoding to use
        """
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.memory_threshold_mb = 100  # Switch to memory mapping above 100MB
    
    def get_file_metadata(self, file_path: Path) -> FileMetadata:
        """
        Get comprehensive metadata about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileMetadata object with file information
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        size_bytes = file_path.stat().st_size
        
        # Detect encoding
        encoding = self._detect_encoding(file_path)
        
        # Count lines efficiently
        line_count = self._count_lines_efficiently(file_path)
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = size_bytes // 4
        
        return FileMetadata(
            path=file_path,
            size_bytes=size_bytes,
            encoding=encoding,
            line_count=line_count,
            estimated_tokens=estimated_tokens
        )
    
    def read_lines(self, file_path: Path, start_line: int = 1, end_line: Optional[int] = None) -> List[str]:
        """
        Read specific line ranges efficiently
        
        Args:
            file_path: Path to the file
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based, inclusive). If None, read to end
            
        Returns:
            List of lines in the specified range
        """
        lines = []
        current_line = 1
        
        with open(file_path, 'r', encoding=self.encoding, buffering=self.buffer_size) as f:
            for line in f:
                if current_line >= start_line:
                    if end_line is None or current_line <= end_line:
                        lines.append(line.rstrip('\n\r'))
                    else:
                        break
                current_line += 1
        
        logger.debug(f"Read {len(lines)} lines from {file_path} (lines {start_line}-{end_line or 'end'})")
        return lines
    
    def read_chunks(self, file_path: Path, chunk_size: int = 1000) -> Iterator[Tuple[int, List[str]]]:
        """
        Stream file in configurable chunks
        
        Args:
            file_path: Path to the file
            chunk_size: Number of lines per chunk
            
        Yields:
            Tuple of (start_line_number, list_of_lines)
        """
        current_line = 1
        chunk_lines = []
        
        with open(file_path, 'r', encoding=self.encoding, buffering=self.buffer_size) as f:
            for line in f:
                chunk_lines.append(line.rstrip('\n\r'))
                
                if len(chunk_lines) >= chunk_size:
                    yield (current_line - len(chunk_lines) + 1, chunk_lines)
                    chunk_lines = []
                
                current_line += 1
            
            # Yield remaining lines if any
            if chunk_lines:
                yield (current_line - len(chunk_lines), chunk_lines)
    
    def read_with_context(self, file_path: Path, line_number: int, context_lines: int = 5) -> Tuple[List[str], List[str], List[str]]:
        """
        Read line with surrounding context
        
        Args:
            file_path: Path to the file
            line_number: Target line number (1-based)
            context_lines: Number of context lines before and after
            
        Returns:
            Tuple of (before_lines, target_lines, after_lines)
        """
        start_line = max(1, line_number - context_lines)
        end_line = line_number + context_lines
        
        all_lines = self.read_lines(file_path, start_line, end_line)
        
        target_index = line_number - start_line
        
        if target_index < 0 or target_index >= len(all_lines):
            return [], [], []
        
        before_lines = all_lines[:target_index]
        target_lines = [all_lines[target_index]]
        after_lines = all_lines[target_index + 1:]
        
        return before_lines, target_lines, after_lines
    
    def memory_mapped_read(self, file_path: Path) -> mmap.mmap:
        """
        Memory-mapped file access for large files
        
        Args:
            file_path: Path to the file
            
        Returns:
            Memory-mapped file object
        """
        file_size = file_path.stat().st_size
        
        if file_size > self.memory_threshold_mb * 1024 * 1024:
            logger.info(f"Using memory-mapped access for large file: {file_path} ({file_size / 1024 / 1024:.1f} MB)")
            
            with open(file_path, 'rb') as f:
                return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        else:
            raise ValueError(f"File {file_path} is too small for memory mapping. Use regular reading methods.")
    
    def estimate_memory_usage(self, file_path: Path, chunk_size: int = 1000) -> dict:
        """
        Estimate memory usage for different processing strategies
        
        Args:
            file_path: Path to the file
            chunk_size: Chunk size for estimation
            
        Returns:
            Dictionary with memory usage estimates
        """
        metadata = self.get_file_metadata(file_path)
        
        # Estimate memory for different strategies
        estimates = {
            'file_size_mb': metadata.size_bytes / 1024 / 1024,
            'full_load_memory_mb': metadata.size_bytes / 1024 / 1024 * 2,  # Assume 2x for strings
            'chunked_memory_mb': (chunk_size * 100) / 1024 / 1024,  # Assume 100 chars per line
            'streaming_memory_mb': self.buffer_size / 1024 / 1024,
            'recommended_strategy': self._recommend_strategy(metadata)
        }
        
        return estimates
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        # Try common encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # Try to read first 1KB
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Default to utf-8 if detection fails
        logger.warning(f"Could not detect encoding for {file_path}, defaulting to utf-8")
        return 'utf-8'
    
    def _count_lines_efficiently(self, file_path: Path) -> int:
        """
        Count lines efficiently without loading entire file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of lines in the file
        """
        line_count = 0
        
        with open(file_path, 'rb') as f:
            buffer = bytearray(self.buffer_size)
            while f.readinto(buffer):
                line_count += buffer.count(b'\n')
        
        return line_count
    
    def _recommend_strategy(self, metadata: FileMetadata) -> str:
        """
        Recommend processing strategy based on file size
        
        Args:
            metadata: File metadata
            
        Returns:
            Recommended strategy string
        """
        size_mb = metadata.size_bytes / 1024 / 1024
        
        if size_mb < 10:
            return "full_load"
        elif size_mb < 100:
            return "chunked_reading"
        else:
            return "memory_mapped"


# Utility functions for easy access
def quick_read_lines(file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> List[str]:
    """Quick utility to read lines from a file"""
    reader = StreamingFileReader()
    return reader.read_lines(Path(file_path), start_line, end_line)


def quick_file_info(file_path: str) -> dict:
    """Quick utility to get file information"""
    reader = StreamingFileReader()
    metadata = reader.get_file_metadata(Path(file_path))
    return {
        'size_mb': metadata.size_bytes / 1024 / 1024,
        'line_count': metadata.line_count,
        'estimated_tokens': metadata.estimated_tokens,
        'encoding': metadata.encoding
    }