from core import lmt_exception
import os
import subprocess

#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(runner_ctx,cmd):

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
            err_msg += " -> {}".format(output)
        raise lmt_exception.LmtException(err_msg)

    #succeeded
    if(output):
        runner_ctx.logger.info("------- output START ----------------------")
        runner_ctx.logger.info("result : {}".format(output))
        runner_ctx.logger.info("------- output END   ----------------------")
    return True


#///////////////////////////////////////////////////////////////////////////////
"""     
#python3
out, err = proc.communicate(timeout=10)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()
    err_msg ="cmd failed : timeout : {}".format(cmd)
    raise lmt_exception.LmtException(err_msg)
"""    
