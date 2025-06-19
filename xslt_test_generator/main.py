"""Main application entry point for XSLT Test Generator."""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from xslt_test_generator.config.settings import settings
from xslt_test_generator.tools.file_tools import FileManager
from xslt_test_generator.agents.xslt_analyzer import XSLTAnalyzerAgent
from xslt_test_generator.agents.xsd_analyzer import XSDAnalyzerAgent 
from xslt_test_generator.agents.test_case_generator import TestCaseGeneratorAgent

app = typer.Typer(help="XSLT Test Generator - Generate comprehensive test cases for XSLT transformations")
console = Console()

@app.command()
def generate(
    xslt_file: str = typer.Argument(..., help="Path to the XSLT file"),
    xsd_file: str = typer.Argument(..., help="Path to the XSD schema file"),
    output_dir: str = typer.Argument(..., help="Output directory for test cases"),
    llm_provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider (openai, anthropic, google)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Generate test cases for XSLT transformation."""
    
    if verbose:
        console.print("🚀 Starting XSLT Test Generator", style="bold green")
    
    # Validate input files
    if not _validate_inputs(xslt_file, xsd_file, output_dir):
        raise typer.Exit(1)
    
    # Initialize agents
    if verbose:
        console.print("🤖 Initializing AI agents...", style="blue")
    
    xslt_agent = XSLTAnalyzerAgent()
    xsd_agent = XSDAnalyzerAgent()
    test_generator = TestCaseGeneratorAgent()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Read files
        task1 = progress.add_task("📖 Reading input files...", total=None)
        try:
            xslt_content = FileManager.read_file(xslt_file)
            xsd_content = FileManager.read_file(xsd_file)
            progress.update(task1, description="✅ Files read successfully")
        except Exception as e:
            console.print(f"❌ Error reading files: {e}", style="red")
            raise typer.Exit(1)
        
        # Step 2: Analyze XSLT
        task2 = progress.add_task("🔍 Analyzing XSLT transformation...", total=None)
        try:
            xslt_analysis = xslt_agent.analyze_xslt_file(xslt_content)
            progress.update(task2, description="✅ XSLT analysis completed")
            
            if verbose:
                _print_xslt_analysis_summary(xslt_analysis)
                
        except Exception as e:
            console.print(f"❌ Error analyzing XSLT: {e}", style="red")
            raise typer.Exit(1)
        
        # Step 3: Analyze XSD
        task3 = progress.add_task("📋 Analyzing XSD schema...", total=None)
        try:
            xsd_analysis = xsd_agent.analyze_xsd_file(xsd_content)
            progress.update(task3, description="✅ XSD analysis completed")
            
            if verbose:
                _print_xsd_analysis_summary(xsd_analysis)
                
        except Exception as e:
            console.print(f"❌ Error analyzing XSD: {e}", style="red")
            raise typer.Exit(1)
        
        # Step 4: Generate test cases
        task4 = progress.add_task("🧪 Generating test cases...", total=None)
        try:
            test_results = test_generator.generate_test_cases(xslt_analysis, xsd_analysis)
            progress.update(task4, description="✅ Test cases generated")
            
            if verbose:
                _print_test_generation_summary(test_results)
                
        except Exception as e:
            console.print(f"❌ Error generating test cases: {e}", style="red")
            raise typer.Exit(1)
        
        # Step 5: Write output files
        task5 = progress.add_task("💾 Writing output files...", total=None)
        try:
            output_path = _write_output_files(output_dir, test_results, xslt_file, xsd_file)
            progress.update(task5, description="✅ Output files written")
            
        except Exception as e:
            console.print(f"❌ Error writing output: {e}", style="red")
            raise typer.Exit(1)
    
    # Success message
    console.print(f"\n🎉 Test generation completed successfully!", style="bold green")
    console.print(f"📁 Output location: {output_path}", style="green")
    console.print(f"📊 Generated test cases are ready for use!", style="green")

def _validate_inputs(xslt_file: str, xsd_file: str, output_dir: str) -> bool:
    """Validate input parameters."""
    
    # Check if XSLT file exists and is valid
    if not Path(xslt_file).exists():
        console.print(f"❌ XSLT file not found: {xslt_file}", style="red")
        return False
    
    if not FileManager.validate_xslt_file(xslt_file):
        console.print(f"❌ Invalid XSLT file: {xslt_file}", style="red")
        return False
    
    # Check if XSD file exists and is valid
    if not Path(xsd_file).exists():
        console.print(f"❌ XSD file not found: {xsd_file}", style="red")
        return False
    
    if not FileManager.validate_xsd_file(xsd_file):
        console.print(f"❌ Invalid XSD file: {xsd_file}", style="red")
        return False
    
    # Check output directory
    try:
        FileManager.ensure_output_directory(output_dir)
    except Exception as e:
        console.print(f"❌ Cannot create output directory: {e}", style="red")
        return False
    
    return True

def _print_xslt_analysis_summary(analysis: dict):
    """Print XSLT analysis summary."""
    summary = analysis.get('summary', {})
    console.print("\n📊 XSLT Analysis Summary:", style="bold blue")
    console.print(f"  • Templates: {summary.get('total_templates', 0)}")
    console.print(f"  • Conditional blocks: {summary.get('conditional_blocks', 0)}")
    console.print(f"  • Value mappings: {summary.get('value_mapping_functions', 0)}")
    console.print(f"  • Complexity: {summary.get('complexity_indicators', {}).get('xpath_complexity', 'unknown')}")

def _print_xsd_analysis_summary(analysis: dict):
    """Print XSD analysis summary."""
    summary = analysis.get('summary', {})
    console.print("\n📋 XSD Analysis Summary:", style="bold blue")
    console.print(f"  • Root elements: {summary.get('total_root_elements', 0)}")
    console.print(f"  • Complex types: {summary.get('total_complex_types', 0)}")
    console.print(f"  • Choice elements: {summary.get('total_choice_elements', 0)}")
    console.print(f"  • Optional elements: {'Yes' if summary.get('schema_characteristics', {}).get('has_optional_elements') else 'No'}")

def _print_test_generation_summary(results: dict):
    """Print test generation summary."""
    analysis = results.get('analysis', {})
    console.print("\n🧪 Test Generation Summary:", style="bold blue")
    console.print(f"  • Features: {analysis.get('feature_count', 0)}")
    console.print(f"  • Scenarios: {analysis.get('scenario_count', 0)}")
    console.print(f"  • Test steps: {analysis.get('given_count', 0) + analysis.get('when_count', 0) + analysis.get('then_count', 0)}")
    console.print(f"  • Has examples: {'Yes' if analysis.get('quality_indicators', {}).get('has_examples') else 'No'}")

def _write_output_files(output_dir: str, test_results: dict, xslt_file: str, xsd_file: str) -> str:
    """Write output files to specified directory."""
    output_path = FileManager.ensure_output_directory(output_dir)
    
    # Generate base filename from input files
    xslt_name = Path(xslt_file).stem
    xsd_name = Path(xsd_file).stem
    base_name = f"{xslt_name}_{xsd_name}_tests"
    
    # Write main Gherkin test file
    gherkin_file = output_path / f"{base_name}.feature"
    gherkin_content = test_results.get('gherkin_content', '')
    
    if 'error' in test_results:
        gherkin_content = test_results.get('fallback_cases', '')
        console.print("⚠️ Using fallback test cases due to generation error", style="yellow")
    
    FileManager.write_file(str(gherkin_file), gherkin_content)
    
    # Write analysis report
    report_file = output_path / f"{base_name}_analysis.md"
    report_content = _generate_analysis_report(test_results, xslt_file, xsd_file)
    FileManager.write_file(str(report_file), report_content)
    
    # Write metadata file
    metadata_file = output_path / f"{base_name}_metadata.yaml"
    import yaml
    metadata_content = yaml.dump(test_results.get('metadata', {}), default_flow_style=False)
    FileManager.write_file(str(metadata_file), metadata_content)
    
    return str(output_path)

def _generate_analysis_report(test_results: dict, xslt_file: str, xsd_file: str) -> str:
    """Generate analysis report in Markdown format."""
    analysis = test_results.get('analysis', {})
    metadata = test_results.get('metadata', {})
    coverage = test_results.get('coverage_matrix', {})
    
    report = f"""# XSLT Test Generation Report

## Input Files
- **XSLT File**: {xslt_file}
- **XSD File**: {xsd_file}
- **Generation Date**: {metadata.get('generation_timestamp', 'Unknown')}

## Test Case Statistics
- **Features Generated**: {analysis.get('feature_count', 0)}
- **Scenarios Generated**: {analysis.get('scenario_count', 0)}
- **Total Test Steps**: {analysis.get('given_count', 0) + analysis.get('when_count', 0) + analysis.get('then_count', 0)}

## Quality Indicators
- **Proper Gherkin Structure**: {'✅' if analysis.get('quality_indicators', {}).get('proper_gherkin_structure') else '❌'}
- **Has Background**: {'✅' if analysis.get('quality_indicators', {}).get('has_background') else '❌'}
- **Has Scenario Outlines**: {'✅' if analysis.get('quality_indicators', {}).get('has_scenario_outline') else '❌'}
- **Has Examples**: {'✅' if analysis.get('quality_indicators', {}).get('has_examples') else '❌'}

## Coverage Analysis
### Template Coverage
- **Total Templates**: {coverage.get('template_coverage', {}).get('total_templates', 0)}
- **Coverage**: {coverage.get('template_coverage', {}).get('coverage_percentage', 0)}%

### Condition Coverage  
- **Total Conditions**: {coverage.get('condition_coverage', {}).get('total_conditions', 0)}
- **Coverage**: {coverage.get('condition_coverage', {}).get('coverage_percentage', 0)}%

### Schema Coverage
- **Total Elements**: {coverage.get('schema_coverage', {}).get('total_elements', 0)}
- **Coverage**: {coverage.get('schema_coverage', {}).get('coverage_percentage', 0)}%

## Coverage Areas
{chr(10).join(f'- {area}' for area in metadata.get('coverage_areas', []))}

## Next Steps
1. Review generated test cases for completeness
2. Create test data XML files based on scenarios
3. Execute test cases against XSLT transformation
4. Validate outputs against expected results
"""
    
    return report

if __name__ == "__main__":
    app()