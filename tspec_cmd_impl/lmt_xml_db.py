#-*- coding: utf-8 -*-

"""
xml db handling 
"""

#202007 kojh create
import os
import shutil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    print ("ImportError")
    import xml.etree.ElementTree as ET

from module_core import lmt_exception
from module_core import lmt_util

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
# 필드 값이 특정값인지 확인. 
# ex) ims_charging_Identifier 필드의 ALLOW_SPACE=N and VALUE_CHECK_TYPE=2 체크
# assert_eq_xml_db_fields("T_DATA_FORMAT", 
#         {"VALUE_CHECK_TYPE":"2","ALLOW_SPACE":"N"}, 
#         {"SERVICE_ID":'000005', 
#          "DATA_NAME":"IMS_META_VLD", 
#          "STRUCTURE_CD":"1", 
#          "FIELD_NAME":"ims_charging_Identifier"})
#///////////////////////////////////////////////////////////////////////////////
def assert_eq_xml_db_fields(runner_ctx,table, dic_asserts, dic_conditions): 
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,table))
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,dic_asserts))
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,dic_conditions))
    table           = table.strip()
    table_path_full = runner_ctx.xml_db_path + os.sep + table +".xml"
    runner_ctx.logger.debug("{}table      [{}]".format(runner_ctx.cur_indent,table_path_full))
    all_condition_cnt = len(dic_conditions)
    runner_ctx.logger.debug("{}all_condition_cnt = {}".format(runner_ctx.cur_indent,all_condition_cnt))
    # backup 불필요. 조회만 하므로 
    for and_conditon in dic_conditions.items():
        runner_ctx.logger.debug("{}cond : {} = {}".
                format(runner_ctx.cur_indent,and_conditon[0], and_conditon[1]))

    try:
        doc = ET.parse(table_path_full) #TODO 테이블 한번만 parse 가능?

    except Exception as e:
        err_msg = 'xml db parse failed {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc is None):
        runner_ctx.logger.error("{}xml db parse failed".format(runner_ctx.cur_indent))
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root is None):
            err_msg = "xml db getroot failed"
            runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)

    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    rows_xpath =  './/ROW' # find all 'ROW' 

    try:
        xml_nodes = xml_root.findall(rows_xpath)
        if xml_nodes is None:
            err_msg = "findall failed = {}".format(rows_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,rows_xpath))
            raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = {}".format(rows_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)

        #print xml_nodes
        for db_row in xml_nodes:
            # now, check this one row 
            is_all_condition_met = True
            for and_conditon in dic_conditions.items():
                # and_conditon[0] --> field name
                # and_conditon[1] --> field value 
                #runner_ctx.logger.debug("cond : {} ".format(and_conditon[0]))
                db_field_val = db_row.find(and_conditon[0]).text
                db_field_val = db_field_val.strip()
                #runner_ctx.logger.debug("{}".format(row_field_val))
                if(db_field_val != and_conditon[1]):
                    is_all_condition_met = False
                    break

            if(is_all_condition_met):   
                runner_ctx.logger.debug("{}*** all  conditions  met ***".format(runner_ctx.cur_indent))
                """
                for found_db in db_row:
                    tmp_text = ET.tostring(found_db, encoding="utf-8", method="xml") 
                    runner_ctx.logger.debug("{}{} = {}".
                            format(runner_ctx.cur_indent,found_db.tag,tmp_text))
                """  
                #XXX check value 
                for eq_assert in dic_asserts.items(): 
                    db_field_to_compare = db_row.find(eq_assert[0])
                    if(db_field_to_compare is not None):
                        db_compare = db_field_to_compare.text.strip()
                        val = eq_assert[1].strip()
                        val = lmt_util.replace_all_symbols(runner_ctx,val) # XXX  ${CURR_HH} ${CURR_HH+1}
                        if(db_compare != val):
                            err_msg = "assert eq failed : [{}] != [{}]".format(db_compare, val)
                            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
                            raise lmt_exception.LmtException(err_msg)
                        else:
                            runner_ctx.logger.info("{}value assert ok : field [{:>20}] -> {} == {}".
                                    format(runner_ctx.cur_indent,eq_assert[0],db_compare,val))

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
# ex) UserLocationInfo 필드의 ALLOW_SPACE = Y 로, VALUE_CHECK_TYPE =2 변경 :
# set_xml_db("T_DATA_FORMAT", 
#         {"VALUE_CHECK_TYPE":"2","ALLOW_SPACE":"N"}, # 확인할 필드 및 값.
#         {"SERVICE_ID":'000007', # - AND - 조건들
#          "DATA_NAME":"GTP_PGW_OUT", 
#          "STRUCTURE_CD":"0", 
#          "FIELD_NAME":"UserLocationInfo"})
#///////////////////////////////////////////////////////////////////////////////
def set_xml_db(runner_ctx,table, dic_field_vals, dic_conditions): 
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,table))
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,dic_field_vals))
    runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent,dic_conditions))
    table           = table.strip()
    table_path_full = runner_ctx.xml_db_path + os.sep + table +".xml"
    runner_ctx.logger.debug("{}table      [{}]".format(runner_ctx.cur_indent,table_path_full))
    all_condition_cnt = len(dic_conditions)
    runner_ctx.logger.debug("{}all_condition_cnt = {}".format(runner_ctx.cur_indent,all_condition_cnt))

    # backup 
    if(table in runner_ctx.change_xml_dbs.keys()) :    
        # 동일한 xml db table 명으로 set_xml_db 이 여러번 호출되는 경우 고려.
        runner_ctx.logger.debug("{}already backed up..{}".format(runner_ctx.cur_indent, table+".xml"))
    else:
        runner_ctx.logger.debug("{}BACKUP xml db {}".format(runner_ctx.cur_indent, table))
        runner_ctx.backup_xml_db(table_path_full, table) # file 단위 백업

    for and_conditon in dic_conditions.items():
        runner_ctx.logger.debug("{}cond : {} = {}".
                format(runner_ctx.cur_indent,and_conditon[0], and_conditon[1]))

    try:
        #------------------------------
        doc = ET.parse(table_path_full) #TODO 테이블 한번만 parse 가능?
        #------------------------------

    except Exception as e:
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,table_path_full))
        err_msg = 'xml db parse failed {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    if(doc is None):
        runner_ctx.logger.error("{}xml db parse failed".format(runner_ctx.cur_indent))
        return False

    try:
        xml_root = doc.getroot()
        if(xml_root is None):
            err_msg = "xml db getroot failed"
            runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)

    except Exception as e:
        err_msg = 'xml getroot failed : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    rows_xpath =  './/ROW' # find all 'ROW' 

    try:
        xml_nodes = xml_root.findall(rows_xpath)
        if xml_nodes is None:
            err_msg = "findall failed = {}".format(rows_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,rows_xpath))
            raise lmt_exception.LmtException(err_msg)
        if len(xml_nodes) == 0:
            err_msg = "invalid xpath = {}".format(rows_xpath)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)

        #print xml_nodes
        for db_row in xml_nodes:
            # now, check this one row 
            is_all_condition_met = True
            for and_conditon in dic_conditions.items():
                # and_conditon[0] --> field name
                # and_conditon[1] --> field value 
                #runner_ctx.logger.debug("cond : {} ".format(and_conditon[0]))
                db_field_val = db_row.find(and_conditon[0]).text
                db_field_val = db_field_val.strip()
                #runner_ctx.logger.debug("{}".format(row_field_val))
                if(db_field_val != and_conditon[1]):
                    is_all_condition_met = False
                    break

            if(is_all_condition_met):   
                runner_ctx.logger.debug("{}*** all  conditions  met ***".format(runner_ctx.cur_indent))
                """
                for found_db in db_row:
                    tmp_text = ET.tostring(found_db, encoding="utf-8", method="xml") # us-ascii
                    runner_ctx.logger.debug("{}{} = {}".
                            format(runner_ctx.cur_indent,found_db.tag, tmp_text)) 
                """  
                #XXX change value 
                is_val_changed = False
                for fld_val in dic_field_vals.items(): 
                    db_field_to_set = db_row.find(fld_val[0])
                    if(db_field_to_set is not None):
                        val = fld_val[1].strip()
                        runner_ctx.logger.debug("{}dic_field_vals  : {}".format(runner_ctx.cur_indent, val))
                        val = lmt_util.replace_all_symbols(runner_ctx,val) # XXX  ${CURR_HH} ${CURR_HH+1}
                        runner_ctx.logger.debug("{}--> resolved  : {}".format(runner_ctx.cur_indent, val))
                        db_field_to_set.text = val
                        is_val_changed = True

                if(is_val_changed == True):
                    #write file
                    runner_ctx.logger.debug("{}write xml db : {}".format(runner_ctx.cur_indent, table_path_full))
                    #doc.write(table_path_full, encoding="utf-8", xml_declaration=True)
                    doc.write(table_path_full) 

    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise

    return True


