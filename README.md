# XML Wizard

A modular Streamlit application for parsing XSD schemas and generating compliant dummy XML files. The application specializes in IATA NDC (New Distribution Capability) XSD schemas, providing advanced analysis, choice element handling, and validation-aware XML generation.

## Features

### Core Functionality
- **File Upload**: Direct XSD file upload with automatic dependency resolution
- **Schema Analysis**: Real-time analysis of XSD structure with choice elements, root elements, and schema information
- **Interactive Tree View**: Professional tree visualization of schema structure with expandable/collapsible nodes
- **Choice Element Selection**: Interactive selection of choice elements for targeted XML generation
- **Unbounded Element Configuration**: Configurable counts for elements with maxOccurs > 1
- **XML Generation**: Type-aware value generation for realistic, validation-compliant XML instances
- **XML Validation**: Comprehensive validation against XSD schemas with detailed error categorization
- **Download Support**: Generated XML can be downloaded directly from the interface

### Advanced Features
- **IATA Schema Specialization**: Optimized for IATA NDC schema patterns and dependencies
- **Namespace Support**: Proper namespace prefix handling for complex multi-namespace schemas
- **Error Categorization**: Intelligent categorization of validation errors (enumeration, boolean, pattern, structural)
- **Performance Optimization**: Efficient processing with recursion limits and memory management
- **Modular Architecture**: Clean separation of concerns with dedicated service modules

## Installation

1. Clone the repository:
```bash
git clone https://github.com/siddswork/xml_wizard.git
cd xml_wizard
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

OR

python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. **Upload XSD File**: Use the sidebar file uploader to select an XSD schema file
3. **Analyze Schema**: The application automatically analyzes the uploaded schema and displays:
   - Schema information (namespace, element/type counts)
   - Interactive tree structure with choice elements highlighted
   - Unbounded elements that can be configured
4. **Configure Generation**:
   - Select preferred choice elements from dropdown menus
   - Set counts for unbounded elements using number inputs
5. **Generate XML**: Click "Generate XML" to create a dummy XML file based on your selections
6. **Validate XML**: Use "Validate XML" to check the generated XML against the schema
7. **Download**: Download the generated XML file directly from the interface

### Workflow for IATA Schemas
1. Upload an IATA NDC schema (e.g., `IATA_OrderViewRS.xsd`)
2. The system automatically handles dependencies like `IATA_OffersAndOrdersCommonTypes.xsd`
3. Choose between Response/Error elements for choice constructs
4. Configure counts for repeating elements (e.g., multiple passengers, flights)
5. Generate and validate XML with proper namespace handling

## Testing

Run the comprehensive test suite:
```bash
pytest                    # Run all tests
pytest -v                 # Run with verbose output
pytest test/test_order_view_rs.py  # Run specific test file
pytest -k "test_xml_generation"    # Run tests matching pattern
```

The application can be tested using the XSD files in the `resource/21_3_5_distribution_schemas` folder. 
For example, you can upload the `IATA_OrderCreateRQ.xsd` or `IATA_OrderViewRS.xsd` files to test the application.

## Project Structure

```
xml_wizard/
├── app.py                      # Main Streamlit application (UI orchestration)
├── config.py                   # Configuration management
├── services/                   # Modular business logic services
│   ├── __init__.py
│   ├── file_manager.py         # File operations and temp directory management
│   ├── xml_validator.py        # XML validation against XSD schemas
│   └── schema_analyzer.py      # XSD schema analysis and structure extraction
├── utils/                      # Core utilities
│   ├── __init__.py
│   ├── xsd_parser.py           # XSD schema parsing utilities
│   ├── xml_generator.py        # Universal XML generation engine
│   └── type_generators.py      # Type-specific value generators
├── test/                       # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_app_functionality.py      # App functionality tests
│   ├── test_choice_selection.py       # Choice element tests
│   ├── test_order_create_rq.py        # IATA OrderCreateRQ tests
│   ├── test_order_view_rs.py          # IATA OrderViewRS tests
│   ├── test_response_choice_generation.py # Response choice tests
│   └── test_xml_validation.py         # XML validation tests
├── resource/                   # Sample XSD files for testing
│   └── 21_3_5_distribution_schemas/   # IATA NDC schema collection
├── requirements.txt            # Project dependencies
├── pytest.ini                 # Test configuration
├── CLAUDE.md                   # Development guidance
└── README.md                   # Project documentation
```

## Architecture Overview

### Modular Design
The application follows a clean, modular architecture with separation of concerns:

- **Presentation Layer** (`app.py`): Streamlit UI components and user interaction
- **Service Layer** (`services/`): Business logic modules with single responsibilities
- **Utility Layer** (`utils/`): Core functionality and data processing
- **Configuration** (`config.py`): Centralized configuration management

### Key Services
- **FileManager**: Handles temporary files, XSD dependencies, and file operations
- **XMLValidator**: Validates generated XML against schemas with detailed error reporting
- **SchemaAnalyzer**: Analyzes XSD structure, extracts choice elements and tree hierarchy
- **XMLGenerator**: Universal XML generation engine with type-aware value creation

### Design Principles
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Services are injected rather than hardcoded
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Performance**: Optimized with recursion limits and memory management
- **Testability**: Extensive test coverage with modular test organization
