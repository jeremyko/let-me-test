#-*- coding: utf-8 -*-

"""
xml config handling 
"""

#202007 kojh create
try:
    import xml.etree.cElementTree as ET
except ImportError:
    print ("ImportError")
    import xml.etree.ElementTree as ET

import os
from pexpect import pxssh
from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_remote

#///////////////////////////////////////////////////////////////////////////////
# auto backup      --> when one tspec begins.
# auto rollback    --> when one tspec ends..
#///////////////////////////////////////////////////////////////////////////////
def set_xml_cfg_ems(runner_ctx, xpath, val):
    local_xml_path = "{}/{}".format(runner_ctx.temp_internal_use_only_dir_remote, os.path.basename(runner_ctx.ems_xml_cfg_path))
    if(runner_ctx.ems_is_xml_config_changed == False):
        # set_xml_cfg 이 여러번 호출되는 경우 고려.
        # -> 최초로 set_xml_cfg 호출됬을때만 한번 backup 수행 
        runner_ctx.logger.debug("{}BACKUP ems xml cfg".format(runner_ctx.cur_indent))
        #runner_ctx.backup_config() 
        lmt_remote.backup_remote_file(runner_ctx, runner_ctx.ems_ip,runner_ctx.ems_id, runner_ctx.ems_passwd, runner_ctx.ems_xml_cfg_path)
        runner_ctx.ems_is_xml_config_changed = True
    
    runner_ctx.logger.info("{}ems config path = {}".format(runner_ctx.cur_indent, runner_ctx.ems_xml_cfg_path))
    lmt_remote.get_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd, runner_ctx.ems_xml_cfg_path)
    set_xml_cfg_this_path(runner_ctx, local_xml_path, xpath, val)

    remote_path = os.path.dirname(runner_ctx.ems_xml_cfg_path)
    lmt_remote.put_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd, remote_path, 
            runner_ctx.temp_internal_use_only_dir_remote, os.path.basename(local_xml_path), os.path.basename(local_xml_path))

#///////////////////////////////////////////////////////////////////////////////
def set_xml_cfg(runner_ctx, xpath, val):
    if(runner_ctx.is_xml_config_changed == False):
        # set_xml_cfg 이 여러번 호출되는 경우 고려.
        # -> 최초로 set_xml_cfg 호출됬을때만 한번 backup 수행 
        runner_ctx.logger.debug("{}BACKUP xml cfg".format(runner_ctx.cur_indent))
        runner_ctx.backup_config() 
        runner_ctx.is_xml_config_changed = True
    set_xml_cfg_this_path(runner_ctx, runner_ctx.xml_cfg_path, xpath, val)

#///////////////////////////////////////////////////////////////////////////////
def set_xml_cfg_this_path(runner_ctx, file_path, xpath, val):

    xpath = lmt_util.replace_all_symbols(runner_ctx,xpath)

    runner_ctx.logger.debug("{}xml_cfg_path = {}".format(runner_ctx.cur_indent,file_path))
    runner_ctx.logger.debug("{}xpath = {}".format(runner_ctx.cur_indent,xpath))
    try:
        #------------------------------
        doc = ET.parse(file_path)
        #------------------------------
        #doc = ET.parse("error.xml")

    except Exception as e:
        err_msg = 'xml parse failed {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc is None):
        runner_ctx.logger.error("{}parse failed ".format(runner_ctx.cur_indent))
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root is None):
            err_msg = "xml getroot failed"
            runner_ctx.logger.error(err_msg)
            raise lmt_exception.LmtException(err_msg)
    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    tmp_xpath =  './' + xpath # root + xpath
    #tmp_xpath = './/' + 'DB_CONNECT_INFO/USER_ID' # OK
    #tmp_xpath = './' + 'COMMON/DB_CONNECT_INFO/USER_ID' # OK

    try:
        xml_nodes = xml_root.findall(tmp_xpath)
        if xml_nodes is None:
            err_msg = "findall failed = {}".format(tmp_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,tmp_xpath))
            raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = {}".format(tmp_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)

        #print xml_nodes
        config_val = xml_nodes[0].text
        runner_ctx.logger.debug("{}old value = {}".format(runner_ctx.cur_indent,config_val))
        runner_ctx.logger.debug("{}new value = {}".format(runner_ctx.cur_indent,val))
        #------------------------
        # XXX change value XXX 
        xml_nodes[0].text = val
        #------------------------

        #last_updated = ET.SubElement(xml_nodes[0], "test_new")
        #last_updated.text = 'TEST'

        #write file
        #doc.write(runner_ctx.xml_cfg_path, encoding="utf-8", xml_declaration=True)
        doc.write(file_path)
    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise

    return True


#///////////////////////////////////////////////////////////////////////////////
def get_xml_cfg_ems(runner_ctx, xpath):
    xml_path = "{}/{}".format(runner_ctx.temp_internal_use_only_dir_remote, os.path.basename(runner_ctx.xml_cfg_path))
    lmt_remote.get_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd, runner_ctx.ems_xml_cfg_path)
    out = get_xml_cfg_this_path(runner_ctx, xml_path, xpath)
    return out

#///////////////////////////////////////////////////////////////////////////////
def get_xml_cfg(runner_ctx, xpath):
    out = get_xml_cfg_this_path(runner_ctx, runner_ctx.xml_cfg_path, xpath)
    return out

#///////////////////////////////////////////////////////////////////////////////
def get_xml_cfg_this_path(runner_ctx, file_path, xpath):

    xpath = lmt_util.replace_all_symbols(runner_ctx,xpath)
    runner_ctx.logger.debug("{}xml_cfg_path = {}".format(runner_ctx.cur_indent,file_path))
    runner_ctx.logger.debug("{}xpath = {}".format(runner_ctx.cur_indent,xpath))
    try:
        #------------------------------
        doc = ET.parse(file_path)
        #------------------------------

    except Exception as e:
        err_msg = 'xml parse failed :{} -> {} :{}'.format(file_path, e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc is None):
        runner_ctx.logger.error("parse failed ")
        return None

    try:
        xml_root = doc.getroot()
        if(xml_root is None):
            err_msg = "xml getroot failed"
            runner_ctx.logger.error(err_msg)
            raise lmt_exception.LmtException(err_msg)
    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    tmp_xpath =  './' + xpath # root + xpath
    #tmp_xpath = './/' + 'DB_CONNECT_INFO/USER_ID' # OK
    #tmp_xpath = './' + 'COMMON/DB_CONNECT_INFO/USER_ID' # OK

    try:
        xml_nodes = xml_root.findall(tmp_xpath)
        if xml_nodes is None:
            err_msg = "findall failed = {}".format(tmp_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,tmp_xpath))
            return None # no error ! this is just get function
            #raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = [{}] get just failed.".format(tmp_xpath)
            runner_ctx.logger.warning("{}{}".format(runner_ctx.cur_indent,err_msg))
            return None # no error ! this is just get function
            #raise lmt_exception.LmtException(err_msg)

        config_val = xml_nodes[0].text
        runner_ctx.logger.info("{}{}={}".format(runner_ctx.cur_indent,xpath, config_val))
        return config_val 

    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}".format(err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner_ctx.logger.error("{}".format(err_msg))
        raise

    return None


