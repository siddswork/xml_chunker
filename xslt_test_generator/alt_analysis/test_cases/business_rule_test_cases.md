# Comprehensive Business Rule Test Cases for OrderCreate XSLT Transformation

## Test Case Generation Methodology
Based on comprehensive analysis of:
- XSLT transformation logic (1,870 lines with 4 helper templates + main template)
- Input schema (AMA_ConnectivityLayerRQ.xsd with TTR_ActorType and setInternalType)
- Output schema (OrderCreateRQ.xsd with IATA NDC standard)
- 8 major business logic patterns identified through manual analysis

## Category 1: Helper Template Function Tests (25 test cases)

### vmf:vmf1_inputtoresult Template Tests (7 test cases)
**Business Logic**: Document type code transformation for visa/passport processing
**XSLT Location**: Lines 12-25
**Input Parameter**: Document type string
**Output**: Standardized visa/passport type code

#### Test Case 1.1: Valid Passport Code 'P'
- **Input**: `<type>P</type>`
- **Expected Output**: `VPT`
- **Business Validation**: Passport type 'P' correctly maps to Visa Passport Type
- **XSLT Line Reference**: Line 15-16

#### Test Case 1.2: Valid Passport Type 'PT'  
- **Input**: `<type>PT</type>`
- **Expected Output**: `VPT`
- **Business Validation**: Passport Type 'PT' correctly maps to Visa Passport Type
- **XSLT Line Reference**: Line 18-19

#### Test Case 1.3: Invalid Document Type
- **Input**: `<type>INVALID</type>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Unrecognized codes return empty string
- **XSLT Line Reference**: Line 21-22

#### Test Case 1.4: Empty Input
- **Input**: `<type></type>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Empty input handled gracefully
- **Edge Case**: Empty element processing

#### Test Case 1.5: Null/Missing Input
- **Input**: No type element provided
- **Expected Output**: `` (empty string)
- **Business Validation**: Missing data handled gracefully
- **Edge Case**: Missing element processing

#### Test Case 1.6: Case Sensitivity Test
- **Input**: `<type>p</type>` (lowercase)
- **Expected Output**: `` (empty string)
- **Business Validation**: XSLT is case-sensitive, lowercase 'p' not recognized
- **Edge Case**: Case sensitivity validation

#### Test Case 1.7: Special Characters
- **Input**: `<type>P@#$</type>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Special characters in type codes rejected
- **Edge Case**: Special character handling

### vmf:vmf2_inputtoresult Template Tests (7 test cases)
**Business Logic**: Visa/document type code transformation for various visa categories
**XSLT Location**: Lines 26-42
**Input Parameter**: Visa type string
**Output**: Standardized NDC visa type code

#### Test Case 2.1: Valid Visa Code 'V'
- **Input**: `<visaType>V</visaType>`
- **Expected Output**: `VVI`
- **Business Validation**: Visa type 'V' maps to Visa Visitor
- **XSLT Line Reference**: Line 29-30

#### Test Case 2.2: Valid Residence Code 'R'
- **Input**: `<visaType>R</visaType>`
- **Expected Output**: `VAEA`
- **Business Validation**: Residence type 'R' maps to Visa Area Entry Authorization
- **XSLT Line Reference**: Line 32-33

#### Test Case 2.3: Valid Card Code 'K'
- **Input**: `<visaType>K</visaType>`
- **Expected Output**: `VCR`
- **Business Validation**: Card type 'K' maps to Visa Card Residence
- **XSLT Line Reference**: Line 35-36

#### Test Case 2.4: Invalid Visa Type
- **Input**: `<visaType>UNKNOWN</visaType>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Unrecognized visa codes return empty string
- **XSLT Line Reference**: Line 38-39

#### Test Case 2.5: Case Sensitivity Test
- **Input**: `<visaType>v</visaType>` (lowercase)
- **Expected Output**: `` (empty string)
- **Business Validation**: Lowercase visa codes not recognized
- **Edge Case**: Case sensitivity for visa processing

#### Test Case 2.6: Multiple Character Input
- **Input**: `<visaType>VV</visaType>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Multi-character codes not supported
- **Edge Case**: Input length validation

#### Test Case 2.7: Numeric Input
- **Input**: `<visaType>1</visaType>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Numeric visa codes rejected
- **Edge Case**: Non-alphabetic input handling

### vmf:vmf3_inputtoresult Template Tests (6 test cases)
**Business Logic**: Contact method transformation for email processing
**XSLT Location**: Lines 43-53
**Input Parameter**: Contact label string
**Output**: Operational contact type designation

#### Test Case 3.1: Valid Email Label
- **Input**: `<label>email</label>`
- **Expected Output**: `Voperational`
- **Business Validation**: Email contact type correctly classified as operational
- **XSLT Line Reference**: Line 46-47

#### Test Case 3.2: Case Sensitivity Test - Uppercase
- **Input**: `<label>EMAIL</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Uppercase email label not recognized
- **Edge Case**: Case sensitivity for contact labels

#### Test Case 3.3: Case Sensitivity Test - Mixed Case
- **Input**: `<label>Email</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Mixed case email label not recognized
- **Edge Case**: Case sensitivity validation

#### Test Case 3.4: Invalid Contact Type
- **Input**: `<label>phone</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Non-email contact types return empty string
- **XSLT Line Reference**: Line 49-50

#### Test Case 3.5: Empty Input
- **Input**: `<label></label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Empty contact labels handled gracefully
- **Edge Case**: Empty element processing

#### Test Case 3.6: Special Characters in Label
- **Input**: `<label>email@</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Contact labels with special characters rejected
- **Edge Case**: Special character validation

### vmf:vmf4_inputtoresult Template Tests (5 test cases)
**Business Logic**: Contact method transformation for mobile processing
**XSLT Location**: Lines 54-64
**Input Parameter**: Contact label string
**Output**: Operational contact type designation

#### Test Case 4.1: Valid Mobile Label
- **Input**: `<label>mobile</label>`
- **Expected Output**: `Voperational`
- **Business Validation**: Mobile contact type correctly classified as operational
- **XSLT Line Reference**: Line 57-58

#### Test Case 4.2: Case Sensitivity Test
- **Input**: `<label>Mobile</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Capitalized mobile label not recognized
- **Edge Case**: Case sensitivity for mobile labels

#### Test Case 4.3: Alternative Mobile Terms
- **Input**: `<label>cell</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Alternative mobile terms not supported
- **Edge Case**: Synonym rejection

#### Test Case 4.4: Invalid Contact Type
- **Input**: `<label>landline</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Non-mobile contact types return empty string
- **XSLT Line Reference**: Line 60-61

#### Test Case 4.5: Numeric Input
- **Input**: `<label>123</label>`
- **Expected Output**: `` (empty string)
- **Business Validation**: Numeric contact labels rejected
- **Edge Case**: Non-alphabetic input validation

## Category 2: Target-Based Processing Tests (12 test cases)

### UA Target Processing Tests (4 test cases)
**Business Logic**: Special processing for United Airlines (UA) target systems
**XSLT Locations**: Lines 425, 485, 616, 683, 1238, 1267, 1750, 1810
**Key Pattern**: `$var4_cur/target = 'UA'` conditional logic

#### Test Case 5.1: UA Target with Visa Type 'R'
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <docRef>
      <visa>
        <visaType>R</visaType>
        <visaNumber>V123456</visaNumber>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Behavior**: Visa processing blocked for UA target with 'R' type
- **Business Rule**: UA systems exclude 'R' visa types from processing
- **XSLT Line Reference**: Lines 425-426, 616-619

#### Test Case 5.2: UA Target with Tax Identifier
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>123456789</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: FOID special service request generated
- **Business Rule**: UA target generates tax ID metadata for adult passengers
- **XSLT Line Reference**: Lines 1810-1860

#### Test Case 5.3: UA Target Adult Passenger Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>John Doe</addresseeName>
      <line>123 Main St</line>
      <cityName>New York</cityName>
      <countryCode>US</countryCode>
    </address>
  </actor>
</Request>
```
- **Expected Behavior**: No GST processing for UA target
- **Business Rule**: UA systems exclude GST passenger processing
- **XSLT Line Reference**: Lines 1238-1241, 1267-1270

#### Test Case 5.4: UA Target Visa Number Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <docRef>
      <visa>
        <visaType>K</visaType>
        <visaNumber>K987654</visaNumber>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: IdentityDocument with 'CR' type generated
- **Business Rule**: UA target with 'K' visa type generates CR document
- **XSLT Line Reference**: Lines 677-730

### UAD Target Processing Tests (4 test cases)
**Business Logic**: Special processing for United Airlines Domestic (UAD) target systems
**XSLT Locations**: Same as UA target but with 'UAD' value
**Key Pattern**: `$var4_cur/target = 'UAD'` conditional logic

#### Test Case 6.1: UAD Target with Visa Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UAD</target>
  <actor>
    <docRef>
      <visa>
        <visaType>R</visaType>
        <visaHostCountryCode>US</visaHostCountryCode>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Behavior**: Similar to UA target - visa processing blocked for 'R' type
- **Business Rule**: UAD systems have same visa restrictions as UA
- **XSLT Line Reference**: Lines 425-426, 485-486

#### Test Case 6.2: UAD Target with Adult Passenger
- **Input XML Structure**:
```xml
<Request>
  <target>UAD</target>
  <actor>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Jane Smith</addresseeName>
      <companyName>ACME Corp</companyName>
    </address>
  </actor>
