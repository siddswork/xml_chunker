#!/usr/bin/env python3
"""
Command Line Interface for Agentic XSLT Test Generator

Simple CLI to test the agentic system with Phase 1 implementation.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_test_gen.system import AgenticXSLTTestGenerator
from agentic_test_gen.config.settings import AgenticSystemSettings


async def main():
    """Main CLI function."""
    
    print("🤖 Agentic XSLT Test Generator - Phase 1 Demo")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Demo file paths (using the existing test files)
    base_dir = Path(__file__).parent.parent
    
    xslt_file = base_dir / "resource" / "orderCreate" / "xslt" / "OrderCreate_MapForce_Full.xslt"
    input_xsd = base_dir / "resource" / "orderCreate" / "input_xsd" / "AMA_ConnectivityLayerRQ.xsd"
    output_xsd = base_dir / "resource" / "orderCreate" / "output_xsd" / "OrderCreateRQ.xsd"
    
    # Check if files exist
    if not xslt_file.exists():
        print(f"❌ XSLT file not found: {xslt_file}")
        print("Please ensure the test files are available.")
        return
    
    print(f"📁 XSLT File: {xslt_file}")
    print(f"📁 Input XSD: {input_xsd}")
    print(f"📁 Output XSD: {output_xsd}")
    print()
    
    # Initialize settings
    settings = AgenticSystemSettings()
    settings.openai_api_key = api_key
    settings.debug_mode = True
    settings.verbose_logging = True
    
    # Initialize system
    print("🚀 Initializing Agentic System...")
    system = AgenticXSLTTestGenerator(settings)
    
    try:
        # Generate test cases
        print("⚡ Starting test case generation...")
        print("📊 Target: 125+ comprehensive test cases")
        print()
        
        results = await system.generate_test_cases(
            xslt_file=str(xslt_file),
            input_xsd_file=str(input_xsd),
            output_xsd_file=str(output_xsd),
            target_test_count=125
        )
        
        # Display results
        print("✅ Test case generation completed!")
        print()
        print("📈 Results Summary:")
        print(f"   Status: {results['status']}")
        print(f"   Execution Time: {results['execution_time_seconds']:.2f} seconds")
        print(f"   Phases Completed: {results['statistics']['phases_completed']}/{results['statistics']['total_phases']}")
        print(f"   Agents Executed: {', '.join(results['statistics']['agents_executed'])}")
        print()
        
        # Show analysis plan summary
        if 'analysis_plan' in results:
            plan = results['analysis_plan']
            print("🎯 Analysis Plan Created:")
            if 'analysis_plan' in plan:
                agent_tasks = plan['analysis_plan'].get('agent_tasks', {})
                print(f"   Agent Tasks: {len(agent_tasks)} agents planned")
                print(f"   Execution Phases: {len(plan['analysis_plan'].get('execution_sequence', {}))}")
            print()
        
        # Show file analysis summary
        if 'file_analysis' in results:
            analysis = results['file_analysis']
            if 'analysis_summary' in analysis:
                summary = analysis['analysis_summary']
                print("📋 File Analysis Summary:")
                print(f"   Total Lines: {summary.get('total_lines', 'Unknown')}")
                print(f"   Analysis Phases: {summary.get('analysis_phases_completed', 0)}")
                print(f"   Templates Found: {summary.get('templates_found', 0)}")
            print()
        
        # Get system status
        status = await system.get_system_status()
        print("🔧 System Status:")
        print(f"   Agents: {len(status['agents'])} initialized")
        print(f"   Knowledge Base: {status['knowledge_base']['total_entries']} entries")
        print(f"   Communication: {status['communication_bus']['total_messages']} messages")
        print()
        
        # Save results
        output_file = Path("agentic_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        print()
        print("🎉 Phase 1 Demo Completed Successfully!")
        print()
        print("Next Steps:")
        print("- Implement remaining agents (Pattern Hunter, Schema Mapper, etc.)")
        print("- Add Phase 2-6 functionality")
        print("- Integrate with actual test case generation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())