#-*- coding: utf-8 -*-

"""
mysql db handling 
"""

#202007 kojh create
import pymysql

from module_core import lmt_exception
from module_core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
# table 에 특정 조건에 맞는 데이터가 있는지 확인. 
# ex) assert_db_select("T_NFW_ALARM_STATUS", "CODE='21119003' AND PRC_DATE='${CUR_YYYYMMDD}'")
#///////////////////////////////////////////////////////////////////////////////
def assert_mysql_exists(runner_ctx,table, where): 
    full_sql = "select count(1) as cnt from " + table + " where " + lmt_util.replace_all_symbols(runner_ctx,where)
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,full_sql))
    runner_ctx.logger.debug("{}[{}]".format(runner_ctx.cur_indent, runner_ctx.mysql_host))
    runner_ctx.logger.debug("{}[{}]".format(runner_ctx.cur_indent, runner_ctx.mysql_user))
    runner_ctx.logger.debug("{}[{}]".format(runner_ctx.cur_indent, runner_ctx.mysql_passwd))
    runner_ctx.logger.debug("{}[{}]".format(runner_ctx.cur_indent, runner_ctx.mysql_db_name))

    try:
        connection = pymysql.connect(host    =runner_ctx.mysql_host, 
                                     user    =runner_ctx.mysql_user,
                                     password=runner_ctx.mysql_passwd,
                                     db      =runner_ctx.mysql_db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor() 
        cursor.execute(full_sql)
        row = cursor.fetchone() #fetchall() fetchone()
        if int(row['cnt']) > 0 : 
            runner_ctx.logger.info("{}data exists : cnt = {}".format(runner_ctx.cur_indent, row['cnt'] ))
        else:
            err_msg = 'data not found : {}'.format(full_sql)
            runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
    except Exception as e:
        err_msg = 'exception : {}'.format(e)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)
    finally:
        connection.close()


#///////////////////////////////////////////////////////////////////////////////
def execute_sql(runner_ctx,full_sql): 
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,full_sql))
    try:
        connection = pymysql.connect(host    =runner_ctx.mysql_host, 
                                     user    =runner_ctx.mysql_user,
                                     password=runner_ctx.mysql_passwd,
                                     db      =runner_ctx.mysql_db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor() 
        cursor.execute(full_sql)
        connection.commit()
    except Exception as e:
        err_msg = 'exception : {}'.format(e)
        runner_ctx.logger.error("{}{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)
    finally:
        connection.close()


