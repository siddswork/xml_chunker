# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XML Chunker is a Streamlit application for parsing XSD schemas and generating dummy XML files. The application processes IATA NDC (New Distribution Capability) XSD schemas and creates valid XML instances with sample data.

## Common Commands

### Running the Application
```bash


```

### Python Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Testing
Run pytest test suite:
```bash
pytest                    # Run all tests
pytest -v                 # Run with verbose output
pytest test/test_order_view_rs.py  # Run specific test file
pytest -k "test_xml_generation"    # Run tests matching pattern
```

Run individual test scripts:
```bash
cd test
python xml_generation.py path/to/schema.xsd
```

## Architecture

### Core Components

- **app.py**: Main Streamlit interface handling file uploads and UI rendering
- **utils/xml_generator.py**: Core XML generation logic with XSD schema processing
- **utils/xsd_parser.py**: XSD schema parsing utilities and validation
- **test/xml_generation.py**: Test script for XML generation functionality

### XML Generation Process

1. XSD schema loading with dependency resolution for IATA schemas
2. Schema parsing to extract element definitions and constraints
3. Random data generation based on XSD types (string, int, date, etc.)
4. XML tree construction with proper namespace handling
5. Comment insertion for element occurrence information

### IATA Schema Specifics

The application is specifically designed for IATA NDC schemas with:
- Automatic copying of related XSD files for dependency resolution
- Special handling for `IATA_OffersAndOrdersCommonTypes.xsd` imports
- Namespace prefix mapping (e.g., `cns:` for common types)
- Complex type processing with choice elements and unbounded occurrences

### Key Features

- **Schema Dependency Management**: Automatically resolves XSD imports by copying related schema files
- **Random Data Generation**: Type-aware value generation for realistic XML instances
- **Occurrence Constraints**: Handles minOccurs/maxOccurs with appropriate XML comments
- **Namespace Support**: Proper namespace prefix handling for complex IATA schemas
- **Error Handling**: Graceful fallbacks when schema processing fails

## Development Notes

### Working with XSD Files
- Test schemas are located in `resource/21_3_5_distribution_schemas/`
- The application expects IATA NDC schema structure and dependencies
- All related XSD files should be in the same directory for proper import resolution

### XML Generation Logic
- Elements with `maxOccurs > 1` generate multiple instances (2-3 random items)
- Optional elements (minOccurs=0) are always included with occurrence comments
- Complex types are recursively processed with proper namespace handling