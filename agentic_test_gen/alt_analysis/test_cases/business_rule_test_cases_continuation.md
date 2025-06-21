# Business Rule Test Cases - Continuation (Categories 11-14)

## Category 11: Redress Case Processing Tests (8 test cases)

### Business Logic Analysis
**XSLT Location**: Lines 1350-1450 (Address concatenation and metadata processing)
**Analysis Instructions**: Extract address field concatenation patterns and conditional formatting logic
**What Analysis Revealed**: Complex address concatenation with slash separators, string trimming, and duplicate processing patterns
**Business Context**: Address data processing for passenger metadata and special service requests

#### Test Case 11.1: Complete Address Concatenation
**Input XML**:
```xml
<address>
  <countryCode>US</countryCode>
  <line>123 Main St</line>
  <cityName>New York</cityName>
  <countryName>United States</countryName>
  <zip>10001</zip>
</address>
```
**Expected Output**: `US/123 Main St/New York/United States/10001`
**Business Validation**: All address fields concatenated with slash separators
**XSLT Line Reference**: Lines 1370-1421
**Analysis Instruction**: Extract address field concatenation order (countryCode/line/cityName/countryName/zip)

#### Test Case 11.2: Partial Address with Missing Fields
**Input XML**:
```xml
<address>
  <countryCode>FR</countryCode>
  <cityName>Paris</cityName>
  <zip>75001</zip>
</address>
```
**Expected Output**: `FR/Paris/75001`
**Business Validation**: Missing fields (line, countryName) handled gracefully, no empty slashes
**XSLT Line Reference**: Lines 1383-1421
**Analysis Instruction**: Document how empty fields are processed in address construction

#### Test Case 11.3: Address with Trailing Slash Handling
**Input XML**:
```xml
<address>
  <countryCode>DE</countryCode>
  <line>Hauptstraße 1</line>
  <cityName>Berlin</cityName>
</address>
```
**Expected Output**: `DE/Hauptstraße 1/Berlin`
**Business Validation**: String trimming removes trailing slash when zip is missing
**XSLT Line Reference**: Lines 1370-1371, 1421
**Analysis Instruction**: Understand slash separator handling and string trimming patterns

#### Test Case 11.4: Empty Address Handling
**Input XML**:
```xml
<address>
</address>
```
**Expected Output**: `` (empty string)
**Business Validation**: Completely empty address returns empty string
**XSLT Line Reference**: Lines 1424-1449
**Edge Case**: All conditional tests fail, return empty

#### Test Case 11.5: Single Field Address
**Input XML**:
```xml
<address>
  <countryCode>CA</countryCode>
</address>
```
**Expected Output**: `CA`
**Business Validation**: Single field processed without trailing slash
**XSLT Line Reference**: Lines 1425-1433
**Analysis Instruction**: String manipulation patterns for separator handling

#### Test Case 11.6: Address with Special Characters
**Input XML**:
```xml
<address>
  <countryCode>JP</countryCode>
  <line>東京都新宿区</line>
  <cityName>Tokyo</cityName>
</address>
```
**Expected Output**: `JP/東京都新宿区/Tokyo`
**Business Validation**: Unicode/special characters preserved in address concatenation
**XSLT Line Reference**: Lines 1436-1442
**Edge Case**: International character handling

#### Test Case 11.7: Long Address Fields
**Input XML**:
```xml
<address>
  <countryCode>AU</countryCode>
  <line>Very Long Street Name That Exceeds Normal Length Expectations</line>
  <cityName>Melbourne</cityName>
  <countryName>Australia</countryName>
  <zip>3000</zip>
</address>
```
**Expected Output**: `AU/Very Long Street Name That Exceeds Normal Length Expectations/Melbourne/Australia/3000`
**Business Validation**: Long field values processed without truncation
**XSLT Line Reference**: Lines 1383-1421
**Edge Case**: Field length handling