</Request>
```
- **Expected Behavior**: No GST processing for UAD target
- **Business Rule**: UAD systems exclude GST passenger processing like UA
- **XSLT Line Reference**: Lines 1238-1241, 1750-1751

#### Test Case 6.3: UAD Target Tax Identifier Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UAD</target>
  <actor>
    <ID>PAX1</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>TIN</fiscalType>
        <fiscalNumber>987654321</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <set>
    <property>
      <key>OwnerCode</key>
      <value>UA123</value>
    </property>
  </set>
</Request>
```
- **Expected Output**: FOID SSR with airline code and tax ID information
- **Business Rule**: UAD target generates tax metadata same as UA
- **XSLT Line Reference**: Lines 1810-1860

#### Test Case 6.4: UAD Target Identity Document Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UAD</target>
  <actor>
    <docRef>
      <visa>
        <visaType>K</visaType>
        <visaNumber>K555666</visaNumber>
        <visaIssueCountryCode>CA</visaIssueCountryCode>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: CR type identity document with visa information
- **Business Rule**: UAD 'K' visa processing same as UA target
- **XSLT Line Reference**: Lines 677-730

### Non-UA/UAD Target Processing Tests (4 test cases)
**Business Logic**: Standard processing for all other airline targets
**Key Pattern**: Default processing when target is not 'UA' or 'UAD'

#### Test Case 7.1: Standard Target with Adult GST Passenger
- **Input XML Structure**:
```xml
<Request>
  <target>LH</target>
  <actor>
    <ID>PAX1</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Hans Mueller</addresseeName>
      <companyName>Lufthansa Corp</companyName>
      <line>Airport Str 1</line>
      <cityName>Frankfurt</cityName>
      <countryCode>DE</countryCode>
      <zip>60549</zip>
    </address>
    <contact>
      <contactType>GST</contactType>
      <phone>+49691234567</phone>
      <email>hans@lufthansa.com</email>
    </contact>
  </actor>
</Request>
```
- **Expected Output**: Full GST passenger metadata with SSRs
- **Business Rule**: Non-UA targets enable GST passenger processing
- **XSLT Line Reference**: Lines 1255-1863

#### Test Case 7.2: Standard Target with Visa Type 'R'
- **Input XML Structure**:
```xml
<Request>
  <target>AF</target>
  <actor>
    <docRef>
      <visa>
        <visaType>R</visaType>
        <visaNumber>R789123</visaNumber>
        <visaHostCountryCode>FR</visaHostCountryCode>
        <enterBeforeDate>2024-12-31</enterBeforeDate>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: VAEA identity document type with visa details
- **Business Rule**: Non-UA targets allow 'R' visa processing
- **XSLT Line Reference**: Lines 610-676

#### Test Case 7.3: Standard Target without Tax Identifier
- **Input XML Structure**:
```xml
<Request>
  <target>BA</target>
  <actor>
    <ID>PAX2</ID>
    <PTC>ADT</PTC>
    <Name>
      <FirstName>John</FirstName>
      <LastName>Smith</LastName>
    </Name>
  </actor>
</Request>
```
- **Expected Behavior**: No tax ID metadata generated
- **Business Rule**: Tax ID metadata only for passengers with taxIdentifier
- **XSLT Line Reference**: Lines 1750-1806

#### Test Case 7.4: Standard Target Complex Visa Processing
- **Input XML Structure**:
```xml
<Request>
  <target>LX</target>
  <actor>
    <docRef>
      <type>V</type>
      <visa>
        <visaType>V</visaType>
        <visaNumber>V456789</visaNumber>
        <visaIssueCountryCode>CH</visaIssueCountryCode>
        <visaIssuanceDate>2024-01-15</visaIssuanceDate>
        <enterBeforeDate>2024-12-15</enterBeforeDate>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: VVI identity document with complete visa information
- **Business Rule**: Standard visa processing for non-UA targets
- **XSLT Line Reference**: Lines 478-593

## Category 3: Gender and Name Processing Tests (8 test cases)

### Gender Mapping Logic Tests (4 test cases)
**Business Logic**: Name/Type field mapping to Gender output
**XSLT Location**: Lines 279-289
**Key Rule**: Type = 'Other' → Gender = 'Unspecified', otherwise use Type value

#### Test Case 8.1: Other Gender Type
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Type>Other</Type>
    <FirstName>Alex</FirstName>
    <LastName>Johnson</LastName>
  </Name>
</actor>
```
- **Expected Output**: 
```xml
<Individual>
  <Gender>Unspecified</Gender>
  <GivenName>Alex</GivenName>
  <Surname>Johnson</Surname>
</Individual>
```
- **Business Rule**: 'Other' gender type maps to 'Unspecified'
- **XSLT Line Reference**: Lines 279-283

#### Test Case 8.2: Male Gender Type
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Type>Male</Type>
    <FirstName>John</FirstName>
    <LastName>Doe</LastName>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <Gender>Male</Gender>
  <GivenName>John</GivenName>
  <Surname>Doe</Surname>
</Individual>
```
- **Business Rule**: Non-'Other' gender types passed through directly
- **XSLT Line Reference**: Lines 284-289

#### Test Case 8.3: Female Gender Type
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Type>Female</Type>
    <FirstName>Jane</FirstName>
    <LastName>Smith</LastName>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <Gender>Female</Gender>
  <GivenName>Jane</GivenName>
  <Surname>Smith</Surname>
</Individual>
```
- **Business Rule**: Standard gender values preserved
- **XSLT Line Reference**: Lines 284-289

#### Test Case 8.4: Missing Gender Type
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <FirstName>Pat</FirstName>
    <LastName>Wilson</LastName>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <GivenName>Pat</GivenName>
  <Surname>Wilson</Surname>
</Individual>
```
- **Business Rule**: Missing gender type results in no Gender element
- **XSLT Line Reference**: No gender processing when Type missing

### Name Title Processing Tests (4 test cases)
**Business Logic**: Name title processing and mapping
**XSLT Location**: Lines 290-307

#### Test Case 9.1: Complete Name with Title
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Title>Mr.</Title>
    <FirstName>Robert</FirstName>
    <LastName>Brown</LastName>
    <Type>Male</Type>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <Gender>Male</Gender>
  <NameTitle>Mr.</NameTitle>
  <GivenName>Robert</GivenName>
  <Surname>Brown</Surname>
</Individual>
```
- **Business Rule**: All name components mapped to appropriate output elements
- **XSLT Line Reference**: Lines 290-307

#### Test Case 9.2: Name without Title
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <FirstName>Sarah</FirstName>
    <LastName>Davis</LastName>
    <Type>Female</Type>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <Gender>Female</Gender>
  <GivenName>Sarah</GivenName>
  <Surname>Davis</Surname>
</Individual>
```
- **Business Rule**: Missing title handled gracefully
- **XSLT Line Reference**: No NameTitle element when Title missing

#### Test Case 9.3: Multiple Name Elements
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Title>Dr.</Title>
    <FirstName>Elizabeth</FirstName>
    <LastName>Johnson-Smith</LastName>
    <Type>Female</Type>
  </Name>
  <Name>
    <Type>Other</Type>
    <FirstName>Liz</FirstName>
  </Name>
</actor>
```
- **Expected Output**: First Name element processed, second creates separate Gender element
- **Business Rule**: Multiple Name elements processed independently
- **XSLT Line Reference**: Lines 290-307 for each Name occurrence

#### Test Case 9.4: Empty Name Elements
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Type>Male</Type>
  </Name>
</actor>
```
- **Expected Output**:
```xml
<Individual>
  <Gender>Male</Gender>
</Individual>
```
- **Business Rule**: Empty name components result in minimal output
- **XSLT Line Reference**: Only present elements generate output

## Test Case Count Summary So Far: 45 test cases identified
- **Helper Template Tests**: 25 test cases (4 templates × 5-7 tests each)
- **Target-Based Processing**: 12 test cases (UA, UAD, Standard targets)
- **Gender and Name Processing**: 8 test cases (Gender mapping + Name processing)

## Category 4: Contact Processing Tests (15 test cases)

### Phone Number Processing Tests (8 test cases)
**Business Logic**: Phone number transformation and sanitization
**XSLT Locations**: Lines 145-155, 897-961, 1098-1162
**Key Processing**: Phone number sanitization, label transformation, overseas code handling

