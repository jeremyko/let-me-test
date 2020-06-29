from core import lmt_exception
#from inspect import currentframe, getframeinfo

def test_eq(a,b):
    if(a != b):
        #frameinfo = getframeinfo(currentframe())
        #print(frameinfo.filename, frameinfo.lineno)
        #err_msg ="assert failed [{}:{}] : {} != {} ".format(frameinfo.filename, frameinfo.lineno,a,b)
        err_msg ="assert failed : {} != {} ".format(a,b)
        raise lmt_exception.LmtException(err_msg)
    return True
