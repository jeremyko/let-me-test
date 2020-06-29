#-*- coding: utf-8 -*-

import sys
import os
import subprocess
import traceback
import configparser

from tspec_cmd_impl import *
from core import *

__g_info_repo = {}
_g_logger  = None # XXX

#///////////////////////////////////////////////////////////////////////////////
class PkgTestRunner:

    __ini_config = None
    __group_dirs = [] #group dir name only
    __group_dirs_full = [] # group dir full path
    __failed_tests = []
    __test_dirs_per_group_full = []
    __test_dirs_per_group = []
    __args = None
    __tspec_ext ='.tspec'
    __group_prefix ='group_'
    __failed_test_cnt = 0 
    __succeeded_test_cnt = 0

    #==================================================================    
    def reset_variables(self):
        __group_dirs = [] #group dir name only
        __group_dirs_full = [] # group dir full path
        __failed_tests = []
        __test_dirs_per_group_full = []
        __test_dirs_per_group = []
        __args = None
        __tspec_ext ='.tspec'
        __group_prefix ='group_'
        __failed_test_cnt = 0 
        __succeeded_test_cnt = 0

    #==================================================================    
    def __init__(self,logger,args):
        self.__ini_config = configparser.ConfigParser()
        self.logger = logger;
        self.__args = args
        global _g_logger
        _g_logger = logger

    #==================================================================    
    #==================================================================    
    def run_test(self):
        self.reset_variables()

        self.get_groups ()

        if(self.__group_dirs):

            self.run_groups()

            if(self.__failed_test_cnt >0 ):
                self.logger.info    ("TOTAL {} TEST OK".format(self.__succeeded_test_cnt))
                self.logger.critical("TOTAL {} TEST FAILED".format(self.__failed_test_cnt))
                for failed in self.__failed_tests :
                    self.logger.critical(" -> {}".format(failed))
                return False
        else:            
            err_msg ="invalid pkg dir {}".format(__args.pkg_dir)
            self.logger.error(err_msg)
            return False

        self.logger.info(" ")
        self.logger.info(" ")
        self.logger.info("TOTAL {} TEST OK".format(self.__succeeded_test_cnt))
        return True

    #==================================================================    
    def get_groups(self):
        grp_dirs = os.listdir(self.__args.pkg_dir)
        grp_dirs.sort()
        self.__group_dirs = []
        self.__group_dirs_full = []
        for grp_dir_name in grp_dirs :
            if(grp_dir_name.startswith(self.__group_prefix)) :
                # this is group directory
                self.__group_dirs_full.append(self.__args.pkg_dir+grp_dir_name) # pkg_dir ends with os.sep
                self.__group_dirs.append(grp_dir_name) 

    #==================================================================    
    def run_groups(self):
        index =0
        for grp_dir_name in self.__group_dirs :
            self.logger.info(" ")
            self.logger.debug("--- group {}".format(self.__group_dirs_full[index]))
            self.get_test_cases_per_group(self.__group_dirs_full[index],grp_dir_name)
            index += 1    

            if(self.__test_dirs_per_group_full):
                self.run_tests_per_group(grp_dir_name)


    #==================================================================    
    def get_test_cases_per_group(self, group_dir_full, grp_dir_name):
        self.__test_dirs_per_group_full = []
        self.__test_dirs_per_group      = []
        test_dirs = os.listdir(group_dir_full)
        test_dirs.sort()
        for test_dir_name in test_dirs :
            if(self.__args.test_id is not None):
                #run specific test : -t [group name].[test name]
                # ex) 'group_001.grp001_test001' 
                filter_name = grp_dir_name + "." + test_dir_name
                self.logger.debug("filter_name = {}".format(filter_name))
                for grp_and_test in self.__args.test_id:
                    if(filter_name == grp_and_test):
                        self.logger.info("[run specific test] {}".format(grp_and_test))
                        self.__test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir_name)
                        self.__test_dirs_per_group.append(test_dir_name)
            else:       
                self.__test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir_name)
                self.__test_dirs_per_group.append(test_dir_name)

    #==================================================================    
    def run_tests_per_group(self, grp_dir_name):
        self.logger.info("[GROUP] : {}".format(grp_dir_name))
        index = 0
        for test_dir_full in self.__test_dirs_per_group_full :
            self.logger.info("  ")
            self.logger.debug("  --> test dir {}".format(test_dir_full))
            #self.logger.info("  [TEST] : {}".format(test_dir_full))
            self.logger.info("  [TEST] : {}".format(self.__test_dirs_per_group[index]))
            tspecs_dir_full = test_dir_full +"/tspecs" # tspec directory path
            if(os.path.exists(tspecs_dir_full)):
                tspec_names = os.listdir(tspecs_dir_full) # all tspec path in tspec dir.
                if(tspec_names):
                    tspec_names.sort()
                    if(self.run_all_tspecs_per_test(tspecs_dir_full, tspec_names)==True):
                        self.__succeeded_test_cnt += 1
                        #self.logger.info("  [PASSED] : {}".format(test_dir_full))
                        self.logger.info("  [PASSED] : {}".format(self.__test_dirs_per_group[index]))
                    else:
                        #self.logger.error("  [FAILED] : {}".format(test_dir_full))
                        self.logger.error("  [FAILED] : {}".format(self.__test_dirs_per_group[index]))
                        self.__failed_tests.append(test_dir_full)
            else:    
                self.logger.warning("spec dir not exists {}".format(tspecs_dir_full))

            index += 1    


    #==================================================================    
    def run_all_tspecs_per_test(self, tspecs_dir_full, tspec_names):
        self.logger.debug("  [tspec_names] : {}".format(tspec_names))
        for tspec_name in tspec_names:
            if(tspec_name.endswith(self.__tspec_ext)) :
                if (self.run_one_tspec(tspecs_dir_full+os.sep+tspec_name, tspec_name) != True):
                    #self.logger.error("        [FAILED] : {}".format(tspec_name))
                    self.logger.error("        [FAILED] ")
                    self.__failed_test_cnt += 1
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