#### Test Case 10.1: Phone Number Sanitization
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <overseasCode>+1</overseasCode>
      <PhoneNumber>555-123-4567 ext. 123</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <Label>operational</Label>
    <CountryDialingCode>+1</CountryDialingCode>
    <PhoneNumber>5551234567123</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: Phone numbers stripped of all non-numeric characters
- **XSLT Line Reference**: Line 151 - `translate(., concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')`

#### Test Case 10.2: Mobile Label Transformation
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <PhoneNumber>1234567890</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <Label>operational</Label>
    <PhoneNumber>1234567890</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: Mobile phone label transforms to 'operational' via vmf:vmf4_inputtoresult
- **XSLT Line Reference**: Lines 905-934

#### Test Case 10.3: Unrecognized Phone Label
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>landline</label>
      <PhoneNumber>9876543210</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <Label>landline</Label>
    <PhoneNumber>9876543210</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: Unrecognized labels passed through unchanged
- **XSLT Line Reference**: Lines 938-945

#### Test Case 10.4: Multiple Phone Numbers
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <PhoneNumber>1234567890</PhoneNumber>
    </phone>
    <phone>
      <label>office</label>
      <overseasCode>+44</overseasCode>
      <PhoneNumber>20 7946 0958</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**: Two separate Phone elements with different labels and numbers
- **Business Rule**: Multiple phone elements processed independently
- **XSLT Line Reference**: Lines 897-961 (maxOccurs=10 for phone elements)

#### Test Case 10.5: Phone Number with Only Numbers
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <PhoneNumber>5551234567</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <PhoneNumber>5551234567</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: Pure numeric phone numbers passed through unchanged
- **XSLT Line Reference**: Line 956 - `number(.)`

#### Test Case 10.6: Empty Phone Number
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <PhoneNumber></PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**: No Phone element generated or Phone element with empty PhoneNumber
- **Business Rule**: Empty phone numbers handled gracefully
- **Edge Case**: Empty element processing

#### Test Case 10.7: Phone Number with International Format
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <overseasCode>+86</overseasCode>
      <countryCode>CN</countryCode>
      <PhoneNumber>138-0013-8000</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <Label>operational</Label>
    <CountryDialingCode>+86</CountryDialingCode>
    <PhoneNumber>13800138000</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: International format with country code processed correctly
- **XSLT Line Reference**: Lines 947-957

#### Test Case 10.8: Phone Number with Alphabetic Characters
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <phone>
      <label>mobile</label>
      <PhoneNumber>1-800-FLOWERS</PhoneNumber>
    </phone>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <Phone>
    <Label>operational</Label>
    <PhoneNumber>1800</PhoneNumber>
  </Phone>
</ContactProvided>
```
- **Business Rule**: Alphabetic characters stripped from phone numbers
- **XSLT Line Reference**: Line 151 character removal pattern

### Email Processing Tests (7 test cases)
**Business Logic**: Email address transformation and label processing
**XSLT Locations**: Lines 838-896, 1039-1097
**Key Processing**: Email label transformation, address extraction

#### Test Case 11.1: Email Label Transformation
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <label>email</label>
      <EmailAddress>john.doe@example.com</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <EmailAddress>
    <Label>operational</Label>
    <EmailAddressValue>john.doe@example.com</EmailAddressValue>
  </EmailAddress>
</ContactProvided>
```
- **Business Rule**: Email label transforms to 'operational' via vmf:vmf3_inputtoresult
- **XSLT Line Reference**: Lines 846-875

#### Test Case 11.2: Unrecognized Email Label
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <label>work</label>
      <EmailAddress>jane.smith@company.com</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <EmailAddress>
    <Label>work</Label>
    <EmailAddressValue>jane.smith@company.com</EmailAddressValue>
  </EmailAddress>
</ContactProvided>
```
- **Business Rule**: Unrecognized email labels passed through unchanged
- **XSLT Line Reference**: Lines 879-886

#### Test Case 11.3: Multiple Email Addresses
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <label>email</label>
      <EmailAddress>primary@example.com</EmailAddress>
    </email>
    <email>
      <label>work</label>
      <EmailAddress>work@company.com</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**: Two separate EmailAddress elements with different labels
- **Business Rule**: Multiple email elements processed independently
- **XSLT Line Reference**: Lines 838-896 (maxOccurs=5 for email elements)

#### Test Case 11.4: Email Without Label
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <EmailAddress>nolabel@example.com</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <EmailAddress>
    <EmailAddressValue>nolabel@example.com</EmailAddressValue>
  </EmailAddress>
</ContactProvided>
```
- **Business Rule**: Missing email labels result in no Label element
- **XSLT Line Reference**: No Label processing when label missing

#### Test Case 11.5: Empty Email Address
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <label>email</label>
      <EmailAddress></EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**: EmailAddress element with empty EmailAddressValue or no element
- **Business Rule**: Empty email addresses handled gracefully
- **Edge Case**: Empty element validation

#### Test Case 11.6: Complex Email with Special Characters
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <email>
      <label>email</label>
      <EmailAddress>user+tag@sub.domain.co.uk</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactProvided>
  <EmailAddress>
    <Label>operational</Label>
    <EmailAddressValue>user+tag@sub.domain.co.uk</EmailAddressValue>
  </EmailAddress>
</ContactProvided>
```
- **Business Rule**: Complex email formats preserved in output
- **XSLT Line Reference**: Lines 888-893

#### Test Case 11.7: Contact Refused Indicator
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <contactType>CTC</contactType>
    <ContactRefusedInd>True</ContactRefusedInd>
    <email>
      <label>email</label>
      <EmailAddress>refused@example.com</EmailAddress>
    </email>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactInformation ContactID="CI1PAX1">
  <ContactType>CTC</ContactType>
  <ContactProvided>
    <EmailAddress>
      <Label>operational</Label>
      <EmailAddressValue>refused@example.com</EmailAddressValue>
    </EmailAddress>
  </ContactProvided>
  <ContactNotProvided></ContactNotProvided>
</ContactInformation>
```
- **Business Rule**: ContactRefusedInd=True generates ContactNotProvided element
- **XSLT Line Reference**: Lines 962-966

## Category 5: Address and Metadata Processing Tests (18 test cases)

### Address Processing Tests (9 test cases)
**Business Logic**: Address transformation and postal address creation
**XSLT Locations**: Lines 105-133, 789-836, 990-1038, 1172-1226
**Key Processing**: Address line mapping, country code handling, postal code transformation

#### Test Case 12.1: Complete Address Processing
- **Input XML Structure**:
```xml
<actor>
  <ID>PAX1</ID>
  <contact>
    <contactType>CTC</contactType>
    <Address>
      <line>123 Main Street</line>
      <CityName>New York</CityName>
      <Zip>10001</Zip>
      <CountryCode>US</CountryCode>
    </Address>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<ContactInformation ContactID="CI1PAX1">
  <ContactType>CTC</ContactType>
  <PostalAddress>
    <Street>123 Main Street</Street>
    <CityName>New York</CityName>
    <PostalCode>10001</PostalCode>
    <CountryCode>US</CountryCode>
  </PostalAddress>
</ContactInformation>
```
- **Business Rule**: Address components mapped to postal address structure
- **XSLT Line Reference**: Lines 798-835

#### Test Case 12.2: Travel Agency Address Processing
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Contact>
      <Address>
        <line>456 Travel Plaza</line>
        <CityName>Los Angeles</CityName>
        <Zip>90210</Zip>
        <CountryCode>US</CountryCode>
      </Address>
    </Contact>
  </TravelAgency>
</Request>
```
- **Expected Output**:
```xml
<TravelAgencySender>
  <Contacts>
    <Contact>
      <AddressContact>
        <Street>456 Travel Plaza</Street>
        <CityName>Los Angeles</CityName>
        <PostalCode>90210</PostalCode>
        <CountryCode>US</CountryCode>
      </AddressContact>
    </Contact>
  </Contacts>
</TravelAgencySender>
```
- **Business Rule**: Travel agency addresses use AddressContact structure
- **XSLT Line Reference**: Lines 105-133

#### Test Case 12.3: Multiple Address Lines
- **Input XML Structure**:
```xml
<actor>
  <contact>
    <Address>
      <line>Building A</line>
      <line>123 Business Park</line>
      <line>Industrial District</line>
      <CityName>Chicago</CityName>
      <Zip>60601</Zip>
    </Address>
  </contact>
</actor>
```
- **Expected Output**:
```xml
<PostalAddress>
  <Street>Building A</Street>
  <Street>123 Business Park</Street>
  <Street>Industrial District</Street>
  <CityName>Chicago</CityName>
  <PostalCode>60601</PostalCode>
</PostalAddress>
```
- **Business Rule**: Multiple address lines create multiple Street elements
- **XSLT Line Reference**: Lines 805-811

#### Test Case 12.4: International Address with State
- **Input XML Structure**:
```xml
<actor>
  <address>
    <line>100 Queen Street</line>
    <cityName>Toronto</cityName>
    <stateName>Ontario</stateName>
    <zip>M5H 2N1</zip>
    <countryCode>CA</countryCode>
  </address>
