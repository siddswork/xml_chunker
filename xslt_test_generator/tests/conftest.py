"""Pytest configuration and fixtures for XSLT Test Generator tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import json
import sqlite3

from xslt_test_generator.database.connection import DatabaseManager
from xslt_test_generator.core.file_discovery import FileDiscoveryEngine


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_db_path(temp_dir):
    """Create a temporary database path."""
    return str(temp_dir / "test.db")


@pytest.fixture
def db_manager(test_db_path):
    """Create a test database manager."""
    return DatabaseManager(test_db_path)


@pytest.fixture
def file_discovery(db_manager):
    """Create a file discovery engine with test database."""
    return FileDiscoveryEngine(db_manager)


@pytest.fixture
def sample_xslt_content():
    """Sample XSLT content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:import href="common/utils.xsl"/>
    <xsl:include href="templates/passenger.xsl"/>
    
    <xsl:template match="/">
        <output>
            <xsl:call-template name="processPassengers"/>
        </output>
    </xsl:template>
    
    <xsl:template name="processPassengers">
        <passengers>
            <xsl:for-each select="//passenger">
                <xsl:if test="@type='adult'">
                    <adult>
                        <name><xsl:value-of select="name"/></name>
                    </adult>
                </xsl:if>
            </xsl:for-each>
        </passengers>
    </xsl:template>
    
</xsl:stylesheet>'''


@pytest.fixture
def sample_xsd_content():
    """Sample XSD content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/booking"
           xmlns:tns="http://example.com/booking">
    
    <xs:import namespace="http://example.com/common" 
               schemaLocation="common/CommonTypes.xsd"/>
    
    <xs:element name="BookingRequest" type="tns:BookingRequestType"/>
    
    <xs:complexType name="BookingRequestType">
        <xs:sequence>
            <xs:element name="passenger" type="tns:PassengerType" maxOccurs="unbounded"/>
            <xs:element name="itinerary" type="tns:ItineraryType"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:complexType name="PassengerType">
        <xs:sequence>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="age" type="xs:int"/>
        </xs:sequence>
        <xs:attribute name="type" type="xs:string" use="required"/>
    </xs:complexType>
    
</xs:schema>'''


@pytest.fixture
def sample_utils_xslt():
    """Sample utils XSLT file content."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template name="formatName">
        <xsl:param name="firstName"/>
        <xsl:param name="lastName"/>
        <xsl:value-of select="concat($firstName, ' ', $lastName)"/>
    </xsl:template>
    
</xsl:stylesheet>'''


@pytest.fixture
def sample_files_structure(temp_dir, sample_xslt_content, sample_xsd_content, sample_utils_xslt):
    """Create a sample file structure for testing."""
    
    # Create directory structure
    main_dir = temp_dir / "project"
    common_dir = main_dir / "common"
    templates_dir = main_dir / "templates"
    schema_dir = main_dir / "schema"
    
    main_dir.mkdir(parents=True)
    common_dir.mkdir()
    templates_dir.mkdir()
    schema_dir.mkdir()
    
    # Create files
    files = {}
    
    # Main XSLT
    main_xslt = main_dir / "main.xsl"
    main_xslt.write_text(sample_xslt_content)
    files['main_xslt'] = str(main_xslt)
    
    # Utils XSLT (imported by main)
    utils_xslt = common_dir / "utils.xsl"
    utils_xslt.write_text(sample_utils_xslt)
    files['utils_xslt'] = str(utils_xslt)
    
    # Passenger template (included by main)
    passenger_xslt = templates_dir / "passenger.xsl"
    passenger_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="passenger[@type='child']">
        <child><xsl:value-of select="name"/></child>
    </xsl:template>
</xsl:stylesheet>'''
    passenger_xslt.write_text(passenger_content)
    files['passenger_xslt'] = str(passenger_xslt)
    
    # Main XSD
    main_xsd = schema_dir / "Booking.xsd"
    main_xsd.write_text(sample_xsd_content)
    files['main_xsd'] = str(main_xsd)
    
    # Common types XSD (imported by main XSD)
    common_xsd = common_dir / "CommonTypes.xsd"
    common_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/common"
           xmlns:tns="http://example.com/common">
    
    <xs:complexType name="ItineraryType">
        <xs:sequence>
            <xs:element name="departure" type="xs:string"/>
            <xs:element name="arrival" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>
    
</xs:schema>'''
    common_xsd.write_text(common_content)
    files['common_xsd'] = str(common_xsd)
    
    return files


@pytest.fixture
def expected_file_discovery_results():
    """Expected results from file discovery for validation."""
    return {
        'total_files': 5,
        'xslt_files': 3,
        'xsd_files': 2,
        'dependencies': [
            ('main.xsl', 'utils.xsl'),
            ('main.xsl', 'passenger.xsl'),
            ('Booking.xsd', 'CommonTypes.xsd')
        ]
    }


@pytest.fixture
def large_xslt_content():
    """Generate a large XSLT file for performance testing."""
    base_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="/">
        <output>
            <xsl:call-template name="processData"/>
        </output>
    </xsl:template>
'''
    
    # Generate many templates to simulate a large file
    templates = []
    for i in range(1000):  # Create 1000 templates
        template = f'''
    <xsl:template name="template_{i}">
        <element_{i}>
            <xsl:if test="@condition_{i}">
                <xsl:value-of select="data_{i}"/>
            </xsl:if>
        </element_{i}>
    </xsl:template>'''
        templates.append(template)
    
    footer = '''
    <xsl:template name="processData">
        <data>Processing complete</data>
    </xsl:template>
    
</xsl:stylesheet>'''
    
    return base_content + ''.join(templates) + footer


@pytest.fixture 
def corrupted_xslt_content():
    """Corrupted XSLT content for error handling tests."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output>
            <xsl:unclosed-tag>
        </output>
    <!-- Missing closing stylesheet tag -->'''


class DatabaseTestHelper:
    """Helper class for database testing operations."""
    
    @staticmethod
    def get_table_count(db_path: str, table_name: str) -> int:
        """Get the number of rows in a table."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
    
    @staticmethod
    def table_exists(db_path: str, table_name: str) -> bool:
        """Check if a table exists in the database."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            return cursor.fetchone() is not None
    
    @staticmethod
    def get_all_tables(db_path: str) -> list:
        """Get list of all tables in database."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            return [row[0] for row in cursor.fetchall()]


@pytest.fixture
def db_helper():
    """Database testing helper."""
    return DatabaseTestHelper