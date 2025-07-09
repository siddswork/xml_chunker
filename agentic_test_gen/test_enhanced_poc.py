#!/usr/bin/env python3
"""
Test script for Enhanced Interactive XSLT PoC with limited exploration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not found")

from enhanced_interactive_poc import EnhancedXSLTExplorer

async def test_enhanced_poc():
    """Test the enhanced PoC with limited exploration"""
    
    print("🧪 Testing Enhanced XSLT Exploration PoC")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        return False
    
    # Set up paths
    xslt_path = "/home/sidd/dev/xml_wizard/resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt"
    
    if not Path(xslt_path).exists():
        print(f"❌ ERROR: XSLT file not found: {xslt_path}")
        return False
    
    try:
        # Initialize enhanced explorer with limited coverage for testing
        explorer = EnhancedXSLTExplorer(api_key, xslt_path, target_coverage=0.05)  # 5% for testing
        
        # Start exploration
        result = await explorer.start_enhanced_exploration()
        
        print(f"\n🎯 TEST RESULT:")
        print(f"=" * 50)
        print(result)
        
        # Check results
        final_summary = explorer.get_understanding_summary()["summary"]
        
        print(f"\n📊 TEST ASSESSMENT:")
        print(f"   • Chunks Explored: {final_summary['chunks_explored']}/{final_summary['target_chunks']} ({final_summary['progress_percentage']:.1f}%)")
        print(f"   • Mapping Specifications: {final_summary['mapping_specifications']}")
        print(f"   • Template Analyses: {final_summary['template_analyses']}")
        print(f"   • LLM Insights: {len(explorer.llm_insights)}")
        print(f"   • Understanding Evolution: {len(explorer.understanding_evolution)}")
        print(f"   • Validation Milestones: {len(explorer.validation_metrics['evolution_milestones'])}")
        print(f"   • Total Cost: ${explorer.cost_tracker['cumulative_cost_usd']:.6f}")
        
        # Test validation metrics
        validation_metrics = explorer.get_validation_metrics()
        print(f"\n🔍 VALIDATION METRICS:")
        print(f"   • Understanding Building: {validation_metrics['validation_summary']['understanding_building']}")
        print(f"   • Mapping Trend: {validation_metrics['trends']['mapping_extraction']}")
        print(f"   • Understanding Trend: {validation_metrics['trends']['understanding_depth']}")
        
        # Validate success
        success = (
            final_summary['chunks_explored'] > 0 and
            (final_summary['mapping_specifications'] > 0 or len(explorer.llm_insights) > 0) and
            explorer.cost_tracker['cumulative_cost_usd'] < 0.50  # Reasonable cost for testing
        )
        
        if success:
            print(f"\n✅ TEST SUCCESS!")
            print(f"🎉 Enhanced PoC is working correctly")
            print(f"📁 Results saved to: {explorer.results_dir}")
        else:
            print(f"\n❌ TEST FAILED")
            print(f"🔧 Check function calls and understanding extraction")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_poc())
    sys.exit(0 if success else 1)