</actor>
```
- **Expected Output**:
```xml
<PostalAddress>
  <Street>100 Queen Street</Street>
  <CityName>Toronto</CityName>
  <PostalCode>M5H 2N1</PostalCode>
  <CountrySubdivisionName>Ontario</CountrySubdivisionName>
  <CountryCode>CA</CountryCode>
</PostalAddress>
```
- **Business Rule**: stateName maps to CountrySubdivisionName
- **XSLT Line Reference**: Lines 823-828

#### Test Case 12.5: Address with Label
- **Input XML Structure**:
```xml
<actor>
  <address>
    <label>Home</label>
    <line>789 Residential St</line>
    <cityName>Miami</cityName>
    <countryCode>US</countryCode>
  </address>
</actor>
```
- **Expected Output**:
```xml
<PostalAddress>
  <Label>Home</Label>
  <Street>789 Residential St</Street>
  <CityName>Miami</CityName>
  <CountryCode>US</CountryCode>
</PostalAddress>
```
- **Business Rule**: Address labels preserved in output
- **XSLT Line Reference**: Lines 799-804

#### Test Case 12.6: Minimal Address Information
- **Input XML Structure**:
```xml
<actor>
  <address>
    <countryCode>FR</countryCode>
  </address>
</actor>
```
- **Expected Output**:
```xml
<PostalAddress>
  <CountryCode>FR</CountryCode>
</PostalAddress>
```
- **Business Rule**: Minimal address with only country code valid
- **XSLT Line Reference**: Lines 829-834

#### Test Case 12.7: Address with Company Information
- **Input XML Structure**:
```xml
<actor>
  <address>
    <companyName>ACME Corporation</companyName>
    <addresseeName>John Smith</addresseeName>
    <line>500 Corporate Blvd</line>
    <cityName>Austin</cityName>
    <countryCode>US</countryCode>
  </address>
</actor>
```
- **Expected Behavior**: Address excluded from contact processing due to companyName presence
- **Business Rule**: Addresses with companyName/addresseeName trigger GST processing instead
- **XSLT Line Reference**: Lines 794-796 exclusion condition

#### Test Case 12.8: Actor with Address but No Contact
- **Input XML Structure**:
```xml
<actor>
  <ID>PAX2</ID>
  <address>
    <line>321 Solo Street</line>
    <cityName>Denver</cityName>
    <countryCode>US</countryCode>
  </address>
</actor>
```
- **Expected Output**:
```xml
<ContactInformation ContactID="CI1PAX2">
  <PostalAddress>
    <Street>321 Solo Street</Street>
    <CityName>Denver</CityName>
    <CountryCode>US</CountryCode>
  </PostalAddress>
  <ContactNotProvided></ContactNotProvided>
</ContactInformation>
```
- **Business Rule**: Address-only actors get ContactNotProvided element
- **XSLT Line Reference**: Lines 1172-1226

#### Test Case 12.9: Empty Address Elements
- **Input XML Structure**:
```xml
<actor>
  <address>
    <line></line>
    <cityName></cityName>
    <countryCode>XX</countryCode>
  </address>
</actor>
```
- **Expected Output**:
```xml
<PostalAddress>
  <CountryCode>XX</CountryCode>
</PostalAddress>
```
- **Business Rule**: Empty address elements omitted from output
- **Edge Case**: Empty element handling

### GST Passenger Metadata Tests (9 test cases)
**Business Logic**: Guest (GST) passenger special service request generation
**XSLT Locations**: Lines 1255-1863
**Key Processing**: Address concatenation, contact data aggregation, SSR generation

#### Test Case 13.1: Complete GST Passenger with Address and Phone
- **Input XML Structure**:
```xml
<Request>
  <target>LH</target>
  <actor>
    <ID>PAX1</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Hans Mueller</addresseeName>
      <companyName>Lufthansa Corp</companyName>
      <line>Airport Str 1</line>
      <cityName>Frankfurt</cityName>
      <countryCode>DE</countryCode>
      <zip>60549</zip>
    </address>
    <contact>
      <contactType>GST</contactType>
      <phone>+49691234567</phone>
    </contact>
  </actor>
</Request>
```
- **Expected Output**:
```xml
<Metadata>
  <PassengerMetadata MetadataKey="PAX1">
    <AugmentationPoint>
      <AugPoint>
        <SpecialServiceRequest>
          <TravelerIDRef>PAX1</TravelerIDRef>
          <SSRCode>GSTN</SSRCode>
          <Text>DE/Hans Mueller/Lufthansa Corp</Text>
          <ActionCode>NN</ActionCode>
        </SpecialServiceRequest>
      </AugPoint>
      <AugPoint>
        <SpecialServiceRequest>
          <TravelerIDRef>PAX1</TravelerIDRef>
          <SSRCode>GSTA</SSRCode>
          <Text>DE/Airport Str 1/Frankfurt/60549</Text>
          <ActionCode>NN</ActionCode>
        </SpecialServiceRequest>
      </AugPoint>
      <AugPoint>
        <SpecialServiceRequest>
          <TravelerIDRef>PAX1</TravelerIDRef>
          <SSRCode>GSTP</SSRCode>
          <Text>DE/+49691234567</Text>
          <ActionCode>NN</ActionCode>
        </SpecialServiceRequest>
      </AugPoint>
    </AugmentationPoint>
  </PassengerMetadata>
</Metadata>
```
- **Business Rule**: GST passengers generate GSTN, GSTA, GSTP special service requests
- **XSLT Line Reference**: Lines 1274-1743

#### Test Case 13.2: GST Passenger with Email Contact
- **Input XML Structure**:
```xml
<Request>
  <target>AF</target>
  <actor>
    <ID>PAX2</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Marie Dubois</addresseeName>
      <companyName>Air France</companyName>
      <line>123 Charles de Gaulle</line>
      <cityName>Paris</cityName>
      <countryCode>FR</countryCode>
    </address>
    <contact>
      <contactType>GST</contactType>
      <email>marie.dubois@airfrance.fr</email>
    </contact>
  </actor>
</Request>
```
- **Expected Output**: GSTN, GSTA, and GSTE (email) special service requests
- **Business Rule**: GST email contacts generate GSTE SSR instead of GSTP
- **XSLT Line Reference**: Lines 1694-1742

#### Test Case 13.3: UA Target Adult with GST Data (Should Not Process)
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX3</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>John Smith</addresseeName>
      <companyName>United Airlines</companyName>
    </address>
  </actor>
</Request>
```
- **Expected Output**: No GST metadata generated
- **Business Rule**: UA/UAD targets exclude GST passenger processing
- **XSLT Line Reference**: Lines 1238-1241, 1267-1270

#### Test Case 13.4: Non-Adult Passenger with GST Data
- **Input XML Structure**:
```xml
<Request>
  <target>BA</target>
  <actor>
    <ID>PAX4</ID>
    <PTC>CHD</PTC>
    <address>
      <addresseeName>Emma Johnson</addresseeName>
      <companyName>British Airways</companyName>
    </address>
  </actor>
</Request>
```
- **Expected Output**: No GST metadata generated
- **Business Rule**: Only adult (ADT) passengers eligible for GST processing
- **XSLT Line Reference**: Lines 1241, 1270

#### Test Case 13.5: GST Address with Trailing Slash Handling
- **Input XML Structure**:
```xml
<Request>
  <target>KL</target>
  <actor>
    <ID>PAX5</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Jan van der Berg</addresseeName>
      <line>Schiphol Boulevard 123</line>
      <cityName>Amsterdam</cityName>
      <countryCode>NL</countryCode>
    </address>
  </actor>
</Request>
```
- **Expected Output**: Address string with trailing slash removed if present
- **Business Rule**: Complex address concatenation logic handles trailing slashes
- **XSLT Line Reference**: Lines 1368-1476 (complex trailing slash removal logic)

#### Test Case 13.6: GST with Incomplete Address Data
- **Input XML Structure**:
```xml
<Request>
  <target>SAS</target>
  <actor>
    <ID>PAX6</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Erik Larsson</addresseeName>
      <countryCode>SE</countryCode>
    </address>
  </actor>
</Request>
```
- **Expected Output**: GSTN and GSTA with minimal address data (country only)
- **Business Rule**: GST processing works with minimal address components
- **XSLT Line Reference**: Lines 1318-1477

#### Test Case 13.7: Multiple GST Passengers
- **Input XML Structure**:
```xml
<Request>
  <target>LX</target>
  <actor>
    <ID>PAX7</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Hans Weber</addresseeName>
      <companyName>Swiss Air</companyName>
    </address>
  </actor>
  <actor>
    <ID>PAX8</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Anna Weber</addresseeName>
      <companyName>Swiss Air</companyName>
    </address>
  </actor>
</Request>
```
- **Expected Output**: Separate PassengerMetadata elements for each GST passenger
- **Business Rule**: GST processing handles multiple passengers independently
- **XSLT Line Reference**: Lines 1257-1748 (for-each actor processing)