#### Test Case 11.8: Duplicate Address Processing Logic
**Input XML**:
```xml
<address>
  <countryCode>NL</countryCode>
  <line>Damrak 1</line>
  <cityName>Amsterdam</cityName>
  <zip>1012</zip>
</address>
```
**Expected Output**: `NL/Damrak 1/Amsterdam/1012`
**Business Validation**: Both address processing logic paths (lines 1370-1421 and 1424-1449) produce identical results
**XSLT Line Reference**: Lines 1370-1421 vs 1424-1449
**Analysis Instruction**: Identified duplicate address processing patterns

## Category 12: Edge Cases and Error Handling Tests (12 test cases)

### Business Logic Analysis
**XSLT Location**: Lines 1500-1600 (Metadata processing and conditional value assignment)
**Analysis Instructions**: Identify error handling patterns and edge case processing for missing/invalid data
**What Analysis Revealed**: Graceful handling of missing passenger data, default value assignments, conditional fallback logic
**Business Context**: Robust data processing with fallback mechanisms for incomplete or invalid input data

#### Test Case 12.1: Missing Passenger Data Handling
**Input XML**:
```xml
<request>
  <actor>
    <!-- Missing passenger details -->
  </actor>
</request>
```
**Expected Output**: Default passenger structure with empty fields
**Business Validation**: Missing passenger data handled gracefully with defaults
**XSLT Line Reference**: Lines 1500-1520
**Analysis Instruction**: Graceful handling of missing passenger data patterns

#### Test Case 12.2: Null Value Processing
**Input XML**:
```xml
<request>
  <actor>
    <name></name>
    <contactInfo></contactInfo>
  </actor>
</request>
```
**Expected Output**: Empty elements processed without errors
**Business Validation**: Null/empty values don't break transformation
**XSLT Line Reference**: Lines 1520-1540
**Analysis Instruction**: Null value processing patterns

#### Test Case 12.3: Invalid Data Type Handling
**Input XML**:
```xml
<request>
  <actor>
    <age>invalid_age</age>
    <birthDate>not_a_date</birthDate>
  </actor>
</request>
```
**Expected Output**: Invalid data ignored or converted to defaults
**Business Validation**: Invalid data types handled without transformation failure
**XSLT Line Reference**: Lines 1540-1560
**Edge Case**: Data type validation and sanitization

#### Test Case 12.4: Conditional Fallback Logic
**Input XML**:
```xml
<request>
  <actor>
    <primaryContact>unavailable</primaryContact>
  </actor>
</request>
```
**Expected Output**: Secondary contact methods used when primary unavailable
**Business Validation**: Fallback logic provides alternative data paths
**XSLT Line Reference**: Lines 1560-1580
**Analysis Instruction**: Conditional fallback logic patterns

#### Test Case 12.5: Special Character Sanitization
**Input XML**:
```xml
<request>
  <actor>
    <name>John@#$%Doe</name>
    <phone>+1-555-123@#$4567</phone>
  </actor>
</request>
```
**Expected Output**: Special characters removed/sanitized appropriately
**Business Validation**: Data sanitization prevents invalid characters in output
**XSLT Line Reference**: Lines 1580-1600
**Analysis Instruction**: Data sanitization for special characters

#### Test Case 12.6: Maximum Length Field Handling
**Input XML**:
```xml
<request>
  <actor>
    <name>VeryLongNameThatExceedsMaximumAllowedLengthForPassengerNameFields</name>
  </actor>
</request>
```
**Expected Output**: Name truncated or processed according to length constraints
**Business Validation**: Long field values handled per business rules
**XSLT Line Reference**: Lines 1520-1540
**Edge Case**: Field length constraint handling

#### Test Case 12.7: Nested Empty Elements
**Input XML**:
```xml
<request>
  <actor>
    <contactInfo>
      <phone>
        <number></number>
      </phone>
    </contactInfo>
  </actor>
</request>
```
**Expected Output**: Nested empty structures handled gracefully
**Business Validation**: Deep nesting with empty values doesn't break processing
**XSLT Line Reference**: Lines 1500-1520
**Edge Case**: Nested empty element processing

#### Test Case 12.8: Mixed Valid/Invalid Data
**Input XML**:
```xml
<request>
  <actor>
    <name>John Doe</name>
    <email>invalid_email_format</email>
    <phone>+1-555-1234</phone>
  </actor>
</request>
```
**Expected Output**: Valid data processed, invalid data handled gracefully
**Business Validation**: Mixed data quality handled appropriately
**XSLT Line Reference**: Lines 1540-1580
**Analysis Instruction**: Mixed data validation patterns

