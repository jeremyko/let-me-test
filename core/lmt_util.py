
from core import lmt_exception
import os
import datetime
import subprocess

#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(runner_ctx,cmd):

    runner_ctx.logger.info("cmd : {}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = proc.communicate()

    if(err):
        runner_ctx.logger.error("error : {}".format(cmd))
        err_msg ="{} ".format(err)
        raise lmt_exception.LmtException(err_msg)
    elif(proc.returncode != 0): #XXX exit with non 0 -> failed
        runner_ctx.logger.error("error : {}".format(cmd))
        err_msg ="cmd failed : {} -> exit code ={} ".format(cmd,proc.returncode)
        runner_ctx.logger.debug("shell return code = {}".format(proc.returncode))
        if(output):
            err_msg += "\n{}".format(output)
        raise lmt_exception.LmtException(err_msg)

    #succeeded
    if(output):
        runner_ctx.logger.info("------- output START ----------------------")
        runner_ctx.logger.info("\n{}".format(output))
        runner_ctx.logger.info("------- output END   ----------------------")
        return output
    return None

#///////////////////////////////////////////////////////////////////////////////
def replace_all_symbols(runner_ctx, user_str):
    today = datetime.datetime.now().strftime('%Y%m%d')
    resolved = user_str.replace("${PACKAGE_NAME}", runner_ctx.package_name)
    resolved = resolved.replace("${SYSTEM_NAME}" , runner_ctx.system_name)
    resolved = resolved.replace("${CUR_YYYYMMDD}", today)
    resolved = resolved.replace("${TEST_DATA_DIR}", runner_ctx.cur_ctx_test_path+os.sep+"data") 
    runner_ctx.logger.debug("resolved : {}".format(resolved))
    return resolved