#### Test Case 13.8: GST with Country Name Instead of Code
- **Input XML Structure**:
```xml
<Request>
  <target>OS</target>
  <actor>
    <ID>PAX9</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Wolfgang Mozart</addresseeName>
      <countryName>Austria</countryName>
    </address>
  </actor>
</Request>
```
- **Expected Output**: GSTA SSR with country name in address string
- **Business Rule**: countryName used in address concatenation when present
- **XSLT Line Reference**: Lines 1350-1356, 1403-1409

#### Test Case 13.9: GST Address Concatenation Edge Cases
- **Input XML Structure**:
```xml
<Request>
  <target>IB</target>
  <actor>
    <ID>PAX10</ID>
    <PTC>ADT</PTC>
    <address>
      <addresseeName>Carlos Rodriguez</addresseeName>
      <line>Calle Principal</line>
      <cityName></cityName>
      <countryCode>ES</countryCode>
      <zip></zip>
    </address>
  </actor>
</Request>
```
- **Expected Output**: GSTA with clean address string handling empty elements
- **Business Rule**: Empty address components handled gracefully in concatenation
- **XSLT Line Reference**: Lines 1424-1474 (complex conditional concatenation)

## Test Case Count Summary: 78 test cases identified
- **Helper Template Tests**: 25 test cases
- **Target-Based Processing**: 12 test cases
- **Gender and Name Processing**: 8 test cases
- **Contact Processing Tests**: 15 test cases
- **Address and Metadata Processing**: 18 test cases

## Category 6: Seat Selection and Product Processing Tests (12 test cases)

### Seat Selection Processing Tests (6 test cases)
**Business Logic**: Seat number parsing and row/column extraction
**XSLT Locations**: Lines 227-243
**Key Processing**: Row number extraction, column letter extraction from seat numbers

#### Test Case 14.1: Standard Seat Number Parsing
- **Input XML Structure**:
```xml
<Request>
  <set>
    <product>
      <EST>
        <Data>
          <seatNbr>12A</seatNbr>
        </Data>
      </EST>
    </product>
  </set>
</Request>
```
- **Expected Output**:
```xml
<OfferItem>
  <SeatSelection>
    <Row>12</Row>
    <Column>A</Column>
  </SeatSelection>
</OfferItem>
```
- **Business Rule**: Seat number split into numeric row and alphabetic column
- **XSLT Line Reference**: Lines 232-241
- **Analysis Logic**: `number(substring(., 1, (string-length(string(.)) - 1)))` for row, `substring(., string-length(string(.)), 1)` for column

#### Test Case 14.2: Two-Digit Row with Multiple Columns
- **Input XML Structure**:
```xml
<product>
  <EST>
    <Data>
      <seatNbr>34F</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**:
```xml
<SeatSelection>
  <Row>34</Row>
  <Column>F</Column>
</SeatSelection>
```
- **Business Rule**: Two-digit row numbers processed correctly
- **Edge Case**: Higher row numbers with various column letters

#### Test Case 14.3: Single Digit Row
- **Input XML Structure**:
```xml
<product>
  <EST>
    <Data>
      <seatNbr>5C</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**:
```xml
<SeatSelection>
  <Row>5</Row>
  <Column>C</Column>
</SeatSelection>
```
- **Business Rule**: Single digit rows handled with same parsing logic
- **Edge Case**: Minimum row number scenarios

#### Test Case 14.4: Three-Digit Row Numbers
- **Input XML Structure**:
```xml
<product>
  <EST>
    <Data>
      <seatNbr>123B</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**:
```xml
<SeatSelection>
  <Row>123</Row>
  <Column>B</Column>
</SeatSelection>
```
- **Business Rule**: Three-digit rows for large aircraft handled correctly
- **Edge Case**: Maximum row number scenarios

#### Test Case 14.5: Invalid Seat Number Format
- **Input XML Structure**:
```xml
<product>
  <EST>
    <Data>
      <seatNbr>ABC</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**: Row element with NaN or 0, Column with 'C'
- **Business Rule**: Invalid formats handled gracefully by XSLT number() function
- **Edge Case**: Non-numeric row portion handling

#### Test Case 14.6: Empty Seat Number
- **Input XML Structure**:
```xml
<product>
  <EST>
    <Data>
      <seatNbr></seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**: SeatSelection element with empty or missing Row/Column
- **Business Rule**: Empty seat numbers processed without errors
- **Edge Case**: Missing seat data handling

### Product Processing Tests (6 test cases)
**Business Logic**: Product to OfferItem transformation
**XSLT Locations**: Lines 212-246
**Key Processing**: Product ID mapping, passenger references, EST data handling

#### Test Case 15.1: Complete Product with Passenger References
- **Input XML Structure**:
```xml
<set>
  <ID>SET001</ID>
  <product>
    <ID>PROD123</ID>
    <RefIDs>PAX1 PAX2</RefIDs>
    <EST>
      <Data>
        <seatNbr>15D</seatNbr>
      </Data>
    </EST>
  </product>
</set>
```
- **Expected Output**:
```xml
<Offer OfferID="SET001">
  <OfferItem OfferItemID="PROD123">
    <PassengerRefs>PAX1 PAX2</PassengerRefs>
    <SeatSelection>
      <Row>15</Row>
      <Column>D</Column>
    </SeatSelection>
  </OfferItem>
</Offer>
```
- **Business Rule**: Product elements transformed to OfferItem with complete passenger associations
- **XSLT Line Reference**: Lines 214-244

#### Test Case 15.2: Product without Seat Selection
- **Input XML Structure**:
```xml
<set>
  <product>
    <ID>PROD456</ID>
    <RefIDs>PAX3</RefIDs>
  </product>
</set>
```
- **Expected Output**:
```xml
<OfferItem OfferItemID="PROD456">
  <PassengerRefs>PAX3</PassengerRefs>
</OfferItem>
```
- **Business Rule**: Products without EST data still create valid OfferItems
- **XSLT Line Reference**: Lines 214-226

#### Test Case 15.3: Multiple Products in Single Set
- **Input XML Structure**:
```xml
<set>
  <ID>SET002</ID>
  <product>
    <ID>PROD789</ID>
    <RefIDs>PAX1</RefIDs>
  </product>
  <product>
    <ID>PROD790</ID>
    <RefIDs>PAX2</RefIDs>
    <EST>
      <Data>
        <seatNbr>20A</seatNbr>
      </Data>
    </EST>
  </product>
</set>
```
- **Expected Output**: Two separate OfferItem elements within single Offer
- **Business Rule**: Multiple products per set create multiple OfferItems
- **XSLT Line Reference**: Lines 212-246 (for-each product processing)

#### Test Case 15.4: Product with Missing ID
- **Input XML Structure**:
```xml
<product>
  <RefIDs>PAX4</RefIDs>
  <EST>
    <Data>
      <seatNbr>8B</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**: OfferItem without OfferItemID attribute
- **Business Rule**: Missing product IDs handled gracefully
- **Edge Case**: Missing required data handling

#### Test Case 15.5: Product with Missing Passenger References
- **Input XML Structure**:
```xml
<product>
  <ID>PROD999</ID>
  <EST>
    <Data>
      <seatNbr>25F</seatNbr>
    </Data>
  </EST>
</product>
```
- **Expected Output**: OfferItem without PassengerRefs element
- **Business Rule**: Products without passenger associations still processed
- **Edge Case**: Missing passenger reference handling

#### Test Case 15.6: Product with Complex EST Data
- **Input XML Structure**:
```xml
<product>
  <ID>PRODFULL</ID>
  <RefIDs>PAX5 PAX6</RefIDs>
  <EST>
    <Data>
      <seatNbr>42E</seatNbr>
      <additionalData>extra</additionalData>
    </Data>
  </EST>
</product>
```
- **Expected Output**: OfferItem with SeatSelection ignoring additional EST data
- **Business Rule**: Only seatNbr processed from EST Data, other elements ignored
- **XSLT Line Reference**: Lines 230-242 (specific seatNbr processing)

## Category 7: Document Type and Visa Processing Tests (15 test cases)

### Identity Document Processing Tests (8 test cases)
**Business Logic**: Document type transformation and identity document creation
**XSLT Locations**: Lines 328-477
**Key Processing**: Document type filtering, vmf template integration, visa conditional logic

#### Test Case 16.1: Standard Document with Type Processing
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <type>P</type>
    <PassportNumber>AB1234567</PassportNumber>
    <issuer>US</issuer>
    <nationality>US</nationality>
    <issuanceDate>2020-01-15</issuanceDate>
    <expirationDate>2030-01-15</expirationDate>
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>AB1234567</IdentityDocumentNumber>
  <IdentityDocumentType>PT</IdentityDocumentType>
  <IssuingCountryCode>US</IssuingCountryCode>
  <CitizenshipCountryCode>US</CitizenshipCountryCode>
  <IssueDate>2020-01-15</IssueDate>
  <ExpiryDate>2030-01-15</ExpiryDate>
