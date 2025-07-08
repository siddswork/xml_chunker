#!/usr/bin/env python3
"""
PoC Validation Runner

Simple CLI script to run the Proof of Concept validation.
This validates whether our AI approach can match manual analysis quality.

Usage:
    python run_poc.py [test_subset]
    
    test_subset options:
    - "all" (default): Run all 15 baseline test cases
    - "helper": Run only helper template cases (5 cases)  
    - "main": Run only main template cases (5 cases)
    - "integration": Run only integration cases (5 cases)
    - specific case ID: Run single case (e.g., "vmf1_passport_transformation")

Environment Variables:
    OPENAI_API_KEY: Required OpenAI API key for LLM integration

Examples:
    # Run all test cases
    python run_poc.py
    
    # Run only helper template cases
    python run_poc.py helper
    
    # Run single test case
    python run_poc.py vmf1_passport_transformation
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

from agentic_test_gen.poc import run_poc_validation


async def main():
    """Main CLI function"""
    
    print("🎯 PoC Validation for Agentic XSLT Analysis System")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        print("Please set the OPENAI_API_KEY environment variable.")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("python run_poc.py")
        sys.exit(1)
    
    # Get test subset from command line
    test_subset = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print(f"📋 Test Configuration:")
    print(f"   • Test Subset: {test_subset}")
    print(f"   • API Key: {'✅ Configured' if api_key else '❌ Missing'}")
    
    # Validate test subset
    valid_subsets = ["all", "helper", "main", "integration"]
    if test_subset not in valid_subsets and not test_subset.startswith("vmf"):
        print(f"⚠️  Unknown test subset '{test_subset}'")
        print(f"Valid options: {', '.join(valid_subsets)} or specific case ID")
        print("Proceeding with 'all' test cases...")
        test_subset = "all"
    
    print(f"\n🚀 Starting PoC Validation...")
    print("This will validate if our AI approach can match manual analysis quality.")
    print("Target: 90%+ quality match with manual baseline to proceed to Phase 2B.")
    
    try:
        # Run PoC validation
        result = await run_poc_validation(api_key, test_subset)
        
        # Print final summary
        print(f"\n🎯 FINAL RESULT:")
        if result.meets_poc_criteria:
            print(f"✅ SUCCESS: PoC validation passed!")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Decision: Proceed to Phase 2B micro-MVPs")
            print(f"   • Confidence: High")
        elif result.overall_pass_rate >= 0.7:
            print(f"⚠️  PARTIAL SUCCESS: PoC shows promise but needs refinement")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Decision: Refine approach before scaling")
            print(f"   • Action: Address improvement areas and re-test")
        else:
            print(f"❌ FAILURE: PoC validation failed")
            print(f"   • Quality Match: {result.overall_pass_rate:.1%}")
            print(f"   • Decision: Rethink approach")
            print(f"   • Action: Consider alternative strategies")
        
        print(f"\n📊 Detailed Results:")
        print(f"   • Cases Tested: {result.total_cases_tested}")
        print(f"   • Cases Passed: {result.passing_cases}")
        print(f"   • Processing Time: {result.processing_time:.1f}s")
        print(f"   • Business Understanding: {result.average_scores['business_understanding']:.1%}")
        print(f"   • Test Meaningfulness: {result.average_scores['test_meaningfulness']:.1%}")
        
        return result.meets_poc_criteria
        
    except KeyboardInterrupt:
        print(f"\n⏹️  PoC validation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ PoC validation failed with error: {str(e)}")
        return False


def show_help():
    """Show help information"""
    print(__doc__)


if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        sys.exit(0)
    
    # Run the PoC validation
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)