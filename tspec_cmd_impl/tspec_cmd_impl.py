import os
import time
import subprocess

from core import lmt_exception


#///////////////////////////////////////////////////////////////////////////////
def test_eq(a,b):
    if(a != b):
        #frameinfo = getframeinfo(currentframe())
        #print(frameinfo.filename, frameinfo.lineno)
        #err_msg ="assert failed [{}:{}] : {} != {} ".format(frameinfo.filename, frameinfo.lineno,a,b)
        err_msg ="assert failed : {} != {} ".format(a,b)
        raise lmt_exception.LmtException(err_msg)
    return True

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
def wait_secs(logger,secs):
    logger.info("wait_secs start : args = {}".format(secs))
    time.sleep(secs)
    #logger.info("wait_secs end : args = {}".format(secs))
    #raise lmt_exception.LmtException("some error test")