</IdentityDocument>
```
- **Business Rule**: Document type 'P' transformed to 'PT' via vmf:vmf1_inputtoresult, 'V' prefix removed
- **XSLT Line Reference**: Lines 341-372, 365-369 (substring operation)

#### Test Case 16.2: Document Type Not Matching vmf:vmf1 Patterns
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <type>ID</type>
    <DocumentNumber>ID987654321</DocumentNumber>
    <issuer>CA</issuer>
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>ID987654321</IdentityDocumentNumber>
  <IdentityDocumentType>ID</IdentityDocumentType>
  <IssuingCountryCode>CA</IssuingCountryCode>
</IdentityDocument>
```
- **Business Rule**: Unrecognized document types passed through unchanged
- **XSLT Line Reference**: Lines 374-381 (otherwise branch)

#### Test Case 16.3: Document with Tax Identifier (Should Be Filtered Out)
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <taxIdentifier>
      <fiscalType>SSN</fiscalType>
      <fiscalNumber>123456789</fiscalNumber>
    </taxIdentifier>
    <type>P</type>
    <PassportNumber>XX9999999</PassportNumber>
  </docRef>
</actor>
```
- **Expected Behavior**: No IdentityDocument generated for this docRef
- **Business Rule**: Documents with taxIdentifier excluded from identity document processing
- **XSLT Line Reference**: Line 328 filter condition `(not(taxIdentifier) and boolean(type))`

#### Test Case 16.4: Document without Type Element
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <DocumentNumber>NOTYPE123</DocumentNumber>
    <issuer>GB</issuer>
  </docRef>
</actor>
```
- **Expected Behavior**: No IdentityDocument generated
- **Business Rule**: Documents without type element excluded from processing
- **XSLT Line Reference**: Line 328 filter condition requires `boolean(type)`

#### Test Case 16.5: Document with Birth Date from docRef
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <type>PT</type>
    <PassportNumber>BC7777777</PassportNumber>
    <dateOfBirth>1985-06-15</dateOfBirth>
    <issuer>AU</issuer>
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>BC7777777</IdentityDocumentNumber>
  <IdentityDocumentType>PT</IdentityDocumentType>
  <IssuingCountryCode>AU</IssuingCountryCode>
  <Birthdate>1985-06-15</Birthdate>
</IdentityDocument>
```
- **Business Rule**: Birth date from docRef element included in identity document
- **XSLT Line Reference**: Lines 407-412

#### Test Case 16.6: Document with Gender from Actor Name/Type
- **Input XML Structure**:
```xml
<actor>
  <Name>
    <Type>Female</Type>
    <FirstName>Sarah</FirstName>
    <LastName>Johnson</LastName>
  </Name>
  <docRef>
    <type>P</type>
    <PassportNumber>FE5555555</PassportNumber>
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>FE5555555</IdentityDocumentNumber>
  <IdentityDocumentType>PT</IdentityDocumentType>
  <Gender>Female</Gender>
</IdentityDocument>
```
- **Business Rule**: Gender from actor Name/Type included in identity document
- **XSLT Line Reference**: Lines 413-418

#### Test Case 16.7: Multiple Documents per Actor
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <type>P</type>
    <PassportNumber>FIRST123</PassportNumber>
    <issuer>US</issuer>
  </docRef>
  <docRef>
    <type>ID</type>
    <IDNumber>SECOND456</IDNumber>
    <issuer>US</issuer>
  </docRef>
</actor>
```
- **Expected Output**: Two separate IdentityDocument elements
- **Business Rule**: Multiple docRef elements processed independently
- **XSLT Line Reference**: Lines 328-477 (for-each docRef processing)

#### Test Case 16.8: Document Number from Text Content
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <type>P</type>
    <issuer>DE</issuer>
    TEXTDOC999888
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>TEXTDOC999888</IdentityDocumentNumber>
  <IdentityDocumentType>PT</IdentityDocumentType>
  <IssuingCountryCode>DE</IssuingCountryCode>
</IdentityDocument>
```
- **Business Rule**: Document number extracted from text content when no specific element
- **XSLT Line Reference**: Lines 331-336 `(./node())[./self::text()]`

### Visa Processing Tests (7 test cases)
**Business Logic**: Visa processing with target-specific conditional logic
**XSLT Locations**: Lines 419-731
**Key Processing**: Target validation, visa type filtering, document type transformation

#### Test Case 17.1: UA Target Visa Exclusion - Type R
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <docRef>
      <visa>
        <visaType>R</visaType>
        <visaNumber>UAR123456</visaNumber>
        <visaHostCountryCode>US</visaHostCountryCode>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Behavior**: No visa processing due to UA target + R type exclusion
- **Business Rule**: UA targets exclude R visa types from processing
- **XSLT Line Reference**: Lines 425-426, 485-486 `number(('UA' = $var4_cur/target))` + visa type conditions

#### Test Case 17.2: UA Target with K Visa Type (Allowed)
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <docRef>
      <visa>
        <visaType>K</visaType>
        <visaNumber>UAK789123</visaNumber>
        <visaIssueCountryCode>MX</visaIssueCountryCode>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>UAK789123</IdentityDocumentNumber>
  <IdentityDocumentType>CR</IdentityDocumentType>
  <IssuingCountryCode>MX</IssuingCountryCode>
  <Visa>
    <VisaNumber>UAK789123</VisaNumber>
    <VisaType>CR</VisaType>
  </Visa>
</IdentityDocument>
```
- **Business Rule**: UA target with K visa type creates CR identity document
- **XSLT Line Reference**: Lines 677-730

#### Test Case 17.3: Standard Target with R Visa Type (Allowed)
- **Input XML Structure**:
```xml
<Request>
  <target>LH</target>
  <actor>
    <docRef>
      <visa>
        <visaType>R</visaType>
        <visaNumber>LHR456789</visaNumber>
        <visaHostCountryCode>DE</visaHostCountryCode>
        <enterBeforeDate>2024-12-31</enterBeforeDate>
        <durationOfStay>90</durationOfStay>
        <numberOfEntries>2</numberOfEntries>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>LHR456789</IdentityDocumentNumber>
  <IdentityDocumentType>AEA</IdentityDocumentType>
  <Visa>
    <VisaNumber>LHR456789</VisaNumber>
    <VisaType>AEA</VisaType>
    <VisaHostCountryCode>DE</VisaHostCountryCode>
    <EnterBeforeDate>2024-12-31</EnterBeforeDate>
    <DurationOfStay>90</DurationOfStay>
    <NumberOfEntries>2</NumberOfEntries>
  </Visa>
</IdentityDocument>
```
- **Business Rule**: Non-UA targets allow R visa processing with AEA document type
- **XSLT Line Reference**: Lines 610-676

#### Test Case 17.4: Visa Type V Processing
- **Input XML Structure**:
```xml
<Request>
  <target>AF</target>
  <actor>
    <docRef>
      <visa>
        <visaType>V</visaType>
        <visaNumber>AFV111222</visaNumber>
        <visaIssueCountryCode>FR</visaIssueCountryCode>
        <visaIssuanceDate>2024-01-01</visaIssuanceDate>
        <enterBeforeDate>2024-12-31</enterBeforeDate>
      </visa>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: VVI identity document type via vmf:vmf2_inputtoresult transformation
- **Business Rule**: V visa types processed through vmf:vmf2 template for type transformation
- **XSLT Line Reference**: Lines 525-537 `vmf:vmf2_inputtoresult` integration

#### Test Case 17.5: Visa with Document Number Precedence
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <visa>
      <visaType>K</visaType>
      <visaNumber>VISANUM123</visaNumber>
    </visa>
    DOCTEXT456
  </docRef>
</actor>
```
- **Expected Output**: IdentityDocument with visaNumber taking precedence over text content
- **Business Rule**: visaNumber used when available, otherwise text content
- **XSLT Line Reference**: Lines 492-522 conditional document number selection

#### Test Case 17.6: Visa without Host Country
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <visa>
      <visaType>V</visaType>
      <visaNumber>NOHOST789</visaNumber>
      <visaIssuanceDate>2024-06-01</visaIssuanceDate>
    </visa>
  </docRef>
</actor>
```
- **Expected Output**: Visa element without VisaHostCountryCode
- **Business Rule**: Missing visa host country handled gracefully
- **Edge Case**: Optional visa field handling

#### Test Case 17.7: Visa Birthplace Processing
- **Input XML Structure**:
```xml
<actor>
  <docRef>
    <birthPlace>Berlin, Germany</birthPlace>
    <visa>
      <visaType>V</visaType>
      <visaNumber>BIRTH123</visaNumber>
    </visa>
  </docRef>
</actor>
```
- **Expected Output**:
```xml
<IdentityDocument>
  <IdentityDocumentNumber>BIRTH123</IdentityDocumentNumber>
  <IdentityDocumentType>VI</IdentityDocumentType>
  <Birthplace>Berlin, Germany</Birthplace>
  <Visa>
    <!-- visa details -->
  </Visa>
