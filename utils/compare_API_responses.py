import time
import logging
from .send_request import make_api_request  # make sure import path is correct

logger = logging.getLogger(__name__)

# -------------------------------
# JSON / XML Comparison
# -------------------------------
def compare_json_schemas(json1, json2):
    """Compare JSON keys at the top level."""
    return set(json1.keys()) == set(json2.keys())

def compare_xml_tags(xml_str1, xml_str2):
    """Compare XML tags at root and first level."""
    import xml.etree.ElementTree as ET
    root1 = ET.fromstring(xml_str1)
    root2 = ET.fromstring(xml_str2)
    tags1 = {child.tag for child in root1}
    tags2 = {child.tag for child in root2}
    return tags1 == tags2

