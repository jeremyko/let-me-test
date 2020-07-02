#from core import lmt_exception
#import os
#import subprocess
from core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(runner_ctx,cmd):
    lmt_util.run_shell_cmd(runner_ctx,cmd)
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
