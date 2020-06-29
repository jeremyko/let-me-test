"""
this is test module 
"""
from core import lmt_exception
#import inspect
from inspect import currentframe, getframeinfo


def test_1(logger, a,b,c):
    #print("args = {}, {}, {}".format(a,b,c))
    logger.debug("logger test : args = {}, {}, {}".format(a,b,c))

def exception_test(a,b):
    if(a != b):
        err_msg ="a ({}) != b ({})".format(a,b)
        #frameinfo = getframeinfo(currentframe())
        #print(frameinfo.filename, frameinfo.lineno)
        raise lmt_exception.LmtException(err_msg)
