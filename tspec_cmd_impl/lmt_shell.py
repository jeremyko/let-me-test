from core import lmt_exception
import os
import subprocess

#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(logger,cmd):
    stream = os.popen(cmd)
    output = stream.read()

    """
    proc = subprocess.Popen( [cmd], stdout=subprocess.PIPE)
    output, err = proc.communicate()
    """    
    if(output):
        logger.info("------- output START ----------------------")
        logger.info("\n{}".format(output))
        logger.info("------- output END   ----------------------")
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