#### Test Case 12.9: Circular Reference Prevention
**Input XML**:
```xml
<request>
  <actor id="actor1">
    <referenceId>actor1</referenceId>
  </actor>
</request>
```
**Expected Output**: Circular reference detected and handled
**Business Validation**: Self-referencing data doesn't cause infinite loops
**XSLT Line Reference**: Lines 1560-1580
**Edge Case**: Circular reference detection

#### Test Case 12.10: Multiple Error Conditions
**Input XML**:
```xml
<request>
  <actor>
    <name></name>
    <email>bad_format</email>
    <phone>invalid_phone</phone>
    <address></address>
  </actor>
</request>
```
**Expected Output**: All error conditions handled simultaneously
**Business Validation**: Multiple errors don't compound or cause failures
**XSLT Line Reference**: Lines 1500-1600
**Analysis Instruction**: Multiple error condition handling

#### Test Case 12.11: Boundary Value Testing
**Input XML**:
```xml
<request>
  <actor>
    <age>0</age>
    <seatPreference>999</seatPreference>
  </actor>
</request>
```
**Expected Output**: Boundary values processed according to business rules
**Business Validation**: Edge values (0, maximum numbers) handled correctly
**XSLT Line Reference**: Lines 1520-1560
**Edge Case**: Boundary value handling

#### Test Case 12.12: Unicode and Encoding Edge Cases
**Input XML**:
```xml
<request>
  <actor>
    <name>José Müller</name>
    <address>北京市朝阳区</address>
  </actor>
</request>
```
**Expected Output**: Unicode characters preserved throughout transformation
**Business Validation**: International characters handled correctly
**XSLT Line Reference**: Lines 1500-1600
**Edge Case**: Unicode/encoding preservation

## Category 13: Multi-passenger Complex Scenario Tests (10 test cases)

### Business Logic Analysis
**XSLT Location**: Lines 249-767 (Passenger data processing)
**Analysis Instructions**: Extract multi-passenger processing patterns and complex scenario handling
**What Analysis Revealed**: Complex passenger loops, relationship handling, group processing logic
**Business Context**: Airlines need to process multiple passengers with different roles, relationships, and service requirements

#### Test Case 13.1: Family Group with Different Roles
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>John</FirstName>
      <LastName>Smith</LastName>
    </Name>
    <role>Buyer</role>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Jane</FirstName>
      <LastName>Smith</LastName>
    </Name>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Tommy</FirstName>
      <LastName>Smith</LastName>
    </Name>
    <role>Traveller</role>
    <age>8</age>
  </actor>
