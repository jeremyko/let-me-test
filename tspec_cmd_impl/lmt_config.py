"""
xml, init config handling 
"""

from core import lmt_exception
import xml.etree.ElementTree as ET

#///////////////////////////////////////////////////////////////////////////////
def set_cfg(logger,path, xpath, val):
    doc = ET.parse(path)
    root = doc.getroot()
    #TODO
