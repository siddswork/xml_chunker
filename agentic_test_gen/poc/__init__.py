"""
Proof of Concept Validation Package

This package contains all components needed to validate whether our AI-based approach
can match the quality of manual analysis before proceeding with full implementation.

Components:
- manual_analysis_baseline: 15 representative test cases from manual analysis
- quality_validator: 4-dimensional quality scoring framework  
- domain_knowledge: IATA NDC domain knowledge base
- minimal_xslt_analyzer: Business-focused XSLT analysis agent
- poc_validator: Complete validation orchestrator

Usage:
    from agentic_test_gen.poc import run_poc_validation
    
    result = await run_poc_validation(openai_api_key="your-key")
    print(f"PoC Success: {result.meets_poc_criteria}")
"""

from .poc_validator import run_poc_validation, PoCValidator
from .enhanced_poc_validator import run_enhanced_poc_validation, EnhancedPoCValidator
from .manual_analysis_baseline import ManualAnalysisBaseline, BaselineTestCase
from .quality_validator import QualityValidator, QualityScore, AIAnalysisResult
from .domain_knowledge import DomainKnowledgeBase
from .minimal_xslt_analyzer import MinimalXSLTAnalyzer
from .multi_pass_analyzer import MultiPassXSLTAnalyzer, EnhancedMinimalXSLTAnalyzer
from .context_provider import ContextProvider

__all__ = [
    'run_poc_validation',
    'run_enhanced_poc_validation',
    'PoCValidator',
    'EnhancedPoCValidator',
    'ManualAnalysisBaseline',
    'BaselineTestCase',
    'QualityValidator',
    'QualityScore',
    'AIAnalysisResult',
    'DomainKnowledgeBase',
    'MinimalXSLTAnalyzer',
    'MultiPassXSLTAnalyzer',
    'EnhancedMinimalXSLTAnalyzer',
    'ContextProvider'
]

__version__ = "1.0.0"
__author__ = "Agentic XSLT Test Generation Team"
__description__ = "Proof of Concept validation for AI-based XSLT analysis quality"