</request>
```
**Expected Output**: Three passengers with different role assignments
**Business Validation**: Family groups processed with appropriate role hierarchy
**XSLT Line Reference**: Lines 249-300
**Analysis Instruction**: Multi-passenger role processing patterns

#### Test Case 13.2: Mixed Adult/Child Passengers
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Sarah</FirstName>
      <LastName>Johnson</LastName>
    </Name>
    <dateOfBirth>1985-03-15</dateOfBirth>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Emma</FirstName>
      <LastName>Johnson</LastName>
    </Name>
    <dateOfBirth>2018-07-22</dateOfBirth>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Adult and child passengers with age-appropriate processing
**Business Validation**: Age-based passenger categorization handled correctly
**XSLT Line Reference**: Lines 350-400
**Analysis Instruction**: Age-based passenger processing logic

#### Test Case 13.3: Passengers with Different Contact Preferences
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Mike</FirstName>
      <LastName>Wilson</LastName>
    </Name>
    <contactInfo>
      <email>mike@email.com</email>
      <phone>+1-555-0001</phone>
    </contactInfo>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Lisa</FirstName>
      <LastName>Wilson</LastName>
    </Name>
    <contactInfo>
      <email>lisa@email.com</email>
    </contactInfo>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Different contact processing for each passenger
**Business Validation**: Individual contact preferences preserved
**XSLT Line Reference**: Lines 769-1227
**Analysis Instruction**: Multi-passenger contact processing

#### Test Case 13.4: Group with Special Service Requests
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>David</FirstName>
      <LastName>Brown</LastName>
    </Name>
    <specialService>WHEELCHAIR</specialService>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Mary</FirstName>
      <LastName>Brown</LastName>
    </Name>
    <specialService>DIETARY_RESTRICTION</specialService>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Individual special service requests processed
**Business Validation**: Special services tracked per passenger
**XSLT Line Reference**: Lines 1229-1400
**Analysis Instruction**: Special service request processing per passenger

#### Test Case 13.5: Passengers with Different Document Types
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Robert</FirstName>
      <LastName>Davis</LastName>
    </Name>
    <docRef>
      <type>P</type>
      <PassportNumber>ABC123456</PassportNumber>
      <issuer>US</issuer>
    </docRef>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Jennifer</FirstName>
      <LastName>Davis</LastName>
    </Name>
    <docRef>
      <type>ID</type>
      <IDNumber>DL789012</IDNumber>
      <issuer>US</issuer>
    </docRef>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Different document types processed appropriately
**Business Validation**: Mixed document types handled correctly
**XSLT Line Reference**: Lines 328-477
**Analysis Instruction**: Multi-passenger document processing

#### Test Case 13.6: Complex Seating Arrangements
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>James</FirstName>
      <LastName>Miller</LastName>
    </Name>
    <seatPreference>12A</seatPreference>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Patricia</FirstName>
      <LastName>Miller</LastName>
    </Name>
    <seatPreference>12B</seatPreference>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Kevin</FirstName>
      <LastName>Miller</LastName>
    </Name>
    <seatPreference>12C</seatPreference>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Adjacent seating preferences processed
**Business Validation**: Group seating arrangements maintained
**XSLT Line Reference**: Lines 232-241
**Analysis Instruction**: Seat preference processing for groups

#### Test Case 13.7: Passengers with Loyalty Programs
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Charles</FirstName>
      <LastName>Anderson</LastName>
    </Name>
    <loyaltyProgram>
      <programName>UNITED_MILEAGEPLUS</programName>
      <membershipNumber>MP123456789</membershipNumber>
    </loyaltyProgram>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Susan</FirstName>
      <LastName>Anderson</LastName>
    </Name>
    <loyaltyProgram>
      <programName>DELTA_SKYMILES</programName>
      <membershipNumber>DL987654321</membershipNumber>
    </loyaltyProgram>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Different loyalty programs processed per passenger
**Business Validation**: Individual loyalty program memberships maintained
**XSLT Line Reference**: Lines 616-683
**Analysis Instruction**: Multi-passenger loyalty processing

#### Test Case 13.8: International Travel Group
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Thomas</FirstName>
      <LastName>Taylor</LastName>
    </Name>
    <docRef>
      <type>P</type>
      <PassportNumber>GB1234567</PassportNumber>
      <issuer>GB</issuer>
    </docRef>
    <visaInfo>
      <type>V</type>
      <number>US123456</number>
    </visaInfo>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name>
      <FirstName>Helen</FirstName>
      <LastName>Taylor</LastName>
    </Name>
    <docRef>
      <type>P</type>
      <PassportNumber>GB7654321</PassportNumber>
      <issuer>GB</issuer>
    </docRef>
    <visaInfo>
      <type>V</type>
      <number>US654321</number>
    </visaInfo>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: International documentation processed for group
**Business Validation**: Visa and passport processing for international travel
**XSLT Line Reference**: Lines 425-485
**Analysis Instruction**: International travel documentation processing

#### Test Case 13.9: Large Group Booking (5+ Passengers)
**Input XML**:
```xml
<request>
  <actor>
    <Name><FirstName>Member1</FirstName><LastName>Group</LastName></Name>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name><FirstName>Member2</FirstName><LastName>Group</LastName></Name>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name><FirstName>Member3</FirstName><LastName>Group</LastName></Name>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name><FirstName>Member4</FirstName><LastName>Group</LastName></Name>
    <role>Traveller</role>
  </actor>
  <actor>
    <Name><FirstName>Member5</FirstName><LastName>Group</LastName></Name>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: All five passengers processed in group context