# TODO 좋은 방법?
#///////////////////////////////////////////////////////////////////////////////
# lmt_time.py
#///////////////////////////////////////////////////////////////////////////////
def wait_secs(secs):
    lmt_time.wait_secs(_g_logger, secs)
    #tspec_cmd_impl.wait_secs(_g_logger, secs)

#///////////////////////////////////////////////////////////////////////////////
# lmt_shell.py
#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(cmd):
    lmt_shell.run_shell_cmd(_g_logger,cmd)
    #tspec_cmd_impl.run_shell_cmd(_g_logger,cmd)

#///////////////////////////////////////////////////////////////////////////////
# lmt_config.py
#///////////////////////////////////////////////////////////////////////////////
def set_cfg(path, xpath, val):
    lmt_config.set_cfg(_g_logger,path, xpath, val)


#///////////////////////////////////////////////////////////////////////////////
# lmt_assert.py
#///////////////////////////////////////////////////////////////////////////////
def test_eq(a,b):
    lmt_assert.test_eq(a,b)
    return True

def assert_app_running(service_name, process_name):
    lmt_assert.assert_app_running(_g_logger,service_name, process_name)
    return True

def assert_prc_running(proc_name):
    lmt_assert.assert_prc_running(_g_logger,proc_name)
    return True

def assert_file_grep(to_find_str, file_path):
    lmt_assert.assert_file_grep( _g_logger,to_find_str, file_path)
    return True

def assert_prc_same_pid(service_name, process_name):
    lmt_assert.assert_prc_same_pid(_g_logger,service_name, process_name)
    return True

def assert_alarm_exists(alarm_code):
    lmt_assert.assert_alarm_exists(_g_logger,alarm_code)
    return True

def assert_alarm_cleared(alarm_code):
    lmt_assert.assert_alarm_cleared(_g_logger,alarm_code)
    return True

def assert_mes_q_full(log_file_path):
    lmt_assert.assert_mes_q_full(_g_logger,log_file_path)
    return True

def assert_mes_q_not_full(log_file_path):
    lmt_assert.assert_mes_q_not_full(_g_logger,log_file_path)
    return True

def test_run_ok(cmd) :
    lmt_assert.test_run_ok(_g_logger, cmd)
    return True

def test_run_err(cmd) :
    lmt_assert.test_run_err(_g_logger,cmd) 
    return True

def test_eq_prc_output(cmd, val):
    lmt_assert.test_eq_prc_output(_g_logger,cmd, val)
    return True

#///////////////////////////////////////////////////////////////////////////////
# lmt_file.py
#///////////////////////////////////////////////////////////////////////////////
def save_cur_file_line_cnt(file_path):
    lmt_file.save_cur_file_line_cnt(_g_logger,file_path)
    return True

#///////////////////////////////////////////////////////////////////////////////
# lmt_memory.py
#///////////////////////////////////////////////////////////////////////////////
def make_swap(): 
    lmt_memory.make_swap(_g_logger) 
    return True


#///////////////////////////////////////////////////////////////////////////////
# lmt_process.py
#///////////////////////////////////////////////////////////////////////////////
def run_cli_cmd(cli_cmd):
    lmt_process.run_cli_cmd(_g_logger,cli_cmd)
    return True

def run_prc(run_cmd):
    lmt_process.run_prc(_g_logger,run_cmd)
    return True

def terminate_prc(proc_name):
    lmt_process.terminate_prc(_g_logger,proc_name)
    return True

def kill_prc(proc_name):
    lmt_process.kill_prc(_g_logger,proc_name)
    return True

def save_prc_pid(service_name, process_name):
    lmt_process.save_prc_pid(_g_logger,service_name, process_name)
    return True

def make_hangup(service_name, process_name,  hangup_time_sec):
    lmt_process.make_hangup(_g_logger,service_name, process_name, hangup_time_sec)
    return True


#///////////////////////////////////////////////////////////////////////////////
# lmt_report.py
#///////////////////////////////////////////////////////////////////////////////
def write_report_msg (msg):
    lmt_report.write_report_msg (_g_logger,msg)
    return True


#///////////////////////////////////////////////////////////////////////////////
# lmt_simul.py
#///////////////////////////////////////////////////////////////////////////////
def send_simul (cdr_dir):
    lmt_simul.send_simul (_g_logger,cdr_dir)
    return True


#///////////////////////////////////////////////////////////////////////////////
# tspec commands bridge 
#///////////////////////////////////////////////////////////////////////////////
#정보를 저장하고 다음 명령에서 찾을수 있어야 함
#TODO 개선 : tspec command 를 해당 모듈의 명령으로 전달만 수행 
def test_cmd(a,b,c):
    global _g_logger
    global __g_info_repo 
    #self.logger.info("invoked in context ") # error XXX 
    test_lib.test_1(_g_logger, a,b,c)
    __g_info_repo ["val a"] = a
    __g_info_repo ["val b"] = b
    __g_info_repo ["val c"] = c
    _g_logger.debug("_g_logger test 1") 
    #print(__g_info_repo)
    return True

def exception_test(a,b):
    test_lib.exception_test(a,b)

def test_cmd_remember():
    """
    global __g_info_repo 
    print("do you remember : ")
    print(__g_info_repo ) 
    print("clear repo  : ")
    __g_info_repo = {} 
    print(__g_info_repo ) 
    global _g_logger
    _g_logger.debug("_g_logger test 2 ") 
    """
    return True

