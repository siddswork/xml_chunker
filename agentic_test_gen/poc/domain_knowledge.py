"""
IATA NDC Domain Knowledge Base

This module provides comprehensive domain knowledge about IATA NDC (New Distribution Capability)
to enhance AI agent understanding of business context and requirements. The knowledge base
includes business concepts, compliance requirements, and industry-specific patterns.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class BusinessPattern:
    """Represents a business pattern with context"""
    name: str
    description: str
    business_purpose: str
    compliance_requirements: List[str]
    failure_implications: List[str]
    examples: List[str]


@dataclass
class ComplianceRule:
    """Represents a compliance requirement"""
    rule_id: str
    description: str
    regulatory_source: str
    business_impact: str
    validation_requirements: List[str]
    failure_consequences: List[str]


class DomainKnowledgeBase:
    """Comprehensive IATA NDC domain knowledge for AI context enhancement"""
    
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Build comprehensive domain knowledge structure"""
        
        return {
            'iata_ndc_overview': {
                'purpose': 'IATA New Distribution Capability for airline retailing modernization',
                'key_objectives': [
                    'Enable rich content and ancillary service distribution',
                    'Standardize data formats for airline interoperability',
                    'Support direct airline distribution channels',
                    'Enhance customer experience through personalization'
                ],
                'business_drivers': [
                    'Airline revenue optimization',
                    'Distribution cost reduction',
                    'Enhanced customer experience',
                    'Regulatory compliance requirements'
                ],
                'stakeholders': [
                    'Airlines (service providers)',
                    'Travel agencies (distributors)',
                    'GDS systems (aggregators)',
                    'Technology providers (implementers)',
                    'Regulatory bodies (compliance)'
                ]
            },
            
            'document_types': {
                'passport': {
                    'codes': ['P', 'PT'],
                    'ndc_standard': 'VPT',
                    'business_purpose': 'International travel identity verification',
                    'compliance_requirements': [
                        'ICAO Document 9303 compliance',
                        'Airline security validation',
                        'Border control integration'
                    ],
                    'validation_rules': [
                        'Valid passport number format',
                        'Expiration date validation',
                        'Issuing country verification'
                    ],
                    'failure_impacts': [
                        'Booking rejection for international travel',
                        'Border control complications',
                        'Security compliance violations'
                    ]
                },
                'visa': {
                    'codes': ['V', 'R', 'K'],
                    'ndc_standards': {'V': 'VVI', 'R': 'VAEA', 'K': 'VCR'},
                    'business_purpose': 'Legal entry authorization validation',
                    'compliance_requirements': [
                        'Country-specific visa regulations',
                        'Entry/exit requirement validation',
                        'Diplomatic status verification'
                    ],
                    'validation_rules': [
                        'Visa validity period check',
                        'Entry purpose validation',
                        'Host country verification'
                    ],
                    'failure_impacts': [
                        'Entry denial at destination',
                        'Legal complications for airline',
                        'Customer service escalations'
                    ]
                },
                'identity': {
                    'codes': ['I'],
                    'ndc_standard': 'VII',
                    'business_purpose': 'Domestic travel identity verification',
                    'compliance_requirements': [
                        'National identity document standards',
                        'Domestic travel regulations',
                        'Government ID verification'
                    ],
                    'validation_rules': [
                        'Government-issued ID verification',
                        'Photo ID requirements',
                        'Address verification where required'
                    ],
                    'failure_impacts': [
                        'Domestic travel denial',
                        'Security checkpoint issues',
                        'Customer inconvenience'
                    ]
                }
            },
            
            'target_systems': {
                'UA': {
                    'airline': 'United Airlines',
                    'system_type': 'Enhanced validation system',
                    'business_requirements': [
                        'Multi-passenger contact validation',
                        'Enhanced document verification',
                        'Specific visa type restrictions',
                        'Contact information mandatory'
                    ],
                    'compliance_standards': [
                        'TSA security requirements',
                        'United Airlines business rules',
                        'US DOT regulations'
                    ],
                    'processing_patterns': [
                        'GST passenger exclusion',
                        'Tax identifier FOID generation',
                        'Enhanced address processing',
                        'Specific visa type blocking (R-type)'
                    ],
                    'failure_consequences': [
                        'Booking cancellation',
                        'Compliance audit failures',
                        'Revenue loss',
                        'Customer satisfaction impact'
                    ]
                },
                'UAD': {
                    'airline': 'United Airlines Domestic',
                    'system_type': 'Domestic-focused processing',
                    'business_requirements': [
                        'US phone number format validation',
                        'Domestic travel optimization',
                        'Simplified documentation requirements',
                        'Streamlined booking process'
                    ],
                    'compliance_standards': [
                        'Domestic travel regulations',
                        'United Airlines domestic policies',
                        'State-specific requirements'
                    ],
                    'processing_patterns': [
                        'Phone number format optimization',
                        'Domestic address handling',
                        'Simplified visa processing',
                        'Reduced validation complexity'
                    ],
                    'failure_consequences': [
                        'Domestic booking failures',
                        'Customer service burden',
                        'Process inefficiencies'
                    ]
                }
            },
            
            'business_patterns': self._get_business_patterns(),
            'compliance_rules': self._get_compliance_rules(),
            'transformation_contexts': self._get_transformation_contexts(),
            'failure_scenarios': self._get_failure_scenarios(),
            'integration_patterns': self._get_integration_patterns()
        }
    
    def _get_business_patterns(self) -> Dict[str, BusinessPattern]:
        """Define key business patterns in XSLT transformations"""
        
        return {
            'document_standardization': BusinessPattern(
                name="Document Type Standardization",
                description="Transform airline-specific document codes to IATA NDC standard codes",
                business_purpose="Enable interoperability between different airline systems and compliance with IATA standards",
                compliance_requirements=[
                    "IATA NDC specification compliance",
                    "Document type consistency across systems",
                    "Regulatory validation requirements"
                ],
                failure_implications=[
                    "System interoperability failures",
                    "Compliance audit violations",
                    "Booking processing errors"
                ],
                examples=[
                    "P -> VPT (Passport transformation)",
                    "V -> VVI (Visa transformation)",
                    "I -> VII (Identity transformation)"
                ]
            ),
            
            'target_specific_processing': BusinessPattern(
                name="Target-Specific Business Logic",
                description="Apply airline-specific business rules and validation requirements",
                business_purpose="Meet individual airline requirements while maintaining system flexibility",
                compliance_requirements=[
                    "Airline-specific regulatory compliance",
                    "Business rule consistency",
                    "Processing requirement adherence"
                ],
                failure_implications=[
                    "Airline-specific booking failures",
                    "Compliance violations",
                    "Revenue impact"
                ],
                examples=[
                    "UA target enhanced validation",
                    "UAD domestic optimization",
                    "Target-specific visa restrictions"
                ]
            ),
            
            'contact_validation': BusinessPattern(
                name="Contact Information Validation",
                description="Validate and standardize passenger contact information",
                business_purpose="Ensure reliable customer communication and compliance with notification requirements",
                compliance_requirements=[
                    "Customer communication regulations",
                    "Data quality standards",
                    "Contact information completeness"
                ],
                failure_implications=[
                    "Communication failures",
                    "Customer service issues",
                    "Regulatory notification failures"
                ],
                examples=[
                    "Phone number format validation",
                    "Email address verification",
                    "Address standardization"
                ]
            ),
            
            'multi_passenger_processing': BusinessPattern(
                name="Multi-Passenger Booking Handling",
                description="Process group bookings with appropriate validation and relationship management",
                business_purpose="Handle family and group travel requirements efficiently while maintaining individual validation",
                compliance_requirements=[
                    "Group booking regulations",
                    "Individual passenger validation",
                    "Relationship verification requirements"
                ],
                failure_implications=[
                    "Group booking failures",
                    "Incomplete passenger processing",
                    "Validation gaps"
                ],
                examples=[
                    "Family booking validation",
                    "Group contact requirements",
                    "Multi-passenger dependency handling"
                ]
            ),
            
            'error_handling': BusinessPattern(
                name="Graceful Error Handling",
                description="Handle missing or invalid data with appropriate fallback mechanisms",
                business_purpose="Maintain system reliability and prevent booking failures due to incomplete data",
                compliance_requirements=[
                    "System reliability standards",
                    "Data quality requirements",
                    "Error recovery protocols"
                ],
                failure_implications=[
                    "System crashes",
                    "Data corruption",
                    "Booking processing failures"
                ],
                examples=[
                    "Missing document type handling",
                    "Invalid input recovery",
                    "Default value application"
                ]
            )
        }
    
    def _get_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Define compliance rules and requirements"""
        
        return {
            'document_validation': ComplianceRule(
                rule_id="DOC_VAL_001",
                description="All passenger documents must be validated according to IATA NDC standards",
                regulatory_source="IATA NDC Specification v21.3",
                business_impact="Ensures interoperability and compliance across airline systems",
                validation_requirements=[
                    "Document type code standardization",
                    "Document validity verification",
                    "Regulatory compliance checking"
                ],
                failure_consequences=[
                    "Booking rejection",
                    "Compliance audit failures",
                    "System interoperability issues"
                ]
            ),
            
            'target_processing': ComplianceRule(
                rule_id="TGT_PROC_001",
                description="Target-specific processing must comply with airline business rules",
                regulatory_source="Airline-specific business rule specifications",
                business_impact="Meets individual airline requirements and regulatory compliance",
                validation_requirements=[
                    "Airline-specific rule application",
                    "Target system compatibility",
                    "Business rule consistency"
                ],
                failure_consequences=[
                    "Airline system rejection",
                    "Business rule violations",
                    "Revenue impact"
                ]
            ),
            
            'contact_requirements': ComplianceRule(
                rule_id="CONT_REQ_001",
                description="Contact information must meet communication and notification requirements",
                regulatory_source="Customer communication regulations",
                business_impact="Enables reliable customer communication and regulatory compliance",
                validation_requirements=[
                    "Contact information completeness",
                    "Format standardization",
                    "Reachability verification"
                ],
                failure_consequences=[
                    "Communication failures",
                    "Customer service issues",
                    "Regulatory notification failures"
                ]
            )
        }
    
    def _get_transformation_contexts(self) -> Dict[str, Dict[str, str]]:
        """Define contexts for XSLT transformations"""
        
        return {
            'helper_templates': {
                'vmf1': 'Document type standardization for passport/identity documents',
                'vmf2': 'Visa type standardization for international travel documents',
                'vmf3': 'Identity document processing for domestic travel',
                'vmf4': 'Generic document type handling with fallback mechanisms'
            },
            'main_template_sections': {
                'passenger_processing': 'Core passenger data transformation and validation',
                'contact_handling': 'Contact information processing and standardization',
                'address_processing': 'Address field concatenation and formatting',
                'target_validation': 'Airline-specific business rule application',
                'document_integration': 'Integration of helper template results',
                'output_generation': 'Final XML structure generation'
            },
            'integration_flows': {
                'helper_to_main': 'Flow of helper template results into main processing',
                'validation_chain': 'Sequential validation and processing steps',
                'error_recovery': 'Error handling and fallback processing',
                'output_assembly': 'Final output structure assembly'
            }
        }
    
    def _get_failure_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Define potential failure scenarios and their business impacts"""
        
        return {
            'document_processing_failure': {
                'description': 'Failure to properly process document types',
                'triggers': ['Invalid document codes', 'Missing document data', 'Unsupported document types'],
                'business_impact': 'Booking rejection, compliance violations, customer dissatisfaction',
                'system_impact': 'Processing errors, data integrity issues, system reliability concerns',
                'recovery_strategies': ['Fallback to default values', 'Error logging and notification', 'Manual intervention triggers']
            },
            'target_processing_failure': {
                'description': 'Failure in airline-specific processing requirements',
                'triggers': ['Unknown target systems', 'Rule validation failures', 'Configuration errors'],
                'business_impact': 'Airline system rejection, revenue loss, compliance issues',
                'system_impact': 'Integration failures, processing bottlenecks, error cascades',
                'recovery_strategies': ['Default processing rules', 'Target-specific fallbacks', 'Error escalation protocols']
            },
            'validation_failure': {
                'description': 'Failure in contact or document validation processes',
                'triggers': ['Invalid contact formats', 'Missing required fields', 'Validation rule conflicts'],
                'business_impact': 'Communication failures, customer service burden, regulatory issues',
                'system_impact': 'Data quality degradation, processing delays, manual intervention requirements',
                'recovery_strategies': ['Data correction workflows', 'Validation bypass mechanisms', 'Quality assurance alerts']
            }
        }
    
    def _get_integration_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Define integration patterns between system components"""
        
        return {
            'helper_integration': {
                'pattern': 'Helper template results feed into main processing logic',
                'dependencies': ['Helper template execution', 'Result validation', 'Main template processing'],
                'data_flow': 'Input -> Helper -> Validation -> Main -> Output',
                'failure_points': ['Helper execution errors', 'Result format issues', 'Integration mismatches'],
                'business_value': 'Modular processing, code reusability, consistent transformations'
            },
            'validation_integration': {
                'pattern': 'Sequential validation steps with cumulative error handling',
                'dependencies': ['Document validation', 'Contact validation', 'Business rule validation'],
                'data_flow': 'Input -> Document Check -> Contact Check -> Business Rules -> Output',
                'failure_points': ['Individual validation failures', 'Validation rule conflicts', 'Error propagation'],
                'business_value': 'Comprehensive validation, error prevention, quality assurance'
            },
            'target_integration': {
                'pattern': 'Target-specific processing with conditional business logic',
                'dependencies': ['Target identification', 'Rule selection', 'Conditional processing'],
                'data_flow': 'Input -> Target Detection -> Rule Application -> Specialized Processing -> Output',
                'failure_points': ['Target misidentification', 'Rule application errors', 'Logic conflicts'],
                'business_value': 'Airline-specific compliance, flexible processing, business rule adherence'
            }
        }
    
    def get_context_for_business_rule(self, rule_type: str) -> Dict[str, Any]:
        """Get relevant context for a specific business rule type"""
        
        context_map = {
            'document_transformation': ['document_types', 'business_patterns.document_standardization', 'compliance_rules.document_validation'],
            'target_processing': ['target_systems', 'business_patterns.target_specific_processing', 'compliance_rules.target_processing'],
            'contact_validation': ['business_patterns.contact_validation', 'compliance_rules.contact_requirements'],
            'integration_flow': ['transformation_contexts.integration_flows', 'integration_patterns'],
            'error_handling': ['business_patterns.error_handling', 'failure_scenarios']
        }
        
        relevant_paths = context_map.get(rule_type, [])
        context = {}
        
        for path in relevant_paths:
            keys = path.split('.')
            current = self.knowledge_base
            for key in keys:
                if key in current:
                    current = current[key]
                else:
                    current = None
                    break
            if current:
                context[path] = current
        
        return context
    
    def get_domain_context_prompt(self, business_rule_type: str) -> str:
        """Generate domain context prompt for LLM integration"""
        
        base_context = f"""
