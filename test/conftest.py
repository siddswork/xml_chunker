"""
Pytest configuration and fixtures for XML Wizard tests.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from utils.xml_generator import XMLGenerator
from utils.xsd_parser import XSDParser


@pytest.fixture(scope="session")
def resource_dir():
    """Path to the resource directory containing XSD schemas."""
    return Path(__file__).parent.parent / "resource" / "21_3_5_distribution_schemas"


@pytest.fixture(scope="session")
def order_view_rs_xsd(resource_dir):
    """Path to IATA_OrderViewRS.xsd file."""
    return resource_dir / "IATA_OrderViewRS.xsd"


@pytest.fixture(scope="session")
def order_create_rq_xsd(resource_dir):
    """Path to IATA_OrderCreateRQ.xsd file."""
    return resource_dir / "IATA_OrderCreateRQ.xsd"


@pytest.fixture(scope="function")
def temp_xsd_dir(resource_dir):
    """
    Create a temporary directory with all XSD files for testing.
    This ensures proper import resolution for interdependent schemas.
    """
    temp_dir = tempfile.mkdtemp()
    
    # Copy all XSD files to temp directory for proper import resolution
    for xsd_file in resource_dir.glob("*.xsd"):
        shutil.copy2(xsd_file, temp_dir)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def xml_generator_order_view(temp_xsd_dir):
    """XMLGenerator instance for IATA_OrderViewRS.xsd."""
    xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
    return XMLGenerator(xsd_path)


@pytest.fixture(scope="function")
def xml_generator_order_create(temp_xsd_dir):
    """XMLGenerator instance for IATA_OrderCreateRQ.xsd."""
    xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
    return XMLGenerator(xsd_path)


@pytest.fixture(scope="function")
def xsd_parser_order_view(temp_xsd_dir):
    """XSDParser instance for IATA_OrderViewRS.xsd."""
    xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderViewRS.xsd")
    return XSDParser(xsd_path)


@pytest.fixture(scope="function")
def xsd_parser_order_create(temp_xsd_dir):
    """XSDParser instance for IATA_OrderCreateRQ.xsd."""
    xsd_path = os.path.join(temp_xsd_dir, "IATA_OrderCreateRQ.xsd")
    return XSDParser(xsd_path)


@pytest.fixture(scope="function")
def sample_xml_output_dir():
    """Temporary directory for XML output files."""
    temp_dir = tempfile.mkdtemp(prefix="xml_output_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)