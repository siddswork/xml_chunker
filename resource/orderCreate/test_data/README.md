# Test Data for XSLT Transformation

This directory contains test XML files for validating XSLT transformations between AMA Connectivity Layer format and IATA NDC OrderCreate format.

## Input Files (AMA Connectivity Layer Format)

### sample_input.xml
- **Purpose**: Basic flight booking request
- **Content**: Single flight booking with 2 passengers (NYC to LAX)
- **Key Elements**: Flight details, passenger information, contact details

### sample_input_hotel.xml
- **Purpose**: Hotel booking request
- **Content**: Hotel reservation with 2 guests (Paris location)
- **Key Elements**: Hotel details, guest information, special requests

### sample_input_multi_request.xml
- **Purpose**: Multiple service requests in single message
- **Content**: Combined flight search and car rental requests
- **Key Elements**: Flight search criteria, car rental details, driver information

## Expected Output Files (IATA NDC Format)

### expected_output_orderCreate.xml
- **Purpose**: Expected transformation result from sample_input.xml
- **Content**: IATA NDC OrderCreateRQ structure
- **Key Elements**: PointOfSale, Document, Party, OrderCreateParameters, Query

## Usage

These test files can be used with the XSLT processor to:

1. **Validate Transformations**: Compare actual XSLT output with expected results
2. **Test Edge Cases**: Verify handling of different booking scenarios
3. **Debug XSLT Logic**: Identify transformation issues with known input/output pairs
4. **Performance Testing**: Measure transformation speed with various data sizes

## XSLT Files

The transformations use the following XSLT files located in `../xslt/`:
- `OrderCreate_MapForce_Full.xslt`: Complete transformation logic
- `OrderCreate_Part1_AI.xslt`: Partial transformation (first part)

## Schema Validation

Input files validate against: `../input_xsd/AMA_ConnectivityLayerRQ.xsd`
Output files validate against: `../output_xsd/OrderCreateRQ.xsd`