IATA NDC DOMAIN KNOWLEDGE:

Purpose: {self.knowledge_base['iata_ndc_overview']['purpose']}

Key Business Objectives:
{chr(10).join('- ' + obj for obj in self.knowledge_base['iata_ndc_overview']['key_objectives'])}

Business Drivers:
{chr(10).join('- ' + driver for driver in self.knowledge_base['iata_ndc_overview']['business_drivers'])}
"""
        
        # Add specific context based on rule type
        specific_context = self.get_context_for_business_rule(business_rule_type)
        
        if 'document_types' in specific_context:
            base_context += f"""

DOCUMENT TYPE STANDARDS:
{self._format_document_types()}
"""
        
        if 'target_systems' in specific_context:
            base_context += f"""

TARGET SYSTEM REQUIREMENTS:
{self._format_target_systems()}
"""
        
        return base_context
    
    def _format_document_types(self) -> str:
        """Format document type information for prompt"""
        doc_info = []
        for doc_type, details in self.knowledge_base['document_types'].items():
            doc_info.append(f"- {doc_type.upper()}: {details['business_purpose']}")
            if 'codes' in details:
                doc_info.append(f"  Codes: {details['codes']} -> {details.get('ndc_standard', 'Various')}")
            doc_info.append(f"  Business Impact: {'; '.join(details.get('failure_impacts', []))}")
        return '\n'.join(doc_info)
    
    def _format_target_systems(self) -> str:
        """Format target system information for prompt"""
        target_info = []
        for target, details in self.knowledge_base['target_systems'].items():
            target_info.append(f"- {target}: {details['airline']}")
            target_info.append(f"  Requirements: {'; '.join(details['business_requirements'])}")
            target_info.append(f"  Failure Impact: {'; '.join(details['failure_consequences'])}")
        return '\n'.join(target_info)
    
    def validate_business_understanding(self, ai_analysis: str) -> Dict[str, float]:
        """Validate AI's business understanding against domain knowledge"""
        
        validation_scores = {}
        
        # Check for domain keyword presence
        domain_keywords = [
            'iata', 'ndc', 'airline', 'booking', 'compliance', 'interoperability',
            'passenger', 'document', 'validation', 'business rule', 'regulatory'
        ]
        
        ai_text_lower = ai_analysis.lower()
        found_keywords = sum(1 for keyword in domain_keywords if keyword in ai_text_lower)
        validation_scores['domain_awareness'] = min(found_keywords / len(domain_keywords), 1.0)
        
        # Check for business context understanding
        business_concepts = [
            'business purpose', 'business value', 'failure impact', 'compliance',
            'customer', 'revenue', 'system', 'process', 'workflow'
        ]
        
        found_concepts = sum(1 for concept in business_concepts if concept in ai_text_lower)
        validation_scores['business_context'] = min(found_concepts / len(business_concepts), 1.0)
        
        # Check for specific domain knowledge
        specific_terms = [
            'document type', 'target system', 'validation rule', 'transformation',
            'helper template', 'integration', 'processing', 'standardization'
        ]
        
        found_terms = sum(1 for term in specific_terms if term in ai_text_lower)
        validation_scores['domain_specificity'] = min(found_terms / len(specific_terms), 1.0)
        
        return validation_scores


# Example usage
if __name__ == "__main__":
    kb = DomainKnowledgeBase()
    
    # Test domain context generation
    context = kb.get_domain_context_prompt('document_transformation')
    print("Domain Context for Document Transformation:")
    print(context[:500] + "...")
    
    # Test business understanding validation
    sample_analysis = "This rule handles IATA NDC document transformation for airline booking compliance"
    scores = kb.validate_business_understanding(sample_analysis)
    print(f"\nBusiness Understanding Scores: {scores}")