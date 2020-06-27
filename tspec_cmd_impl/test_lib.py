"""
this is test module 
"""
def test_1(logger, a,b,c):
    print("args = {}, {}, {}".format(a,b,c))
    logger.info("logger test : args = {}, {}, {}".format(a,b,c))

