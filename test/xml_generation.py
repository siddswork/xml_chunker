import os
import xmlschema

def get_all_schemas_from_xsd(xsd: xmlschema.XMLSchema):
    # Accessing information about the schema itself (from the xs:schema tag)
    print(f"Schema Target Namespace: {schema.target_namespace}")
    print(f"Schema Version: {schema.version}")
    print(f"Schema ID: {schema.id}")
    print(f"Schema elementFormDefault: {schema.default_attributes.get('elementFormDefault')}")



def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the relative path to the XSD file
    xsd_path = os.path.join(script_dir, '..', 'resource', '21_3_5_distribution_schemas', 'temp_IATA_OrderViewRS.xsd')
    xsd_path = os.path.abspath(xsd_path)

    print(f"Loading XSD from: {xsd_path}")

    try:
        schema = xmlschema.XMLSchema(xsd_path)
        print("XSD loaded successfully.")
        print(f"Root elements: {list(schema.elements.keys())}")
        get_all_schemas_from_xsd(schema)
    except Exception as e:
        print(f"Failed to load XSD: {e}")

if __name__ == "__main__":
    main()