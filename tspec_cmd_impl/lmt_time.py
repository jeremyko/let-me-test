import time

from core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def wait_secs(runner,secs):
    runner.logger.info("wait_secs start : args = {}".format(secs))
    time.sleep(secs)
    #runner.info("wait_secs end : args = {}".format(secs))
    #raise lmt_exception.LmtException("some error test")
    return True