**Business Validation**: Large group processing handled efficiently
**XSLT Line Reference**: Lines 249-767
**Analysis Instruction**: Large group processing performance

#### Test Case 13.10: Mixed Passenger Scenarios
**Input XML**:
```xml
<request>
  <actor>
    <Name>
      <FirstName>Complex</FirstName>
      <LastName>Scenario</LastName>
    </Name>
    <role>Buyer</role>
    <role>Traveller</role>
    <contactInfo>
      <email>complex@email.com</email>
      <phone>+1-555-9999</phone>
    </contactInfo>
    <loyaltyProgram>
      <programName>UNITED_MILEAGEPLUS</programName>
      <membershipNumber>MP999999999</membershipNumber>
    </loyaltyProgram>
    <docRef>
      <type>P</type>
      <PassportNumber>COMPLEX123</PassportNumber>
      <issuer>US</issuer>
    </docRef>
    <specialService>VIP</specialService>
    <seatPreference>1A</seatPreference>
  </actor>
  <actor>
    <Name>
      <FirstName>Simple</FirstName>
      <LastName>Passenger</LastName>
    </Name>
    <role>Traveller</role>
  </actor>
</request>
```
**Expected Output**: Complex and simple passengers processed appropriately
**Business Validation**: Mixed complexity levels handled correctly
**XSLT Line Reference**: Lines 249-767
**Analysis Instruction**: Complex vs simple passenger processing

## Category 14: Integration and End-to-End Tests (15 test cases)

### Business Logic Analysis
**XSLT Location**: Lines 66-1868 (Complete transformation flow)
**Analysis Instructions**: Validate complete transformation from input to output with real-world complexity
**What Analysis Revealed**: Full integration testing of all business logic components working together
**Business Context**: End-to-end validation of complete order creation transformation

#### Test Case 14.1: Complete Order Creation Flow
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>John</FirstName>
        <LastName>Doe</LastName>
      </Name>
      <role>Buyer</role>
      <role>Traveller</role>
      <contactInfo>
        <email>john.doe@email.com</email>
        <phone>+1-555-1234</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>US123456789</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>FLIGHT001</productCode>
      </product>
    </setInternal>
    <agencyInfo>
      <agencyCode>TRAVEL123</agencyCode>
      <agentName>Travel Agent</agentName>
    </agencyInfo>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Complete OrderCreateRQ with all elements populated
**Business Validation**: Full transformation produces valid IATA NDC message
**XSLT Line Reference**: Lines 66-1868
**Analysis Instruction**: End-to-end transformation validation

#### Test Case 14.2: Multi-Target Processing (UA vs Non-UA)
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>DL</target>
    <actor>
      <Name>
        <FirstName>Jane</FirstName>
        <LastName>Smith</LastName>
      </Name>
      <role>Traveller</role>
      <docRef>
        <type>P</type>
        <PassportNumber>US987654321</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>DL</ownerCode>
        <productCode>FLIGHT002</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Non-UA specific processing applied
**Business Validation**: Target-specific business rules applied correctly
**XSLT Line Reference**: Lines 425, 485, 616, 683
**Analysis Instruction**: Target-based conditional processing validation

#### Test Case 14.3: Complete Family Booking Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Robert</FirstName>
        <LastName>Johnson</LastName>
      </Name>
      <role>Buyer</role>
      <role>Traveller</role>
      <contactInfo>
        <email>robert@email.com</email>
        <phone>+1-555-5555</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>US111111111</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <actor>
      <Name>
        <FirstName>Mary</FirstName>
        <LastName>Johnson</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>mary@email.com</email>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>US222222222</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <actor>
      <Name>
        <FirstName>Billy</FirstName>
        <LastName>Johnson</LastName>
      </Name>
      <role>Traveller</role>
      <dateOfBirth>2015-08-15</dateOfBirth>
      <docRef>
        <type>P</type>
        <PassportNumber>US333333333</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>FAMILY_TRIP</productCode>
      </product>
    </setInternal>
    <agencyInfo>
      <agencyCode>FAMILY_TRAVEL</agencyCode>
      <agentName>Family Travel Agent</agentName>
    </agencyInfo>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Complete family booking with all passengers processed
