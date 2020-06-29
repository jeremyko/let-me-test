#-*- coding: utf-8 -*-

import sys
import os
import subprocess
import traceback

from tspec_cmd_impl import test_lib
from tspec_cmd_impl import lmt_time
from tspec_cmd_impl import lmt_assert
from core import lmt_exception

_g_info_repo = {}
_g_logger  = None

#///////////////////////////////////////////////////////////////////////////////
class PkgTestRunner:

    #config = None
    _group_dirs = []
    _test_dir_per_group = []
    _failed_tests = []
    _args = None
    _tspec_ext ='.tspec'
    _group_prefix ='group_'
    _failed_test_cnt = 0 
    _succeeded_test_cnt = 0

    #==================================================================    
    def __init__(self,logger,args):
        self.logger = logger;
        self._args = args
        global _g_logger
        _g_logger = logger

    #==================================================================    
    def run_test(self):
        _failed_test_cnt = 0 
        _succeeded_test_cnt = 0
        _group_dirs = []
        _test_dir_per_group = []
        _failed_tests = []
        _args = None
        self.logger.debug("run test")
        #test_cmd.test_cmd("1","2",3) #XXX TEST
        #self.just_test_func ("test args") # XXX TEST
        """
        logger.debug   ("--- log debug ")
        logger.info    ("--- log info ")
        logger.warning ("--- log warning ")
        logger.error   ("--- log error ")
        logger.critical("--- log critical ")
        """
        if(self._args.test_id is not None):
            #XXX run specific tests : -t [group name].[test name]
            self.logger.debug("arg : test_id = {} ".format(self._args.test_id))
            #TODO
        else:
            #XXX run all tests 
            self.get_all_groups (self._args.pkg_dir)
            if(self._group_dirs):
                self.run_all_groups(self._group_dirs)
                if(self._failed_test_cnt >0 ):
                    self.logger.info    ("TOTAL {} TEST OK".format(self._succeeded_test_cnt))
                    self.logger.critical("TOTAL {} TEST FAILED".format(self._failed_test_cnt))
                    for failed in self._failed_tests :
                        self.logger.critical(" -> {}".format(failed))
                    return False
            else:            
                err_msg ="invalid pkg dir {}".format(_args.pkg_dir)
                self.logger.error(err_msg)
                return False
        self.logger.info(" ")
        self.logger.info(" ")
        self.logger.info("TOTAL {} TEST OK".format(self._succeeded_test_cnt))
        return True

    #==================================================================    
    def get_all_groups(self,pkg_dir):
        temp_dirs = os.listdir(pkg_dir)
        temp_dirs.sort()
        self._group_dirs = []
        for dir_name in temp_dirs :
            #print('dir_name : {}'.format(dir_name))
            if(dir_name.startswith(self._group_prefix)) :
                # this is group directory
                #print('group : {}'.format(dir_name))
                self._group_dirs.append(pkg_dir+dir_name) # pkg_dir ends with os.sep

    #==================================================================    
    def get_all_test_cases_per_group(self,grp_dir):
        temp_dirs = os.listdir(grp_dir)
        temp_dirs.sort()
        self._test_dirs_per_group = []
        for dir_name in temp_dirs :
            self._test_dirs_per_group.append(grp_dir+os.sep+dir_name)

    #==================================================================    
    def run_all_groups(self, groups):
        for grp_dir in groups:
            #self.logger.debug("--- group {}".format(grp_dir))
            self.logger.info(" ")
            self.logger.info("[RUN GROUP] : {}".format(grp_dir))
            self.get_all_test_cases_per_group(grp_dir)
            if(self._test_dirs_per_group):
                self.run_all_tests_per_group(self._test_dirs_per_group)

    #==================================================================    
    def run_all_tests_per_group(self, test_dirs):
        for test_dir in test_dirs:
            self.logger.info("  ")
            self.logger.debug("  --> test dir {}".format(test_dir))
            self.logger.info("  [RUN TEST] : {}".format(test_dir))
            tspecs_dir = test_dir +"/tspecs"
            if(os.path.exists(tspecs_dir)):
                test_specs_per_test = os.listdir(tspecs_dir)
                if(test_specs_per_test):
                    test_specs_per_test.sort()
                    if(self.run_all_tspecs_per_test(tspecs_dir,test_specs_per_test)==True):
                        self._succeeded_test_cnt += 1
                        self.logger.info("  [PASSED] : {}".format(test_dir))
                    else:
                        self.logger.error("  [FAILED] : {}".format(test_dir))
                        self._failed_tests.append(test_dir)
            else:    
                self.logger.warning("spec dir not exists {}".format(test_specs_per_test))

    #==================================================================    
    def run_all_tspecs_per_test(self,tspecs_dir,test_specs_per_test):
        for tspec in test_specs_per_test:
            if(tspec.endswith(self._tspec_ext)) :
                # group_dir , test_dir, specs_dir, test_specs_per_test
                if (self.run_one_tspec(tspecs_dir+os.sep+tspec) != True):
                    #self.logger.error("        [FAILED] : {}".format(tspec))
                    self.logger.error("        [FAILED] ")
                    self._failed_test_cnt += 1
                    return False
        return True

    #==================================================================    
    # run tspec file
    #==================================================================    
    def run_one_tspec(self, tspec):
        self.logger.info("    --> [RUN TSPEC] : {}".format(tspec))
        try:
            #----------------
            execfile(tspec)
            #----------------
        except lmt_exception.LmtException as lmt_e:
            err_msg = '      error : {} '.format(lmt_e)
            self.logger.error(err_msg)
            #traceback.print_exc()
            cl, exc, tb = sys.exc_info()
            self.logger.error("       - tspec   => {}".format(traceback.extract_tb(tb)[1][0])) 
            self.logger.error("       - line no => {}".format(traceback.extract_tb(tb)[1][1])) 
            self.logger.error("       - test    => {}".format(traceback.extract_tb(tb)[1][3]))
            return False
        except Exception as e:
            err_msg = '      error : {} :{}'.format(e.__doc__, e.message)
            self.logger.error(err_msg)
            return False
        #self.logger.info("        [PASSED]    : {}".format(tspec))
        self.logger.info("        [PASSED]")
        return True


    #==================================================================    
    def just_test_func(self, args):
        self.logger.info("args : {}".format(args))


#///////////////////////////////////////////////////////////////////////////////
# tspec commands bridge 
#///////////////////////////////////////////////////////////////////////////////
#정보를 저장하고 다음 명령에서 찾을수 있어야 함
#TODO XXX 개선 : tspec command 를 해당 모듈의 명령으로 전달만 수행 
def test_cmd(a,b,c):
    global _g_logger
    global _g_info_repo 
    #self.logger.info("invoked in context ") # error XXX 
    #print("globals : ")
    #print(globals())
    test_lib.test_1(_g_logger, a,b,c)
    _g_info_repo ["val a"] = a
    _g_info_repo ["val b"] = b
    _g_info_repo ["val c"] = c
    _g_logger.debug("_g_logger test 1") 
    #print(_g_info_repo)
    return True

def test_cmd_remember():
    """
    global _g_info_repo 
    print("do you remember : ")
    print(_g_info_repo ) 
    print("clear repo  : ")
    _g_info_repo = {} 
    print(_g_info_repo ) 
    global _g_logger
    _g_logger.debug("_g_logger test 2 ") 
    """
    return True

def wait_secs(secs):
    lmt_time.wait_secs(_g_logger, secs)

def test_eq(a,b):
    lmt_assert.test_eq(a,b)

def exception_test(a,b):
    test_lib.exception_test(a,b)
