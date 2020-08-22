#!/usr/bin/env python3

# This script defines a libvirt domain from a json file in a specific format.
# It can either be run as the main script with the paramter given as commandline arguments
# or the method define_dom_from_json can be called from another python script.
#
# Remember that the domain must be rebooted for most changes to take effect.
#
# For this script to work the json must have the following form:
# Each XML element is a dict with the following keys:
#   name: mandatory, string, the name of the xml element
#   attrs: dict, the attributes of the xml element
#   content: string, number or list, the string (number is converted to string) in the element or a list of xml elements contained inside this one
#
# The described xml must be in the format described here: https://libvirt.org/formatdomain.html


import sys
import libvirt
import json_to_xml

def fail(message: str, code: int):
    print(message)
    exit(code)

def define_dom_from_json(dom_json_file: str) -> None:
    """
    Define a libvirt domain from the given json file
      Parameters:
        dom_json_file: The json file from which to the define the domain
      Returns: None
    """

    dom_xml_file: str = json_to_xml.json_to_xml(dom_json_file)

    dom_xml: str
    with open(dom_xml_file, 'r') as f:
        dom_xml = f.read()

    conn: libvirt.virConnect = libvirt.open()
    if conn == None:
        fail('Failed to open connection to the libvirt deamon', 101)
    try:
        domain: libvirt.virDomain = conn.defineXMLFlags(dom_xml, libvirt.VIR_DOMAIN_DEFINE_VALIDATE)
        domain.__del__()
    except:
        error: libvirt.libvirtError = conn.virConnGetLastError()

        if error[0] == libvirt.VIR_ERR_XML_DETAIL:
            fail('Failed to define domain beacuse the xml is not valid xml.', 102)
        if error[0] == libvirt.VIR_ERR_XML_INVALID_SCHEMA:
            fail('Failed to define domain beacuse the xml does not validate against the schema.', 103)

        fail('Failed to define domain. Error code:' + str(error[0]), 104)
    finally:
        conn.__del__()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need exactly one argument: The json file to define the domain from.")
        exit(11)
    define_dom_from_json(sys.argv[1])