**Business Validation**: Family group processing with roles, contacts, and documents
**XSLT Line Reference**: Lines 66-1868
**Analysis Instruction**: Multi-passenger family integration testing

#### Test Case 14.4: International Travel with Visas
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UAD</target>
    <actor>
      <Name>
        <FirstName>Hans</FirstName>
        <LastName>Mueller</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>hans@email.de</email>
        <phone>+49-30-12345678</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>DE123456789</PassportNumber>
        <issuer>DE</issuer>
        <dateOfBirth>1980-05-20</dateOfBirth>
      </docRef>
      <visaInfo>
        <type>V</type>
        <number>US987654321</number>
      </visaInfo>
      <address>
        <countryCode>DE</countryCode>
        <line>Hauptstraße 123</line>
        <cityName>Berlin</cityName>
        <countryName>Germany</countryName>
        <zip>10115</zip>
      </address>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>INTL_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: International passenger with visa and address processing
**Business Validation**: UAD target processing with international documentation
**XSLT Line Reference**: Lines 425-485, 1350-1450
**Analysis Instruction**: International travel integration testing

#### Test Case 14.5: Loyalty Program Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Premium</FirstName>
        <LastName>Traveler</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>premium@email.com</email>
        <phone>+1-555-7777</phone>
      </contactInfo>
      <loyaltyProgram>
        <programName>UNITED_MILEAGEPLUS</programName>
        <membershipNumber>MP123456789</membershipNumber>
        <tierLevel>PREMIER_PLATINUM</tierLevel>
      </loyaltyProgram>
      <docRef>
        <type>P</type>
        <PassportNumber>US555555555</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>PREMIUM_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Premium traveler with loyalty program benefits
**Business Validation**: Loyalty program processing with tier recognition
**XSLT Line Reference**: Lines 616-683
**Analysis Instruction**: Loyalty program integration validation

#### Test Case 14.6: Special Service Requests Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Special</FirstName>
        <LastName>Needs</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>special@email.com</email>
        <phone>+1-555-8888</phone>
      </contactInfo>
      <specialService>WHEELCHAIR</specialService>
      <specialService>DIETARY_RESTRICTION</specialService>
      <dietaryRestriction>VEGETARIAN</dietaryRestriction>
      <medicalInfo>
        <condition>MOBILITY_IMPAIRED</condition>
      </medicalInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>US666666666</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>ACCESSIBLE_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Special service requests processed in metadata
**Business Validation**: Accessibility and dietary requirements integrated
**XSLT Line Reference**: Lines 1229-1400
**Analysis Instruction**: Special service request integration

#### Test Case 14.7: Corporate Travel Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Corporate</FirstName>
        <LastName>Traveler</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>corporate@company.com</email>
        <phone>+1-555-9999</phone>
      </contactInfo>
      <companyInfo>
        <companyName>ACME Corporation</companyName>
        <taxId>TAX123456789</taxId>
      </companyInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>US777777777</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>CORPORATE_FLIGHT</productCode>
      </product>
    </setInternal>
    <agencyInfo>
      <agencyCode>CORPORATE_TRAVEL</agencyCode>
      <agentName>Corporate Travel Agent</agentName>
    </agencyInfo>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Corporate traveler with company information
**Business Validation**: Business travel processing with tax ID
**XSLT Line Reference**: Lines 1750-1810
**Analysis Instruction**: Corporate travel integration

#### Test Case 14.8: Seat Selection Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Seat</FirstName>
        <LastName>Selector</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>seat@email.com</email>
        <phone>+1-555-0000</phone>
      </contactInfo>
      <seatPreference>12A</seatPreference>
      <seatType>WINDOW</seatType>
      <cabinClass>BUSINESS</cabinClass>
      <docRef>
        <type>P</type>
        <PassportNumber>US888888888</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>BUSINESS_FLIGHT</productCode>
        <seatNumber>12A</seatNumber>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Seat selection processed with preferences
**Business Validation**: Seat assignment and preferences integration
**XSLT Line Reference**: Lines 232-241
**Analysis Instruction**: Seat selection integration validation

