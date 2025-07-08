"""
PoC Validation Orchestrator

This module orchestrates the complete PoC validation process:
1. Load manual analysis baseline cases
2. Run minimal XSLT analyzer on each case
3. Score quality match using 4-dimensional framework
4. Generate comprehensive validation report
5. Make go/no-go decision for Phase 2B

The PoC must achieve 90%+ quality match to proceed with micro-MVP implementation.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

from .manual_analysis_baseline import ManualAnalysisBaseline, BaselineTestCase
from .minimal_xslt_analyzer import MinimalXSLTAnalyzer
from .quality_validator import QualityValidator, QualityScore
from .domain_knowledge import DomainKnowledgeBase


@dataclass
class PoCResult:
    """Complete PoC validation result"""
    overall_pass_rate: float
    meets_poc_criteria: bool
    total_cases_tested: int
    passing_cases: int
    failing_cases: int
    average_scores: Dict[str, float]
    detailed_results: List[Dict[str, Any]]
    processing_time: float
    recommendation: Dict[str, str]
    improvement_areas: List[str]
    success_stories: List[str]


@dataclass
class CaseResult:
    """Individual test case result"""
    case_id: str
    case_category: str
    quality_score: QualityScore
    processing_time: float
    ai_analysis_preview: str
    meets_threshold: bool


class PoCValidator:
    """Main PoC validation orchestrator"""
    
    def __init__(self, openai_api_key: str):
        """Initialize PoC validator with all required components"""
        self.baseline = ManualAnalysisBaseline()
        self.analyzer = MinimalXSLTAnalyzer(openai_api_key)
        self.quality_validator = QualityValidator()
        self.domain_kb = DomainKnowledgeBase()
        
        # PoC success criteria
        self.success_threshold = 0.9  # 90% overall quality match
        self.business_understanding_threshold = 0.85  # 85% business understanding
        self.test_meaningfulness_threshold = 0.90  # 90% test meaningfulness
        
        # Processing configuration
        self.max_concurrent_analyses = 3  # Limit concurrent LLM calls
        self.case_timeout = 120  # seconds per case
        
    async def run_comprehensive_validation(self, test_subset: str = "all") -> PoCResult:
        """
        Run comprehensive PoC validation
        
        Args:
            test_subset: "all", "helper", "main", "integration", or specific case ID
        """
        
        print("🚀 Starting PoC Validation...")
        start_time = time.time()
        
        # Get test cases based on subset
        test_cases = self._get_test_cases(test_subset)
        print(f"📋 Testing {len(test_cases)} baseline cases")
        
        # Run validation on all cases
        case_results = await self._run_validation_cases(test_cases)
        
        # Calculate overall results
        overall_result = self._calculate_overall_results(case_results, time.time() - start_time)
        
        # Generate recommendation
        overall_result.recommendation = self._generate_recommendation(overall_result)
        overall_result.improvement_areas = self._identify_improvement_areas(case_results)
        overall_result.success_stories = self._identify_success_stories(case_results)
        
        # Save results
        await self._save_results(overall_result)
        
        # Print summary
        self._print_validation_summary(overall_result)
        
        return overall_result
    
    def _get_test_cases(self, test_subset: str) -> List[BaselineTestCase]:
        """Get test cases based on subset specification"""
        
        if test_subset == "all":
            return self.baseline.get_baseline_cases()
        elif test_subset == "helper":
            return self.baseline.get_helper_template_cases()
        elif test_subset == "main":
            return self.baseline.get_main_template_cases()
        elif test_subset == "integration":
            return self.baseline.get_integration_cases()
        else:
            # Assume it's a specific case ID
            try:
                return [self.baseline.get_case_by_id(test_subset)]
            except ValueError:
                print(f"⚠️ Unknown test subset '{test_subset}', using all cases")
                return self.baseline.get_baseline_cases()
    
    async def _run_validation_cases(self, test_cases: List[BaselineTestCase]) -> List[CaseResult]:
        """Run validation on all test cases with concurrency control"""
        
        semaphore = asyncio.Semaphore(self.max_concurrent_analyses)
        
        async def process_case(case: BaselineTestCase) -> CaseResult:
            async with semaphore:
                return await self._validate_single_case(case)
        
        # Process all cases concurrently (with limit)
        tasks = [process_case(case) for case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to case results
        case_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Case {test_cases[i].id} failed: {str(result)}")
                # Create failed case result
                case_results.append(CaseResult(
                    case_id=test_cases[i].id,
                    case_category=test_cases[i].category,
                    quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, {}),
                    processing_time=0.0,
                    ai_analysis_preview="Analysis failed",
                    meets_threshold=False
                ))
            else:
                case_results.append(result)
        
        return case_results
    
    async def _validate_single_case(self, case: BaselineTestCase) -> CaseResult:
        """Validate a single baseline case"""
        
        print(f"🔍 Analyzing case: {case.id}")
        case_start_time = time.time()
        
        try:
            # Run AI analysis with timeout
            ai_result = await asyncio.wait_for(
                self.analyzer.analyze_with_business_context(case.xslt_chunk, case),
                timeout=self.case_timeout
            )
            
            # Score quality match
            quality_score = self.quality_validator.score_quality_match(case, ai_result)
            
            # Create preview of AI analysis
            ai_preview = f"Business Context: {ai_result.business_context[:100]}..."
            
            processing_time = time.time() - case_start_time
            
            print(f"✅ Case {case.id}: {quality_score.overall_score:.2f} quality score ({processing_time:.1f}s)")
            
            return CaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=quality_score,
                processing_time=processing_time,
                ai_analysis_preview=ai_preview,
                meets_threshold=quality_score.meets_threshold
            )
            
        except asyncio.TimeoutError:
            print(f"⏰ Case {case.id} timed out after {self.case_timeout}s")
            return CaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, 
                                         {"error": "Analysis timed out"}),
                processing_time=self.case_timeout,
                ai_analysis_preview="Analysis timed out",
                meets_threshold=False
            )
        except Exception as e:
            print(f"❌ Case {case.id} failed: {str(e)}")
            return CaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, 
                                         {"error": str(e)}),
                processing_time=time.time() - case_start_time,
                ai_analysis_preview=f"Analysis failed: {str(e)}",
                meets_threshold=False
            )
    
    def _calculate_overall_results(self, case_results: List[CaseResult], 
                                  total_time: float) -> PoCResult:
        """Calculate overall PoC results from individual case results"""
        
        total_cases = len(case_results)
        passing_cases = sum(1 for result in case_results if result.meets_threshold)
        failing_cases = total_cases - passing_cases
        overall_pass_rate = passing_cases / total_cases if total_cases > 0 else 0.0
        
        # Calculate average scores across dimensions
        all_scores = [result.quality_score for result in case_results]
        average_scores = {
            'overall': statistics.mean([score.overall_score for score in all_scores]),
            'business_understanding': statistics.mean([score.business_understanding for score in all_scores]),
            'scenario_coverage': statistics.mean([score.scenario_coverage for score in all_scores]),
            'test_meaningfulness': statistics.mean([score.test_meaningfulness for score in all_scores]),
            'integration_awareness': statistics.mean([score.integration_awareness for score in all_scores])
        }
        
        # Create detailed results
        detailed_results = []
        for result in case_results:
            detailed_results.append({
                'case_id': result.case_id,
                'category': result.case_category,
                'overall_score': result.quality_score.overall_score,
                'business_understanding': result.quality_score.business_understanding,
                'scenario_coverage': result.quality_score.scenario_coverage,
                'test_meaningfulness': result.quality_score.test_meaningfulness,
                'integration_awareness': result.quality_score.integration_awareness,
                'meets_threshold': result.meets_threshold,
                'processing_time': result.processing_time,
                'feedback': result.quality_score.detailed_feedback
            })
        
        # Determine if PoC criteria are met
        meets_criteria = (
            overall_pass_rate >= self.success_threshold and
            average_scores['business_understanding'] >= self.business_understanding_threshold and
            average_scores['test_meaningfulness'] >= self.test_meaningfulness_threshold
        )
        
        return PoCResult(
            overall_pass_rate=overall_pass_rate,
            meets_poc_criteria=meets_criteria,
            total_cases_tested=total_cases,
            passing_cases=passing_cases,
            failing_cases=failing_cases,
            average_scores=average_scores,
            detailed_results=detailed_results,
            processing_time=total_time,
            recommendation={},  # Will be filled later
            improvement_areas=[],  # Will be filled later
            success_stories=[]  # Will be filled later
        )
    
    def _generate_recommendation(self, overall_result: PoCResult) -> Dict[str, str]:
        """Generate recommendation based on PoC results"""
        
        if overall_result.meets_poc_criteria:
            return {
                'decision': 'PROCEED_TO_MICRO_MVPS',
                'confidence': 'HIGH',
                'rationale': f'PoC achieved {overall_result.overall_pass_rate:.1%} pass rate with strong business understanding. Agent demonstrates ability to match manual analysis quality.',
                'next_steps': [
                    'Begin Phase 2B micro-MVP implementation',
                    'Scale proven approach to full 6-agent system',
                    'Apply PoC learnings to agent design',
                    'Maintain quality gates throughout development'
                ]
            }
        elif overall_result.overall_pass_rate >= 0.7:
            return {
                'decision': 'REFINE_APPROACH',
                'confidence': 'MEDIUM',
                'rationale': f'PoC achieved {overall_result.overall_pass_rate:.1%} pass rate. Shows promise but needs refinement before scaling.',
                'focus_areas': self._identify_refinement_areas(overall_result),
                'next_steps': [
                    'Enhance weak areas identified in analysis',
                    'Improve domain knowledge integration',
                    'Refine business context prompting strategies',
                    'Re-run PoC validation with improvements'
                ]
            }
        else:
            return {
                'decision': 'RETHINK_APPROACH',
                'confidence': 'LOW',
                'rationale': f'PoC achieved only {overall_result.overall_pass_rate:.1%} pass rate. Current approach unlikely to achieve manual analysis quality.',
                'alternative_strategies': [
                    'Hybrid human-AI workflow approach',
                    'Enhanced domain knowledge integration',
                    'Alternative LLM models or approaches',
                    'Manual analysis with AI assistance'
                ],
                'next_steps': [
                    'Evaluate alternative approaches',
                    'Consider hybrid human-AI workflow',
                    'Investigate different LLM strategies',
                    'Reassess project approach and timeline'
                ]
            }
    
    def _identify_refinement_areas(self, overall_result: PoCResult) -> List[str]:
        """Identify specific areas that need refinement"""
        
        refinement_areas = []
        scores = overall_result.average_scores
        
        if scores['business_understanding'] < 0.8:
            refinement_areas.append('Business context understanding needs improvement')
        
        if scores['scenario_coverage'] < 0.8:
            refinement_areas.append('Business scenario identification needs enhancement')
        
        if scores['test_meaningfulness'] < 0.8:
            refinement_areas.append('Test meaningfulness and business relevance needs work')
        
        if scores['integration_awareness'] < 0.8:
            refinement_areas.append('Cross-chunk dependency understanding needs development')
        
        return refinement_areas
    
    def _identify_improvement_areas(self, case_results: List[CaseResult]) -> List[str]:
        """Identify specific improvement areas from detailed results"""
        
        improvement_areas = []
        
        # Analyze feedback from failing cases
        failing_cases = [result for result in case_results if not result.meets_threshold]
        
        feedback_categories = {}
        for case in failing_cases:
            for category, feedback in case.quality_score.detailed_feedback.items():
                if category not in feedback_categories:
                    feedback_categories[category] = []
                feedback_categories[category].append(feedback)
        
        # Identify common improvement themes
        for category, feedbacks in feedback_categories.items():
            if len(feedbacks) >= 2:  # Common issue
                improvement_areas.append(f"{category.replace('_', ' ').title()}: Common issue across multiple cases")
        
        return improvement_areas
    
    def _identify_success_stories(self, case_results: List[CaseResult]) -> List[str]:
        """Identify successful cases for learning"""
        
        success_stories = []
        
        # Find cases with high scores
        high_scoring_cases = [
            result for result in case_results 
            if result.quality_score.overall_score >= 0.95
        ]
        
        for case in high_scoring_cases:
            success_stories.append(
                f"Case {case.case_id} ({case.case_category}): Achieved {case.quality_score.overall_score:.1%} quality match"
            )
        
        return success_stories
    
    async def _save_results(self, result: PoCResult):
        """Save PoC results to file"""
        
        results_dir = Path("poc_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"poc_validation_{timestamp}.json"
        
        # Convert result to dict for JSON serialization
        result_dict = asdict(result)
        
        with open(results_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
    
    def _print_validation_summary(self, result: PoCResult):
        """Print comprehensive validation summary"""
        
        print("\n" + "="*80)
        print("🎯 PoC VALIDATION SUMMARY")
        print("="*80)
        
        print(f"📊 Overall Results:")
        print(f"   • Pass Rate: {result.overall_pass_rate:.1%} ({result.passing_cases}/{result.total_cases_tested} cases)")
        print(f"   • PoC Criteria Met: {'✅ YES' if result.meets_poc_criteria else '❌ NO'}")
        print(f"   • Processing Time: {result.processing_time:.1f} seconds")
        
        print(f"\n📈 Quality Dimension Scores:")
        for dimension, score in result.average_scores.items():
            status = "✅" if score >= 0.8 else "⚠️" if score >= 0.7 else "❌"
            print(f"   • {dimension.replace('_', ' ').title()}: {score:.1%} {status}")
        
        print(f"\n🎯 Recommendation:")
        rec = result.recommendation
        print(f"   • Decision: {rec['decision']}")
        print(f"   • Confidence: {rec['confidence']}")
        print(f"   • Rationale: {rec['rationale']}")
        
        if result.improvement_areas:
            print(f"\n🔧 Improvement Areas:")
            for area in result.improvement_areas:
                print(f"   • {area}")
        
        if result.success_stories:
            print(f"\n🌟 Success Stories:")
            for story in result.success_stories:
                print(f"   • {story}")
        
        print("\n" + "="*80)
        
        # Final decision
        if result.meets_poc_criteria:
            print("🚀 PROCEED TO PHASE 2B: Micro-MVP Implementation")
        elif result.overall_pass_rate >= 0.7:
            print("🔧 REFINE APPROACH: Improvements needed before scaling")
        else:
            print("🤔 RETHINK APPROACH: Consider alternative strategies")
        
        print("="*80)


# Main execution function
async def run_poc_validation(openai_api_key: str, test_subset: str = "all"):
    """
    Main function to run PoC validation
    
    Args:
        openai_api_key: OpenAI API key for LLM integration
        test_subset: Which test cases to run ("all", "helper", "main", "integration")
    """
    
    validator = PoCValidator(openai_api_key)
    result = await validator.run_comprehensive_validation(test_subset)
    
    return result


# Command line interface
if __name__ == "__main__":
    import sys
    import os
    
    # Get API key from environment or command line
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Get test subset from command line
    test_subset = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print("🚀 Starting PoC Validation...")
    print(f"📋 Test subset: {test_subset}")
    print(f"🔑 API key configured: {'Yes' if api_key else 'No'}")
    
    # Run validation
    result = asyncio.run(run_poc_validation(api_key, test_subset))
    
    print(f"\n✅ PoC Validation Complete!")
    print(f"📊 Final Decision: {result.recommendation['decision']}")