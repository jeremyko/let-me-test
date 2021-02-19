#-*- coding: utf-8 -*-

#202007 kojh create

import os
import re
import sys
import datetime
import subprocess
import shlex
import pexpect
import psutil

from module_core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def is_file_contains(file_path, pattern):
    with open(file_path) as f:
        for line in f:
            if re.search(pattern, line):
                return True
    return False

#///////////////////////////////////////////////////////////////////////////////
# 1.리턴값을 받을수 있어야 함.
# 2.잘못된 명령등에 대한 에러를 알수 있어야 함
# 3.사용자의 명령중에 pipe ('|') 가 있는 경우에 처리모두 되어야 함
# 4.명령의 출력이 매우 많고 클때도 처리 되어야 함 
# 5.background process 를 기동하는 경우에 처리 TODO
#   (ex: pfmRun.sh all 01 -> 현재 os.sytem 으로만 가능)
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
# 명령이 끝날때까지 대기한다. 프로세스를 기동한 경우에는 child가 종료될때까지 대기한다.
def run_shell_cmd(runner_ctx,cmd):
    cmd = replace_all_symbols(runner_ctx,cmd)

    try:
        runner_ctx.logger.info("{}cmd : {}".format(runner_ctx.cur_indent,cmd))
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True,universal_newlines=True)

        # If the return code was non-zero it raises a CalledProcessError. 
        # The CalledProcessError object will have the return code in the returncode attribute 
        # and any output in the output attribute.
        if(output):
            out_list = output.split("\n")
            if(out_list):
                for outval in out_list:
                    if(len(outval)>0 and outval != 'grep: write error' ):
                        runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,outval))
            return output

    except subprocess.CalledProcessError as e:
        err_msg = 'error -> {} : return code = {}'.format(e.output, e.returncode )
        raise lmt_exception.LmtException(err_msg)

    except Exception as e:
        err_msg = 'error -> {} : {} '. format( e.__doc__, e.message)
        runner_ctx.logger.error("{}error: {}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    runner_ctx.logger.info("{}cmd done".format(runner_ctx.cur_indent))
    return None

#///////////////////////////////////////////////////////////////////////////////
# background 로 명령을 수행하고 바로 나온다. (위 run_shell_cmd 와 다름)
def run_shell_cmd_background(runner_ctx,cmd):
    cmd = replace_all_symbols(runner_ctx,cmd)
    runner_ctx.logger.info("{}cmd : {}".format(runner_ctx.cur_indent, cmd))
    #child = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=120,maxread=1)
    #child.logfile = sys.stdout
    #child.expect(pexpect.EOF)
   
    #XXX close_fds=True XXX  
    subprocess.Popen(cmd, shell=True,universal_newlines=True, close_fds=True)
    #os.spawnl(os.P_NOWAIT, cmd)



#///////////////////////////////////////////////////////////////////////////////
def replace_all_symbols(runner_ctx, user_str):
    runner_ctx.logger.debug("{}before replace : {}".format(runner_ctx.cur_indent,user_str))
    today = datetime.datetime.now().strftime('%Y%m%d')
    today_yyyymmddhh = datetime.datetime.now().strftime('%Y%m%d%H')
    curr_hh = datetime.datetime.now().strftime('%H') # string 
    #runner_ctx.logger.debug("{}curr hh : {}".format(runner_ctx.cur_indent, curr_hh))
    resolved = user_str.replace("${PACKAGE_ID}", runner_ctx.package_id)
    resolved = resolved.replace("${PACKAGE_NAME}", runner_ctx.package_name)
    resolved = resolved.replace("${SYSTEM_NAME}" , runner_ctx.system_name)
    resolved = resolved.replace("${SERVICE_NAME}" , runner_ctx.service_name)
    resolved = resolved.replace("${CUR_YYYYMMDD}", today)
    resolved = resolved.replace("${CUR_YYYYMMDDHH}", today_yyyymmddhh)
    if runner_ctx.cur_ctx_test_path :
        resolved = resolved.replace("${TEST_DATA_DIR}", runner_ctx.cur_ctx_test_path+os.sep+"data") 
    resolved = resolved.replace("${XML_DB_PATH}", runner_ctx.xml_db_path) 
    resolved = resolved.replace("${OUTPUT_IPMD}", runner_ctx.output_path+os.sep +
                                runner_ctx.service_name + os.sep + "IPMD") 
    resolved = resolved.replace("${OUTPUT_ERR}", runner_ctx.output_path+os.sep +
                                runner_ctx.service_name + os.sep + "ERR") 
    resolved = resolved.replace("${LOG_BASE_PATH}" , runner_ctx.log_base_path)
    curr_hh_plus_1_str = str(int(curr_hh) + 1)
    #runner_ctx.logger.debug("{}curr_hh_plus_1_str : {}".format(runner_ctx.cur_indent, curr_hh_plus_1_str))
    resolved = resolved.replace("${CURR_HH}" ,  curr_hh )
    resolved = resolved.replace("${CURR_HH+1}" ,curr_hh_plus_1_str )

    resolved = resolved.replace("${EMS_PACKAGE_NAME}", runner_ctx.ems_package_name)
    resolved = resolved.replace("${EMS_SYSTEM_NAME}" , runner_ctx.ems_system_name)
    resolved = resolved.replace("${EMS_SERVICE_NAME}" , runner_ctx.ems_service_name)
    resolved = resolved.replace("${STAT_PATH}" , runner_ctx.stat_path)
    resolved = resolved.replace("${WORK_PATH}" , runner_ctx.work_path)

    if "${TEST_RESULT_DIR}" in user_str :
        if(os.path.isdir(runner_ctx.test_result_dir)==False):
            runner_ctx.logger.info("{}create dir : {}".format(runner_ctx.cur_indent,runner_ctx.test_result_dir))
            os.mkdir(runner_ctx.test_result_dir)

    resolved = resolved.replace("${TEST_RESULT_DIR}" , runner_ctx.test_result_dir)
    runner_ctx.logger.debug("{}resolved : {}".format(runner_ctx.cur_indent,resolved))
    return resolved


#///////////////////////////////////////////////////////////////////////////////
# XXX ipcs -m | grep `whoami` 에서 데이터 없으면 $? == 1 이므로 에러발생됨 !!!
def clear_all_shared_memory(runner_ctx): 
    runner_ctx.logger.info("{}공유메모리 모두 삭제 수행 시작".format(runner_ctx.cur_indent))
    runner_ctx.logger.info("{}공유메모리 현재 상태 출력".format(runner_ctx.cur_indent))
    run_shell_cmd(runner_ctx,"ipcs -m | grep `whoami`")

    runner_ctx.logger.info("{}공유메모리 삭제 시작 ".format(runner_ctx.cur_indent))
    run_shell_cmd(runner_ctx,"ipcs -m | grep `whoami` | awk '{ print $2 }' | xargs -n1 ipcrm -m ")

    runner_ctx.logger.info("{}공유메모리 삭제 완료 ".format(runner_ctx.cur_indent))
    run_shell_cmd(runner_ctx,"ipcs -m ")


#///////////////////////////////////////////////////////////////////////////////
def is_runnig(script_name):
    running_cnt = 0
    for q in psutil.process_iter():
        if q.name() == 'python':
            #print q.cmdline()
            if len(q.cmdline())>1 and script_name in q.cmdline()[1]:
                running_cnt += 1
    if(running_cnt > 1):
        return True, running_cnt

    return False, 0



