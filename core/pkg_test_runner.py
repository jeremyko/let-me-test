#-*- coding: utf-8 -*-

import sys
import os
import subprocess
import traceback

from tspec_cmd_impl import test_lib
from tspec_cmd_impl import lmt_time
from tspec_cmd_impl import lmt_assert
from tspec_cmd_impl import lmt_shell
#from tspec_cmd_impl import tspec_cmd_impl
from core import lmt_exception

_g_info_repo = {}
_g_logger  = None

#///////////////////////////////////////////////////////////////////////////////
class PkgTestRunner:

    #config = None
    _group_dirs = [] #group dir name only
    _group_dirs_full_path = [] # group dir full path
    _test_dir_per_group = []
    _failed_tests = []
    _test_dirs_per_group_full = []
    _test_dirs_per_group = []
    _args = None
    _tspec_ext ='.tspec'
    _group_prefix ='group_'
    _failed_test_cnt = 0 
    _succeeded_test_cnt = 0

    #==================================================================    
    def reset_variables(self):
        _group_dirs = [] #group dir name only
        _group_dirs_full_path = [] # group dir full path
        _test_dir_per_group = []
        _failed_tests = []
        _test_dirs_per_group_full = []
        _test_dirs_per_group = []
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
        self.reset_variables()

        self.get_groups ()

        if(self._group_dirs):
            self.run_groups()

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
    def get_groups(self):
        temp_dirs = os.listdir(self._args.pkg_dir)
        temp_dirs.sort()
        self._group_dirs = []
        self._group_dirs_full_path = []
        for dir_name in temp_dirs :
            #print('dir_name : {}'.format(dir_name))
            if(dir_name.startswith(self._group_prefix)) :
                # this is group directory
                #print('group : {}'.format(dir_name))
                self._group_dirs_full_path.append(self._args.pkg_dir+dir_name) # pkg_dir ends with os.sep
                self._group_dirs.append(dir_name) 

    #==================================================================    
    def run_groups(self):
        index =0
        for grp_dir in self._group_dirs :
            self.logger.info(" ")
            #self.logger.info("[RUN GROUP] : {}".format(grp_dir))
            self.logger.debug("--- group {}".format(self._group_dirs_full_path[index]))
            self.get_test_cases_per_group(self._group_dirs_full_path[index],grp_dir)
            if(self._test_dirs_per_group_full):
                self.run_tests_per_group(grp_dir)
            index += 1    

    #==================================================================    
    def get_test_cases_per_group(self,group_dir_full, grp_dir):
        self._test_dirs_per_group_full = []
        self._test_dirs_per_group = []
        temp_dirs = os.listdir(group_dir_full)
        temp_dirs.sort()
        for test_dir in temp_dirs :
            if(self._args.test_id is not None):
                #run specific test : -t [group name].[test name]
                # ex) 'group_001.grp001_test001' 
                filter_name = grp_dir + "." +test_dir
                self.logger.debug("filter_name = {}".format(filter_name))
                for grp_and_test in self._args.test_id:
                    if(filter_name == grp_and_test):
                        self.logger.info("[run specific test] {}".format(grp_and_test))
                        self._test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir)
                        self._test_dirs_per_group.append(test_dir)
            else:       
                self._test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir)
                self._test_dirs_per_group.append(test_dir)

    #==================================================================    
    def run_tests_per_group(self, grp_dir):
        self.logger.info("[GROUP] : {}".format(grp_dir))
        index = 0
        for test_dir_full in self._test_dirs_per_group_full :
            self.logger.info("  ")
            self.logger.debug("  --> test dir {}".format(test_dir_full))
            #self.logger.info("  [TEST] : {}".format(test_dir_full))
            self.logger.info("  [TEST] : {}".format(self._test_dirs_per_group[index]))
            tspecs_dir_full = test_dir_full +"/tspecs" # tspec directory path
            if(os.path.exists(tspecs_dir_full)):
                tspec_names = os.listdir(tspecs_dir_full) # all tspec path in tspec dir.
                if(tspec_names):
                    tspec_names.sort()
                    if(self.run_all_tspecs_per_test(tspecs_dir_full, tspec_names)==True):
                        self._succeeded_test_cnt += 1
                        #self.logger.info("  [PASSED] : {}".format(test_dir_full))
                        self.logger.info("  [PASSED] : {}".format(self._test_dirs_per_group[index]))
                    else:
                        #self.logger.error("  [FAILED] : {}".format(test_dir_full))
                        self.logger.error("  [FAILED] : {}".format(self._test_dirs_per_group[index]))
                        self._failed_tests.append(test_dir_full)
            else:    
                self.logger.warning("spec dir not exists {}".format(tspecs_dir_full))

            index += 1    


    #==================================================================    
    def run_all_tspecs_per_test(self, tspecs_dir_full, tspec_names):
        self.logger.debug("  [tspec_names] : {}".format(tspec_names))
        for tspec_name in tspec_names:
            if(tspec_name.endswith(self._tspec_ext)) :
                # group_dir , test_dir, specs_dir, test_specs_per_test
                if (self.run_one_tspec(tspecs_dir_full+os.sep+tspec_name, tspec_name) != True):
                    #self.logger.error("        [FAILED] : {}".format(tspec_name))
                    self.logger.error("        [FAILED] ")
                    self._failed_test_cnt += 1
                    return False
        return True

    #==================================================================    
    # run tspec file
    #==================================================================    
    def run_one_tspec(self, tspec_path_full, tspec_name):
        self.logger.info("    [TSPEC] : {}".format(tspec_path_full))
        #self.logger.info("    [TSPEC] : {}".format(tspec_name))
        try:
            #exec("self.logger.info('in exec test ')")
            #----------------
            execfile(tspec_path_full)
            #----------------
        except lmt_exception.LmtException as lmt_e:
            err_msg = '      error : {} '.format(lmt_e)
            self.logger.error(err_msg)
            #traceback.print_exc()
            cl, exc, tb = sys.exc_info()
            self.logger.error("       - tspec   => {}".format(traceback.extract_tb(tb)[1][0])) 
            self.logger.error("       - line no => {}".format(traceback.extract_tb(tb)[1][1])) 
            self.logger.error("       - test    => {}".format(traceback.extract_tb(tb)[1][3]))
            del tb
            return False
        except Exception as e:
            err_msg = '      error : {} :{}'.format(e.__doc__, e.message)
            self.logger.error(err_msg)
            cl, exc, tb = sys.exc_info()
            self.logger.error("       - tspec   => {}".format(traceback.extract_tb(tb)[1][0])) 
            self.logger.error("       - line no => {}".format(traceback.extract_tb(tb)[1][1])) 
            self.logger.error("       - test    => {}".format(traceback.extract_tb(tb)[1][3]))
            del tb
            return False
        #self.logger.info("        [PASSED]    : {}".format(tspec_path_full))
        self.logger.info("    [PASSED]")
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

#///////////////////////////////////////////////////////////////////////////////
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

#///////////////////////////////////////////////////////////////////////////////
def wait_secs(secs):
    lmt_time.wait_secs(_g_logger, secs)
    #tspec_cmd_impl.wait_secs(_g_logger, secs)

#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(cmd):
    lmt_shell.run_shell_cmd(_g_logger,cmd)
    #tspec_cmd_impl.run_shell_cmd(_g_logger,cmd)

#///////////////////////////////////////////////////////////////////////////////
def test_eq(a,b):
    lmt_assert.test_eq(a,b)
    #tspec_cmd_impl.test_eq(a,b)

#///////////////////////////////////////////////////////////////////////////////
def exception_test(a,b):
    test_lib.exception_test(a,b)



