#!/usr/bin/env python3
"""
Debug the actual XML generation flow to see why FlightNumberTextType isn't being used.
"""

from utils.xml_generator import XMLGenerator
import xmlschema

# Monkey patch to add debugging
original_generate_value = XMLGenerator._generate_value_for_type

def debug_generate_value_for_type(self, type_name, element_name: str = ""):
    """Debug wrapper for _generate_value_for_type."""
    
    # Check if this is the element we're interested in
    if 'MarketingCarrierFlightNumberText' in element_name:
        print(f"\n=== DEBUG: Generating value for {element_name} ===")
        print(f"Type name: {type_name}")
        print(f"Type object: {type(type_name)}")
        
        if hasattr(type_name, 'name'):
            print(f"Type name attribute: {type_name.name}")
        
        # Check constraints extraction
        constraints = self._extract_type_constraints(type_name)
        print(f"Extracted constraints: {constraints}")
        
        # Check what generator will be created
        generator = self.type_factory.create_generator(type_name, constraints)
        print(f"Created generator: {type(generator)}")
        
        # Generate and show result
        result = generator.generate(element_name, constraints)
        print(f"Generated result: {result}")
        print("=== END DEBUG ===\n")
        
        return result
    
    # Call original for other elements
    return original_generate_value(self, type_name, element_name)

# Apply monkey patch
XMLGenerator._generate_value_for_type = debug_generate_value_for_type

def test_generation_flow():
    """Test the generation flow with debugging."""
    
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    generator = XMLGenerator(schema_path)
    
    print("=== Testing XML Generation Flow ===")
    
    # Generate a small XML with debugging
    generator.user_unbounded_counts = {}  # Keep it small
    xml_data = generator.generate_dummy_xml_with_choices(selected_choices={"Response": True})
    
    if xml_data:
        print(f"Generated XML size: {len(xml_data)} characters")
        
        # Check if the XML contains the problematic element
        if 'MarketingCarrierFlightNumberText' in xml_data:
            print("XML contains MarketingCarrierFlightNumberText")
            
            # Extract the value
            import re
            match = re.search(r'<[^>]*MarketingCarrierFlightNumberText[^>]*>([^<]*)</[^>]*MarketingCarrierFlightNumberText', xml_data)
            if match:
                value = match.group(1)
                print(f"Value in XML: '{value}'")
            else:
                print("Could not extract value from XML")
        else:
            print("XML does not contain MarketingCarrierFlightNumberText")
    else:
        print("Failed to generate XML")

if __name__ == "__main__":
    test_generation_flow()