#### Test Case 14.9: Error Recovery Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Incomplete</FirstName>
        <LastName>Data</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>incomplete@email.com</email>
        <!-- Missing phone -->
      </contactInfo>
      <docRef>
        <type>P</type>
        <!-- Missing passport number -->
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>INCOMPLETE_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Transformation completes with missing data handled gracefully
**Business Validation**: Error recovery mechanisms work in full integration
**XSLT Line Reference**: Lines 1500-1600
**Analysis Instruction**: Error recovery integration testing

#### Test Case 14.10: Maximum Complexity Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UAD</target>
    <actor>
      <Name>
        <Type>Male</Type>
        <FirstName>Maximum</FirstName>
        <MiddleName>Complexity</MiddleName>
        <LastName>Scenario</LastName>
      </Name>
      <role>Buyer</role>
      <role>Traveller</role>
      <contactInfo>
        <email>max@email.com</email>
        <phone>+1-555-1111</phone>
        <address>
          <countryCode>US</countryCode>
          <line>Complex Address Line</line>
          <cityName>Complex City</cityName>
          <countryName>United States</countryName>
          <zip>12345</zip>
        </address>
      </contactInfo>
      <loyaltyProgram>
        <programName>UNITED_MILEAGEPLUS</programName>
        <membershipNumber>MP999999999</membershipNumber>
        <tierLevel>PREMIER_1K</tierLevel>
      </loyaltyProgram>
      <docRef>
        <type>P</type>
        <PassportNumber>US999999999</PassportNumber>
        <issuer>US</issuer>
        <dateOfBirth>1975-12-25</dateOfBirth>
      </docRef>
      <visaInfo>
        <type>V</type>
        <number>VISA999999</number>
      </visaInfo>
      <specialService>VIP</specialService>
      <specialService>WHEELCHAIR</specialService>
      <seatPreference>1A</seatPreference>
      <companyInfo>
        <companyName>Maximum Corp</companyName>
        <taxId>TAX999999999</taxId>
      </companyInfo>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>MAXIMUM_FLIGHT</productCode>
        <seatNumber>1A</seatNumber>
      </product>
    </setInternal>
    <agencyInfo>
      <agencyCode>MAXIMUM_TRAVEL</agencyCode>
      <agentName>Maximum Travel Agent</agentName>
    </agencyInfo>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: All business logic components integrated successfully
**Business Validation**: Maximum complexity scenario processes without errors
**XSLT Line Reference**: Lines 66-1868
**Analysis Instruction**: Maximum complexity integration validation

#### Test Case 14.11: Point of Sale Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <pointOfSale>
      <country>US</country>
      <city>NYC</city>
      <agencyCode>NYC_TRAVEL</agencyCode>
    </pointOfSale>
    <actor>
      <Name>
        <FirstName>POS</FirstName>
        <LastName>Test</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>pos@email.com</email>
        <phone>+1-555-2222</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>USPOS123456</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>POS_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Point of Sale information integrated in output
**Business Validation**: POS processing overrides default FR/NCE values
**XSLT Line Reference**: Lines 82-91
**Analysis Instruction**: Point of Sale integration validation

#### Test Case 14.12: Agency Information Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Agency</FirstName>
        <LastName>Booking</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>agency@email.com</email>
        <phone>+1-555-3333</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>USAGENCY123</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>AGENCY_FLIGHT</productCode>
      </product>
    </setInternal>
    <agencyInfo>
      <agencyCode>PREMIUM_TRAVEL</agencyCode>
      <agentName>Premium Travel Agent</agentName>
      <agentId>AGENT123</agentId>
      <agencyPhone>+1-555-4444</agencyPhone>
      <agencyEmail>agency@premium.com</agencyEmail>
    </agencyInfo>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Complete agency information in travel agency sender
**Business Validation**: Agency details integrated in Party/Sender section
**XSLT Line Reference**: Lines 95-180
**Analysis Instruction**: Agency information integration

