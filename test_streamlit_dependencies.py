#!/usr/bin/env python3
"""
Test if Streamlit dependency setup is working correctly.
"""

import tempfile
import os
import shutil
from config import get_config

def test_dependency_setup():
    """Test the setup_temp_directory_with_dependencies function."""
    
    print("🔍 Testing Streamlit Dependency Setup")
    print("=" * 50)
    
    # Step 1: Get config and resource directory
    config = get_config()
    resource_dir = config.get_resource_dir('iata')
    
    print(f"Resource directory: {resource_dir}")
    print(f"Resource dir exists: {os.path.exists(resource_dir)}")
    
    if os.path.exists(resource_dir):
        xsd_files = [f for f in os.listdir(resource_dir) if f.endswith('.xsd')]
        print(f"XSD files in resource dir: {len(xsd_files)}")
        print(f"Key files: {[f for f in xsd_files if 'Common' in f or 'OrderView' in f]}")
    
    # Step 2: Create temp directory and copy main file
    temp_dir = tempfile.mkdtemp()
    print(f"\nTemp directory: {temp_dir}")
    
    main_xsd_path = os.path.join(resource_dir, "IATA_OrderViewRS.xsd")
    temp_xsd_path = os.path.join(temp_dir, "IATA_OrderViewRS.xsd")
    
    # Copy main file
    shutil.copy2(main_xsd_path, temp_xsd_path)
    print(f"Copied main XSD to temp")
    
    # Step 3: Test the dependency setup function
    print(f"\n3. Testing dependency setup...")
    
    try:
        # Import and call the function using the new services
        from services.file_manager import FileManager
        
        file_manager = FileManager()
        file_manager.setup_temp_directory_with_dependencies(temp_xsd_path, "IATA_OrderViewRS.xsd")
        
        # Check what files are now in temp directory
        temp_files = os.listdir(temp_dir)
        xsd_files_in_temp = [f for f in temp_files if f.endswith('.xsd')]
        
        print(f"Files in temp after setup: {len(temp_files)}")
        print(f"XSD files in temp: {len(xsd_files_in_temp)}")
        
        # Check for key dependency
        common_types_exists = 'IATA_OffersAndOrdersCommonTypes.xsd' in xsd_files_in_temp
        print(f"CommonTypes dependency copied: {common_types_exists}")
        
        if common_types_exists:
            print("✅ Dependency setup working correctly")
        else:
            print("❌ Dependency setup missing CommonTypes file")
            print(f"Available XSD files: {xsd_files_in_temp}")
        
        # Step 4: Test XML generation with dependencies
        print(f"\n4. Testing XML generation with dependencies...")
        
        from utils.xml_generator import XMLGenerator
        
        try:
            generator = XMLGenerator(temp_xsd_path)
            print("✅ XMLGenerator created successfully with dependencies")
            
            # Test generation
            xml_content = generator.generate_dummy_xml_with_choices(
                selected_choices={"Response": True},
                unbounded_counts={}
            )
            
            if xml_content and xml_content.startswith('<?xml'):
                print(f"✅ XML generation successful: {len(xml_content)} chars")
                assert True  # Test passed
            else:
                print(f"❌ XML generation failed: {xml_content[:100]}...")
                assert False, f"XML generation failed: {xml_content[:100] if xml_content else 'No content'}"
                
        except Exception as gen_error:
            print(f"❌ XMLGenerator failed: {gen_error}")
            assert False, f"XMLGenerator failed: {gen_error}"
        
    except Exception as setup_error:
        print(f"❌ Dependency setup failed: {setup_error}")
        assert False, f"Dependency setup failed: {setup_error}"
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    try:
        test_dependency_setup()
        print("\n🎉 Streamlit dependencies working correctly!")
    except AssertionError as e:
        print(f"\n💥 Streamlit dependencies have issues! {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")