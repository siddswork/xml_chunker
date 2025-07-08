"""
Quality Validation Framework for PoC

This module implements the 4-dimensional quality scoring framework to measure
how well AI agents match the quality of manual analysis. The framework evaluates:

1. Business Understanding (30%) - Does AI understand WHY rules exist?
2. Scenario Coverage (25%) - Does AI identify same business scenarios?  
3. Test Meaningfulness (25%) - Are generated tests business-relevant?
4. Integration Awareness (20%) - Does AI understand cross-chunk dependencies?
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class QualityScore:
    """Quality score result with dimension breakdown"""
    overall_score: float
    business_understanding: float
    scenario_coverage: float
    test_meaningfulness: float
    integration_awareness: float
    meets_threshold: bool
    detailed_feedback: Dict[str, str]


@dataclass
class AIAnalysisResult:
    """Structure for AI agent analysis result"""
    business_context: str
    business_scenarios: List[str]
    generated_tests: List[Dict[str, Any]]
    dependencies: List[str]
    extracted_rules: List[str]
    domain_understanding: str
    failure_impacts: List[str]


class QualityValidator:
    """Quality validation framework for AI analysis results"""
    
    def __init__(self):
        self.quality_dimensions = {
            'business_understanding': 0.30,
            'scenario_coverage': 0.25,
            'test_meaningfulness': 0.25,
            'integration_awareness': 0.20
        }
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        # Domain-specific keywords for IATA NDC context
        self.domain_keywords = {
            'iata_ndc': ['ndc', 'iata', 'airline', 'booking', 'compliance', 'interoperability'],
            'document_types': ['passport', 'visa', 'identity', 'document', 'validation'],
            'business_value': ['compliance', 'regulatory', 'booking', 'customer', 'system'],
            'failure_impacts': ['rejection', 'failure', 'error', 'crash', 'compliance']
        }
    
    def score_quality_match(self, manual_case, ai_result: AIAnalysisResult) -> QualityScore:
        """Score how well AI matches manual analysis quality"""
        
        # Calculate individual dimension scores
        business_score = self.score_business_understanding(
            manual_case.business_context,
            manual_case.business_value,
            manual_case.failure_impact,
            ai_result
        )
        
        scenario_score = self.score_scenario_coverage(
            manual_case.business_scenario,
            manual_case.test_scenarios,
            ai_result
        )
        
        test_score = self.score_test_meaningfulness(
            manual_case.business_value,
            manual_case.failure_impact,
            ai_result
        )
        
        integration_score = self.score_integration_awareness(
            manual_case.cross_chunk_dependencies,
            manual_case.domain_context,
            ai_result
        )
        
        # Calculate weighted overall score
        overall_score = (
            business_score * self.quality_dimensions['business_understanding'] +
            scenario_score * self.quality_dimensions['scenario_coverage'] +
            test_score * self.quality_dimensions['test_meaningfulness'] +
            integration_score * self.quality_dimensions['integration_awareness']
        )
        
        # Generate detailed feedback
        feedback = self._generate_detailed_feedback(
            business_score, scenario_score, test_score, integration_score,
            manual_case, ai_result
        )
        
        return QualityScore(
            overall_score=overall_score,
            business_understanding=business_score,
            scenario_coverage=scenario_score,
            test_meaningfulness=test_score,
            integration_awareness=integration_score,
            meets_threshold=overall_score >= 0.9,
            detailed_feedback=feedback
        )
    
    def score_business_understanding(self, manual_context: str, manual_value: str, 
                                   manual_impact: str, ai_result: AIAnalysisResult) -> float:
        """Score business context understanding (30% weight)"""
        scores = []
        
        # Context accuracy: Does AI identify same business reasons?
        context_similarity = self._semantic_similarity(
            manual_context, ai_result.business_context
        )
        scores.append(context_similarity * 0.4)
        
        # Domain awareness: Does AI show IATA NDC understanding?
        domain_score = self._check_domain_knowledge(
            ai_result.domain_understanding, "iata_ndc"
        )
        scores.append(domain_score * 0.3)
        
        # Business value understanding: Does AI grasp value proposition?
        value_similarity = self._semantic_similarity(
            manual_value, ai_result.business_context
        )
        scores.append(value_similarity * 0.3)
        
        return sum(scores)
    
    def score_scenario_coverage(self, manual_scenario: str, manual_test_scenarios: List[Dict],
                               ai_result: AIAnalysisResult) -> float:
        """Score business scenario identification (25% weight)"""
        scores = []
        
        # Scenario overlap: Same scenarios identified?
        scenario_overlap = self._calculate_scenario_overlap(
            manual_test_scenarios, ai_result.business_scenarios
        )
        scores.append(scenario_overlap * 0.5)
        
        # Scenario depth: Adequate detail in scenarios?
        depth_score = self._evaluate_scenario_depth(ai_result.business_scenarios)
        scores.append(depth_score * 0.3)
        
        # Business relevance: Are scenarios business-meaningful?
        relevance_score = self._evaluate_business_relevance(ai_result.business_scenarios)
        scores.append(relevance_score * 0.2)
        
        return sum(scores)
    
    def score_test_meaningfulness(self, manual_value: str, manual_impact: str,
                                 ai_result: AIAnalysisResult) -> float:
        """Score whether AI generates business-meaningful tests (25% weight)"""
        scores = []
        
        # Bug detection potential: Would tests catch real bugs?
        bug_detection_score = self._evaluate_bug_detection_potential(ai_result.generated_tests)
        scores.append(bug_detection_score * 0.5)
        
        # Business scenario coverage: Do tests cover business scenarios?
        test_scenario_coverage = self._evaluate_test_scenario_coverage(ai_result.generated_tests)
        scores.append(test_scenario_coverage * 0.3)
        
        # Test structure quality: Are tests well-structured?
        test_quality = self._evaluate_test_structure_quality(ai_result.generated_tests)
        scores.append(test_quality * 0.2)
        
        return sum(scores)
    
    def score_integration_awareness(self, manual_dependencies: List[str], 
                                   manual_domain: str, ai_result: AIAnalysisResult) -> float:
        """Score understanding of cross-chunk integration (20% weight)"""
        scores = []
        
        # Dependency identification: Same dependencies found?
        dependency_match = self._compare_dependencies(manual_dependencies, ai_result.dependencies)
        scores.append(dependency_match * 0.4)
        
        # Integration understanding: Understands how chunks connect?
        integration_score = self._evaluate_integration_understanding(ai_result.dependencies)
        scores.append(integration_score * 0.3)
        
        # Flow comprehension: Understands end-to-end processing?
        flow_score = self._evaluate_flow_comprehension(ai_result.dependencies)
        scores.append(flow_score * 0.3)
        
        return sum(scores)
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        try:
            # Use TF-IDF vectorization and cosine similarity
            texts = [text1.lower(), text2.lower()]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception:
            # Fallback to simple string similarity
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _check_domain_knowledge(self, ai_text: str, domain: str) -> float:
        """Check if AI demonstrates domain knowledge"""
        if not ai_text:
            return 0.0
        
        domain_words = self.domain_keywords.get(domain, [])
        ai_text_lower = ai_text.lower()
        
        found_keywords = sum(1 for keyword in domain_words if keyword in ai_text_lower)
        return min(found_keywords / len(domain_words), 1.0) if domain_words else 0.0
    
    def _calculate_scenario_overlap(self, manual_scenarios: List[Dict], 
                                   ai_scenarios: List[str]) -> float:
        """Calculate overlap between manual and AI identified scenarios"""
        if not manual_scenarios or not ai_scenarios:
            return 0.0
        
        # Extract scenario descriptions from manual cases
        manual_scenario_texts = [scenario.get('scenario', '') for scenario in manual_scenarios]
        
        # Calculate best match for each manual scenario
        total_similarity = 0.0
        for manual_scenario in manual_scenario_texts:
            best_match = max(
                (self._semantic_similarity(manual_scenario, ai_scenario) 
                 for ai_scenario in ai_scenarios),
                default=0.0
            )
            total_similarity += best_match
        
        return total_similarity / len(manual_scenario_texts)
    
    def _evaluate_scenario_depth(self, ai_scenarios: List[str]) -> float:
        """Evaluate depth and detail of AI scenarios"""
        if not ai_scenarios:
            return 0.0
        
        # Check for detailed scenarios (length, specific terms, context)
        depth_scores = []
        for scenario in ai_scenarios:
            # Length indicator (detailed scenarios tend to be longer)
            length_score = min(len(scenario.split()) / 10, 1.0)
            
            # Specificity indicator (contains specific business terms)
            specificity_score = self._check_domain_knowledge(scenario, 'business_value')
            
            depth_scores.append((length_score + specificity_score) / 2)
        
        return sum(depth_scores) / len(depth_scores)
    
    def _evaluate_business_relevance(self, ai_scenarios: List[str]) -> float:
        """Evaluate business relevance of AI scenarios"""
        if not ai_scenarios:
            return 0.0
        
        relevance_scores = []
        business_indicators = ['booking', 'passenger', 'airline', 'compliance', 'validation', 'customer']
        
        for scenario in ai_scenarios:
            scenario_lower = scenario.lower()
            found_indicators = sum(1 for indicator in business_indicators if indicator in scenario_lower)
            relevance_score = min(found_indicators / 3, 1.0)  # Normalize to max 1.0
            relevance_scores.append(relevance_score)
        
        return sum(relevance_scores) / len(relevance_scores)
    
    def _evaluate_bug_detection_potential(self, ai_tests: List[Dict]) -> float:
        """Evaluate whether AI tests would catch real business bugs"""
        if not ai_tests:
            return 0.0
        
        bug_detection_indicators = [
            'edge case', 'boundary', 'invalid', 'error', 'validation',
            'failure', 'missing', 'empty', 'null', 'exception'
        ]
        
        bug_detection_scores = []
        for test in ai_tests:
            test_text = str(test).lower()
            found_indicators = sum(1 for indicator in bug_detection_indicators if indicator in test_text)
            score = min(found_indicators / 3, 1.0)
            bug_detection_scores.append(score)
        
        return sum(bug_detection_scores) / len(bug_detection_scores)
    
    def _evaluate_test_scenario_coverage(self, ai_tests: List[Dict]) -> float:
        """Evaluate whether tests cover business scenarios comprehensively"""
        if not ai_tests:
            return 0.0
        
        scenario_indicators = [
            'scenario', 'use case', 'business case', 'customer', 'booking',
            'passenger', 'workflow', 'process', 'integration'
        ]
        
        coverage_scores = []
        for test in ai_tests:
            test_text = str(test).lower()
            found_indicators = sum(1 for indicator in scenario_indicators if indicator in test_text)
            score = min(found_indicators / 3, 1.0)
            coverage_scores.append(score)
        
        return sum(coverage_scores) / len(coverage_scores)
    
    def _evaluate_test_structure_quality(self, ai_tests: List[Dict]) -> float:
        """Evaluate structural quality of generated tests"""
        if not ai_tests:
            return 0.0
        
        quality_indicators = [
            'assert', 'expect', 'input', 'output', 'test_', 'def test',
            'given', 'when', 'then', 'validate', 'verify'
        ]
        
        quality_scores = []
        for test in ai_tests:
            test_text = str(test).lower()
            found_indicators = sum(1 for indicator in quality_indicators if indicator in test_text)
            score = min(found_indicators / 4, 1.0)
            quality_scores.append(score)
        
        return sum(quality_scores) / len(quality_scores)
    
    def _compare_dependencies(self, manual_deps: List[str], ai_deps: List[str]) -> float:
        """Compare dependency identification between manual and AI"""
        if not manual_deps or not ai_deps:
            return 0.0
        
        # Calculate best match for each manual dependency
        total_similarity = 0.0
        for manual_dep in manual_deps:
            best_match = max(
                (self._semantic_similarity(manual_dep, ai_dep) for ai_dep in ai_deps),
                default=0.0
            )
            total_similarity += best_match
        
        return total_similarity / len(manual_deps)
    
    def _evaluate_integration_understanding(self, ai_deps: List[str]) -> float:
        """Evaluate AI understanding of integration patterns"""
        if not ai_deps:
            return 0.0
        
        integration_indicators = [
            'helper', 'template', 'main', 'flow', 'integration', 'dependency',
            'chain', 'workflow', 'processing', 'connection', 'cross-chunk'
        ]
        
        understanding_scores = []
        for dep in ai_deps:
            dep_text = dep.lower()
            found_indicators = sum(1 for indicator in integration_indicators if indicator in dep_text)
            score = min(found_indicators / 3, 1.0)
            understanding_scores.append(score)
        
        return sum(understanding_scores) / len(understanding_scores)
    
    def _evaluate_flow_comprehension(self, ai_deps: List[str]) -> float:
        """Evaluate AI comprehension of end-to-end flow"""
        if not ai_deps:
            return 0.0
        
        flow_indicators = [
            'end-to-end', 'complete', 'workflow', 'process', 'transformation',
            'input', 'output', 'validation', 'generation', 'pipeline'
        ]
        
        flow_scores = []
        for dep in ai_deps:
            dep_text = dep.lower()
            found_indicators = sum(1 for indicator in flow_indicators if indicator in dep_text)
            score = min(found_indicators / 3, 1.0)
            flow_scores.append(score)
        
        return sum(flow_scores) / len(flow_scores)
    
    def _generate_detailed_feedback(self, business_score: float, scenario_score: float,
                                   test_score: float, integration_score: float,
                                   manual_case, ai_result: AIAnalysisResult) -> Dict[str, str]:
        """Generate detailed feedback for improvement"""
        feedback = {}
        
        if business_score < 0.8:
            feedback['business_understanding'] = (
                "AI needs better business context understanding. "
                f"Expected business context about {manual_case.business_context[:100]}... "
                "AI should focus more on WHY the rule exists and business value."
            )
        
        if scenario_score < 0.8:
            feedback['scenario_coverage'] = (
                "AI scenario identification needs improvement. "
                f"Manual analysis identified scenarios like '{manual_case.business_scenario}'. "
                "AI should identify more specific, business-relevant scenarios."
            )
        
        if test_score < 0.8:
            feedback['test_meaningfulness'] = (
                "AI-generated tests need to be more business-meaningful. "
                "Tests should focus on catching real business bugs, not just syntax errors. "
                "Include edge cases and business validation scenarios."
            )
        
        if integration_score < 0.8:
            feedback['integration_awareness'] = (
                "AI needs better understanding of cross-chunk dependencies. "
                f"Manual analysis identified dependencies: {manual_case.cross_chunk_dependencies}. "
                "AI should understand how different parts integrate together."
            )
        
        return feedback


# Example usage for PoC validation
if __name__ == "__main__":
    # Example AI result for testing
    ai_result = AIAnalysisResult(
        business_context="IATA NDC document type standardization for compliance",
        business_scenarios=["Passport validation scenario", "International travel booking"],
        generated_tests=[
            {"test_name": "test_passport_type_p", "input": "P", "expected": "VPT"},
            {"test_name": "test_invalid_input", "input": "INVALID", "expected": ""}
        ],
        dependencies=["helper_template", "main_processing", "validation"],
        extracted_rules=["P -> VPT transformation"],
        domain_understanding="IATA NDC compliance requirements",
        failure_impacts=["Booking rejection", "Compliance failure"]
    )
    
    validator = QualityValidator()
    print("Quality Validator initialized successfully")
    print(f"Quality dimensions: {validator.quality_dimensions}")