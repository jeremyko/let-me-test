#-*- coding: utf-8 -*-

"""
oracle db handling 
"""

#202007 kojh create
#import os
import cx_Oracle

from module_core import lmt_exception
from module_core import lmt_util


#///////////////////////////////////////////////////////////////////////////////
# oracle table 에 특정 조건에 맞는 데이터가 있는지 확인. 
# ex) assert_db_select("T_NFW_ALARM_STATUS", "CODE='21119003' AND PRC_DATE='${CUR_YYYYMMDD}'")
#///////////////////////////////////////////////////////////////////////////////
def assert_oracle_exists(runner_ctx,table, where): 
    full_sql = "select count(1) as cnt from " + table + " where " + lmt_util.replace_all_symbols(runner_ctx,where)
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,full_sql))
    try:
        con = cx_Oracle.connect(runner_ctx.ora_conn_str ) # ex)'PEMS/PEMS@OFCSEMS'
        cur = con.cursor()
        cur.execute(full_sql)

        """    
        res_list = cur.fetchall()
        if(len(res_list) > 0):
            #runner_ctx.logger.info("{}sql count : {}".format(runner_ctx.cur_indent,res_list[0][0]))
            runner_ctx.logger.info("{}sql count : {}".format(runner_ctx.cur_indent,len(res_list)))
            for res in res_list:
                runner_ctx.logger.info("{}result : {}".format(runner_ctx.cur_indent,res))
        """        
        result = cur.fetchone()
        for row in result:
            runner_ctx.logger.info("{}row={}".format(runner_ctx.cur_indent,row))

            if row > 0 : 
                runner_ctx.logger.info("{}data exists : cnt = {}".format(runner_ctx.cur_indent, row ))
            else:
                err_msg = 'data not found : {}'.format(full_sql)
                runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
                raise lmt_exception.LmtException(err_msg)
    except Exception as e:
        err_msg = 'exception : {}'.format(e)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)
    finally:
        cur.close()
        con.close()

    return True


#///////////////////////////////////////////////////////////////////////////////
def execute_sql(runner_ctx,full_sql): 
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,full_sql))
    try:
        con = cx_Oracle.connect(runner_ctx.ora_conn_str ) # ex)'PEMS/PEMS@OFCSEMS'
        cur = con.cursor()
        cur.execute(full_sql)
        con.commit()
    except Exception as e:
        err_msg = 'exception : {}'.format(e)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)
    finally:
        cur.close()
        con.close()

    return True


