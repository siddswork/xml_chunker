#!/usr/bin/env python3
"""
Test enumeration value tracking and rotation functionality.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import EnumerationTypeGenerator

def test_enum_tracking():
    """Test enumeration value tracking and smart selection."""
    schema_path = "resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd"
    
    try:
        generator = XMLGenerator(schema_path)
        
        print("🔍 Testing Enumeration Value Tracking")
        print("=" * 50)
        
        # Reset tracker for clean test
        EnumerationTypeGenerator.reset_usage_tracker()
        
        # Get ActionCodeContentType for testing
        for import_url, imported_schema in generator.schema.imports.items():
            if 'CommonTypes' in import_url:
                if 'ActionCodeContentType' in imported_schema.types:
                    type_obj = imported_schema.types['ActionCodeContentType']
                    
                    # Extract constraints
                    constraints = generator._extract_type_constraints(type_obj)
                    print(f"Available enum values: {constraints['enum_values']}")
                    
                    # Create generator
                    enum_gen = EnumerationTypeGenerator(generator.config)
                    
                    # Generate multiple values to test tracking
                    print(f"\n🧪 Testing value rotation:")
                    generated_values = []
                    for i in range(8):  # Generate more than available enum values
                        value = enum_gen.generate("ActionCode", constraints)
                        generated_values.append(value)
                        print(f"  Generation {i+1}: '{value}'")
                    
                    print(f"\n📊 Generated values: {generated_values}")
                    print(f"Unique values used: {set(generated_values)}")
                    
                    # Show usage statistics
                    stats = EnumerationTypeGenerator.get_usage_stats()
                    print(f"\n📈 Usage Statistics:")
                    for key, usage in stats.items():
                        print(f"  {key}: {usage}")
                    
                    # Test with different enum type
                    print(f"\n🧪 Testing different enum type (BagRuleCode):")
                    if 'BagRuleCodeContentType' in imported_schema.types:
                        bag_type = imported_schema.types['BagRuleCodeContentType']
                        bag_constraints = generator._extract_type_constraints(bag_type)
                        
                        bag_values = []
                        for i in range(6):
                            value = enum_gen.generate("BagRuleCode", bag_constraints)
                            bag_values.append(value)
                            print(f"  BagRule {i+1}: '{value}'")
                        
                        print(f"BagRule values: {bag_values}")
                    
                    # Final statistics
                    final_stats = EnumerationTypeGenerator.get_usage_stats()
                    print(f"\n📈 Final Usage Statistics:")
                    for key, usage in final_stats.items():
                        print(f"  {key}: {usage}")
                    
                    break
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enum_tracking()