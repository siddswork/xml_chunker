import streamlit as st
import xml.etree.ElementTree as ET
import json

def xml_to_dict(element):
    result = {}
    if element.text and element.text.strip():
        result['text'] = element.text.strip()
    if element.attrib:
        result['attributes'] = element.attrib
    if len(element) > 0:
        result['children'] = {}
        for child in element:
            if child.tag in result['children']:
                if not isinstance(result['children'][child.tag], list):
                    result['children'][child.tag] = [result['children'][child.tag]]
                result['children'][child.tag].append(xml_to_dict(child))
            else:
                result['children'][child.tag] = xml_to_dict(child)
    return result

# Usage
xml_string = """<root><item id="1">Text</item><item id="2">More text</item></root>"""
root = ET.fromstring(xml_string)
tree_dict = xml_to_dict(root)
st.json(tree_dict)