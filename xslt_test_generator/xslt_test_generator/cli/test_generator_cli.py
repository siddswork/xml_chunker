"""Unified CLI for intelligent test generation using Phase 2 analysis."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree

from ..core.base import LoggerMixin
from ..database.connection import DatabaseManager
from ..analysis.analysis_coordinator import AnalysisCoordinator
from ..agents.intelligent_test_generator import IntelligentTestGenerator
from ..agents.test_case_formatter import TestCaseFormatter, FormattedTestCase

console = Console()


class TestGeneratorCLI(LoggerMixin):
    """Unified CLI for end-to-end intelligent test generation."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.analysis_coordinator = AnalysisCoordinator(self.db_manager)
        self.test_generator = IntelligentTestGenerator()
        self.test_formatter = TestCaseFormatter()
    
    def generate_tests(self, 
                      xslt_file: str,
                      output_dir: str = "generated_tests",
                      output_formats: List[str] = None,
                      force_reanalysis: bool = False,
                      verbose: bool = False) -> Dict[str, Any]:
        """
        Generate intelligent test cases for XSLT transformation.
        
        Args:
            xslt_file: Path to XSLT file
            output_dir: Directory to save generated tests
            output_formats: List of output formats ['cucumber', 'pytest', 'xml_unit', 'json']
            force_reanalysis: Force reanalysis even if cached
            verbose: Enable verbose output
            
        Returns:
            Generation results and statistics
        """
        if output_formats is None:
            output_formats = ['cucumber', 'pytest', 'json']
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                
                # Phase 1: XSLT Analysis
                analysis_task = progress.add_task("Analyzing XSLT transformation...", total=1)
                
                self.logger.info(f"Starting intelligent test generation for {xslt_file}")
                analysis_results = self.analysis_coordinator.analyze_xslt_file(
                    xslt_file, force_reanalysis
                )
                
                if 'error' in analysis_results:
                    raise Exception(f"Analysis failed: {analysis_results['error']}")
                
                progress.update(analysis_task, completed=1)
                
                # Phase 2: Intelligent Test Generation
                generation_task = progress.add_task("Generating intelligent test scenarios...", total=1)
                
                test_suite = self.test_generator.generate_test_suite(analysis_results)
                progress.update(generation_task, completed=1)
                
                # Phase 3: Format Generation
                formatting_task = progress.add_task("Formatting test cases...", total=len(output_formats))
                
                formatted_tests = self.test_formatter.format_test_suite(test_suite, output_formats)
                
                # Phase 4: Save Test Files
                save_task = progress.add_task("Saving test files...", total=1)
                
                saved_files = self._save_test_files(formatted_tests, output_path)
                progress.update(save_task, completed=1)
            
            # Generate summary
            results = {
                'xslt_file': xslt_file,
                'analysis_results': analysis_results,
                'test_suite': test_suite,
                'generated_files': saved_files,
                'output_directory': str(output_path),
                'statistics': self._generate_statistics(test_suite, formatted_tests)
            }
            
            if verbose:
                self._display_detailed_results(results)
            else:
                self._display_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            rprint(f"[red]❌ Test generation failed: {e}[/red]")
            raise
    
    def _save_test_files(self, formatted_tests: Dict[str, List[FormattedTestCase]], 
                        output_path: Path) -> List[Dict[str, Any]]:
        """Save formatted test cases to files."""
        saved_files = []
        
        for format_type, test_cases in formatted_tests.items():
            format_dir = output_path / format_type
            format_dir.mkdir(exist_ok=True)
            
            for test_case in test_cases:
                file_path = format_dir / test_case.file_name
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(test_case.content)
                
                saved_files.append({
                    'format': format_type,
                    'file_path': str(file_path),
                    'file_name': test_case.file_name,
                    'test_id': test_case.test_id,
                    'metadata': test_case.metadata
                })
                
                self.logger.info(f"Saved {format_type} test: {file_path}")
        
        return saved_files
    
    def _generate_statistics(self, test_suite, formatted_tests: Dict) -> Dict[str, Any]:
        """Generate test generation statistics."""
        return {
            'total_scenarios': test_suite.total_scenarios,
            'scenarios_by_priority': test_suite.scenarios_by_priority,
            'scenarios_by_type': test_suite.scenarios_by_type,
            'coverage_metrics': {
                'template_coverage': f"{test_suite.template_coverage:.1%}",
                'path_coverage': f"{test_suite.path_coverage:.1%}",
                'pattern_coverage': f"{test_suite.pattern_coverage:.1%}"
            },
            'output_formats': list(formatted_tests.keys()),
            'total_files_generated': sum(len(tests) for tests in formatted_tests.values()),
            'estimated_execution_time': test_suite.estimated_execution_time
        }
    
    def _display_summary(self, results: Dict[str, Any]) -> None:
        """Display generation summary."""
        stats = results['statistics']
        
        # Main summary panel
        summary_text = f"""
[bold green]✅ Test Generation Complete![/bold green]

📁 **XSLT File**: {Path(results['xslt_file']).name}
🎯 **Test Scenarios**: {stats['total_scenarios']} generated
📊 **Coverage**: Template {stats['coverage_metrics']['template_coverage']} | Path {stats['coverage_metrics']['path_coverage']} | Pattern {stats['coverage_metrics']['pattern_coverage']}
⏱️  **Est. Execution Time**: {stats['estimated_execution_time']}
📂 **Output Directory**: {results['output_directory']}
"""
        
        rprint(Panel(summary_text, title="🧪 Intelligent Test Generation Results", border_style="green"))
        
        # Priority distribution
        priority_table = Table(title="Test Priority Distribution")
        priority_table.add_column("Priority", style="cyan")
        priority_table.add_column("Count", style="magenta")
        
        for priority, count in stats['scenarios_by_priority'].items():
            priority_table.add_row(priority.title(), str(count))
        
        console.print(priority_table)
        
        # Generated files
        files_table = Table(title="Generated Test Files")
        files_table.add_column("Format", style="cyan")
        files_table.add_column("Files", style="magenta")
        files_table.add_column("Location", style="green")
        
        for format_name in stats['output_formats']:
            format_files = [f for f in results['generated_files'] if f['format'] == format_name]
            files_table.add_row(
                format_name.title(),
                str(len(format_files)),
                f"{results['output_directory']}/{format_name}/"
            )
        
        console.print(files_table)
    
    def _display_detailed_results(self, results: Dict[str, Any]) -> None:
        """Display detailed generation results."""
        self._display_summary(results)
        
        # Analysis details
        analysis = results['analysis_results']
        if 'summary' in analysis:
            summary = analysis['summary']
            
            analysis_text = f"""
[bold blue]📋 Analysis Summary[/bold blue]

🔍 **Key Findings**: {', '.join(summary.get('key_findings', []))}
⚡ **Overall Complexity**: {summary.get('overall_complexity', 'Unknown')}
🎯 **Test Priority**: {summary.get('test_generation_priority', 'medium').title()}
"""
            
            rprint(Panel(analysis_text, title="XSLT Analysis Results", border_style="blue"))
        
        # Test scenarios breakdown
        test_suite = results['test_suite']
        
        scenarios_tree = Tree("🧪 Generated Test Scenarios")
        
        for scenario_type, count in test_suite.scenarios_by_type.items():
            type_node = scenarios_tree.add(f"[cyan]{scenario_type.replace('_', ' ').title()}[/cyan] ({count} scenarios)")
            
            # Show sample scenarios of this type
            type_scenarios = [s for s in test_suite.scenarios if s.scenario_type == scenario_type][:3]
            for scenario in type_scenarios:
                type_node.add(f"[green]✓[/green] {scenario.description}")
            
            if len(type_scenarios) < count:
                type_node.add(f"[dim]... and {count - len(type_scenarios)} more[/dim]")
        
        console.print(scenarios_tree)
    
    def analyze_only(self, xslt_file: str, force_reanalysis: bool = False) -> Dict[str, Any]:
        """Run analysis only without test generation."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                
                task = progress.add_task("Analyzing XSLT transformation...", total=1)
                
                analysis_results = self.analysis_coordinator.analyze_xslt_file(
                    xslt_file, force_reanalysis
                )
                
                progress.update(task, completed=1)
            
            if 'error' in analysis_results:
                rprint(f"[red]❌ Analysis failed: {analysis_results['error']}[/red]")
                return analysis_results
            
            # Display analysis summary
            self._display_analysis_results(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            rprint(f"[red]❌ Analysis failed: {e}[/red]")
            raise
    
    def _display_analysis_results(self, analysis_results: Dict[str, Any]) -> None:
        """Display analysis results."""
        template_analysis = analysis_results.get('template_analysis', {})
        semantic_analysis = analysis_results.get('semantic_analysis', {})
        execution_analysis = analysis_results.get('execution_analysis', {})
        
        # Template analysis
        templates = template_analysis.get('templates', {})
        template_text = f"""
