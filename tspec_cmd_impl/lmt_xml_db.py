#-*- coding: utf-8 -*-
"""
xml db handling 
"""
import os
from core import lmt_exception
#import xml.etree.ElementTree as ET
try:
    import xml.etree.cElementTree as ET
except ImportError:
    print "ImportError"
    import xml.etree.ElementTree as ET

"""
<ROWSET>
 <ROW num="376">
      <SERVICE_ID>000009</SERVICE_ID>
      <DATA_NAME>SOFCS_CMP_META</DATA_NAME>
      <STRUCTURE_CD>1</STRUCTURE_CD>
      <SEQ_NO>26</SEQ_NO>
      <FIELD_NAME>ofcs_error_code</FIELD_NAME>
      <FIELD_TYPE>1</FIELD_TYPE>
      <FIELD_EXT_TYPE>99</FIELD_EXT_TYPE>
      <FIELD_LENGTH>8</FIELD_LENGTH>
      <VALUE_CHECK_TYPE>1</VALUE_CHECK_TYPE>
      <MIN_VALUE>0</MIN_VALUE>
      <MAX_VALUE>0</MAX_VALUE>
      <DATE_FORMAT NULL="TRUE"/>
      <FIELD_KOR_NAME NULL="TRUE"/>
      <DESCRIPTION NULL="TRUE"/>
      <ALLOW_SPACE>Y</ALLOW_SPACE>
      <CHECK_PATTERN NULL="TRUE"/>
   </ROW>
</ROWSET>
"""
#///////////////////////////////////////////////////////////////////////////////
def replace_xml_db_table (runner_ctx, src, dest):
    #TODO
    return True

#///////////////////////////////////////////////////////////////////////////////
#
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
    table = args[0][0].strip()
    attr_field = args[0][1]
    val   = args[0][2]
    table_path = runner_ctx.xml_db_path + os.sep + table +".xml"
    attr_field = attr_field.strip()
    val        = val.strip()
    runner_ctx.logger.debug("table      [{}]".format(table_path))
    runner_ctx.logger.debug("attr_field [{}]".format(attr_field))
    runner_ctx.logger.debug("val        [{}]".format(val  ))
    all_condition_cnt = len(args[1])
    runner_ctx.logger.debug("all_condition_cnt = {}".format(all_condition_cnt))

    for where_conditon in args[1].items():
        runner_ctx.logger.debug("cond : {} = {}".format(where_conditon[0], where_conditon[1]))

    try:
        doc = ET.parse(table_path)

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
            for where_conditon in args[1].items():
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
                    runner_ctx.logger.debug("write xml db : {}".format(table_path))
                    doc.write(table_path, encoding="utf-8", xml_declaration=True)

    except Exception as e:
        err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
        runner_ctx.logger.error("{}".format(err_msg))
        raise
    except (SyntaxError, AttributeError):
        err_msg = 'Syntax or Attribute error '
        runner_ctx.logger.error("{}".format(err_msg))
        raise

    return True


