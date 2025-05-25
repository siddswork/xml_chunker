"""
Test script for XML Generator.
"""
from utils.xml_generator import XMLGenerator

def test_xml_generation():
    """Test XML generation with IATA_OrderCreateRQ.xsd."""
    xsd_path = 'resource/21_3_5_distribution_schemas/IATA_OrderCreateRQ.xsd'
    generator = XMLGenerator(xsd_path)
    xml_content = generator.generate_dummy_xml()
    print(xml_content)
    return xml_content

if __name__ == "__main__":
    test_xml_generation()