[bold blue]📝 Template Analysis[/bold blue]

🎯 **Templates Found**: {len(templates)}
📊 **Analysis Summary**: {template_analysis.get('analysis_summary', {})}
"""
        
        rprint(Panel(template_text, title="Template Analysis", border_style="blue"))
        
        # Semantic analysis  
        patterns = semantic_analysis.get('semantic_patterns', [])
        hotspots = semantic_analysis.get('transformation_hotspots', [])
        
        semantic_text = f"""
[bold purple]🧠 Semantic Analysis[/bold purple]

🔍 **Patterns Identified**: {len(patterns)}
🔥 **Complexity Hotspots**: {len(hotspots)}
📈 **Analysis Summary**: {semantic_analysis.get('analysis_summary', {})}
"""
        
        rprint(Panel(semantic_text, title="Semantic Analysis", border_style="purple"))
        
        # Execution analysis
        paths = execution_analysis.get('execution_paths', [])
        entry_points = execution_analysis.get('entry_points', [])
        
        execution_text = f"""
[bold green]🛤️  Execution Analysis[/bold green]

🚪 **Entry Points**: {len(entry_points)}
🛤️  **Execution Paths**: {len(paths)}
📊 **Path Statistics**: {execution_analysis.get('path_statistics', {})}
"""
        
        rprint(Panel(execution_text, title="Execution Analysis", border_style="green"))


# CLI Application
app = typer.Typer(help="Intelligent XSLT Test Generator", rich_markup_mode="rich")
cli = TestGeneratorCLI()


@app.command()
def generate(
    xslt_file: str = typer.Argument(..., help="Path to XSLT file"),
    output_dir: str = typer.Option("generated_tests", "--output", "-o", help="Output directory for generated tests"),
    formats: List[str] = typer.Option(["cucumber", "pytest", "json"], "--format", "-f", help="Output formats"),
    force: bool = typer.Option(False, "--force", help="Force reanalysis"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate intelligent test cases for XSLT transformation."""
    
    xslt_path = Path(xslt_file)
    if not xslt_path.exists():
        rprint(f"[red]❌ XSLT file not found: {xslt_file}[/red]")
        raise typer.Exit(1)
    
    try:
        results = cli.generate_tests(
            xslt_file=str(xslt_path),
            output_dir=output_dir,
            output_formats=formats,
            force_reanalysis=force,
            verbose=verbose
        )
        
        rprint(f"\n[green]🎉 Test generation completed successfully![/green]")
        rprint(f"[dim]Generated {results['statistics']['total_scenarios']} test scenarios in {len(formats)} formats[/dim]")
        
    except Exception as e:
        rprint(f"[red]❌ Test generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze(
    xslt_file: str = typer.Argument(..., help="Path to XSLT file"),
    force: bool = typer.Option(False, "--force", help="Force reanalysis")
):
    """Analyze XSLT transformation without generating tests."""
    
    xslt_path = Path(xslt_file)
    if not xslt_path.exists():
        rprint(f"[red]❌ XSLT file not found: {xslt_file}[/red]")
        raise typer.Exit(1)
    
    try:
        results = cli.analyze_only(str(xslt_path), force_reanalysis=force)
        
        if 'error' not in results:
            rprint(f"\n[green]✅ Analysis completed successfully![/green]")
        else:
            raise typer.Exit(1)
            
    except Exception as e:
        rprint(f"[red]❌ Analysis failed: {e}[/red]")
        raise typer.Exit(1)


@app.command() 
def status():
    """Show database status and statistics."""
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_database_statistics()
        
        # Create status display
        status_text = f"""
[bold blue]📊 Database Status[/bold blue]

📁 **Files Tracked**: {stats.get('total_files', 0)}
📝 **Templates Analyzed**: {stats.get('total_templates', 0)}
🛤️  **Execution Paths**: {stats.get('total_paths', 0)}
🧪 **Test Specifications**: {stats.get('total_test_specs', 0)}
"""
        
        rprint(Panel(status_text, title="XSLT Test Generator Status", border_style="blue"))
        
    except Exception as e:
        rprint(f"[red]❌ Failed to get status: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()