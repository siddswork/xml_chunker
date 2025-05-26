import os
import sys
import tempfile
import xmlschema

def get_all_schemas_from_xsd(xsd: xmlschema.XMLSchema):
    # Accessing information about the schema itself (from the xs:schema tag)
    print(f"Schema Target Namespace: {schema.target_namespace}")
    print(f"Schema Version: {schema.version}")
    print(f"Schema ID: {schema.id}")
    print(f"Schema elementFormDefault: {schema.default_attributes.get('elementFormDefault')}")



def main():
    try:

        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the relative path to the XSD file
        xsd_path = os.path.join(script_dir, '..', 'resource', '21_3_5_distribution_schemas', 'temp_IATA_OrderViewRS.xsd')
        xsd_path = os.path.abspath(xsd_path)

        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(uploaded_file.getvalue())

        resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resource', '21_3_5_distribution_schemas')
        print(f"Resource directory: {resource_dir}")

        if os.path.exists(resource_dir):
            temp_dir = os.path.dirname(xsd_path)
            
            for filename in os.listdir(resource_dir):
                if filename.endswith('.xsd') and filename != xsd_file_name:
                    src_path = os.path.join(resource_dir, filename)
                    dst_path = os.path.join(temp_dir, filename)
                    with open(src_path, 'rb') as src_file:
                        with open(dst_path, 'wb') as dst_file:
                            dst_file.write(src_file.read())

        print(f"Loading XSD from: {xsd_path}")

        try:
            schema = xmlschema.XMLSchema(xsd_path)
            print("XSD loaded successfully.")
            print(f"Root elements: {list(schema.elements.keys())}")
            get_all_schemas_from_xsd(schema)
        except Exception as e:
            print(f"Failed to load XSD: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main_2():
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        arguments = sys.argv[1:]
        if len(arguments) == 0:
            print("No arguments provided.")
            return
        if len(arguments) > 1:
            print("Too many arguments provided.")
            return
        if not arguments[0].endswith('.xsd'):
            print("Invalid XSD file provided.")
            return
        
        xsd_file_name = arguments[0]
        xsd_abs_file_path = os.path.abspath(xsd_file_name)
        xsd_file_name = os.path.basename(xsd_abs_file_path)
        xsd_file_dir = os.path.dirname(xsd_abs_file_path)
        print(f"Input XSD file name: {xsd_file_name}")
        print(f"Input XSD file path: {xsd_abs_file_path}")
        print(f"Input XSD file directory: {xsd_file_dir}")

        resource_dir = xsd_file_dir

        # Copy the XSD file to a temporary working directory
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, xsd_file_name)
        print(f"Temporary file path: {temp_file_path}")
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(open(xsd_abs_file_path, 'rb').read())

        if os.path.exists(resource_dir):
            for filename in os.listdir(resource_dir):
                if filename.endswith('.xsd') and filename != xsd_file_name:
                    src_path = os.path.join(resource_dir, filename)
                    dst_path = os.path.join(temp_dir, filename)
                    with open(src_path, 'rb') as src_file:
                        with open(dst_path, 'wb') as dst_file:
                            dst_file.write(src_file.read())

        # Print the contents of the temporary directory
        print(f"Files in {temp_dir}:")
        for filename in os.listdir(temp_dir):
            print(f" - {filename}")

        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
    except Exception as e:
        print(f"An error occurred in main_2: {e}")

if __name__ == "__main__":
    main_2()