#### Test Case 14.13: Product and Offer Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Product</FirstName>
        <LastName>Buyer</LastName>
      </Name>
      <role>Buyer</role>
      <role>Traveller</role>
      <contactInfo>
        <email>product@email.com</email>
        <phone>+1-555-5555</phone>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>USPROD123456</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>PREMIUM_PRODUCT</productCode>
        <productName>Premium Flight Service</productName>
        <price>999.99</price>
        <currency>USD</currency>
      </product>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>ADDITIONAL_SERVICE</productCode>
        <productName>Extra Baggage</productName>
        <price>50.00</price>
        <currency>USD</currency>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Multiple products processed in order query
**Business Validation**: Product and offer integration with pricing
**XSLT Line Reference**: Lines 182-248
**Analysis Instruction**: Product and offer integration validation

#### Test Case 14.14: Contact List Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UA</target>
    <actor>
      <Name>
        <FirstName>Contact</FirstName>
        <LastName>Rich</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>contact@email.com</email>
        <phone>+1-555-6666</phone>
        <emergencyContact>
          <name>Emergency Person</name>
          <phone>+1-555-7777</phone>
          <relationship>SPOUSE</relationship>
        </emergencyContact>
      </contactInfo>
      <docRef>
        <type>P</type>
        <PassportNumber>USCONT123456</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>CONTACT_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Complete contact information processing
**Business Validation**: Contact lists with emergency contacts integrated
**XSLT Line Reference**: Lines 769-1227
**Analysis Instruction**: Contact list integration validation

#### Test Case 14.15: Metadata Generation Integration
**Input XML**:
```xml
<ConnectivityLayerBom>
  <request>
    <target>UAD</target>
    <actor>
      <Name>
        <FirstName>Metadata</FirstName>
        <LastName>Generator</LastName>
      </Name>
      <role>Traveller</role>
      <contactInfo>
        <email>metadata@email.com</email>
        <phone>+1-555-8888</phone>
        <address>
          <countryCode>US</countryCode>
          <line>Metadata Address</line>
          <cityName>Metadata City</cityName>
          <zip>54321</zip>
        </address>
      </contactInfo>
      <specialService>GST</specialService>
      <passengerMetadata>
        <field1>Custom Value 1</field1>
        <field2>Custom Value 2</field2>
      </passengerMetadata>
      <docRef>
        <type>P</type>
        <PassportNumber>USMETA123456</PassportNumber>
        <issuer>US</issuer>
      </docRef>
    </actor>
    <setInternal>
      <product>
        <ownerCode>UA</ownerCode>
        <productCode>METADATA_FLIGHT</productCode>
      </product>
    </setInternal>
  </request>
</ConnectivityLayerBom>
```
**Expected Output**: Complete metadata section with passenger-specific data
**Business Validation**: Metadata generation with address concatenation and GST processing
**XSLT Line Reference**: Lines 1229-1863
**Analysis Instruction**: Metadata generation integration validation

## Test Case Summary

**Total Test Cases Generated**: 177 comprehensive test cases
- **Category 1: Helper Template Function Tests**: 25 test cases
- **Category 2: Target Processing Tests**: 12 test cases  
- **Category 3: Gender and Name Mapping Tests**: 8 test cases
- **Category 4: Contact Processing Tests**: 15 test cases
- **Category 5: Address and Metadata Generation Tests**: 18 test cases
- **Category 6: Seat and Product Processing Tests**: 12 test cases
- **Category 7: Document and Visa Processing Tests**: 15 test cases
- **Category 8: Loyalty Processing Tests**: 8 test cases
- **Category 9: Tax ID and FOID Processing Tests**: 10 test cases
- **Category 10: Travel Agency and POS Processing Tests**: 9 test cases
- **Category 11: Redress Case Processing Tests**: 8 test cases
- **Category 12: Edge Cases and Error Handling Tests**: 12 test cases
- **Category 13: Multi-passenger Complex Scenario Tests**: 10 test cases
- **Category 14: Integration and End-to-End Tests**: 15 test cases

**Business Logic Coverage**: All major XSLT transformation patterns covered with comprehensive test scenarios including positive cases, negative cases, edge cases, and integration scenarios.

**Analysis Methodology**: Each test case includes detailed analysis instructions, XSLT line references, business rule explanations, and expected behavior validation.