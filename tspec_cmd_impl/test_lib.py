"""
this is test module 
"""

from core import lmt_exception
from inspect import currentframe, getframeinfo

#///////////////////////////////////////////////////////////////////////////////
def test_1(runner_ctx, a,b,c):
    runner_ctx.logger.debug("runner_ctx logger test : args = {}, {}, {}".format(a,b,c))

#///////////////////////////////////////////////////////////////////////////////
def exception_test(a,b):
    if(a != b):
        err_msg ="a ({}) != b ({})".format(a,b)
        raise lmt_exception.LmtException(err_msg)
