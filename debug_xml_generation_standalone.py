#!/usr/bin/env python3
"""
Standalone XML Generation Debug Tool

This script simulates the exact flow that app.py uses to generate XML from XSD + JSON configuration.
It helps identify issues with XML generation outside of the Streamlit environment.

Enhanced Features:
- Count empty tags in generated XML
- XML validation against XSD schema
- Comparison between with/without JSON config
- Detailed error analysis

Usage:
    python debug_xml_generation_standalone.py
"""

import os
import sys
import json
import tempfile
import shutil
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import xmlschema

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.xml_generator import XMLGenerator
from utils.xsd_parser import XSDParser
from config import get_config
from services.file_manager import FileManager
from services.xml_validator import XMLValidator
from services.schema_analyzer import SchemaAnalyzer
from utils.config_manager import ConfigManager


class StandaloneXMLGenerationDebugger:
    """Standalone debugging tool for XML generation issues."""
    
    def __init__(self):
        """Initialize the debugger with necessary components."""
        print("🔧 Initializing XML Generation Debugger...")
        
        # Initialize configuration and services (same as app.py)
        self.config = get_config()
        self.file_manager = FileManager(self.config)
        self.xml_validator = XMLValidator(self.config)
        self.schema_analyzer = SchemaAnalyzer(self.config)
        self.config_manager = ConfigManager(self.config)
        
        print("✅ Components initialized successfully")
    
    def count_empty_tags(self, xml_content: str) -> Dict[str, Any]:
        """Count empty/self-closing tags in XML content."""
        try:
            # Parse XML to count empty elements
            root = ET.fromstring(xml_content)
            
            empty_tags = []
            total_elements = 0
            
            def analyze_element(element, path=""):
                nonlocal total_elements
                total_elements += 1
                current_path = f"{path}/{element.tag}" if path else element.tag
                
                # Check if element is empty (no text and no children)
                is_empty = (not element.text or element.text.strip() == "") and len(element) == 0
                if is_empty:
                    empty_tags.append(current_path)
                
                # Recursively analyze children
                for child in element:
                    analyze_element(child, current_path)
            
            analyze_element(root)
            
            # Also count self-closing tags using regex
            self_closing_pattern = r'<([^>]+?)/>'
            self_closing_matches = re.findall(self_closing_pattern, xml_content)
            
            return {
                "total_elements": total_elements,
                "empty_elements": len(empty_tags),
                "empty_element_list": empty_tags[:20],  # Show first 20
                "self_closing_tags": len(self_closing_matches),
                "self_closing_examples": self_closing_matches[:10],  # Show first 10
                "empty_percentage": round((len(empty_tags) / total_elements) * 100, 2) if total_elements > 0 else 0
            }
        except Exception as e:
            return {
                "error": f"Failed to analyze empty tags: {str(e)}",
                "total_elements": 0,
                "empty_elements": 0,
                "empty_percentage": 0
            }
    
    def validate_xml_against_xsd(self, xml_content: str, xsd_file_path: str) -> Dict[str, Any]:
        """Validate XML against XSD schema and return detailed error analysis."""
        try:
            # Load schema
            schema = xmlschema.XMLSchema(xsd_file_path)
            
            # Validate XML
            validation_errors = []
            try:
                schema.validate(xml_content)
                is_valid = True
            except xmlschema.XMLSchemaException as e:
                is_valid = False
                validation_errors.append(str(e))
            except Exception as e:
                is_valid = False
                validation_errors.append(f"Validation error: {str(e)}")
            
            # Try to get more detailed errors
            try:
                for error in schema.iter_errors(xml_content):
                    validation_errors.append(f"Line {getattr(error, 'line', 'unknown')}: {str(error)}")
            except:
                pass  # Already have at least one error
            
            return {
                "is_valid": is_valid,
                "error_count": len(validation_errors),
                "errors": validation_errors[:20],  # Show first 20 errors
                "schema_loaded": True
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error_count": 1,
                "errors": [f"Schema loading failed: {str(e)}"],
                "schema_loaded": False
            }
    
    def simulate_file_upload(self, xsd_file_path: str, json_config_path: str) -> Dict[str, Any]:
        """Simulate file upload process from app.py."""
        print(f"📁 Simulating file upload process...")
        print(f"   XSD File: {xsd_file_path}")
        print(f"   JSON Config: {json_config_path}")
        
        # Check if files exist
        if not os.path.exists(xsd_file_path):
            raise FileNotFoundError(f"XSD file not found: {xsd_file_path}")
        if not os.path.exists(json_config_path):
            raise FileNotFoundError(f"JSON config file not found: {json_config_path}")
        
        # Read files
        with open(xsd_file_path, 'r', encoding='utf-8') as f:
            xsd_content = f.read()
        
        with open(json_config_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
        
        # Create temporary directory and copy XSD file (simulate app.py behavior)
        temp_dir = tempfile.mkdtemp(prefix="xml_gen_debug_")
        temp_xsd_path = os.path.join(temp_dir, os.path.basename(xsd_file_path))
        
        # Copy XSD file and its dependencies
        shutil.copy2(xsd_file_path, temp_xsd_path)
        
        # Copy any dependency files in the same directory
        xsd_dir = os.path.dirname(xsd_file_path)
        for file in os.listdir(xsd_dir):
            if file.endswith('.xsd') and file != os.path.basename(xsd_file_path):
                shutil.copy2(os.path.join(xsd_dir, file), os.path.join(temp_dir, file))
        
        print(f"📄 Temporary directory created: {temp_dir}")
        print(f"📄 XSD copied to: {temp_xsd_path}")
        
        return {
            'success': True,
            'temp_dir': temp_dir,
            'temp_xsd_path': temp_xsd_path,
            'xsd_content': xsd_content,
            'json_content': json_content,
            'original_xsd_path': xsd_file_path,
            'original_json_path': json_config_path
        }
    
    def analyze_schema(self, temp_xsd_path: str) -> Dict[str, Any]:
        """Analyze XSD schema (simulate Tab 1 of app.py)."""
        print("🔍 Analyzing XSD schema...")
        
        try:
            # Use the same analysis function from app.py
            analysis = self._analyze_xsd_schema(temp_xsd_path)
            
            if analysis['success']:
                schema_info = analysis['schema_info']
                choices = analysis['choices']
                unbounded_elements = analysis['unbounded_elements']
                element_tree = analysis['element_tree']
                
                print(f"✅ Schema analysis successful:")
                print(f"   - Elements: {schema_info.get('elements_count', 0)}")
                print(f"   - Types: {schema_info.get('types_count', 0)}")
                print(f"   - Choices: {len(choices) if choices else 0}")
                print(f"   - Unbounded elements: {len(unbounded_elements) if unbounded_elements else 0}")
                print(f"   - Target namespace: {schema_info.get('target_namespace', 'None')}")
                
                return analysis
            else:
                print(f"❌ Schema analysis failed: {analysis['error']}")
                return analysis
                
        except Exception as e:
            print(f"❌ Schema analysis exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_xsd_schema(self, xsd_file_path: str) -> Dict[str, Any]:
        """Analyze XSD schema - copied from app.py."""
        try:
            # First try basic XSD parsing for initial validation
            parser = XSDParser(xsd_file_path)
            basic_info = parser.get_schema_info()
            
            # Use SchemaAnalyzer for detailed analysis
            analysis = self.schema_analyzer.analyze_xsd_schema(xsd_file_path)
            
            if analysis['success']:
                # Merge basic info with detailed analysis
                schema_info = {
                    **basic_info,
                    **analysis.get('schema_info', {})
                }
                
                return {
                    'success': True,
                    'schema_info': schema_info,
                    'choices': analysis.get('choices', []),
                    'unbounded_elements': analysis.get('unbounded_elements', []),
                    'element_tree': analysis.get('element_tree', {}),
                    'detailed_analysis': analysis
                }
            else:
                return {
                    'success': False,
                    'error': analysis.get('error', 'Unknown analysis error'),
                    'basic_info': basic_info
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Schema analysis failed: {str(e)}"
            }
    
    def load_json_configuration(self, json_content: str) -> Dict[str, Any]:
        """Load and validate JSON configuration (simulate app.py behavior)."""
        print("📋 Loading JSON configuration...")
        
        try:
            # Parse JSON first to check for syntax errors
            raw_config_data = json.loads(json_content)
            print("✅ JSON parsed successfully")
            
            # Validate using ConfigManager with StringIO
            import io
            config_io = io.StringIO(json_content)
            validated_config = self.config_manager.load_config(config_io)
            print("✅ JSON configuration validated")
            
            # Print configuration summary
            print(f"   - Configuration name: {validated_config.get('metadata', {}).get('name', 'Unknown')}")
            print(f"   - Schema name: {validated_config.get('metadata', {}).get('schema_name', 'Unknown')}")
            print(f"   - Generation mode: {validated_config.get('generation_settings', {}).get('mode', 'Unknown')}")
            print(f"   - Element configs: {len(validated_config.get('element_configs', {}))}")
            print(f"   - Data contexts: {len(validated_config.get('data_contexts', {}))}")
            print(f"   - Smart relationships: {len(validated_config.get('smart_relationships', {}))}")
            
            return {
                'success': True,
                'config_data': validated_config,
                'raw_config': raw_config_data
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            return {'success': False, 'error': f"JSON parsing error: {e}"}
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return {'success': False, 'error': f"Configuration validation error: {e}"}
    
    def generate_xml(self, temp_xsd_path: str, config_data: Dict[str, Any], 
                    analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate XML using the same process as app.py."""
        print("🔧 Generating XML...")
        
        try:
            # Extract basic parameters from analysis (simulate UI selections)
            choices = analysis.get('choices', [])
            unbounded_elements = analysis.get('unbounded_elements', [])
            
            # Create default selections (simulate user choices)
            selected_choices = {}
            for i, choice in enumerate(choices):
                if choice.get('elements'):
                    selected_element = choice['elements'][0]['name']  # Select first choice
                    selected_choices[f"choice_{i}"] = {
                        'path': choice['path'],
                        'selected_element': selected_element,
                        'choice_data': choice
                    }
                    print(f"   - Auto-selected choice {i}: {selected_element} at {choice['path']}")
            
            unbounded_counts = {}
            for elem in unbounded_elements:
                unbounded_counts[elem['name']] = 2  # Default count of 2
                print(f"   - Set unbounded element '{elem['name']}' count to 2")
            
            # Get generation settings from config
            generation_settings = config_data.get('generation_settings', {})
            generation_mode = generation_settings.get('mode', 'Complete')
            
            print(f"   - Generation mode: {generation_mode}")
            print(f"   - Selected choices: {len(selected_choices)}")
            print(f"   - Unbounded counts: {len(unbounded_counts)}")
            
            # Create XMLGenerator with enhanced configuration (same as app.py)
            print("🔧 Initializing XMLGenerator with enhanced configuration...")
            generator = XMLGenerator(temp_xsd_path, config_data=config_data)
            print("✅ XMLGenerator initialized")
            
            # Generate XML (replicate app.py's generate_xml_from_xsd function)
            print("🔧 Calling generate_dummy_xml_with_options...")
            xml_content = generator.generate_dummy_xml_with_options(
                selected_choices=selected_choices,
                unbounded_counts=unbounded_counts,
                generation_mode=generation_mode,
                optional_selections=None,  # Use defaults
                custom_values=None  # Config data provides custom values
            )
            
            # Check if generation was successful (no error XML)
            if xml_content and not xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?><error>'):
                print(f"✅ XML generation successful!")
                print(f"   - XML length: {len(xml_content)} characters")
                print(f"   - XML lines: {xml_content.count(chr(10)) + 1}")
                
                # Print first few lines of XML for inspection
                xml_lines = xml_content.split('\n')
                print("📄 Generated XML preview (first 20 lines):")
                for i, line in enumerate(xml_lines[:20]):
                    print(f"   {i+1:2d}: {line}")
                if len(xml_lines) > 20:
                    print(f"   ... ({len(xml_lines) - 20} more lines)")
                
                return {
                    'success': True,
                    'xml_content': xml_content,
                    'generation_info': {
                        'selected_choices': selected_choices,
                        'unbounded_counts': unbounded_counts,
                        'generation_mode': generation_mode
                    }
                }
            else:
                print(f"❌ XML generation failed")
                if xml_content:
                    print(f"   Error XML: {xml_content[:200]}...")
                else:
                    print("   No XML content returned")
                    
                return {
                    'success': False,
                    'error': f"XML generation returned error content: {xml_content[:100]}..." if xml_content else "No XML content generated"
                }
                
        except Exception as e:
            print(f"❌ XML generation exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f"XML generation exception: {e}"
            }
    
    def validate_generated_xml(self, xml_content: str, temp_xsd_path: str) -> Dict[str, Any]:
        """Validate generated XML against XSD schema."""
        print("🔍 Validating generated XML...")
        
        try:
            validation_result = self.xml_validator.validate_xml_content(xml_content, temp_xsd_path)
            
            if validation_result['is_valid']:
                print("✅ XML validation successful - XML is valid!")
            else:
                print("❌ XML validation failed")
                errors = validation_result.get('errors', [])
                print(f"   - Total errors: {len(errors)}")
                for i, error in enumerate(errors[:5]):  # Show first 5 errors
                    print(f"   {i+1}: {error}")
                if len(errors) > 5:
                    print(f"   ... and {len(errors) - 5} more errors")
            
            return validation_result
            
        except Exception as e:
            print(f"❌ XML validation exception: {e}")
            return {
                'is_valid': False,
                'error': f"Validation exception: {e}"
            }
    
    def save_output_files(self, xml_content: str, temp_dir: str) -> Dict[str, str]:
        """Save generated XML and debug information to files."""
        print("💾 Saving output files...")
        
        output_files = {}
        
        # Save generated XML
        xml_output_path = os.path.join(temp_dir, "generated_output.xml")
        with open(xml_output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        output_files['xml'] = xml_output_path
        print(f"   - XML saved to: {xml_output_path}")
        
        # Create debug summary
        debug_info = {
            'timestamp': str(datetime.now()),
            'xml_length': len(xml_content),
            'xml_lines': xml_content.count('\n') + 1,
            'temp_directory': temp_dir
        }
        
        debug_path = os.path.join(temp_dir, "debug_info.json")
        with open(debug_path, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2)
        output_files['debug'] = debug_path
        print(f"   - Debug info saved to: {debug_path}")
        
        return output_files
    
    def generate_xml_without_config(self, temp_xsd_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate XML without JSON configuration for comparison."""
        print("🔧 Generating XML WITHOUT JSON config...")
        
        try:
            # Extract basic parameters from analysis
            choices = analysis.get('choices', [])
            unbounded_elements = analysis.get('unbounded_elements', [])
            
            # Create default selections
            selected_choices = {}
            for i, choice in enumerate(choices):
                if choice.get('elements'):
                    selected_element = choice['elements'][0]['name']
                    selected_choices[f"choice_{i}"] = {
                        'path': choice['path'],
                        'selected_element': selected_element,
                        'choice_data': choice
                    }
            
            unbounded_counts = {}
            for elem in unbounded_elements:
                unbounded_counts[elem['name']] = 2
            
            # Create XMLGenerator WITHOUT config_data
            generator = XMLGenerator(temp_xsd_path)
            
            # Generate XML with Complete mode but no custom config
            xml_content = generator.generate_dummy_xml_with_options(
                selected_choices=selected_choices,
                unbounded_counts=unbounded_counts,
                generation_mode="Complete",
                optional_selections=None,
                custom_values=None
            )
            
            return {
                'success': True,
                'xml_content': xml_content,
                'xml_length': len(xml_content),
                'xml_lines': xml_content.count('\n') + 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"XML generation without config failed: {e}"
            }
    
    def run_comparison_analysis(self, xsd_file_path: str, json_config_path: str) -> Dict[str, Any]:
        """Run comprehensive comparison between with/without JSON config."""
        print("=" * 80)
        print("🔄 COMPREHENSIVE XML GENERATION COMPARISON")
        print("=" * 80)
        
        results = {
            'with_config': {},
            'without_config': {},
            'comparison': {},
            'temp_dir': None
        }
        
        try:
            # Setup
            upload_result = self.simulate_file_upload(xsd_file_path, json_config_path)
            analysis_result = self.analyze_schema(upload_result['temp_xsd_path'])
            config_result = self.load_json_configuration(upload_result['json_content'])
            results['temp_dir'] = upload_result['temp_dir']
            
            if not all([upload_result.get('success'), analysis_result.get('success'), config_result.get('success')]):
                print(f"Setup failed - Upload: {upload_result.get('success')}, Analysis: {analysis_result.get('success')}, Config: {config_result.get('success')}")
                if not upload_result.get('success'):
                    print(f"Upload error: {upload_result.get('error')}")
                if not analysis_result.get('success'):
                    print(f"Analysis error: {analysis_result.get('error')}")
                if not config_result.get('success'):
                    print(f"Config error: {config_result.get('error')}")
                results['error'] = "Setup failed"
                return results
            
            print("\n" + "=" * 50)
            print("GENERATION 1: WITH JSON CONFIG")
            print("=" * 50)
            
            # Generate XML WITH config
            xml_with_config = self.generate_xml(
                upload_result['temp_xsd_path'],
                config_result['config_data'],
                analysis_result
            )
            
            if xml_with_config.get('success'):
                xml_content_with = xml_with_config['xml_content']
                
                # Analyze empty tags
                empty_analysis_with = self.count_empty_tags(xml_content_with)
                
                # Validate XML
                validation_with = self.validate_xml_against_xsd(xml_content_with, upload_result['temp_xsd_path'])
                
                results['with_config'] = {
                    'xml_length': len(xml_content_with),
                    'xml_lines': xml_content_with.count('\n') + 1,
                    'empty_analysis': empty_analysis_with,
                    'validation': validation_with
                }
                
                # Save XML with config
                with_config_path = os.path.join(upload_result['temp_dir'], "generated_with_config.xml")
                with open(with_config_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content_with)
                results['with_config']['file_path'] = with_config_path
            
            print("\n" + "=" * 50)
            print("GENERATION 2: WITHOUT JSON CONFIG")
            print("=" * 50)
            
            # Generate XML WITHOUT config
            xml_without_config = self.generate_xml_without_config(
                upload_result['temp_xsd_path'],
                analysis_result
            )
            
            if xml_without_config.get('success'):
                xml_content_without = xml_without_config['xml_content']
                
                # Analyze empty tags
                empty_analysis_without = self.count_empty_tags(xml_content_without)
                
                # Validate XML
                validation_without = self.validate_xml_against_xsd(xml_content_without, upload_result['temp_xsd_path'])
                
                results['without_config'] = {
                    'xml_length': len(xml_content_without),
                    'xml_lines': xml_content_without.count('\n') + 1,
                    'empty_analysis': empty_analysis_without,
                    'validation': validation_without
                }
                
                # Save XML without config
                without_config_path = os.path.join(upload_result['temp_dir'], "generated_without_config.xml")
                with open(without_config_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content_without)
                results['without_config']['file_path'] = without_config_path
            
            # Create comparison
            if results.get('with_config') and results.get('without_config'):
                with_empty = results['with_config']['empty_analysis']
                without_empty = results['without_config']['empty_analysis']
                with_validation = results['with_config']['validation']
                without_validation = results['without_config']['validation']
                
                results['comparison'] = {
                    'empty_tags_improvement': without_empty.get('empty_elements', 0) - with_empty.get('empty_elements', 0),
                    'validation_errors_improvement': without_validation.get('error_count', 0) - with_validation.get('error_count', 0),
                    'file_size_difference': results['with_config']['xml_length'] - results['without_config']['xml_length'],
                    'summary': {
                        'with_config_empty_tags': with_empty.get('empty_elements', 0),
                        'without_config_empty_tags': without_empty.get('empty_elements', 0),
                        'with_config_validation_errors': with_validation.get('error_count', 0),
                        'without_config_validation_errors': without_validation.get('error_count', 0)
                    }
                }
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results
    
    def run_complete_test(self, xsd_file_path: str, json_config_path: str) -> Dict[str, Any]:
        """Run complete end-to-end test simulation."""
        print("=" * 80)
        print("🚀 STARTING COMPLETE XML GENERATION DEBUG TEST")
        print("=" * 80)
        
        results = {
            'success': False,
            'steps': {},
            'files': {},
            'errors': []
        }
        
        temp_dir = None
        
        try:
            # Step 1: Simulate file upload
            print("\n" + "=" * 50)
            print("STEP 1: File Upload Simulation")
            print("=" * 50)
            
            upload_result = self.simulate_file_upload(xsd_file_path, json_config_path)
            results['steps']['file_upload'] = upload_result
            temp_dir = upload_result['temp_dir']
            
            # Step 2: Schema analysis
            print("\n" + "=" * 50)
            print("STEP 2: Schema Analysis")
            print("=" * 50)
            
            analysis_result = self.analyze_schema(upload_result['temp_xsd_path'])
            results['steps']['schema_analysis'] = analysis_result
            
            if not analysis_result['success']:
                results['errors'].append(f"Schema analysis failed: {analysis_result['error']}")
                return results
            
            # Step 3: JSON configuration loading
            print("\n" + "=" * 50)
            print("STEP 3: JSON Configuration Loading")
            print("=" * 50)
            
            config_result = self.load_json_configuration(upload_result['json_content'])
            results['steps']['config_loading'] = config_result
            
            if not config_result['success']:
                results['errors'].append(f"Config loading failed: {config_result['error']}")
                return results
            
            # Step 4: XML generation
            print("\n" + "=" * 50)
            print("STEP 4: XML Generation")
            print("=" * 50)
            
            xml_result = self.generate_xml(
                upload_result['temp_xsd_path'],
                config_result['config_data'],
                analysis_result
            )
            results['steps']['xml_generation'] = xml_result
            
            if not xml_result['success']:
                results['errors'].append(f"XML generation failed: {xml_result['error']}")
                return results
            
            # Step 5: XML validation
            print("\n" + "=" * 50)
            print("STEP 5: XML Validation")
            print("=" * 50)
            
            validation_result = self.validate_generated_xml(
                xml_result['xml_content'],
                upload_result['temp_xsd_path']
            )
            results['steps']['xml_validation'] = validation_result
            
            # Step 6: Save output files
            print("\n" + "=" * 50)
            print("STEP 6: Save Output Files")
            print("=" * 50)
            
            output_files = self.save_output_files(xml_result['xml_content'], temp_dir)
            results['files'] = output_files
            
            # Mark as successful
            results['success'] = True
            
            print("\n" + "=" * 80)
            print("🎉 XML GENERATION DEBUG TEST COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"✅ All steps completed successfully")
            print(f"📁 Temporary directory: {temp_dir}")
            print(f"📄 Generated XML: {output_files['xml']}")
            print(f"🔍 Debug info: {output_files['debug']}")
            
            if validation_result.get('is_valid'):
                print("✅ Generated XML is valid according to XSD schema")
            else:
                print("❌ Generated XML has validation errors")
                results['errors'].append("XML validation failed")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during test execution: {e}")
            import traceback
            traceback.print_exc()
            results['errors'].append(f"Critical error: {e}")
        
        finally:
            if temp_dir and not results['success']:
                print(f"🧹 Cleaning up temporary directory: {temp_dir}")
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
        
        return results


def print_comparison_summary(results: Dict[str, Any]):
    """Print detailed comparison summary."""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE COMPARISON RESULTS")
    print("=" * 80)
    
    if results.get('error'):
        print(f"❌ Comparison failed: {results['error']}")
        return
    
    with_config = results.get('with_config', {})
    without_config = results.get('without_config', {})
    comparison = results.get('comparison', {})
    
    if not with_config or not without_config:
        print("❌ Missing generation results for comparison")
        return
    
    print("\n📋 EMPTY TAGS ANALYSIS:")
    print(f"   With JSON Config:    {with_config['empty_analysis'].get('empty_elements', 0):4d} empty tags ({with_config['empty_analysis'].get('empty_percentage', 0):5.1f}%)")
    print(f"   Without JSON Config: {without_config['empty_analysis'].get('empty_elements', 0):4d} empty tags ({without_config['empty_analysis'].get('empty_percentage', 0):5.1f}%)")
    print(f"   Improvement:         {comparison.get('empty_tags_improvement', 0):4d} fewer empty tags with JSON config")
    
    print("\n🔍 XML VALIDATION ANALYSIS:")
    print(f"   With JSON Config:    {with_config['validation'].get('error_count', 0):4d} validation errors")
    print(f"   Without JSON Config: {without_config['validation'].get('error_count', 0):4d} validation errors")
    print(f"   Improvement:         {comparison.get('validation_errors_improvement', 0):4d} fewer errors with JSON config")
    
    print("\n📊 FILE SIZE ANALYSIS:")
    print(f"   With JSON Config:    {with_config.get('xml_length', 0):6d} characters ({with_config.get('xml_lines', 0):4d} lines)")
    print(f"   Without JSON Config: {without_config.get('xml_length', 0):6d} characters ({without_config.get('xml_lines', 0):4d} lines)")
    print(f"   Size difference:     {comparison.get('file_size_difference', 0):+6d} characters (positive = with config is larger)")
    
    # Show example empty tags
    if with_config['empty_analysis'].get('empty_element_list'):
        print("\n🔗 SAMPLE EMPTY TAGS (WITH CONFIG):")
        for tag in with_config['empty_analysis']['empty_element_list'][:10]:
            print(f"     {tag}")
    
    if without_config['empty_analysis'].get('empty_element_list'):
        print("\n🔗 SAMPLE EMPTY TAGS (WITHOUT CONFIG):")
        for tag in without_config['empty_analysis']['empty_element_list'][:10]:
            print(f"     {tag}")
    
    # Show validation errors
    if with_config['validation'].get('errors'):
        print("\n❌ SAMPLE VALIDATION ERRORS (WITH CONFIG):")
        for error in with_config['validation']['errors'][:5]:
            print(f"     {error}")
    
    if without_config['validation'].get('errors'):
        print("\n❌ SAMPLE VALIDATION ERRORS (WITHOUT CONFIG):")
        for error in without_config['validation']['errors'][:5]:
            print(f"     {error}")
    
    print(f"\n📁 GENERATED FILES:")
    if with_config.get('file_path'):
        print(f"   With Config:    {with_config['file_path']}")
    if without_config.get('file_path'):
        print(f"   Without Config: {without_config['file_path']}")
    if results.get('temp_dir'):
        print(f"   Directory:      {results['temp_dir']}")


def main():
    """Main function to run the standalone debugger with comprehensive comparison."""
    
    # File paths
    xsd_path = "/home/sidd/dev/xml_chunker/resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd"
    json_path = "/home/sidd/dev/xml_chunker/resource/orderCreate/test_data_config/sample_input_config.json"
    
    print("🔧 XML Generation Standalone Debugger with Comprehensive Analysis")
    print(f"XSD File: {xsd_path}")
    print(f"JSON Config: {json_path}")
    
    # Initialize debugger
    debugger = StandaloneXMLGenerationDebugger()
    
    # Run comprehensive comparison analysis
    results = debugger.run_comparison_analysis(xsd_path, json_path)
    
    # Print detailed comparison summary
    print_comparison_summary(results)


if __name__ == "__main__":
    main()