</IdentityDocument>
```
- **Business Rule**: Birth place from docRef included in visa processing
- **XSLT Line Reference**: Lines 557-562

## Test Case Count Summary: 105 test cases identified
- **Helper Template Tests**: 25 test cases
- **Target-Based Processing**: 12 test cases  
- **Gender and Name Processing**: 8 test cases
- **Contact Processing Tests**: 15 test cases
- **Address and Metadata Processing**: 18 test cases
- **Seat Selection and Product Processing**: 12 test cases  
- **Document Type and Visa Processing**: 15 test cases

## Category 8: Loyalty Program Processing Tests (8 test cases)

### Loyalty Program Data Processing Tests (8 test cases)
**Business Logic**: Loyalty program account transformation to airline frequent flyer programs
**XSLT Locations**: Lines 309-327
**Key Processing**: Company code mapping, account number extraction, airline designator transformation

#### Test Case 18.1: Complete Loyalty Program Processing
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>UA</companyCode>
    <identifier>1234567890</identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator>UA</AirlineDesignator>
  </Airline>
  <AccountNumber>1234567890</AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: Loyalty program data transformed to IATA airline designator structure
- **XSLT Line Reference**: Lines 312-325
- **Analysis Logic**: Direct mapping of companyCode to AirlineDesignator, identifier to AccountNumber

#### Test Case 18.2: Multiple Loyalty Programs per Passenger
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>AA</companyCode>
    <identifier>AA123456789</identifier>
  </loyalty>
  <loyalty>
    <companyCode>DL</companyCode>
    <identifier>DL987654321</identifier>
  </loyalty>
</actor>
```
- **Expected Output**: Two separate LoyaltyProgramAccount elements
- **Business Rule**: Multiple loyalty programs processed independently per passenger
- **XSLT Line Reference**: Lines 309-327 (for-each loyalty processing)

#### Test Case 18.3: Loyalty Program with Missing Company Code
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <identifier>NOCODE123</identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <AccountNumber>NOCODE123</AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: Missing company code results in LoyaltyProgramAccount without Airline element
- **Edge Case**: Missing required data handling

#### Test Case 18.4: Loyalty Program with Missing Account Number
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>LH</companyCode>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator>LH</AirlineDesignator>
  </Airline>
</LoyaltyProgramAccount>
```
- **Business Rule**: Missing identifier results in LoyaltyProgramAccount without AccountNumber element
- **Edge Case**: Missing account data handling

#### Test Case 18.5: Three-Character Airline Code
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>SWA</companyCode>
    <identifier>SWA555666777</identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator>SWA</AirlineDesignator>
  </Airline>
  <AccountNumber>SWA555666777</AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: Three-character airline codes supported alongside two-character codes
- **XSLT Line Reference**: Lines 314-318

#### Test Case 18.6: International Airline Loyalty Program
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>SQ</companyCode>
    <identifier>SQ8888999000</identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator>SQ</AirlineDesignator>
  </Airline>
  <AccountNumber>SQ8888999000</AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: International airline codes processed same as domestic
- **Business Context**: Singapore Airlines loyalty program processing

#### Test Case 18.7: Empty Loyalty Program Elements
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode></companyCode>
    <identifier></identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator></AirlineDesignator>
  </Airline>
  <AccountNumber></AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: Empty elements result in empty but present output elements
- **Edge Case**: Empty data value handling

#### Test Case 18.8: Loyalty Program with Special Characters
- **Input XML Structure**:
```xml
<actor>
  <loyalty>
    <companyCode>B6</companyCode>
    <identifier>B6-ALPHA-123-BETA</identifier>
  </loyalty>
</actor>
```
- **Expected Output**:
```xml
<LoyaltyProgramAccount>
  <Airline>
    <AirlineDesignator>B6</AirlineDesignator>
  </Airline>
  <AccountNumber>B6-ALPHA-123-BETA</AccountNumber>
</LoyaltyProgramAccount>
```
- **Business Rule**: Account numbers with special characters preserved unchanged
- **Edge Case**: Special character handling in account identifiers

## Category 9: Tax Identifier and FOID Processing Tests (10 test cases)

### Tax Identifier Processing Tests (10 test cases)
**Business Logic**: Tax identifier transformation to FOID special service requests for UA/UAD targets
**XSLT Locations**: Lines 1749-1862
**Key Processing**: Target validation, passenger type filtering, FOID SSR generation with airline codes

#### Test Case 19.1: UA Target Tax Identifier with Airline Code
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX1</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>123456789</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <set>
    <property>
      <key>OwnerCode</key>
      <value>UA567890</value>
    </property>
  </set>
</Request>
```
- **Expected Output**:
```xml
<PassengerMetadata MetadataKey="SSRPAX1">
  <AugmentationPoint>
    <AugPoint>
      <SpecialServiceRequest>
        <TravelerIDRef>PAX1</TravelerIDRef>
        <AirlineCode>UA</AirlineCode>
        <SSRCode>FOID</SSRCode>
        <Text>IDTIDSSN123456789</Text>
        <NumberInParty>1</NumberInParty>
        <ActionCode>NN</ActionCode>
      </SpecialServiceRequest>
    </AugPoint>
  </AugmentationPoint>
</PassengerMetadata>
```
- **Business Rule**: UA target with tax ID generates FOID SSR with airline code extraction
- **XSLT Line Reference**: Lines 1820-1860
- **Analysis Logic**: Extract first 2 characters from OwnerCode value for airline code (substring(., 1, 2))

#### Test Case 19.2: UAD Target Tax Identifier Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UAD</target>
  <actor>
    <ID>PAX2</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>TIN</fiscalType>
        <fiscalNumber>987654321</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <set>
    <property>
      <key>OwnerCode</key>
      <value>UA123ABC</value>
    </property>
  </set>
</Request>
```
- **Expected Output**:
```xml
<PassengerMetadata MetadataKey="SSR2">
  <AugmentationPoint>
    <AugPoint>
      <SpecialServiceRequest>
        <TravelerIDRef>PAX2</TravelerIDRef>
        <AirlineCode>UA</AirlineCode>
        <SSRCode>FOID</SSRCode>
        <Text>IDTIDTIN987654321</Text>
        <NumberInParty>1</NumberInParty>
        <ActionCode>NN</ActionCode>
      </SpecialServiceRequest>
    </AugPoint>
  </AugmentationPoint>
</PassengerMetadata>
```
- **Business Rule**: UAD target processes tax IDs same as UA target
- **XSLT Line Reference**: Lines 1810-1811 (UAD target check)

#### Test Case 19.3: Non-UA Target with Tax Identifier (Should Not Process)
- **Input XML Structure**:
```xml
<Request>
  <target>LH</target>
  <actor>
    <ID>PAX3</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>TAXID</fiscalType>
        <fiscalNumber>EURO123456</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Behavior**: No FOID SSR generated due to non-UA/UAD target
- **Business Rule**: Only UA/UAD targets generate tax identifier metadata
- **XSLT Line Reference**: Lines 1759, 1819 (target validation logic)

#### Test Case 19.4: Non-Adult Passenger with Tax Identifier
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX4</ID>
    <PTC>CHD</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>CHILD123</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Behavior**: No FOID SSR generated for non-adult passenger
- **Business Rule**: Tax ID processing only for adult (not INF) passengers
- **XSLT Line Reference**: Lines 1770-1778 (PTC validation logic)

#### Test Case 19.5: Multiple Tax Identifiers per Passenger
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX5</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>PRIMARY123</fiscalNumber>
      </taxIdentifier>
    </docRef>
    <docRef>
      <taxIdentifier>
        <fiscalType>EIN</fiscalType>
        <fiscalNumber>BUSINESS456</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <set>
    <property>
      <key>OwnerCode</key>
      <value>UA999</value>
    </property>
  </set>
</Request>
```
- **Expected Output**: Two separate FOID SSRs for each tax identifier
- **Business Rule**: Multiple tax IDs processed independently
- **XSLT Line Reference**: Lines 1814-1817 (for-each docRef processing)

#### Test Case 19.6: Tax Identifier with Missing Fiscal Type
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX6</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalNumber>NOTYPE789</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: FOID SSR with incomplete IDTID string
- **Business Rule**: Missing fiscal type handled gracefully in text generation
- **XSLT Line Reference**: Lines 1845-1849 (text concatenation)

#### Test Case 19.7: Tax Identifier with Missing Fiscal Number
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX7</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: FOID SSR with incomplete IDTID string
- **Business Rule**: Missing fiscal number handled gracefully
- **Edge Case**: Incomplete tax identifier data

#### Test Case 19.8: Tax Identifier with Non-Standard Fiscal Types
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX8</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>CUSTOM_TYPE</fiscalType>
        <fiscalNumber>CUSTOM123456</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <set>
    <property>
      <key>OwnerCode</key>
      <value>UA444</value>
    </property>
  </set>
</Request>
```
- **Expected Output**:
```xml
<SpecialServiceRequest>
  <TravelerIDRef>PAX8</TravelerIDRef>
  <AirlineCode>UA</AirlineCode>
  <SSRCode>FOID</SSRCode>
  <Text>IDTIDCUSTOM_TYPECUSTOM123456</Text>
  <NumberInParty>1</NumberInParty>
  <ActionCode>NN</ActionCode>
</SpecialServiceRequest>
```
- **Business Rule**: Non-standard fiscal types preserved in FOID text
- **Edge Case**: Custom fiscal type handling

