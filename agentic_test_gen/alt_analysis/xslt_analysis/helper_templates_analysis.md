# Helper Templates Analysis

## vmf:vmf1_inputtoresult (Lines 12-25)
**Purpose**: Document type code transformation
**Business Logic**: Maps document type codes to standardized visa/passport types
**Input Parameter**: $input (string)
**Transformation Rules**:
- 'P' → 'VPT' (Passport → Visa Passport Type)
- 'PT' → 'VPT' (Passport Type → Visa Passport Type)  
- Any other value → '' (empty string)

**Test Cases Identified**:
1. Valid passport code 'P'
2. Valid passport type 'PT'
3. Invalid/unrecognized code
4. Empty input
5. Null input
6. Special characters
7. Numeric input

## vmf:vmf2_inputtoresult (Lines 26-42)
**Purpose**: Visa/document type code transformation
**Business Logic**: Maps various visa/document codes to standardized NDC types
**Input Parameter**: $input (string)
**Transformation Rules**:
- 'V' → 'VVI' (Visa → Visa Visitor)
- 'R' → 'VAEA' (Residence → Visa Area Entry Authorization)
- 'K' → 'VCR' (Card → Visa Card Residence)
- Any other value → '' (empty string)

**Test Cases Identified**:
1. Valid visa code 'V'
2. Valid residence code 'R'
3. Valid card code 'K'
4. Invalid/unrecognized code
5. Case sensitivity test ('v', 'r', 'k')
6. Mixed case input
7. Empty/null input

## vmf:vmf3_inputtoresult (Lines 43-53)
**Purpose**: Contact method transformation for email
**Business Logic**: Maps contact labels to operational contact types
**Input Parameter**: $input (string)
**Transformation Rules**:
- 'email' → 'Voperational' (Email contact → Operational contact)
- Any other value → '' (empty string)

**Test Cases Identified**:
1. Valid email label 'email'
2. Case sensitivity test ('Email', 'EMAIL')
3. Invalid contact type
4. Empty/null input
5. Numeric input
6. Special characters

## vmf:vmf4_inputtoresult (Lines 54-64)
**Purpose**: Contact method transformation for mobile
**Business Logic**: Maps contact labels to operational contact types
**Input Parameter**: $input (string)
**Transformation Rules**:
- 'mobile' → 'Voperational' (Mobile contact → Operational contact)
- Any other value → '' (empty string)

**Test Cases Identified**:
1. Valid mobile label 'mobile'
2. Case sensitivity test ('Mobile', 'MOBILE')
3. Invalid contact type
4. Empty/null input
5. Alternative mobile terms ('cell', 'phone')

## Business Context Understanding
These helper templates appear to be lookup functions for:
1. **Document Type Standardization**: Converting various passport/ID codes to NDC standard codes
2. **Visa Processing**: Mapping visa types to appropriate NDC visa categories
3. **Contact Classification**: Standardizing contact method labels for operational processing

## Usage Patterns in Main Template
- vmf:vmf1_inputtoresult: Used in identity document processing (lines 341, 358, 365)
- vmf:vmf2_inputtoresult: Used in visa processing for non-UA/UAD targets (lines 525, 532)
- vmf:vmf3_inputtoresult: Used in email contact processing (lines 846, 863, 870, 1047, 1064, 1071)
- vmf:vmf4_inputtoresult: Used in phone contact processing (lines 905, 922, 929, 1106, 1123, 1130)