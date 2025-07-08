#!/usr/bin/env python3
"""
Enhanced PoC Validation Runner with Multi-Pass Analysis

This script runs the enhanced PoC validation that uses multi-pass analysis
to overcome the limitations of single-chunk analysis identified in the
original PoC results.

Expected improvements:
- Integration awareness: 41% → 80%+ (with progressive context)
- Business understanding: 36% → 70%+ (with workflow context)
- Overall quality: 41% → 75%+ (approaching refinement threshold)

Usage:
    python run_enhanced_poc.py [test_subset]
    
    test_subset options:
    - "all" (default): Run all 15 baseline test cases
    - "helper": Run only helper template cases (5 cases)  
    - "main": Run only main template cases (5 cases)
    - "integration": Run only integration cases (5 cases)
    - specific case ID: Run single case (e.g., "vmf1_passport_transformation")

Environment Variables:
    OPENAI_API_KEY: Required OpenAI API key for LLM integration

Examples:
    # Run all test cases with multi-pass analysis
    python run_enhanced_poc.py
    
    # Run only helper template cases
    python run_enhanced_poc.py helper
    
    # Run single test case
    python run_enhanced_poc.py vmf1_passport_transformation
    
    # Compare with original results
    python run_poc.py > original_results.txt
    python run_enhanced_poc.py > enhanced_results.txt
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not found. Install with: pip install python-dotenv")
    print("Or manually export OPENAI_API_KEY environment variable")

from agentic_test_gen.poc import run_enhanced_poc_validation


async def main():
    """Main CLI function for enhanced PoC validation"""
    
    print("🎯 Enhanced Multi-Pass PoC Validation for Agentic XSLT Analysis System")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        print("Please set the OPENAI_API_KEY environment variable.")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("python run_enhanced_poc.py")
        sys.exit(1)
    
    # Get test subset from command line
    test_subset = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print(f"📋 Enhanced Test Configuration:")
    print(f"   • Analysis Approach: Multi-Pass (Isolated → Contextual → Full Workflow)")
    print(f"   • Test Subset: {test_subset}")
    print(f"   • API Key: {'✅ Configured' if api_key else '❌ Missing'}")
    print(f"   • Expected Improvements: Integration awareness, business understanding")
    
    # Validate test subset
    valid_subsets = ["all", "helper", "main", "integration"]
    if test_subset not in valid_subsets and not test_subset.startswith(("vmf", "ua_", "multi_", "phone_", "address_", "contact_", "end_", "error_", "conditional_", "performance_", "compliance_", "helper_")):
        print(f"⚠️  Unknown test subset '{test_subset}'")
        print(f"Valid options: {', '.join(valid_subsets)} or specific case ID")
        print("Proceeding with 'all' test cases...")
        test_subset = "all"
    
    print(f"\n🚀 Starting Enhanced Multi-Pass PoC Validation...")
    print("This approach analyzes each chunk in three progressive passes:")
    print("   1️⃣ Isolated Analysis: Understand chunk in isolation")
    print("   2️⃣ Contextual Analysis: Add immediate dependencies")
    print("   3️⃣ Full Workflow Analysis: Complete business workflow context")
    print("\nTarget: Significant improvement in integration awareness and business understanding")
    
    try:
        # Run enhanced PoC validation
        result = await run_enhanced_poc_validation(api_key, test_subset)
        
        # Print comparison with original PoC results
        print(f"\n📊 MULTI-PASS vs SINGLE-PASS COMPARISON:")
        print(f"{'Dimension':<25} {'Single-Pass':<12} {'Multi-Pass':<12} {'Improvement':<12}")
        print(f"{'-'*25} {'-'*12} {'-'*12} {'-'*12}")
        
        # Original baseline scores (from previous PoC)
        baseline_scores = {
            'overall': 0.408,
            'business_understanding': 0.360,
            'scenario_coverage': 0.386,
            'test_meaningfulness': 0.485,
            'integration_awareness': 0.413
        }
        
        for dimension in baseline_scores:
            baseline = baseline_scores[dimension]
            enhanced = result.average_scores[dimension]
            improvement = enhanced - baseline
            improvement_pct = (improvement / baseline * 100) if baseline > 0 else 0
            
            print(f"{dimension.replace('_', ' ').title():<25} {baseline:<12.3f} {enhanced:<12.3f} {improvement:+.3f} ({improvement_pct:+.1f}%)")
        
        print(f"\n🎯 ENHANCED PoC FINAL RESULT:")
        if result.meets_poc_criteria:
            print(f"✅ SUCCESS: Enhanced multi-pass validation passed!")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Context Improvement: {result.context_improvement_average:.2f}")
            print(f"   • Decision: Proceed to Phase 2B micro-MVPs")
            print(f"   • Confidence: High")
            print(f"   • Approach: Multi-pass analysis validated")
        elif result.overall_pass_rate >= 0.7:
            print(f"⚠️  PARTIAL SUCCESS: Multi-pass shows improvement but needs refinement")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Context Improvement: {result.context_improvement_average:.2f}")
            print(f"   • Decision: Refine multi-pass approach")
            print(f"   • Action: Optimize progressive analysis and re-test")
        else:
            print(f"❌ INSUFFICIENT: Multi-pass improvement not enough")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Context Improvement: {result.context_improvement_average:.2f}")
            print(f"   • Decision: Consider alternative approaches")
            print(f"   • Action: Explore hybrid or different strategies")
        
        print(f"\n📈 Progressive Learning Evidence:")
        evidence = result.progressive_learning_evidence
        print(f"   • Cases Showing Context Improvement: {evidence['improvement_rate']:.1%}")
        print(f"   • Total Cases with Gains: {evidence['cases_showing_improvement']}")
        
        if evidence.get('average_confidence_progression'):
            progression = evidence['average_confidence_progression']
            print(f"   • Confidence Progression: {progression[0]:.2f} → {progression[-1]:.2f}")
        
        print(f"\n📊 Detailed Results:")
        print(f"   • Cases Tested: {result.total_cases_tested}")
        print(f"   • Cases Passed: {result.passing_cases}")
        print(f"   • Processing Time: {result.processing_time:.1f}s")
        print(f"   • Integration Awareness: {result.average_scores['integration_awareness']:.1%}")
        print(f"   • Business Understanding: {result.average_scores['business_understanding']:.1%}")
        
        # Show key improvements
        if result.improvement_areas:
            print(f"\n🔧 Multi-Pass Specific Improvements Needed:")
            for area in result.improvement_areas:
                print(f"   • {area}")
        
        if result.success_stories:
            print(f"\n🌟 Multi-Pass Success Stories:")
            for story in result.success_stories[:3]:  # Show top 3
                print(f"   • {story}")
        
        return result.meets_poc_criteria
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Enhanced PoC validation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Enhanced PoC validation failed with error: {str(e)}")
        print(f"Check that all dependencies are installed: pip install -r poc_requirements.txt")
        return False


def show_help():
    """Show help information"""
    print(__doc__)


if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        sys.exit(0)
    
    # Run the enhanced PoC validation
    success = asyncio.run(main())
    
    # Print final recommendation
    print(f"\n🎯 RECOMMENDATION:")
    if success:
        print("✅ PROCEED: Multi-pass approach validates the concept")
        print("   Next: Begin Phase 2B with multi-pass agent architecture")
    else:
        print("🔧 ITERATE: Continue refining the multi-pass approach")
        print("   Next: Analyze results and optimize progressive context understanding")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)