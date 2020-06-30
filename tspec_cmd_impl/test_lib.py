"""
this is test module 
"""
from core import lmt_exception
from inspect import currentframe, getframeinfo


#frameinfo = getframeinfo(currentframe())
#print(frameinfo.filename, frameinfo.lineno)
#err_msg ="assert failed [{}:{}] : {} != {} ".format(frameinfo.filename, frameinfo.lineno,a,b)

#///////////////////////////////////////////////////////////////////////////////
def test_1(runner, a,b,c):
    #print("args = {}, {}, {}".format(a,b,c))
    runner.logger.debug("runner logger test : args = {}, {}, {}".format(a,b,c))

#///////////////////////////////////////////////////////////////////////////////
def exception_test(a,b):
    if(a != b):
        err_msg ="a ({}) != b ({})".format(a,b)
        #frameinfo = getframeinfo(currentframe())
        #print(frameinfo.filename, frameinfo.lineno)
        raise lmt_exception.LmtException(err_msg)