#### Test Case 19.9: Tax Identifier Passenger ID Translation
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PASSENGER_ABC123</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>999888777</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: MetadataKey with numeric-only portion "123" from passenger ID
- **Business Rule**: Passenger ID translated removing alphabetic characters for metadata key
- **XSLT Line Reference**: Lines 1783-1785 `translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '')` 

#### Test Case 19.10: Tax Identifier Global Metadata Processing
- **Input XML Structure**:
```xml
<Request>
  <target>UA</target>
  <actor>
    <ID>PAX9</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>ITIN</fiscalType>
        <fiscalNumber>GLOBAL456789</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
  <actor>
    <ID>PAX10</ID>
    <PTC>ADT</PTC>
    <docRef>
      <taxIdentifier>
        <fiscalType>SSN</fiscalType>
        <fiscalNumber>GLOBAL987654</fiscalNumber>
      </taxIdentifier>
    </docRef>
  </actor>
</Request>
```
- **Expected Output**: Global M5 metadata plus individual passenger FOID SSRs
- **Business Rule**: Tax ID presence triggers both global and individual metadata
- **XSLT Line Reference**: Lines 1759-1806 (global metadata), 1807-1862 (individual metadata)

## Category 10: Travel Agency and Point of Sale Processing Tests (9 test cases)

### Travel Agency Processing Tests (5 test cases)
**Business Logic**: Travel agency data transformation to TravelAgencySender structure
**XSLT Locations**: Lines 96-180
**Key Processing**: Agency name mapping, contact transformation, IATA number processing, agent user creation

#### Test Case 20.1: Complete Travel Agency Processing
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Name>Global Travel Solutions</Name>
    <IATA_Number>12345678</IATA_Number>
    <Contact>
      <Address>
        <line>100 Travel Plaza</line>
        <CityName>Miami</CityName>
        <Zip>33101</Zip>
        <CountryCode>US</CountryCode>
      </Address>
      <Email>
        <EmailAddress>bookings@globaltravel.com</EmailAddress>
      </Email>
      <Phone>
        <PhoneNumber>1-800-555-TRIP</PhoneNumber>
      </Phone>
    </Contact>
  </TravelAgency>
</Request>
```
- **Expected Output**:
```xml
<TravelAgencySender>
  <Name>Global Travel Solutions</Name>
  <Contacts>
    <Contact>
      <AddressContact>
        <Street>100 Travel Plaza</Street>
        <CityName>Miami</CityName>
        <PostalCode>33101</PostalCode>
        <CountryCode>US</CountryCode>
      </AddressContact>
      <EmailContact>
        <Address>bookings@globaltravel.com</Address>
      </EmailContact>
      <PhoneContact>
        <Number>1800555TRIP</Number>
      </PhoneContact>
    </Contact>
  </Contacts>
  <PseudoCity>AH9D</PseudoCity>
  <IATA_Number>12345678</IATA_Number>
  <AgencyID>12345678</AgencyID>
  <AgentUser>
    <AgentUserID>xmluser001</AgentUserID>
  </AgentUser>
</TravelAgencySender>
```
- **Business Rule**: Complete travel agency transformation with hardcoded PseudoCity and AgentUserID
- **XSLT Line Reference**: Lines 98-178
- **Analysis Logic**: Phone number sanitization applied (line 151), hardcoded values for PseudoCity/AgentUserID

#### Test Case 20.2: Travel Agency with Missing IATA Number
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Name>Local Travel Agency</Name>
    <Contact>
      <Email>
        <EmailAddress>info@localtravel.com</EmailAddress>
      </Email>
    </Contact>
  </TravelAgency>
</Request>
```
- **Expected Output**: TravelAgencySender without IATA_Number and AgencyID elements
- **Business Rule**: Missing IATA number handled gracefully
- **XSLT Line Reference**: Lines 162-173 (conditional IATA processing)

#### Test Case 20.3: Travel Agency with Multiple Contact Methods
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Name>Multi Contact Agency</Name>
    <Contact>
      <Phone>
        <PhoneNumber>555-123-4567</PhoneNumber>
      </Phone>
      <Phone>
        <PhoneNumber>555-987-6543</PhoneNumber>
      </Phone>
      <Email>
        <EmailAddress>primary@agency.com</EmailAddress>
      </Email>
      <Email>
        <EmailAddress>backup@agency.com</EmailAddress>
      </Email>
    </Contact>
  </TravelAgency>
</Request>
```
- **Expected Output**: Multiple PhoneContact and EmailContact elements within single Contact
- **Business Rule**: Multiple contact methods processed independently
- **XSLT Line Reference**: Lines 108-155 (for-each phone/email processing)

#### Test Case 20.4: Travel Agency with Address Only
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Name>Address Only Agency</Name>
    <Contact>
      <Address>
        <line>789 Business Ave</line>
        <CityName>Denver</CityName>
        <CountryCode>US</CountryCode>
      </Address>
    </Contact>
  </TravelAgency>
</Request>
```
- **Expected Output**: Contact with only AddressContact element
- **Business Rule**: Partial contact information processed correctly
- **XSLT Line Reference**: Lines 105-133

#### Test Case 20.5: Travel Agency without Contact Information
- **Input XML Structure**:
```xml
<Request>
  <TravelAgency>
    <Name>Minimal Agency</Name>
    <IATA_Number>99887766</IATA_Number>
  </TravelAgency>
</Request>
```
- **Expected Output**: TravelAgencySender with only Name, PseudoCity, IATA_Number, AgencyID, AgentUser
- **Business Rule**: Missing contact information results in minimal TravelAgencySender
- **Edge Case**: Missing contact data handling

### Point of Sale Processing Tests (4 test cases)
**Business Logic**: Hardcoded point of sale data creation
**XSLT Locations**: Lines 82-91
**Key Processing**: Hardcoded country/city codes for French market

#### Test Case 21.1: Standard Point of Sale Processing
- **Input XML Structure**:
```xml
<Request>
  <!-- Any valid request structure -->
</Request>
```
- **Expected Output**:
```xml
<PointOfSale>
  <Location>
    <CountryCode>FR</CountryCode>
    <CityCode>NCE</CityCode>
  </Location>
</PointOfSale>
```
- **Business Rule**: All requests generate hardcoded French point of sale (Nice, France)
- **XSLT Line Reference**: Lines 84-89
- **Analysis Logic**: Hardcoded values 'FR' for country, 'NCE' for city regardless of input

#### Test Case 21.2: Point of Sale with Multiple Requests
- **Input XML Structure**:
```xml
<Requests>
  <Request>
    <target>UA</target>
  </Request>
  <Request>
    <target>LH</target>
  </Request>
</Requests>
```
- **Expected Output**: Single PointOfSale element (not duplicated per request)
- **Business Rule**: PointOfSale generated once per transformation
- **XSLT Line Reference**: Lines 82-91 (outside Request for-each loop)

#### Test Case 21.3: Point of Sale with Empty Request
- **Input XML Structure**:
```xml
<Request>
</Request>
```
- **Expected Output**: Standard PointOfSale with FR/NCE regardless of empty request
- **Business Rule**: PointOfSale generation independent of request content
- **Edge Case**: Empty request handling

#### Test Case 21.4: Point of Sale Value Consistency
- **Input XML Structure**:
```xml
<Request>
  <target>DIFFERENT_TARGET</target>
  <CustomData>Various input data</CustomData>
</Request>
```
- **Expected Output**: Always FR/NCE regardless of input variation
- **Business Rule**: PointOfSale values are constant across all scenarios
- **Business Context**: Indicates system configured for French market operations

## Test Case Count Summary: 132 test cases identified
- **Helper Template Tests**: 25 test cases
- **Target-Based Processing**: 12 test cases  
- **Gender and Name Processing**: 8 test cases
- **Contact Processing Tests**: 15 test cases
- **Address and Metadata Processing**: 18 test cases
- **Seat Selection and Product Processing**: 12 test cases  
- **Document Type and Visa Processing**: 15 test cases
- **Loyalty Program Processing**: 8 test cases
- **Tax Identifier and FOID Processing**: 10 test cases
- **Travel Agency and Point of Sale**: 9 test cases

## Remaining Categories (Final comprehensive coverage):
- **Redress Case Processing Tests**
- **Edge Cases and Error Handling Tests**
- **Multi-passenger Complex Scenario Tests**
- **Integration and End-to-End Tests**