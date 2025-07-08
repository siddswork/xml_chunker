"""
Enhanced PoC Validator with Multi-Pass Analysis

This validator uses the multi-pass analysis approach to test whether
progressive context understanding can significantly improve quality scores
and achieve the 90% threshold for proceeding to Phase 2B.
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

from .manual_analysis_baseline import ManualAnalysisBaseline, BaselineTestCase
from .multi_pass_analyzer import MultiPassXSLTAnalyzer, MultiPassResult
from .quality_validator import QualityValidator, QualityScore
from .domain_knowledge import DomainKnowledgeBase


@dataclass
class EnhancedCaseResult:
    """Enhanced test case result with multi-pass details"""
    case_id: str
    case_category: str
    quality_score: QualityScore
    processing_time: float
    meets_threshold: bool
    
    # Multi-pass specific fields
    pass_progression: Dict[str, List[float]]
    final_confidence: float
    context_improvement: float
    multi_pass_details: Dict[str, Any]


@dataclass
class EnhancedPoCResult:
    """Enhanced PoC result with multi-pass analysis insights"""
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
    
    # Multi-pass specific metrics
    context_improvement_average: float
    progressive_learning_evidence: Dict[str, Any]
    multi_pass_vs_single_pass: Dict[str, float]


class EnhancedPoCValidator:
    """Enhanced PoC validator using multi-pass analysis"""
    
    def __init__(self, openai_api_key: str):
        """Initialize with multi-pass analyzer"""
        self.baseline = ManualAnalysisBaseline()
        self.analyzer = MultiPassXSLTAnalyzer(openai_api_key)
        self.quality_validator = QualityValidator()
        self.domain_kb = DomainKnowledgeBase()
        
        # Enhanced success criteria
        self.success_threshold = 0.9  # 90% overall quality match
        self.business_understanding_threshold = 0.85  # 85% business understanding
        self.test_meaningfulness_threshold = 0.90  # 90% test meaningfulness
        self.integration_awareness_threshold = 0.80  # 80% integration awareness (key improvement target)
        
        # Processing configuration
        self.max_concurrent_analyses = 2  # Reduced due to multi-pass complexity
        self.case_timeout = 180  # Increased for multi-pass analysis
    
    async def run_enhanced_validation(self, test_subset: str = "all") -> EnhancedPoCResult:
        """Run enhanced PoC validation with multi-pass analysis"""
        
        print("🚀 Starting Enhanced Multi-Pass PoC Validation...")
        start_time = time.time()
        
        # Get test cases
        test_cases = self._get_test_cases(test_subset)
        print(f"📋 Testing {len(test_cases)} baseline cases with multi-pass analysis")
        
        # Run enhanced validation
        case_results = await self._run_enhanced_validation_cases(test_cases)
        
        # Calculate enhanced results
        enhanced_result = self._calculate_enhanced_results(case_results, time.time() - start_time)
        
        # Generate recommendation
        enhanced_result.recommendation = self._generate_enhanced_recommendation(enhanced_result)
        enhanced_result.improvement_areas = self._identify_enhanced_improvement_areas(case_results)
        enhanced_result.success_stories = self._identify_enhanced_success_stories(case_results)
        
        # Save results
        await self._save_enhanced_results(enhanced_result)
        
        # Print summary
        self._print_enhanced_validation_summary(enhanced_result)
        
        return enhanced_result
    
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
            try:
                return [self.baseline.get_case_by_id(test_subset)]
            except ValueError:
                print(f"⚠️ Unknown test subset '{test_subset}', using all cases")
                return self.baseline.get_baseline_cases()
    
    async def _run_enhanced_validation_cases(self, test_cases: List[BaselineTestCase]) -> List[EnhancedCaseResult]:
        """Run enhanced validation with multi-pass analysis"""
        
        semaphore = asyncio.Semaphore(self.max_concurrent_analyses)
        
        async def process_case(case: BaselineTestCase) -> EnhancedCaseResult:
            async with semaphore:
                return await self._validate_single_case_enhanced(case)
        
        # Process cases with enhanced analysis
        tasks = [process_case(case) for case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        case_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Case {test_cases[i].id} failed: {str(result)}")
                # Create failed case result
                case_results.append(EnhancedCaseResult(
                    case_id=test_cases[i].id,
                    case_category=test_cases[i].category,
                    quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, {}),
                    processing_time=0.0,
                    meets_threshold=False,
                    pass_progression={},
                    final_confidence=0.0,
                    context_improvement=0.0,
                    multi_pass_details={"error": str(result)}
                ))
            else:
                case_results.append(result)
        
        return case_results
    
    async def _validate_single_case_enhanced(self, case: BaselineTestCase) -> EnhancedCaseResult:
        """Validate single case with enhanced multi-pass analysis"""
        
        print(f"🔍 Multi-pass analyzing case: {case.id}")
        case_start_time = time.time()
        
        try:
            # Run multi-pass analysis
            multi_pass_result = await asyncio.wait_for(
                self.analyzer.analyze_with_multi_pass(case.xslt_chunk, case),
                timeout=self.case_timeout
            )
            
            # Score quality match
            quality_score = self.quality_validator.score_quality_match(case, multi_pass_result.final_result)
            
            # Calculate context improvement
            context_improvement = self._calculate_context_improvement(multi_pass_result)
            
            processing_time = time.time() - case_start_time
            
            print(f"✅ Case {case.id}: {quality_score.overall_score:.2f} quality score, {context_improvement:.2f} context improvement ({processing_time:.1f}s)")
            
            return EnhancedCaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=quality_score,
                processing_time=processing_time,
                meets_threshold=quality_score.meets_threshold,
                pass_progression=multi_pass_result.improvement_progression,
                final_confidence=multi_pass_result.final_confidence,
                context_improvement=context_improvement,
                multi_pass_details={
                    "total_passes": len(multi_pass_result.pass_results),
                    "pass_confidence_scores": [p.confidence_score for p in multi_pass_result.pass_results],
                    "final_dependencies_count": len(multi_pass_result.final_result.dependencies),
                    "final_scenarios_count": len(multi_pass_result.final_result.business_scenarios),
                    "final_tests_count": len(multi_pass_result.final_result.generated_tests)
                }
            )
            
        except asyncio.TimeoutError:
            print(f"⏰ Case {case.id} timed out after {self.case_timeout}s")
            return EnhancedCaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, 
                                         {"error": "Multi-pass analysis timed out"}),
                processing_time=self.case_timeout,
                meets_threshold=False,
                pass_progression={},
                final_confidence=0.0,
                context_improvement=0.0,
                multi_pass_details={"error": "Analysis timed out"}
            )
        except Exception as e:
            print(f"❌ Case {case.id} failed: {str(e)}")
            return EnhancedCaseResult(
                case_id=case.id,
                case_category=case.category,
                quality_score=QualityScore(0.0, 0.0, 0.0, 0.0, 0.0, False, 
                                         {"error": str(e)}),
                processing_time=time.time() - case_start_time,
                meets_threshold=False,
                pass_progression={},
                final_confidence=0.0,
                context_improvement=0.0,
                multi_pass_details={"error": str(e)}
            )
    
    def _calculate_context_improvement(self, multi_pass_result: MultiPassResult) -> float:
        """Calculate improvement from first to last pass"""
        
        if len(multi_pass_result.pass_results) < 2:
            return 0.0
        
        first_pass = multi_pass_result.pass_results[0]
        last_pass = multi_pass_result.pass_results[-1]
        
        # Calculate improvement in key areas
        dependency_improvement = (
            len(last_pass.ai_result.dependencies) - len(first_pass.ai_result.dependencies)
        ) / max(len(first_pass.ai_result.dependencies), 1)
        
        scenario_improvement = (
            len(last_pass.ai_result.business_scenarios) - len(first_pass.ai_result.business_scenarios)
        ) / max(len(first_pass.ai_result.business_scenarios), 1)
        
        confidence_improvement = last_pass.confidence_score - first_pass.confidence_score
        
        # Average improvement across dimensions
        return (dependency_improvement + scenario_improvement + confidence_improvement) / 3
    
    def _calculate_enhanced_results(self, case_results: List[EnhancedCaseResult], 
                                  total_time: float) -> EnhancedPoCResult:
        """Calculate enhanced results with multi-pass metrics"""
        
        total_cases = len(case_results)
        passing_cases = sum(1 for result in case_results if result.meets_threshold)
        failing_cases = total_cases - passing_cases
        overall_pass_rate = passing_cases / total_cases if total_cases > 0 else 0.0
        
        # Calculate average scores
        all_scores = [result.quality_score for result in case_results]
        average_scores = {
            'overall': statistics.mean([score.overall_score for score in all_scores]),
            'business_understanding': statistics.mean([score.business_understanding for score in all_scores]),
            'scenario_coverage': statistics.mean([score.scenario_coverage for score in all_scores]),
            'test_meaningfulness': statistics.mean([score.test_meaningfulness for score in all_scores]),
            'integration_awareness': statistics.mean([score.integration_awareness for score in all_scores])
        }
        
        # Calculate multi-pass specific metrics
        context_improvement_average = statistics.mean([result.context_improvement for result in case_results])
        
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
                'context_improvement': result.context_improvement,
                'final_confidence': result.final_confidence,
                'multi_pass_details': result.multi_pass_details,
                'feedback': result.quality_score.detailed_feedback
            })
        
        # Enhanced success criteria
        meets_criteria = (
            overall_pass_rate >= self.success_threshold and
            average_scores['business_understanding'] >= self.business_understanding_threshold and
            average_scores['test_meaningfulness'] >= self.test_meaningfulness_threshold and
            average_scores['integration_awareness'] >= self.integration_awareness_threshold
        )
        
        return EnhancedPoCResult(
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
            success_stories=[],  # Will be filled later
            context_improvement_average=context_improvement_average,
            progressive_learning_evidence=self._analyze_progressive_learning(case_results),
            multi_pass_vs_single_pass=self._compare_to_baseline(average_scores)
        )
    
    def _analyze_progressive_learning(self, case_results: List[EnhancedCaseResult]) -> Dict[str, Any]:
        """Analyze evidence of progressive learning across passes"""
        
        evidence = {
            "cases_showing_improvement": 0,
            "average_confidence_progression": [],
            "dependency_identification_improvement": 0,
            "scenario_enrichment_improvement": 0
        }
        
        for result in case_results:
            if result.context_improvement > 0:
                evidence["cases_showing_improvement"] += 1
            
            # Analyze confidence progression
            if "pass_confidence_scores" in result.multi_pass_details:
                confidence_scores = result.multi_pass_details["pass_confidence_scores"]
                if confidence_scores:
                    evidence["average_confidence_progression"].append(confidence_scores)
        
        # Calculate overall progression metrics
        if evidence["average_confidence_progression"]:
            # Average progression across all cases
            all_progressions = evidence["average_confidence_progression"]
            max_passes = max(len(progression) for progression in all_progressions)
            
            averaged_progression = []
            for pass_idx in range(max_passes):
                pass_scores = [prog[pass_idx] for prog in all_progressions if len(prog) > pass_idx]
                if pass_scores:
                    averaged_progression.append(statistics.mean(pass_scores))
            
            evidence["average_confidence_progression"] = averaged_progression
        
        evidence["improvement_rate"] = evidence["cases_showing_improvement"] / len(case_results) if case_results else 0
        
        return evidence
    
    def _compare_to_baseline(self, average_scores: Dict[str, float]) -> Dict[str, float]:
        """Compare multi-pass results to single-pass baseline"""
        
        # Baseline scores from original PoC (reference values)
        single_pass_baseline = {
            'overall': 0.408,
            'business_understanding': 0.360,
            'scenario_coverage': 0.386,
            'test_meaningfulness': 0.485,
            'integration_awareness': 0.413
        }
        
        improvements = {}
        for dimension, multi_pass_score in average_scores.items():
            baseline_score = single_pass_baseline.get(dimension, 0.0)
            improvement = multi_pass_score - baseline_score
            improvements[f"{dimension}_improvement"] = improvement
            improvements[f"{dimension}_improvement_percent"] = (improvement / baseline_score * 100) if baseline_score > 0 else 0
        
        return improvements
    
    def _generate_enhanced_recommendation(self, result: EnhancedPoCResult) -> Dict[str, str]:
        """Generate enhanced recommendation based on multi-pass results"""
        
        if result.meets_poc_criteria:
            return {
                'decision': 'PROCEED_TO_MICRO_MVPS',
                'confidence': 'HIGH',
                'rationale': f'Enhanced PoC achieved {result.overall_pass_rate:.1%} pass rate with multi-pass analysis demonstrating progressive learning. Context improvement average: {result.context_improvement_average:.2f}.',
                'multi_pass_evidence': f'Progressive learning demonstrated in {result.progressive_learning_evidence["improvement_rate"]:.1%} of cases.',
                'next_steps': [
                    'Begin Phase 2B with validated multi-pass approach',
                    'Integrate multi-pass analysis into agent architecture',
                    'Apply progressive context understanding to all agents',
                    'Scale proven approach to full 6-agent system'
                ]
            }
        elif result.overall_pass_rate >= 0.7:
            return {
                'decision': 'REFINE_MULTI_PASS_APPROACH',
                'confidence': 'MEDIUM',
                'rationale': f'Multi-pass PoC achieved {result.overall_pass_rate:.1%} pass rate with {result.context_improvement_average:.2f} average context improvement. Shows promise but needs refinement.',
                'improvement_potential': 'Multi-pass approach shows clear benefits but needs optimization',
                'next_steps': [
                    'Optimize multi-pass prompting strategies',
                    'Enhance context provider with better dependency mapping',
                    'Improve progressive analysis framework',
                    'Re-run PoC with enhanced multi-pass approach'
                ]
            }
        else:
            return {
                'decision': 'RECONSIDER_APPROACH',
                'confidence': 'LOW',
                'rationale': f'Multi-pass PoC achieved only {result.overall_pass_rate:.1%} pass rate. Even with progressive context, unable to achieve manual analysis quality.',
                'context_analysis': f'Context improvement average: {result.context_improvement_average:.2f} suggests approach has merit but insufficient for goal.',
                'alternative_strategies': [
                    'Hybrid human-AI workflow with multi-pass assistance',
                    'Domain-specific fine-tuning approach',
                    'Enhanced domain knowledge integration',
                    'Manual analysis with AI augmentation'
                ]
            }
    
    def _identify_enhanced_improvement_areas(self, case_results: List[EnhancedCaseResult]) -> List[str]:
        """Identify improvement areas specific to multi-pass analysis"""
        
        improvement_areas = []
        
        # Analyze multi-pass specific issues
        low_improvement_cases = [r for r in case_results if r.context_improvement < 0.1]
        if len(low_improvement_cases) > len(case_results) * 0.5:
            improvement_areas.append("Multi-pass context improvement insufficient - need better progressive prompting")
        
        # Analyze confidence progression
        low_confidence_cases = [r for r in case_results if r.final_confidence < 0.7]
        if len(low_confidence_cases) > len(case_results) * 0.3:
            improvement_areas.append("Final confidence scores too low - need enhanced context understanding")
        
        # Analyze integration awareness improvement
        integration_scores = [r.quality_score.integration_awareness for r in case_results]
        avg_integration = statistics.mean(integration_scores) if integration_scores else 0
        if avg_integration < self.integration_awareness_threshold:
            improvement_areas.append(f"Integration awareness ({avg_integration:.1%}) still below threshold - need better dependency analysis")
        
        return improvement_areas
    
    def _identify_enhanced_success_stories(self, case_results: List[EnhancedCaseResult]) -> List[str]:
        """Identify success stories from enhanced analysis"""
        
        success_stories = []
        
        # High-performing cases
        high_scoring_cases = [r for r in case_results if r.quality_score.overall_score >= 0.85]
        for case in high_scoring_cases:
            success_stories.append(
                f"Case {case.case_id}: Achieved {case.quality_score.overall_score:.1%} with {case.context_improvement:.2f} context improvement"
            )
        
        # Cases showing significant improvement
        high_improvement_cases = [r for r in case_results if r.context_improvement >= 0.5]
        for case in high_improvement_cases:
            success_stories.append(
                f"Case {case.case_id}: Demonstrated {case.context_improvement:.2f} context improvement through multi-pass analysis"
            )
        
        return success_stories
    
    async def _save_enhanced_results(self, result: EnhancedPoCResult):
        """Save enhanced PoC results"""
        
        results_dir = Path("poc_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"enhanced_poc_validation_{timestamp}.json"
        
        # Convert result to dict for JSON serialization
        result_dict = asdict(result)
        
        with open(results_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        print(f"💾 Enhanced results saved to: {results_file}")
    
    def _print_enhanced_validation_summary(self, result: EnhancedPoCResult):
        """Print enhanced validation summary"""
        
        print("\n" + "="*80)
        print("🎯 ENHANCED MULTI-PASS PoC VALIDATION SUMMARY")
        print("="*80)
        
        print(f"📊 Overall Results:")
        print(f"   • Pass Rate: {result.overall_pass_rate:.1%} ({result.passing_cases}/{result.total_cases_tested} cases)")
        print(f"   • PoC Criteria Met: {'✅ YES' if result.meets_poc_criteria else '❌ NO'}")
        print(f"   • Context Improvement Average: {result.context_improvement_average:.2f}")
        print(f"   • Processing Time: {result.processing_time:.1f} seconds")
        
        print(f"\n📈 Quality Dimension Scores (vs Single-Pass Baseline):")
        for dimension, score in result.average_scores.items():
            status = "✅" if score >= 0.8 else "⚠️" if score >= 0.7 else "❌"
            improvement_key = f"{dimension}_improvement"
            improvement = result.multi_pass_vs_single_pass.get(improvement_key, 0)
            print(f"   • {dimension.replace('_', ' ').title()}: {score:.1%} (+{improvement:.3f}) {status}")
        
        print(f"\n🔄 Progressive Learning Evidence:")
        evidence = result.progressive_learning_evidence
        print(f"   • Cases Showing Improvement: {evidence['improvement_rate']:.1%}")
        print(f"   • Cases with Context Gains: {evidence['cases_showing_improvement']}")
        if evidence['average_confidence_progression']:
            progression = evidence['average_confidence_progression']
            print(f"   • Confidence Progression: {progression[0]:.2f} → {progression[-1]:.2f}")
        
        print(f"\n🎯 Enhanced Recommendation:")
        rec = result.recommendation
        print(f"   • Decision: {rec['decision']}")
        print(f"   • Confidence: {rec['confidence']}")
        print(f"   • Rationale: {rec['rationale']}")
        
        if result.improvement_areas:
            print(f"\n🔧 Multi-Pass Specific Improvements:")
            for area in result.improvement_areas:
                print(f"   • {area}")
        
        if result.success_stories:
            print(f"\n🌟 Multi-Pass Success Stories:")
            for story in result.success_stories:
                print(f"   • {story}")
        
        print("\n" + "="*80)
        
        # Final decision with multi-pass context
        if result.meets_poc_criteria:
            print("🚀 PROCEED TO PHASE 2B: Multi-Pass Approach Validated!")
        elif result.overall_pass_rate >= 0.7:
            print("🔧 REFINE MULTI-PASS APPROACH: Promising but needs optimization")
        else:
            print("🤔 RECONSIDER: Multi-pass insufficient, explore alternatives")
        
        print("="*80)


# Main execution function
async def run_enhanced_poc_validation(openai_api_key: str, test_subset: str = "all"):
    """
    Main function to run enhanced PoC validation with multi-pass analysis
    """
    
    validator = EnhancedPoCValidator(openai_api_key)
    result = await validator.run_enhanced_validation(test_subset)
    
    return result


if __name__ == "__main__":
    import sys
    import os
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Get test subset from command line
    test_subset = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print("🚀 Starting Enhanced Multi-Pass PoC Validation...")
    
    # Run enhanced validation
    result = asyncio.run(run_enhanced_poc_validation(api_key, test_subset))
    
    print(f"\n✅ Enhanced PoC Validation Complete!")
    print(f"📊 Final Decision: {result.recommendation['decision']}")