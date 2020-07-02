#-*- coding: utf-8 -*-

"""
xml db handling 
"""

import os
import shutil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    print "ImportError"
    import xml.etree.ElementTree as ET

from core import lmt_exception
from core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
#    replace_xml_db_file  (테스트로 사용할 파일경로, table명)
#ex) replace_xml_db_file("${TEST_DATA_DIR}/test_xml_db_files/T_DATA_FORMAT.xml", "T_DATA_FORMAT" )
#///////////////////////////////////////////////////////////////////////////////
def replace_xml_db_file (runner_ctx, testing_file_path_full, table_name):
    testing_file_path_full = lmt_util.replace_all_symbols(runner_ctx,testing_file_path_full)
    runner_ctx.logger.debug("resolved xml db : {}".format(testing_file_path_full))
    #파일 교체 전, 백업
    existing_old_path_full = runner_ctx.xml_db_path + os.sep + table_name +".xml"
    if(table_name in runner_ctx.change_xml_dbs.keys()) :    
        # 동일한 xml db table 명으로 set_xml_db 등과 함께 여러번 호출되는 경우 고려.
        runner_ctx.logger.debug("already backed up..{}".format(table_name+".xml"))
    else:
        runner_ctx.change_xml_dbs[table_name] = True
        runner_ctx.logger.debug("BACKUP xml db {}".format(table_name))
        runner_ctx.backup_xml_db(existing_old_path_full, table_name) 

    runner_ctx.logger.debug("replace xml db : from ={}".format(testing_file_path_full))
    runner_ctx.logger.debug("replace xml db : to   ={}".format(existing_old_path_full))
    #replace file
    shutil.copyfile(testing_file_path_full, existing_old_path_full)
    return True


#///////////////////////////////////////////////////////////////////////////////
# ex) ofcs_error_code 필드의 ALLOW_SPACE 속성을 Y 로 변경 :
#    set_xml_db(" T_DATA_FORMAT ", " ALLOW_SPACE ", " Y ", 
#        SERVICE_ID='000009', 
#        DATA_NAME='SOFCS_CMP_META', 
#        STRUCTURE_CD='1', 
#        FIELD_NAME='ofcs_error_code')
#///////////////////////////////////////////////////////////////////////////////
def set_xml_db(runner_ctx, *args):

    # arg[0] -> list -> table, attr, val 
    # arg[1] -> dic  -> db where conditions 

    for arg in args:
        runner_ctx.logger.debug("{}".format(arg))
    table           = args[0][0].strip()
    attr_field      = args[0][1]
    val             = args[0][2]
    where_conditons = args[1]

    table_path_full = runner_ctx.xml_db_path + os.sep + table +".xml"
    attr_field      = attr_field.strip()
    val             = val.strip()
    runner_ctx.logger.debug("table      [{}]".format(table_path_full))
    runner_ctx.logger.debug("attr_field [{}]".format(attr_field))
    runner_ctx.logger.debug("val        [{}]".format(val  ))
    all_condition_cnt = len(where_conditons)
    runner_ctx.logger.debug("all_condition_cnt = {}".format(all_condition_cnt))

    if(table in runner_ctx.change_xml_dbs.keys()) :    
        # 동일한 xml db table 명으로 set_xml_db 이 여러번 호출되는 경우 고려.
        runner_ctx.logger.debug("already backed up..{}".format(table+".xml"))
    else:
        runner_ctx.logger.debug("BACKUP xml db {}".format(table))
        runner_ctx.backup_xml_db(table_path_full, table) # file 단위 백업

    for where_conditon in where_conditons.items():
        runner_ctx.logger.debug("cond : {} = {}".format(where_conditon[0], where_conditon[1]))

    try:
        doc = ET.parse(table_path_full)

    except Exception as e:
        err_msg = 'xml db parse failed {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}".format(err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc == None):
        runner_ctx.logger.error("xml db parse failed ")
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root == None):
            err_msg = "xml db getroot failed"
            runner_ctx.logger.error(err_msg)
            raise lmt_exception.LmtException(err_msg)

    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}".format(err_msg))
        raise lmt_exception.LmtException(err_msg)

    rows_xpath =  './/ROW' # find all 'ROW' 

    try:
        xml_nodes = xml_root.findall(rows_xpath)
        if xml_nodes == None:
            err_msg = "findall failed = {}".format(rows_xpath)
            runner_ctx.logger.error("{}".format(rows_xpath))
            raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = {}".format(rows_xpath)
            runner_ctx.logger.error("{}".format(err_msg))
            raise lmt_exception.LmtException(err_msg)

        #print xml_nodes
        for db_row in xml_nodes:
            # now, check this one row 
            is_all_condition_met = True
            for where_conditon in where_conditons.items():
                # where_conditon[0] --> field name
                # where_conditon[1] --> field value 
                #runner_ctx.logger.debug("cond : {} ".format(where_conditon[0]))
                # get db row's field value
                db_field_val = db_row.find(where_conditon[0]).text
                #runner_ctx.logger.debug("{}".format(row_field_val))
                if(db_field_val != where_conditon[1]):
                    is_all_condition_met = False
                    break

            if(is_all_condition_met):   
                runner_ctx.logger.debug("****************************")
                runner_ctx.logger.debug("*** all  conditions  met ***")
                runner_ctx.logger.debug("****************************")

                for found_db in db_row:
                    runner_ctx.logger.debug("{} = {}".format(found_db.tag,found_db.text))

                #XXX change value 
                db_field_to_change = db_row.find(attr_field)
                if(db_field_to_change is not None):
                    db_field_to_change.text = val
                    #write file
                    runner_ctx.logger.debug("write xml db : {}".format(table_path_full))
                    doc.write(table_path_full, encoding="utf-8", xml_declaration=True)

    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}".format(err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner_ctx.logger.error("{}".format(err_msg))
        raise

    return True


