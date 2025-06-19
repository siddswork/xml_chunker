"""File I/O operations for XSLT Test Generator."""

import os
from pathlib import Path
from typing import Optional
from lxml import etree

class FileManager:
    """Handle file operations for XSLT and XSD files."""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file content safely."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path: str, content: str, create_dirs: bool = True) -> None:
        """Write content to file, optionally creating directories."""
        path = Path(file_path)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def validate_xslt_file(file_path: str) -> bool:
        """Validate if file is a proper XSLT file."""
        try:
            content = FileManager.read_file(file_path)
            # Basic validation - check for XSLT namespace and structure
            doc = etree.fromstring(content.encode('utf-8'))
            xslt_namespace = "http://www.w3.org/1999/XSL/Transform"
            
            # Check if root element is xsl:stylesheet or xsl:transform
            if doc.tag in [f"{{{xslt_namespace}}}stylesheet", f"{{{xslt_namespace}}}transform"]:
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def validate_xsd_file(file_path: str) -> bool:
        """Validate if file is a proper XSD file."""
        try:
            content = FileManager.read_file(file_path)
            doc = etree.fromstring(content.encode('utf-8'))
            schema_namespace = "http://www.w3.org/2001/XMLSchema"
            
            # Check if root element is xs:schema
            if doc.tag == f"{{{schema_namespace}}}schema":
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def extract_file_info(file_path: str) -> dict:
        """Extract basic information about the file."""
        path = Path(file_path)
        return {
            "name": path.name,
            "size": path.stat().st_size if path.exists() else 0,
            "extension": path.suffix,
            "absolute_path": str(path.absolute()),
            "exists": path.exists()
        }
    
    @staticmethod
    def ensure_output_directory(output_path: str) -> Path:
        """Ensure output directory exists and return Path object."""
        path = Path(output_path)
        path.mkdir(parents=True, exist_ok=True)
        return path