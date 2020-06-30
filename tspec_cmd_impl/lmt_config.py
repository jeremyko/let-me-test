"""
xml config handling 
"""

from core import lmt_exception
import xml.etree.ElementTree as ET

#///////////////////////////////////////////////////////////////////////////////
# auto backup      --> when one tspec begins.
# auto rollback    --> when one tspec ends..
# manual rollback  --> user 
#///////////////////////////////////////////////////////////////////////////////
def set_cfg(runner, xpath, val):
    runner.logger.debug("xml_cfg_path = {}".format(runner.xml_cfg_path))
    runner.logger.debug("xpath = {}".format(xpath))
    try:
        doc = ET.parse(runner.xml_cfg_path)
        #doc = ET.parse("error.xml")

    except Exception as e:
        err_msg = 'xml parse failed {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("{}".format(err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc == None):
        runner.logger.error("parse failed ")
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root == None):
            err_msg = "xml getroot failed"
            runner.logger.error(err_msg)
            raise lmt_exception.LmtException(err_msg)
    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("{}".format(err_msg))
        raise lmt_exception.LmtException(err_msg)

    tmp_xpath =  './' + xpath # root + xpath
    #tmp_xpath = './/' + 'DB_CONNECT_INFO/USER_ID' # OK
    #tmp_xpath = './' + 'COMMON/DB_CONNECT_INFO/USER_ID' # OK

    try:
        xml_nodes = xml_root.findall(tmp_xpath)
        if xml_nodes == None:
            err_msg = "findall failed = {}".format(tmp_xpath)
            runner.logger.error("{}".format(tmp_xpath))
            raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = {}".format(tmp_xpath)
            runner.logger.error("{}".format(err_msg))
            raise lmt_exception.LmtException(err_msg)

        #print xml_nodes
        config_val = xml_nodes[0].text
        runner.logger.debug("before = {}".format(config_val))
        #------------------------
        # XXX change value XXX 
        xml_nodes[0].text = val
        #------------------------

        #last_updated = ET.SubElement(xml_nodes[0], "test_new")
        #last_updated.text = 'TEST'

        #write file
        doc.write(runner.xml_cfg_path, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("{}".format(err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner.logger.error("{}".format(err_msg))
        raise

    return True
