"""
Manual Analysis Baseline Extraction for PoC Validation

This module extracts 15 representative test cases from the comprehensive manual analysis
that generated 132+ test cases. These baseline cases will be used to validate that our
AI agents can match the quality of manual analysis.

The baseline cases are selected to cover:
- Helper template analysis (business logic understanding)
- Main template integration (cross-chunk dependencies)
- Complex business scenarios (real-world applicability)
- Edge cases and error handling
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class BaselineTestCase:
    """Structure for manual analysis baseline test case"""
    id: str
    business_rule: str
    business_context: str
    business_scenario: str
    xslt_chunk: str
    input_conditions: Dict[str, Any]
    expected_behavior: str
    business_value: str
    failure_impact: str
    cross_chunk_dependencies: List[str]
    domain_context: str
    test_scenarios: List[Dict[str, str]]
    xslt_line_reference: str
    category: str


class ManualAnalysisBaseline:
    """Extracted baseline test cases from comprehensive manual analysis"""
    
    def __init__(self):
        self.baseline_cases = self._create_baseline_cases()
    
    def _create_baseline_cases(self) -> List[BaselineTestCase]:
        """Create 15 representative baseline test cases"""
        
        return [
            # Helper Template Cases (5 cases)
            BaselineTestCase(
                id="vmf1_passport_transformation",
                business_rule="Document type 'P'/'PT' transforms to 'VPT' for passport validation",
                business_context="IATA NDC requires standardized document type codes for airline interoperability and regulatory compliance",
                business_scenario="Passenger with passport document needs NDC-compliant processing for international travel booking",
                xslt_chunk="""<xsl:template name="vmf:vmf1_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'P'">VPT</xsl:when>
        <xsl:when test="$input = 'PT'">VPT</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>""",
                input_conditions={"document_type": "P", "target": "UA"},
                expected_behavior="Transform 'P' to 'VPT' for visa passport type standardization",
                business_value="Ensures passport documents meet IATA NDC standards for airline system interoperability",
                failure_impact="Invalid passport processing leads to booking rejection, compliance failure, and customer dissatisfaction",
                cross_chunk_dependencies=["main_passenger_section", "document_validation", "target_processing"],
                domain_context="IATA NDC document type standardization for airline industry compliance",
                test_scenarios=[
                    {"input": "P", "output": "VPT", "scenario": "Standard passport"},
                    {"input": "PT", "output": "VPT", "scenario": "Passport type variant"},
                    {"input": "INVALID", "output": "", "scenario": "Unknown document type"}
                ],
                xslt_line_reference="Lines 15-16",
                category="helper_template"
            ),
            
            BaselineTestCase(
                id="vmf2_visa_transformation",
                business_rule="Document type 'V' transforms to 'VVI' for visa validation, 'R' to 'VAEA', 'K' to 'VCR'",
                business_context="Different visa types require specific NDC encoding for border control systems and airline compliance",
                business_scenario="International passenger with various visa documentation types requiring proper NDC encoding",
                xslt_chunk="""<xsl:template name="vmf:vmf2_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'V'">VVI</xsl:when>
        <xsl:when test="$input = 'R'">VAEA</xsl:when>
        <xsl:when test="$input = 'K'">VCR</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>""",
                input_conditions={"visa_type": "V", "target": "UAD"},
                expected_behavior="Transform visa types to NDC-compliant codes for border control processing",
                business_value="Enables proper visa validation and border control integration for international travel",
                failure_impact="Incorrect visa processing can result in travel denial, legal complications, and system failures",
                cross_chunk_dependencies=["visa_processing_section", "border_control_validation", "target_specific_rules"],
                domain_context="IATA NDC visa type standardization for international travel compliance",
                test_scenarios=[
                    {"input": "V", "output": "VVI", "scenario": "Visitor visa"},
                    {"input": "R", "output": "VAEA", "scenario": "Residence visa"},
                    {"input": "K", "output": "VCR", "scenario": "Card residence visa"}
                ],
                xslt_line_reference="Lines 29-36",
                category="helper_template"
            ),
            
            BaselineTestCase(
                id="helper_template_integration",
                business_rule="Helper template results integrate into main passenger processing with cross-validation",
                business_context="Document type transformations from helpers must flow correctly into downstream validation and processing logic",
                business_scenario="Complete passenger booking workflow where document types from helpers affect validation rules",
                xslt_chunk="""<!-- Helper template call in main template -->
