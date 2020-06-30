"""
xml config handling 
"""

from core import lmt_exception
import xml.etree.ElementTree as ET

#TODO backup config first --> when tspec begins.
#TODO auto rollback       --> when tspec file ends..
#TODO manual rollback     --> user 

#///////////////////////////////////////////////////////////////////////////////
def set_cfg(runner, xpath, val):
    runner.logger.info("xpath = {}".format(xpath))
    try:
        doc = ET.parse('/root/CFG/NMD_Config.xml')
    except Exception as e:
        err_msg = 'exception : {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("parse failed = {}".format(err_msg))
        return False

    if(doc == None):
        runner.logger.error("parse failed ")
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root == None):
            runner.logger.error("getroot failed ")
            return False
    except Exception as e:
        err_msg = 'exception : {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("getroot failed = {}".format(err_msg))
        return False

    tmp_xpath =  './' + xpath # root + xpath
    #tmp_xpath = './/' + 'DB_CONNECT_INFO/USER_ID' # OK
    #tmp_xpath = './' + 'COMMON/DB_CONNECT_INFO/USER_ID' # OK

    try:
        xml_nodes = xml_root.findall(tmp_xpath)
        if xml_nodes == None:
            runner.logger.error("findall failed = {}".format(tmp_xpath))
            return False
        #print xml_nodes
        config_val = xml_nodes[0].text
        runner.logger.debug("config_val = {}".format(config_val))
    except Exception as e:
        err_msg = 'exception : {} :{}'.format(e.__doc__, e.message)
        runner.logger.error("findall failed = {}".format(err_msg))
        return False
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner.logger.error("findall failed = {}".format(err_msg))
        print err_msg
        return False

    return True
