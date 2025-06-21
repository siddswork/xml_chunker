"""Main application entry point for XSLT Test Generator v2.0."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, List
import time

from xslt_test_generator.config.logging_config import setup_logging, get_logger
from xslt_test_generator.database.connection import DatabaseManager
from xslt_test_generator.core.file_discovery import FileDiscoveryEngine
from xslt_test_generator.analysis.analysis_coordinator import AnalysisCoordinator
from xslt_test_generator.cli.test_generator_cli import TestGeneratorCLI

app = typer.Typer(help="XSLT Test Generator v2.0 - Enterprise-grade XSLT analysis and test generation")
console = Console()
logger = None  # Will be initialized after logging setup


@app.command()
def analyze(
    entry_file: str = typer.Argument(..., help="Path to the main XSLT or XSD file"),
    db_path: Optional[str] = typer.Option(None, "--db", "-d", help="Database file path"),
    output_dir: str = typer.Option("./analysis_output", "--output", "-o", help="Output directory"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
    log_to_file: bool = typer.Option(True, "--log-to-file/--no-log-to-file", help="Enable file logging"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    force_reanalysis: bool = typer.Option(False, "--force", "-f", help="Force reanalysis of all files")
):
    """Analyze XSLT transformation ecosystem and generate test specifications."""
    
    # Initialize logging
    setup_logging(
        log_level=log_level.upper(),
        log_to_file=log_to_file,
        log_dir="logs",
        enable_structured_logging=True
    )
    
    global logger
    logger = get_logger(__name__)
    
    logger.info("Starting XSLT Test Generator v2.0", extra={
        "entry_file": entry_file,
        "db_path": db_path,
        "output_dir": output_dir,
        "force_reanalysis": force_reanalysis
    })
    
    if verbose:
        console.print("🚀 Starting XSLT Test Generator v2.0", style="bold green")
    
    try:
        # Validate entry file
        entry_path = Path(entry_file)
        if not entry_path.exists():
            console.print(f"❌ Entry file not found: {entry_file}", style="red")
            raise typer.Exit(1)
        
        # Initialize database
        db_manager = DatabaseManager(db_path)
        
        # Initialize file discovery
        file_discovery = FileDiscoveryEngine(db_manager)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Phase 1: File Discovery
            task1 = progress.add_task("🔍 Discovering transformation ecosystem...", total=None)
            logger.info("Starting file discovery")
            
            start_time = time.time()
            discovered_files = file_discovery.discover_transformation_ecosystem(entry_file)
            discovery_time = time.time() - start_time
            
            progress.update(task1, description=f"✅ Discovered {len(discovered_files)} files")
            logger.info("File discovery completed", extra={
                "files_discovered": len(discovered_files),
                "discovery_time": discovery_time
            })
            
            if verbose:
                _print_discovery_summary(discovered_files)
            
            # Phase 2: Store Files in Database
            task2 = progress.add_task("💾 Storing files in database...", total=None)
            logger.info("Storing discovered files in database")
            
            file_id_map = file_discovery.store_discovered_files()
            progress.update(task2, description="✅ Files stored in database")
            
            if verbose:
                _print_database_summary(db_manager)
            
            # Phase 3: Determine Analysis Plan
            if force_reanalysis:
                files_to_analyze = list(discovered_files.keys())
                logger.info("Force reanalysis requested - analyzing all files")
            else:
                files_to_analyze = file_discovery.detect_changed_files()
                logger.info(f"Incremental analysis - {len(files_to_analyze)} files need analysis")
            
            if files_to_analyze:
                task3 = progress.add_task(f"📋 Analysis plan: {len(files_to_analyze)} files to process", total=None)
                progress.update(task3, description="✅ Analysis plan ready")
                
                if verbose:
                    _print_analysis_plan(files_to_analyze, discovered_files)
                
                # Phase 4: XSLT Analysis Engine
                progress.remove_task(task3)
                xslt_files = [f for f in files_to_analyze if discovered_files.get(f, {}).file_type == 'xslt']
                
                if xslt_files:
                    task4 = progress.add_task("🧠 Analyzing XSLT transformations...", total=len(xslt_files))
                    
                    # Initialize analysis coordinator
                    analysis_coordinator = AnalysisCoordinator(db_manager)
                    
                    analysis_results = {}
                    successful_analyses = 0
                    
                    for i, xslt_file in enumerate(xslt_files):
                        progress.update(task4, description=f"🧠 Analyzing {Path(xslt_file).name}...")
                        
                        try:
                            result = analysis_coordinator.analyze_xslt_file(xslt_file, force_reanalysis)
                            
                            if 'error' not in result:
                                analysis_results[xslt_file] = result
                                successful_analyses += 1
                            else:
                                logger.error(f"XSLT analysis failed for {xslt_file}: {result['error']}")
                                
                        except Exception as e:
                            logger.error(f"Error analyzing {xslt_file}: {e}")
                        
                        progress.update(task4, advance=1)
                    
                    progress.update(task4, description=f"✅ XSLT analysis complete: {successful_analyses}/{len(xslt_files)} files")
                    
                    # Display analysis summary
                    if verbose and analysis_results:
                        _print_xslt_analysis_summary(analysis_results)
                else:
                    console.print("ℹ️  No XSLT files found for detailed analysis", style="yellow")
            else:
                console.print("✅ All files are up to date - no analysis needed", style="green")
        
        # Success summary
        total_analyzed = len([f for f in files_to_analyze if discovered_files.get(f, {}).file_type == 'xslt']) if files_to_analyze else 0
        
        console.print(f"\n🎉 Analysis completed successfully!", style="bold green")
        console.print(f"📁 Database: {db_manager.db_path}", style="green")
        console.print(f"📊 Discovered {len(discovered_files)} files in ecosystem", style="green")
        console.print(f"🧠 Analyzed {total_analyzed} XSLT files", style="green")
        
        logger.info("Phase 1 analysis completed successfully", extra={
            "total_files": len(discovered_files),
            "files_to_analyze": len(files_to_analyze) if files_to_analyze else 0
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        console.print(f"❌ Analysis failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def status(
    db_path: Optional[str] = typer.Option(None, "--db", "-d", help="Database file path")
):
    """Show analysis status and database statistics."""
    
    setup_logging(log_level="INFO", log_to_file=False)
    
    try:
        db_manager = DatabaseManager(db_path)
        stats = db_manager.get_analysis_statistics()
        
        console.print("\n📊 XSLT Test Generator v2.0 Status", style="bold blue")
        console.print(f"🗄️  Database: {db_manager.db_path}")
        
        # File statistics
        if 'files' in stats:
            table = Table(title="File Statistics")
            table.add_column("File Type", style="cyan")
            table.add_column("Count", justify="right", style="magenta")
            table.add_column("Total Size", justify="right", style="green")
            
            for file_type, file_stats in stats['files'].items():
                size_mb = file_stats['total_size'] / (1024 * 1024)
                table.add_row(
                    file_type.upper(),
                    str(file_stats['count']),
                    f"{size_mb:.2f} MB"
                )
            
            console.print(table)
        
        # Template statistics
        if 'templates' in stats and stats['templates']:
            console.print(f"\n📝 Templates: {stats['templates'].get('total_templates', 0)}")
            console.print(f"   • Named: {stats['templates'].get('named_templates', 0)}")
            console.print(f"   • Match: {stats['templates'].get('match_templates', 0)}")
            if stats['templates'].get('avg_complexity'):
                console.print(f"   • Avg Complexity: {stats['templates']['avg_complexity']:.1f}")
        
        # Path statistics
        if 'paths' in stats and stats['paths']:
            console.print(f"\n🛤️  Execution Paths: {stats['paths'].get('total_paths', 0)}")
            if stats['paths'].get('avg_path_complexity'):
                console.print(f"   • Avg Complexity: {stats['paths']['avg_path_complexity']:.1f}")
            console.print(f"   • Recursive: {stats['paths'].get('recursive_paths', 0)}")
        
        # Test statistics
        if 'tests' in stats and stats['tests'].get('total', 0) > 0:
            console.print(f"\n🧪 Test Cases: {stats['tests']['total']}")
            for category, count in stats['tests'].get('by_category', {}).items():
                console.print(f"   • {category.replace('_', ' ').title()}: {count}")
        
    except Exception as e:
        console.print(f"❌ Error getting status: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def generate_tests(
    xslt_file: str = typer.Argument(..., help="Path to XSLT file"),
    output_dir: str = typer.Option("generated_tests", "--output", "-o", help="Output directory for generated tests"),
    formats: List[str] = typer.Option(["cucumber", "pytest", "json"], "--format", "-f", help="Output formats"),
    force: bool = typer.Option(False, "--force", help="Force reanalysis"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
    log_to_file: bool = typer.Option(True, "--log-to-file/--no-log-to-file", help="Enable file logging")
):
    """Generate intelligent test cases for XSLT transformation using Phase 2 analysis."""
    
    # Initialize logging
    setup_logging(
        log_level=log_level.upper(),
        log_to_file=log_to_file,
        log_dir="logs",
        enable_structured_logging=True
    )
    
    global logger
    logger = get_logger(__name__)
    
    xslt_path = Path(xslt_file)
    if not xslt_path.exists():
        console.print(f"❌ XSLT file not found: {xslt_file}", style="red")
        raise typer.Exit(1)
    
    try:
        # Initialize test generator CLI
        test_cli = TestGeneratorCLI()
        
        # Generate tests
        results = test_cli.generate_tests(
            xslt_file=str(xslt_path),
            output_dir=output_dir,
            output_formats=formats,
            force_reanalysis=force,
            verbose=verbose
        )
        
        console.print(f"\n🎉 Test generation completed successfully!", style="bold green")
        console.print(f"📁 Generated {results['statistics']['total_scenarios']} test scenarios", style="green")
        console.print(f"📂 Output directory: {results['output_directory']}", style="green")
        
        logger.info("Test generation completed successfully", extra={
            "total_scenarios": results['statistics']['total_scenarios'],
            "output_directory": results['output_directory']
        })
        
    except Exception as e:
        logger.error(f"Test generation failed: {e}", exc_info=True)
        console.print(f"❌ Test generation failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def analyze_only(
    xslt_file: str = typer.Argument(..., help="Path to XSLT file"),
    force: bool = typer.Option(False, "--force", help="Force reanalysis"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
    log_to_file: bool = typer.Option(True, "--log-to-file/--no-log-to-file", help="Enable file logging")
):
    """Analyze XSLT transformation without generating tests."""
    
    # Initialize logging
    setup_logging(
        log_level=log_level.upper(),
        log_to_file=log_to_file,
        log_dir="logs",
        enable_structured_logging=True
    )
    
    global logger
    logger = get_logger(__name__)
    
    xslt_path = Path(xslt_file)
    if not xslt_path.exists():
        console.print(f"❌ XSLT file not found: {xslt_file}", style="red")
        raise typer.Exit(1)
    
    try:
        # Initialize test generator CLI
        test_cli = TestGeneratorCLI()
        
        # Run analysis only
        results = test_cli.analyze_only(str(xslt_path), force_reanalysis=force)
        
        if 'error' not in results:
            console.print(f"\n✅ Analysis completed successfully!", style="green")
            logger.info("Analysis completed successfully")
        else:
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        console.print(f"❌ Analysis failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def clean(
    db_path: Optional[str] = typer.Option(None, "--db", "-d", help="Database file path"),
    keep_files: bool = typer.Option(True, "--keep-files/--clean-all", help="Keep file records")
):
    """Clean analysis data from database."""
    
    setup_logging(log_level="INFO", log_to_file=False)
    
    if not typer.confirm(f"Clean analysis data (keep_files={keep_files})?"):
        console.print("❌ Operation cancelled", style="yellow")
        return
    
    try:
        db_manager = DatabaseManager(db_path)
        db_manager.cleanup_analysis(keep_files=keep_files)
        
        console.print("✅ Analysis data cleaned successfully", style="green")
        
    except Exception as e:
        console.print(f"❌ Error cleaning database: {e}", style="red")
        raise typer.Exit(1)


def _print_discovery_summary(discovered_files: dict):
    """Print file discovery summary."""
    console.print("\n📁 File Discovery Summary:", style="bold blue")
    
    by_type = {}
    for file_info in discovered_files.values():
        file_type = file_info.file_type
        if file_type not in by_type:
            by_type[file_type] = []
        by_type[file_type].append(file_info)
    
    for file_type, files in by_type.items():
        console.print(f"  • {file_type.upper()}: {len(files)} files")
        for file_info in files[:3]:  # Show first 3 files
            console.print(f"    - {Path(file_info.path).name}")
        if len(files) > 3:
            console.print(f"    ... and {len(files) - 3} more")


def _print_database_summary(db_manager: DatabaseManager):
    """Print database summary."""
    console.print("\n🗄️  Database Summary:", style="bold blue")
    
    all_files = db_manager.get_all_files()
    by_status = {}
    for file_row in all_files:
        status = file_row['analysis_status']
        by_status[status] = by_status.get(status, 0) + 1
    
    for status, count in by_status.items():
        status_style = {
            'completed': 'green',
            'pending': 'yellow', 
            'analyzing': 'cyan',
            'error': 'red'
        }.get(status, 'white')
        console.print(f"  • {status.title()}: {count}", style=status_style)


def _print_analysis_plan(files_to_analyze: list, discovered_files: dict):
    """Print analysis plan."""
    console.print("\n📋 Analysis Plan:", style="bold blue")
    
    for file_path in files_to_analyze[:5]:  # Show first 5
        file_info = discovered_files.get(file_path)
        if file_info:
            console.print(f"  • {Path(file_path).name} ({file_info.file_type})")
    
    if len(files_to_analyze) > 5:
        console.print(f"  ... and {len(files_to_analyze) - 5} more files")


def _print_xslt_analysis_summary(analysis_results: dict):
    """Print XSLT analysis results summary."""
    console.print("\n🧠 XSLT Analysis Summary:", style="bold blue")
    
    total_templates = 0
    total_patterns = 0
    total_paths = 0
    high_complexity_files = []
    
    for file_path, result in analysis_results.items():
        file_name = Path(file_path).name
        summary = result.get('summary', {})
        
        # Template count
        template_summary = summary.get('parsing_summary', {})
        file_templates = template_summary.get('total_templates', 0)
        total_templates += file_templates
        
        # Semantic patterns
        semantic_summary = summary.get('semantic_summary', {})
        file_patterns = semantic_summary.get('total_patterns', 0)
        total_patterns += file_patterns
        
        # Execution paths
        execution_summary = summary.get('execution_summary', {})
        file_paths = execution_summary.get('total_paths', 0)
        total_paths += file_paths
        
        # Check complexity
        complexity = summary.get('overall_complexity', 0)
        if complexity > 50:
            high_complexity_files.append((file_name, complexity))
        
        # Print file summary
        console.print(f"  📄 {file_name}:")
        console.print(f"     Templates: {file_templates}, Patterns: {file_patterns}, Paths: {file_paths}")
        if complexity > 30:
            console.print(f"     Complexity: {complexity} {'🔥' if complexity > 50 else '⚠️'}")
    
    # Overall summary
    console.print(f"\n📊 Overall Totals:")
    console.print(f"  • Templates: {total_templates}")
    console.print(f"  • Semantic Patterns: {total_patterns}")
    console.print(f"  • Execution Paths: {total_paths}")
    
    if high_complexity_files:
        console.print(f"\n🔥 High Complexity Files:")
        for file_name, complexity in sorted(high_complexity_files, key=lambda x: x[1], reverse=True):
            console.print(f"  • {file_name}: {complexity}")


if __name__ == "__main__":
    app()