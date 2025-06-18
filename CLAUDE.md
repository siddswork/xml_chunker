# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XML Wizard is a Streamlit application for parsing XSD schemas and generating dummy XML files. The application processes IATA NDC (New Distribution Capability) XSD schemas, analyzes their structure (including choice elements), and creates valid XML instances with sample data.

## Common Commands

### Running the Application
```bash
streamlit run app.py
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

### Modular Design Overview

The application follows a clean, layered architecture with separation of concerns:

- **Presentation Layer**: Streamlit UI (app.py)
- **Service Layer**: Business logic modules (services/)
- **Utility Layer**: Core functionality (utils/)
- **Configuration Layer**: Centralized config management

### Core Components

#### Presentation Layer
- **app.py**: Main Streamlit interface for file uploads, UI rendering, and user interaction orchestration

#### Service Layer (services/)
- **file_manager.py**: File operations, temporary directory management, and XSD dependency resolution
- **xml_validator.py**: XML validation against XSD schemas with detailed error categorization and reporting
- **schema_analyzer.py**: XSD schema analysis, choice element detection, and element tree structure extraction

#### Utility Layer (utils/)
- **xml_generator.py**: Universal XML generation engine with deep recursive parsing and type-aware value creation
- **xsd_parser.py**: XSD schema parsing utilities and basic validation
- **type_generators.py**: Modular type-specific value generators for validation compliance

#### Test Suite (test/)
- **test_app_functionality.py**: Integration tests for app functionality
- **test_choice_selection.py**: Choice element handling tests
- **test_order_create_rq.py**: IATA OrderCreateRQ schema tests
- **test_order_view_rs.py**: IATA OrderViewRS schema tests  
- **test_response_choice_generation.py**: Response/Error choice tests
- **test_xml_validation.py**: XML validation functionality tests

### XML Generation Process

1. **File Upload & Dependency Resolution**: FileManager handles XSD uploads and automatically copies related schema dependencies
2. **Schema Analysis**: SchemaAnalyzer extracts element definitions, choice constructs, and occurrence constraints
3. **User Configuration**: UI collects user preferences for choice elements and unbounded element counts
4. **Type-Aware Value Generation**: TypeGeneratorFactory creates validation-compliant values based on XSD constraints
5. **XML Tree Construction**: XMLGenerator builds XML structure with proper namespace handling and recursive processing
6. **Validation & Error Reporting**: XMLValidator checks generated XML against schema with categorized error reporting

### IATA Schema Specifics

The application is specifically designed for IATA NDC schemas with:
- Automatic copying of related XSD files for dependency resolution
- Special handling for `IATA_OffersAndOrdersCommonTypes.xsd` imports
- Namespace prefix mapping (e.g., `cns:` for common types)
- Complex type processing with choice elements and unbounded occurrences

### Key Features

- **Schema Analysis**: Real-time analysis of XSD structure showing choice elements, root elements, and schema information
- **Choice Element Detection**: Identifies and displays all choice elements with their occurrence constraints
- **Schema Dependency Management**: Automatically resolves XSD imports by copying related schema files
- **Random Data Generation**: Type-aware value generation for realistic XML instances
- **Occurrence Constraints**: Handles minOccurs/maxOccurs with appropriate XML comments
- **Namespace Support**: Proper namespace prefix handling for complex IATA schemas
- **Download Support**: Generated XML can be downloaded directly from the interface
- **Error Handling**: Graceful fallbacks when schema processing fails

## Development Notes

### Working with XSD Files
- Test schemas are located in `resource/21_3_5_distribution_schemas/`
- The application expects IATA NDC schema structure and dependencies
- All related XSD files should be in the same directory for proper import resolution

### XML Generation Logic
- Elements with `maxOccurs > 1` generate multiple instances based on user configuration
- Optional elements (minOccurs=0) are always included for comprehensive XML structure
- Complex types are recursively processed with proper namespace handling
- Performance optimized with recursion depth limits and circular reference protection
- Type-specific generators ensure validation compliance for different XSD types

### Modular Development

#### Working with Services
- Import services from their respective modules: `from services.file_manager import FileManager`
- Services are injected with configuration instances for consistency
- Each service handles one primary responsibility (Single Responsibility Principle)

#### Adding New Features
- **New validation logic**: Extend `xml_validator.py` or create specialized validators
- **New schema analysis**: Add methods to `schema_analyzer.py` for new schema patterns
- **New file operations**: Extend `file_manager.py` with additional file handling capabilities
- **New UI components**: Add to `app.py` while keeping business logic in services

#### Testing Guidelines
- Service modules are independently testable with clear interfaces
- Mock services for unit testing UI components
- Integration tests verify service interaction and end-to-end workflows
- Use pytest fixtures for consistent test data and configuration