<xsl:variable name="var196_resultof_vmf1" select="vmf:vmf1_inputtoresult($var195_result)" />
<xsl:if test="$var196_resultof_vmf1 != ''">
    <IdentityDocument>
        <IdentityDocumentType><xsl:value-of select="$var196_resultof_vmf1"/></IdentityDocumentType>
    </IdentityDocument>
</xsl:if>""",
                input_conditions={"document_flow": "helper_to_main", "passenger_type": "ADT"},
                expected_behavior="Helper template output properly integrated into main processing flow",
                business_value="Ensures consistent document processing across the entire transformation workflow",
                failure_impact="Broken integration leads to incomplete document processing and system errors",
                cross_chunk_dependencies=["vmf1_template", "main_passenger_section", "document_output_generation"],
                domain_context="IATA NDC end-to-end document processing workflow integration",
                test_scenarios=[
                    {"flow": "vmf1->main", "result": "integrated_processing", "scenario": "Document type flow"},
                    {"flow": "vmf2->main", "result": "visa_integration", "scenario": "Visa type flow"}
                ],
                xslt_line_reference="Lines 300-310",
                category="integration"
            ),
            
            BaselineTestCase(
                id="vmf3_identity_transformation",
                business_rule="Document type 'I' transforms to 'VII' for identity verification processing",
                business_context="National ID documents require specific NDC standardization for domestic travel validation",
                business_scenario="Domestic passenger using national ID for identity verification in booking system",
                xslt_chunk="""<xsl:template name="vmf:vmf3_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:when test="$input = 'I'">VII</xsl:when>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>""",
                input_conditions={"document_type": "I", "travel_type": "domestic"},
                expected_behavior="Transform 'I' to 'VII' for identity document processing",
                business_value="Enables proper identity verification for domestic travel bookings",
                failure_impact="Failed identity processing can block domestic travel bookings",
                cross_chunk_dependencies=["identity_validation", "domestic_travel_rules"],
                domain_context="IATA NDC identity document standardization for domestic travel",
                test_scenarios=[
                    {"input": "I", "output": "VII", "scenario": "National ID card"},
                    {"input": "OTHER", "output": "", "scenario": "Unknown identity document"}
                ],
                xslt_line_reference="Lines 44-50",
                category="helper_template"
            ),
            
            BaselineTestCase(
                id="vmf4_unknown_document_handling",
                business_rule="Unknown document types return empty string as safe default behavior",
                business_context="Graceful handling of non-standard or legacy document types to prevent system failures",
                business_scenario="Legacy system integration where unusual document types might be encountered",
                xslt_chunk="""<xsl:template name="vmf:vmf4_inputtoresult">
    <xsl:param name="input" />
    <xsl:choose>
        <xsl:otherwise></xsl:otherwise>
    </xsl:choose>
</xsl:template>""",
                input_conditions={"document_type": "UNKNOWN", "system": "legacy"},
                expected_behavior="Return empty string for unrecognized document types",
                business_value="Prevents system crashes when encountering unexpected document types",
                failure_impact="System errors or crashes when processing unknown document types",
                cross_chunk_dependencies=["error_handling", "fallback_processing"],
                domain_context="IATA NDC error handling and graceful degradation for system reliability",
                test_scenarios=[
                    {"input": "UNKNOWN", "output": "", "scenario": "Unrecognized document"},
                    {"input": "", "output": "", "scenario": "Empty input handling"}
                ],
                xslt_line_reference="Lines 52-58",
                category="helper_template"
            ),
            
            # Main Template Integration Cases (5 cases)
            BaselineTestCase(
                id="ua_target_specific_processing",
                business_rule="target='UA' triggers enhanced validation and processing for United Airlines specific requirements",
                business_context="United Airlines has specific compliance requirements and business rules that differ from standard processing",
                business_scenario="United Airlines booking requiring enhanced contact validation and document processing",
                xslt_chunk="""<xsl:if test="$var4_cur/target = 'UA'">
    <xsl:variable name="var196_resultof_vmf1" select="vmf:vmf1_inputtoresult($var195_result)" />
    <xsl:if test="$var196_resultof_vmf1 != ''">
        <!-- Enhanced UA processing -->
    </xsl:if>
</xsl:if>""",
                input_conditions={"target": "UA", "passenger_count": "multiple", "contact_required": True},
                expected_behavior="Enhanced validation triggered for UA target with additional business rules",
                business_value="Ensures United Airlines specific compliance requirements are met",
                failure_impact="Booking rejection due to non-compliance with UA specific business rules",
                cross_chunk_dependencies=["target_detection", "validation_rules", "contact_processing", "helper_templates"],
                domain_context="Airline-specific business rule compliance within IATA NDC framework",
                test_scenarios=[
                    {"target": "UA", "result": "enhanced_validation", "scenario": "UA booking"},
                    {"target": "OTHER", "result": "standard_processing", "scenario": "Non-UA booking"}
                ],
                xslt_line_reference="Lines 425-426, 616-619",
                category="main_template"
            ),
            
            BaselineTestCase(
                id="multi_passenger_contact_validation",
                business_rule="Multiple passengers require contact information validation for specific targets (UA/UAD)",
                business_context="Family or group bookings need contact verification for compliance and communication purposes",
                business_scenario="Family of 4 booking UA flight requiring contact validation for all passengers",
                xslt_chunk="""<xsl:if test="count(//actor[@type='Individual']) > 1 and ($target='UA' or $target='UAD')">
    <xsl:for-each select="//actor[@type='Individual']">
        <xsl:if test="contactInfo">
            <!-- Contact validation logic -->
        </xsl:if>
    </xsl:for-each>
</xsl:if>""",
                input_conditions={"passenger_count": 4, "target": "UA", "booking_type": "family"},
                expected_behavior="Contact validation applied to all passengers in multi-passenger UA booking",
                business_value="Ensures proper contact information for group bookings and compliance",
                failure_impact="Booking failure due to incomplete contact validation for group travel",
                cross_chunk_dependencies=["passenger_counting", "contact_validation", "target_processing", "loop_processing"],
                domain_context="IATA NDC group booking compliance and contact verification requirements",
                test_scenarios=[
                    {"passengers": 4, "target": "UA", "result": "all_validated", "scenario": "Family booking"},
                    {"passengers": 1, "target": "UA", "result": "single_validation", "scenario": "Solo booking"}
                ],
                xslt_line_reference="Lines 1238-1270",
                category="main_template"
            ),
            
            BaselineTestCase(
                id="phone_number_standardization",
                business_rule="Phone numbers are normalized and validated against target-specific format requirements",
                business_context="Different airlines and regions have different phone number format requirements for compliance",
                business_scenario="International phone number needs proper formatting for specific airline target system",
                xslt_chunk="""<xsl:variable name="phone_normalized">
    <xsl:value-of select="normalize-space(contactInfo/phone)"/>
</xsl:variable>
<xsl:if test="starts-with($phone_normalized, '+1') and $target='UAD'">
    <!-- US phone number processing for UAD -->
</xsl:if>""",
                input_conditions={"phone": "+1-555-1234", "target": "UAD", "region": "US"},
                expected_behavior="Phone number formatted according to UAD target requirements",
                business_value="Ensures phone numbers meet target system format requirements for communication",
                failure_impact="Contact failure due to improperly formatted phone numbers",
                cross_chunk_dependencies=["contact_processing", "target_validation", "string_normalization"],
                domain_context="IATA NDC contact information standardization for airline system compatibility",
                test_scenarios=[
                    {"phone": "+1-555-1234", "target": "UAD", "result": "us_format", "scenario": "US phone for UAD"},
                    {"phone": "+44-20-1234", "target": "UA", "result": "intl_format", "scenario": "International phone"}
                ],
                xslt_line_reference="Lines 769-800",
                category="main_template"
            ),
            
            BaselineTestCase(
                id="address_concatenation_logic",
                business_rule="Address fields are concatenated with proper spacing and validation for metadata generation",
                business_context="Address standardization is required for booking systems, compliance, and customer communication",
                business_scenario="Multi-line international address needs proper formatting for booking confirmation",
                xslt_chunk="""<xsl:variable name="address_concat">
    <xsl:value-of select="concat(address/countryCode, '/', address/line, '/', address/cityName, '/', address/countryName, '/', address/zip)"/>
</xsl:variable>
<xsl:variable name="address_clean">
    <xsl:value-of select="substring($address_concat, 1, string-length($address_concat)-1)"/>
</xsl:variable>""",
                input_conditions={"address_fields": "multiple", "format": "international", "validation": "required"},
                expected_behavior="Address fields properly concatenated with slash separators and trailing slash removal",
                business_value="Standardized address format for booking systems and customer communication",
                failure_impact="Address formatting errors leading to delivery and communication problems",
                cross_chunk_dependencies=["address_processing", "string_manipulation", "validation_rules"],
                domain_context="IATA NDC address standardization for international booking compliance",
                test_scenarios=[
                    {"address": "complete", "result": "US/123 Main St/New York/United States/10001", "scenario": "Full address"},
                    {"address": "partial", "result": "FR/Paris/75001", "scenario": "Missing fields handled"}
                ],
                xslt_line_reference="Lines 1370-1421",
                category="main_template"
            ),
            
            BaselineTestCase(
                id="contact_type_processing",
                business_rule="Different contact types (email, phone, address) are processed with type-specific validation rules",
                business_context="Contact information has different validation requirements and business rules based on type",
                business_scenario="Passenger with multiple contact methods requiring type-specific processing and validation",
                xslt_chunk="""<xsl:for-each select="contactInfo">
    <xsl:choose>
        <xsl:when test="@type='email'">
            <!-- Email validation and processing -->
        </xsl:when>
        <xsl:when test="@type='phone'">
            <!-- Phone validation and processing -->
        </xsl:when>
        <xsl:when test="@type='address'">
            <!-- Address validation and processing -->
        </xsl:when>
    </xsl:choose>
</xsl:for-each>""",
                input_conditions={"contact_types": ["email", "phone", "address"], "validation": "all_types"},
                expected_behavior="Each contact type processed with appropriate validation rules",
                business_value="Ensures proper validation and processing for all contact methods",
                failure_impact="Contact validation failures leading to communication problems",
                cross_chunk_dependencies=["contact_validation", "type_processing", "validation_rules"],
                domain_context="IATA NDC contact type standardization and validation requirements",
                test_scenarios=[
                    {"type": "email", "validation": "format_check", "scenario": "Email validation"},
                    {"type": "phone", "validation": "number_format", "scenario": "Phone validation"},
                    {"type": "address", "validation": "field_check", "scenario": "Address validation"}
                ],
                xslt_line_reference="Lines 769-1227",
                category="main_template"
            ),
            
            # Complex Integration Cases (5 cases)
            BaselineTestCase(
                id="end_to_end_passenger_flow",
                business_rule="Complete passenger processing from input to output with all business rules and validations applied",
                business_context="Full passenger booking workflow must integrate all helper templates, validation rules, and target-specific processing",
                business_scenario="Complete booking process for UA flight with family passengers requiring full workflow validation",
                xslt_chunk="""<!-- Complete passenger flow integration -->
<xsl:template match="/">
    <xsl:for-each select="//actor[@type='Individual']">
        <xsl:variable name="doc_type" select="vmf:vmf1_inputtoresult(docRef/document/type)"/>
        <xsl:variable name="visa_type" select="vmf:vmf2_inputtoresult(docRef/visa/type)"/>
        <xsl:if test="$target='UA'">
            <!-- UA specific processing with helper results -->
        </xsl:if>
    </xsl:for-each>
</xsl:template>""",
                input_conditions={"workflow": "complete", "target": "UA", "passengers": "family", "validation": "full"},
                expected_behavior="End-to-end processing with all business rules, validations, and transformations applied",
                business_value="Complete booking workflow ensuring all business requirements and compliance rules are met",
                failure_impact="Booking failure due to incomplete workflow processing or validation gaps",
                cross_chunk_dependencies=["all_helper_templates", "main_processing", "validation_engine", "output_generation", "target_processing"],
                domain_context="Complete IATA NDC booking workflow with full compliance and business rule integration",
                test_scenarios=[
                    {"workflow": "complete_success", "result": "booking_confirmed", "scenario": "Full successful flow"},
                    {"workflow": "partial_failure", "result": "validation_error", "scenario": "Workflow validation failure"}
                ],
                xslt_line_reference="Lines 66-1868 (entire main template)",
                category="integration"
            ),
            
            BaselineTestCase(
                id="error_handling_and_fallbacks",
                business_rule="Graceful handling of missing data with appropriate defaults and fallback processing",
                business_context="Robust system behavior when input data is incomplete or invalid, preventing system failures",
                business_scenario="Passenger record with missing required fields requiring fallback processing",
                xslt_chunk="""<xsl:choose>
    <xsl:when test="docRef/document/type">
        <xsl:value-of select="vmf:vmf1_inputtoresult(docRef/document/type)"/>
    </xsl:when>
    <xsl:otherwise>
        <!-- Fallback processing for missing document type -->
        <xsl:text></xsl:text>
    </xsl:otherwise>
</xsl:choose>""",
                input_conditions={"data_completeness": "partial", "fallback_required": True, "error_handling": "graceful"},
                expected_behavior="System continues processing with appropriate fallbacks when data is missing",
                business_value="Prevents booking failures due to incomplete data, maintains system reliability",
                failure_impact="System crashes or booking failures when encountering incomplete data",
                cross_chunk_dependencies=["error_handling", "fallback_processing", "validation_engine", "default_values"],
                domain_context="IATA NDC system reliability and graceful degradation for incomplete data scenarios",
                test_scenarios=[
                    {"data": "missing_document", "result": "fallback_applied", "scenario": "Missing document handling"},
                    {"data": "invalid_format", "result": "error_recovery", "scenario": "Invalid data recovery"}
                ],
                xslt_line_reference="Lines 21-22, 38-39 (otherwise clauses)",
                category="integration"
            ),
            
            BaselineTestCase(
                id="conditional_logic_chains",
                business_rule="Complex nested conditions handle multiple combinations of business scenarios and data states",
                business_context="Business logic must handle complex combinations of conditions for different booking scenarios",
                business_scenario="Complex booking scenario with multiple conditional paths requiring nested decision logic",
                xslt_chunk="""<xsl:choose>
    <xsl:when test="$target='UA' and count(//actor) > 1 and docRef/visa[@type='R']">
        <!-- Complex UA multi-passenger with R visa -->
    </xsl:when>
    <xsl:when test="$target='UAD' and PTC='ADT' and contactInfo/phone[starts-with(., '+1')]">
        <!-- UAD adult with US phone -->
    </xsl:when>
    <xsl:otherwise>
        <!-- Standard processing -->
    </xsl:otherwise>
</xsl:choose>""",
                input_conditions={"complexity": "high", "conditions": "nested", "scenarios": "multiple"},
                expected_behavior="Correct processing path selected based on complex condition evaluation",
                business_value="Handles diverse booking scenarios with appropriate business logic",
                failure_impact="Incorrect processing due to failed condition evaluation",
                cross_chunk_dependencies=["condition_evaluation", "target_processing", "passenger_analysis", "contact_validation"],
                domain_context="IATA NDC complex business rule evaluation for diverse booking scenarios",
                test_scenarios=[
                    {"conditions": "ua_multi_r_visa", "result": "path_1", "scenario": "Complex UA scenario"},
                    {"conditions": "uad_adult_us_phone", "result": "path_2", "scenario": "UAD adult scenario"},
                    {"conditions": "standard", "result": "default_path", "scenario": "Standard processing"}
                ],
                xslt_line_reference="Lines 425-486 (complex conditions)",
                category="integration"
            ),
            
            BaselineTestCase(
                id="performance_optimization_patterns",
                business_rule="Efficient processing patterns are used for large passenger lists and complex transformations",
                business_context="System performance must be maintained under load with many passengers and complex processing",
                business_scenario="Large group booking with 50+ passengers requiring efficient processing patterns",
                xslt_chunk="""<xsl:for-each select="//actor[@type='Individual']">
    <xsl:variable name="current_actor" select="."/>
    <xsl:variable name="doc_result" select="vmf:vmf1_inputtoresult($current_actor/docRef/document/type)"/>
    <xsl:if test="$doc_result != ''">
        <!-- Efficient processing with variable reuse -->
    </xsl:if>
</xsl:for-each>""",
                input_conditions={"passenger_count": 50, "performance": "optimized", "load": "high"},
                expected_behavior="Efficient processing maintains performance with large passenger counts",
                business_value="System scalability and performance under high load conditions",
                failure_impact="Performance degradation or timeouts with large bookings",
                cross_chunk_dependencies=["loop_optimization", "variable_management", "performance_patterns"],
                domain_context="IATA NDC system performance optimization for high-volume booking scenarios",
                test_scenarios=[
                    {"passengers": 50, "result": "efficient_processing", "scenario": "Large group booking"},
                    {"passengers": 1, "result": "standard_processing", "scenario": "Single passenger baseline"}
                ],
                xslt_line_reference="Lines 249-767 (passenger processing loops)",
                category="integration"
            ),
            
            BaselineTestCase(
                id="compliance_validation_integration",
                business_rule="All transformations must pass integrated compliance checks across multiple business rule categories",
                business_context="Regulatory compliance requirements must be validated across the entire transformation workflow",
                business_scenario="International booking requiring compliance validation across all business rule categories",
                xslt_chunk="""<!-- Integrated compliance validation -->
<xsl:variable name="compliance_doc" select="vmf:vmf1_inputtoresult(docRef/document/type)"/>
<xsl:variable name="compliance_visa" select="vmf:vmf2_inputtoresult(docRef/visa/type)"/>
<xsl:if test="$compliance_doc != '' and $compliance_visa != '' and $target='UA'">
    <!-- Full compliance validation -->
</xsl:if>""",
                input_conditions={"compliance": "full", "validation": "all_categories", "regulatory": "international"},
                expected_behavior="Complete compliance validation across all business rule categories",
                business_value="Ensures full regulatory compliance for international bookings",
                failure_impact="Regulatory compliance failures leading to legal and operational issues",
                cross_chunk_dependencies=["all_business_rules", "compliance_engine", "validation_framework", "regulatory_checks"],
                domain_context="Complete IATA NDC regulatory compliance validation for international travel",
                test_scenarios=[
                    {"compliance": "full_pass", "result": "compliant_booking", "scenario": "Full compliance success"},
                    {"compliance": "partial_fail", "result": "compliance_error", "scenario": "Compliance validation failure"}
                ],
                xslt_line_reference="Lines 66-1868 (integrated compliance)",
                category="integration"
            )
        ]
    
    def get_baseline_cases(self) -> List[BaselineTestCase]:
        """Get all baseline test cases"""
        return self.baseline_cases
    
    def get_cases_by_category(self, category: str) -> List[BaselineTestCase]:
        """Get baseline cases filtered by category"""
        return [case for case in self.baseline_cases if case.category == category]
    
    def get_helper_template_cases(self) -> List[BaselineTestCase]:
        """Get helper template baseline cases"""
        return self.get_cases_by_category("helper_template")
    
    def get_main_template_cases(self) -> List[BaselineTestCase]:
        """Get main template baseline cases"""
        return self.get_cases_by_category("main_template")
    
    def get_integration_cases(self) -> List[BaselineTestCase]:
        """Get integration baseline cases"""
        return self.get_cases_by_category("integration")
    
    def get_case_by_id(self, case_id: str) -> BaselineTestCase:
        """Get specific baseline case by ID"""
        for case in self.baseline_cases:
            if case.id == case_id:
                return case
        raise ValueError(f"Baseline case '{case_id}' not found")


# Example usage for PoC validation
if __name__ == "__main__":
    baseline = ManualAnalysisBaseline()
    
    print(f"Total baseline cases: {len(baseline.get_baseline_cases())}")
    print(f"Helper template cases: {len(baseline.get_helper_template_cases())}")
    print(f"Main template cases: {len(baseline.get_main_template_cases())}")
    print(f"Integration cases: {len(baseline.get_integration_cases())}")
    
    # Show example case
    case = baseline.get_case_by_id("vmf1_passport_transformation")
    print(f"\nExample case: {case.business_rule}")
    print(f"Business context: {case.business_context}")
    print(f"Expected behavior: {case.expected_behavior}")