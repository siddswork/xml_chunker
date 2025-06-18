"""
Services Package for XML Wizard

This package contains the business logic services that handle core functionality
with clean separation of concerns:

- file_manager.py: File operations and temporary directory management
- xml_validator.py: XML validation against XSD schemas with error categorization  
- schema_analyzer.py: XSD schema analysis and structure extraction
- xslt_processor.py: XSLT transformations and equivalence testing

Each service is designed to be independently testable and follows the Single
Responsibility Principle for maintainable, modular code.
"""