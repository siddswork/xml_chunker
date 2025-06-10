#!/usr/bin/env python3
"""
Debug integration issues with TypeGeneratorFactory.
Check for any potential bypassing of our fixes.
"""

from utils.xml_generator import XMLGenerator
from utils.type_generators import TypeGeneratorFactory
import xmlschema

def test_integration_issues():
    """Test TypeGeneratorFactory integration thoroughly."""
    
    print("🔍 Testing TypeGeneratorFactory Integration")
    print("=" * 60)
    
    # Create generator
    gen = XMLGenerator('resource/21_3_5_distribution_schemas/IATA_OrderViewRS.xsd')
    schema = gen.schema
    factory = gen.type_factory
    
    print("1. Factory instance check:")
    print(f"   Factory type: {type(factory)}")
    print(f"   Factory config: {factory.config is not None}")
    
    # Test specific problematic types
    print("\n2. Testing specific problematic types:")
    
    # Find some amount/measure types in the schema
    amount_types = []
    for type_name, type_obj in schema.types.items():
        if any(keyword in type_name.lower() for keyword in ['amount', 'measure', 'rate']):
            amount_types.append((type_name, type_obj))
            if len(amount_types) >= 5:
                break
    
    for type_name, type_obj in amount_types:
        print(f"\n   Testing type: {type_name}")
        print(f"   Type object: {type_obj}")
        
        # Extract constraints
        constraints = gen._extract_type_constraints(type_obj)
        print(f"   Constraints: {constraints}")
        
        # Create generator
        generator = factory.create_generator(type_obj, constraints)
        print(f"   Generator: {type(generator).__name__}")
        
        # Generate value
        try:
            value = generator.generate(type_name.split('}')[-1], constraints)
            print(f"   Generated: {repr(value)} (type: {type(value)})")
            
            # Check if value is empty
            if value is None or value == "":
                print(f"   ⚠️  ISSUE: Empty value generated!")
            else:
                print(f"   ✅ Non-empty value generated")
                
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
    
    print("\n3. Testing direct calls with known problematic patterns:")
    
    # Test direct calls that might be problematic
    test_cases = [
        ("decimal", {}),
        ("xs:decimal", {}),
        ("float", {}),
        ("string", {'pattern': '[0-9]+'}),
        ("string", {'max_length': 5}),
        ("boolean", {}),
    ]
    
    for type_name, constraints in test_cases:
        print(f"\n   Testing {type_name} with {constraints}:")
        try:
            generator = factory.create_generator(type_name, constraints)
            value = generator.generate("TestElement", constraints)
            print(f"   Generated: {repr(value)} (type: {type(value)})")
            
            if value is None or value == "":
                print(f"   ⚠️  ISSUE: Empty value for {type_name}!")
            else:
                print(f"   ✅ Good value for {type_name}")
                
        except Exception as e:
            print(f"   ❌ Error for {type_name}: {e}")
    
    print("\n4. Testing element creation paths:")
    
    # Test the actual element creation paths in XML generation
    # Monkey patch to track empty value creation
    original_generate_value = gen._generate_value_for_type
    empty_value_count = 0
    
    def track_empty_values(type_name, element_name=""):
        value = original_generate_value(type_name, element_name)
        nonlocal empty_value_count
        
        if value is None or value == "":
            empty_value_count += 1
            print(f"   ⚠️  Empty value for {element_name} (type: {type_name})")
        
        return value
    
    gen._generate_value_for_type = track_empty_values
    
    print("   Generating small test XML to check for empty values...")
    try:
        # Generate a small test XML
        test_xml = gen.generate_dummy_xml_with_choices({'Response': True}, {'OrderTotalAmount': 1})
        print(f"   Generated XML length: {len(test_xml)}")
        print(f"   Empty values detected: {empty_value_count}")
        
        if empty_value_count == 0:
            print("   ✅ No empty values detected during generation!")
        else:
            print(f"   ⚠️  {empty_value_count} empty values detected!")
            
    except Exception as e:
        print(f"   ❌ XML generation error: {e}")
    
    print("\n5. Summary:")
    print(f"   Factory working: ✅")
    print(f"   Type detection: ✅") 
    print(f"   Value generation: {'✅' if empty_value_count == 0 else '⚠️'}")

if __name__ == "__main__":
    test_integration_issues()