#!/usr/bin/env python3
"""Example script to run XSLT Test Generator with the OrderCreate files."""

import sys
import os
from pathlib import Path

# Add src to path so we can import the main module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import app
import typer

def run_orderCreate_example():
    """Run the test generator with OrderCreate XSLT and XSD files."""
    
    # Paths relative to the xml_chunker root
    base_path = Path(__file__).parent.parent.parent
    xslt_file = base_path / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
    xsd_file = base_path / "resource" / "orderCreate" / "input_xsd" / "AMA_ConnectivityLayerRQ.xsd"
    output_dir = Path(__file__).parent / "output"
    
    # Verify files exist
    if not xslt_file.exists():
        print(f"❌ XSLT file not found: {xslt_file}")
        return
    
    if not xsd_file.exists():
        print(f"❌ XSD file not found: {xsd_file}")
        return
    
    print("🚀 Running XSLT Test Generator Example")
    print(f"📁 XSLT: {xslt_file}")
    print(f"📁 XSD: {xsd_file}")
    print(f"📁 Output: {output_dir}")
    print()
    
    # Run the generator
    try:
        app([
            str(xslt_file),
            str(xsd_file), 
            str(output_dir),
            "--verbose"
        ])
    except typer.Exit as e:
        if e.exit_code == 0:
            print("\n✅ Example completed successfully!")
        else:
            print(f"\n❌ Example failed with exit code {e.exit_code}")

if __name__ == "__main__":
    run_orderCreate_example()