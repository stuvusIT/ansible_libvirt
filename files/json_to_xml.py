#!/usr/bin/env python3

# This script converts a json file in a specific format to a xml file.
# It can either be run as the main script with the paramters given as commandline arguments
# or the method json_to_xml can be called from another python script.
#
# For this script to work the json must have the following form:
# Each XML element is a dict with the following keys:
#   name: mandatory, string, the name of the xml element
#   attrs: dict, the attributes of the xml element
#   content: string, number or list, the string (number is converted to string) in the element or a list of xml elements contained inside this one

from typing import Dict, Optional, Any
from numbers import Number
import sys
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

def process_dict_to_xml(data: Dict[str, Any], xml_parent: ET.Element = None) -> ET.Element:
    """
    Process the given dict of data (one element in the specified format) and convert it to xml elements.
      Parameters:
        data: A dict of data in the specified format to process into xml elements
        xml_parent: An optional parent for the element in the given data
      Returns: The resulting xml element
    """
    if not "name" in data:
        raise ValueError("The key name must be in every xml element description")
    name: str = data["name"]
    if not isinstance(name, str):
        raise ValueError("The name must be a string")
    child: ET.Element = ET.Element(name)
    if xml_parent is not None:
        xml_parent.append(child)
    if "attrs" in data:
        attrs = data["attrs"]
        if isinstance(attrs, dict):
            for k, v in attrs.items():
                child.attrib[str(k)] = str(v)
        else:
            raise ValueError("[%s] attrs must be a dict" % name)
    if "content" in data:
        content = data["content"]
        if isinstance(content, str):
            child.text = content
        elif isinstance(content, Number):
            child.text = str(content)
        elif isinstance(content, list):
            for element in content:
                process_dict_to_xml(element, child)
        else:
            raise ValueError("[%s] content must be a string, int or" % name)
    return child

def json_to_xml(json_file: str, dest_file: Optional[str] = None) -> str:
    """
    Convert the given json file to xml and save it as the given dest_file.
      Parameters:
        json_file: The file with the json to convert
        dest_file: [Default: None] The file to save the resulting xml in.
                   When None is given, will generate a filename from the json filename,
                   by removing .json from the end and adding .xml.

      Returns: The path of the xml file created
    """
    real_dest_file: str = dest_file
    if not dest_file:
        real_dest_file = json_file
        if real_dest_file.endswith(".json"):
            real_dest_file = real_dest_file[:-5]
        real_dest_file += ".xml"

    data: Dict[str, Any]
    with open(json_file, 'r') as f:
        data = json.load(f)

    root: ET.Element = process_dict_to_xml(data)
    xml_string = ET.tostring(root)
    xmlstr = minidom.parseString(xml_string).toprettyxml(indent="   ")
    with open(real_dest_file, "w") as f:
        f.write(xmlstr)

    return real_dest_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Need at least one argument: The json file to convert.")
        print("Possible second argument is: The filename for the resulting xml file.")
        exit(11)
    if len(sys.argv) > 3:
        print("Expected at maximum 2 arguments: The json file to convert and optionally the resulting xml file")
        exit(12)
    dest_file: Optional[str] = None
    if len(sys.argv) == 3:
        dest_file = sys.argv[2]
    json_to_xml(sys.argv[1], dest_file)
