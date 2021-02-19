#-*- coding: utf-8 -*-

#202007 kojh create

import sys
import os
import glob
import datetime
import subprocess
import traceback
import configparser
import shutil
import logging

from tspec_cmd_impl import *
from module_core import *

_g_runner_self  = None # XXX

#///////////////////////////////////////////////////////////////////////////////
class PkgTestRunner:
    logger = None
    logger_summary = None
    __args = None
    __ini_config = None
    __group_dirs      = [] # name only
    __group_dirs_full = [] # full path
    __test_dirs_per_group      = []
    __test_dirs_per_group_full = []
    __total_test_cnt  = 0
    __total_tspec_cnt = 0
    __failed_tests  = [] 
    __succeeded_tests  = [] 
    __failed_test_cnt = 0 
    __succeeded_test_cnt = 0
    temp_internal_use_only_dir = None
    temp_internal_use_only_dir_remote = None
    __log_level    = None

    #DB ----------------
    ora_conn_str = None
    mysql_host   = None 
    mysql_user   = None  
    mysql_passwd = None
    mysql_db_name= None
    #  ----------------
    pkg_dir      = None
    package_id   = None
    package_name = None
    system_name  = None
    service_name  = None
    xml_cfg_path = None
    xml_db_path  = None
    input_path   = None
    work_path    = None
    stat_path = None
    output_path  = None
    pfnm_userid  = None
    pfnm_passwd  = None
    cli_name     = None
    db_type      = None
    log_base_path= None
    cur_ctx_test_path= None
    is_xml_config_changed = False
    start_all_prc_per_tspec = 'Y'
    ini_config_path_full = None
    simul_name   = None  
    cur_indent   = None
    simul_gsn_binding_ip   = None
    simul_gsn_binding_port = None
    simul_gtp_ip           = None
    simul_gtp_port         = None
    simul_dm_base_path  = None # XXX diameter simul only XXX
    #simul_tps       = 0 
    pid_save        = [] 
    info_repo        = {} 
    cleanup_cli_cmds = [] # 1개의 tspec 이 종료되고, xml db, xml config가 원복된후 수행될 CLI 명령을 관리
    change_xml_dbs   = {} # table_name:is_changed
    dm_sim_cfg_backup_files = [] # dm simul only. client.list, tas01.ini ...

    PKG_CFG_NAME     ='per_pkg.ini'
    TSPEC_FILE_EXT   ='.tspec'
    TSPEC_DIR_NAME   = 'tspecs'
    GROUP_DIR_PREFIX ='group_'
    xml_data_string =''
    ems_ip = None
    ems_id = None
    ems_passwd = None
    ems_xml_cfg_path = None
    ems_is_xml_config_changed = False
    ems_cli_cmd = None
    ems_package_name = None
    ems_system_name = None
    ems_service_name = None
    ems_policy_path = None
    start_timestamp = None 
    test_result_dir = None
    #==================================================================    
    def __init__(self,logger,logger_summary,timestamp,args):
        self.__ini_config = configparser.ConfigParser()
        self.pkg_dir = args.pkg_dir 
        self.logger = logger;
        self.logger_summary = logger_summary;
        self.start_timestamp = timestamp 
        self.test_result_dir = self.pkg_dir + "pkg_test_result"
        self.test_result_dir = os.path.join(self.test_result_dir, "{}_RESULT_DATA".format(timestamp) )
        self.__args = args
        self.pkg_dir = os.path.abspath(self.pkg_dir) + os.sep

        global _g_runner_self
        _g_runner_self = self
        self.reset_variables()

    #==================================================================    
    def reset_variables(self):
        self.cur_ctx_test_path = None
        self.__group_dirs      = [] 
        self.__group_dirs_full = [] 
        self.__test_dirs_per_group      = []
        self.__test_dirs_per_group_full = []
        self.__total_test_cnt = 0
        self.__total_tspec_cnt = 0
        self.__failed_tests    = []
        self.__succeeded_tests = []
        self.__failed_test_cnt = 0 
        self.__succeeded_test_cnt = 0
        self.__failed_tspec_cnt = 0 
        self.__succeeded_tspec_cnt = 0
        self.pid_save = [] 
        self.info_repo = {} 
        self.cleanup_cli_cmds = [] 
        self.change_xml_dbs  = {} 
        self.dm_sim_cfg_backup_files =[]
        self.cur_indent   = '          '

    #==================================================================    
    def run_teardown_if_any(self):
        self.logger.info("\n\n")
        setup_path = os.path.join(self.pkg_dir,'pkg_teardown.tspec')
        if os.path.isfile(setup_path): 
            self.logger.info(">> run pkg common tspec (teardown.tspec)")
            execfile(setup_path)

    #==================================================================    
    def display_run_result(self):
        if self.__total_tspec_cnt == 0 :
            self.logger.error("invalid run command. check cmd arguments")
            return;
        self.logger.info(" ")
        self.logger.info(" ")
        self.logger.info("---------------------------------------------------------")
        msg ="TOTAL {} TSPEC".format(self.__total_tspec_cnt)

        self.logger.info         (msg)
        self.logger_summary.info (msg)
        msg ="      {} OK".format(self.__succeeded_tspec_cnt)
        self.logger.info         (msg)
        self.logger_summary.info (msg)

        for succeeded in self.__succeeded_tests :
            msg = "        succeeded : {}".format(succeeded)
            self.logger.info        (msg)
            self.logger_summary.info(msg)

        if(self.__failed_test_cnt >0 ):
            msg ="      {} FAILED".format(self.__failed_tspec_cnt)
            self.logger.error        (msg)
            self.logger_summary.error(msg)

            for failed in self.__failed_tests :
                msg = "        failed    : {}".format(failed)
                self.logger.error        (msg)
                self.logger_summary.error(msg)

    #==================================================================    
    # run test 
    #==================================================================    
    def run_test(self):
        self.logger.info("pkg dir [{}]".format(self.pkg_dir))
        self.read_pkg_ini()
        self.reset_variables()
        #create temporary work directory 
        if(os.path.isdir(self.temp_internal_use_only_dir)==False):
            self.logger.debug("create internal use only dir : {}".
                    format(self.temp_internal_use_only_dir))
            os.mkdir(self.temp_internal_use_only_dir)

        #create result directory 
        self.__result_base_dir = self.pkg_dir + 'pkg_test_result'
        if(os.path.isdir(self.__result_base_dir)==False):
            self.logger.debug("create result dir : {}".
                    format(self.__result_base_dir))
            os.mkdir(self.__result_base_dir)

        self.set_log_level()

        self.get_groups ()

        if(self.__group_dirs):
            #-------------------------------------------
            # XXX : run setup.tspec if any.
            setup_path = os.path.join(self.pkg_dir,'pkg_setup.tspec')
            if os.path.isfile(setup_path): 
                self.logger.info("\n\n")
                self.logger.info(">> run pkg common tspec (setup.tspec)")
                execfile(setup_path)
            #-------------------------------------------
            self.logger.info("run groups : {}".format(self.__group_dirs))
            self.run_groups()
        else:            
            err_msg ="invalid pkg dir or usage {}".format(self.pkg_dir)
            self.logger.error(err_msg)
            self.logger_summary.error(err_msg)
            return False

        return True

    #==================================================================    
    def strip_all_members(self):
        self.xml_cfg_path = self.xml_cfg_path.strip()
        self.xml_db_path  = self.xml_db_path .strip()
        self.package_id   = self.package_id.strip()
        self.package_name = self.package_name.strip()
        self.system_name  = self.system_name .strip()
        self.service_name = self.service_name.strip()
        self.cli_name     = self.cli_name    .strip()
        self.log_base_path= self.log_base_path.strip()
        self.pfnm_userid  = self.pfnm_userid.strip()
        self.pfnm_passwd  = self.pfnm_passwd.strip()
        self.db_type      = self.db_type.strip()
        self.start_all_prc_per_tspec  = self.start_all_prc_per_tspec.strip()
        self.input_path   = self.input_path.strip() 
        self.work_path    = self.work_path.strip()
        self.output_path  = self.output_path.strip()
        self.stat_path    = self.stat_path.strip()
        self.ems_xml_cfg_path    = self.ems_xml_cfg_path.strip()
        self.ems_policy_path     = self.ems_policy_path.strip()

        if(self.simul_dm_base_path):
            self.simul_dm_base_path  = self.simul_dm_base_path.strip()

    #==================================================================    
    def remove_tailing_os_sep (self): 
        # XXX 모든 설정의 경로 값은 끝에 '/' 가 불필요하다. 만약 잘못 설정한 경우
        # 마지막 '/' 를 제거한다.
        """
        '/LOG/'  --> '/LOG'
        """   
        if self.xml_cfg_path.endswith(os.sep):
            self.xml_cfg_path = self.xml_cfg_path[:-1]

        if self.xml_db_path.endswith(os.sep):
            self.xml_db_path = self.xml_db_path[:-1]

        if self.log_base_path.endswith(os.sep):
            self.log_base_path = self.log_base_path[:-1]

        if(self.simul_dm_base_path):
            if self.simul_dm_base_path.endswith(os.sep):
                self.simul_dm_base_path = self.simul_dm_base_path[:-1]

        if self.input_path.endswith(os.sep):
            self.input_path = self.input_path[:-1]

        if self.work_path.endswith(os.sep):
            self.work_path = self.work_path[:-1]

        if self.output_path.endswith(os.sep):
            self.output_path = self.output_path[:-1]

        if self.stat_path.endswith(os.sep):
            self.stat_path = self.stat_path[:-1]

        if self.ems_xml_cfg_path.endswith(os.sep):
            self.ems_xml_cfg_path = self.ems_xml_cfg_path[:-1]

        if self.ems_policy_path.endswith(os.sep):
            self.ems_policy_path = self.ems_policy_path[:-1]

    #==================================================================    
    def read_pkg_ini(self):
        # read per_pkg.ini, pkg_dir ends with os.sep
        self.ini_config_path_full = self.pkg_dir+self.PKG_CFG_NAME
        if (os.path.isfile(self.ini_config_path_full) == False):
            err_msg ="invalid cfg path {}".format(self.ini_config_path_full)
            self.logger.error(err_msg)
            return False

        self.__ini_config.read(self.ini_config_path_full)
        self.package_id   = self.__ini_config['COMMON']['PACKAGE_ID']
        self.package_name = self.__ini_config['COMMON']['PACKAGE_NAME']
        self.system_name  = self.__ini_config['COMMON']['SYSTEM_NAME']
        self.service_name = self.__ini_config['COMMON']['SERVICE_NAME']
        self.xml_cfg_path = self.__ini_config['COMMON']['CONFIG_PATH']
        self.xml_db_path  = self.__ini_config['COMMON']['XML_DB_PATH']
        self.input_path   = self.__ini_config['COMMON']['INPUT_PATH']
        self.work_path    = self.__ini_config['COMMON']['WORK_PATH']
        self.output_path  = self.__ini_config['COMMON']['OUTPUT_PATH']
        self.stat_path    = self.__ini_config['COMMON']['STAT_PATH']
        self.cli_name     = self.__ini_config['COMMON']['CLI_NAME']
        self.start_all_prc_per_tspec = self.__ini_config['COMMON']['START_ALL_PRC_PER_TSPEC']
        self.__log_level  = self.__ini_config['LOG']['LOG_LEVEL']
        self.log_base_path= self.__ini_config['LOG']['LOG_BASE_PATH']

        self.pfnm_userid  = self.__ini_config['PFNM']['USER']
        self.pfnm_passwd  = self.__ini_config['PFNM']['PASSWD']
        self.db_type      = self.__ini_config['DB']['DB_TYPE']
        if(self.__ini_config.has_option('DB', 'ORA_CONN')):
            self.ora_conn_str = self.__ini_config['DB']['ORA_CONN']
        if(self.__ini_config.has_option('DB', 'MYSQL_HOST')):
            self.mysql_host   = self.__ini_config['DB']['MYSQL_HOST']
            self.mysql_user   = self.__ini_config['DB']['MYSQL_USER']
            self.mysql_passwd = self.__ini_config['DB']['MYSQL_PASSWD']
            self.mysql_db_name= self.__ini_config['DB']['MYSQL_DB_NAME']

        if(self.db_type =='ORACLE' and self.ora_conn_str ==None):
            err_msg ="oracle connection string not set"
            self.logger.error(err_msg)
            return False
        if self.db_type =='MYSQL' :
            if self.mysql_host ==None or self.mysql_user ==None or \
               self.mysql_passwd ==None or self.mysql_db_name ==None  :
                err_msg ="mysql db info not all set"
                self.logger.error(err_msg)
                return False

        if(self.__ini_config.has_option('SIMUL', 'SIMUL_NAME')):
            self.simul_name             = self.__ini_config['SIMUL']['SIMUL_NAME']

        if(self.__ini_config.has_option('GSN_CONFIG', 'GSN_BINDING_IP')):
            # XXX gtp only !
            # T_GTP_NODE_INFO 에 존재해야함. GTP 가 미리 정의된 GSN 으로 부터만 수신함.
            # GTP 에서 메시지 수신시 전송처의 port ,ip 를 찾는 로직이 존재한다.
            self.simul_gsn_binding_ip   = self.__ini_config['GSN_CONFIG']['GSN_BINDING_IP']
            self.simul_gsn_binding_port = self.__ini_config['GSN_CONFIG']['GSN_BINDING_PORT']
            # GTP info : GTP 프로세스가 binding한 ip, port 정보
            # T_GTP_DEF 에 존재해야함. GTP 기동시 server로 동작하는 정보임
            self.simul_gtp_ip           = self.__ini_config['GTP_CONFIG']['GTP_IP']
            self.simul_gtp_port         = self.__ini_config['GTP_CONFIG']['GTP_PORT']
            #self.simul_tps              = self.__ini_config['TPS_CONFIG']['SEND_PER_SECOND']
            #simul 에서 직접 설정을 읽어서 TPS 처리 하므로 여기서 불필요


        if(self.__ini_config.has_option('SIMUL', 'SUMUL_DM_BASE_PATH')):
            # diameter simul only !!
            # XXX : diameter simul use relative path !!!! 
            # /CG/OFCS_SIM/IMS_SIM/config --> client.list
            # /CG/OFCS_SIM/IMS_SIM/raw    --> tas01.ini 
            self.simul_dm_base_path  = self.__ini_config['SIMUL']['SUMUL_DM_BASE_PATH']

        if(self.__ini_config.has_option('EMS', 'IP')==False):
            self.logger.error("- EMS CONFIG NOT EXISTS")
            return False

        self.ems_ip             = self.__ini_config['EMS']['IP']
        self.ems_id             = self.__ini_config['EMS']['ID']
        self.ems_passwd         = self.__ini_config['EMS']['PASSWD']
        self.ems_xml_cfg_path   = self.__ini_config['EMS']['CONFIG_PATH']
        self.ems_cli_name       = self.__ini_config['EMS']['CLI_NAME']
        self.ems_package_name   = self.__ini_config['EMS']['PACKAGE_NAME']
        self.ems_system_name    = self.__ini_config['EMS']['SYSTEM_NAME']
        self.ems_service_name    = self.__ini_config['EMS']['SERVICE_NAME']
        self.ems_policy_path    = self.__ini_config['EMS']['POLICY_PATH']


        self.strip_all_members()
        self.remove_tailing_os_sep()

        self.logger.info("- xml_cfg_path [{}]".format(self.xml_cfg_path))
        self.logger.info("- xml_db_path  [{}]".format(self.xml_db_path))
        self.logger.info("- input_path   [{}]".format(self.input_path))
        self.logger.info("- work_path    [{}]".format(self.work_path))
        self.logger.info("- stat_path    [{}]".format(self.stat_path))
        self.logger.info("- output_path  [{}]".format(self.output_path))
        self.logger.info("- package_id   [{}]".format(self.package_id))
        self.logger.info("- package_name [{}]".format(self.package_name))
        self.logger.info("- system_name  [{}]".format(self.system_name ))
        self.logger.info("- service_name [{}]".format(self.service_name ))
        self.logger.info("- cli_name     [{}]".format(self.cli_name ))
        self.logger.info("- log_level    [{}]".format(self.__log_level   ))
        self.logger.info("- log_base_path[{}]".format(self.log_base_path ))
        self.logger.info("- db_type      [{}]".format(self.db_type ))
        if self.db_type =='ORACLE' : 
            self.logger.info("- conn str     [{}]".format(self.ora_conn_str))
        if self.db_type =='MYSQL' :
            self.logger.info("- host         [{}]".format(self.mysql_host   ))
            self.logger.info("- user         [{}]".format(self.mysql_user   ))
            #self.logger.info("- passwd       [{}]".format(self.mysql_passwd ))
            self.logger.info("- db name      [{}]".format(self.mysql_db_name))

        self.logger.info("- simul_name   [{}]".format(self.simul_name ))
        self.logger.info("- simul_gsn_binding_ip  [{}]".format(self.simul_gsn_binding_ip ))
        self.logger.info("- simul_gsn_binding_port[{}]".format(self.simul_gsn_binding_port ))
        self.logger.info("- simul_gtp_ip [{}]".format(self.simul_gtp_ip ))
        self.logger.info("- simul_gtp_ip [{}]".format(self.simul_gtp_port ))
        #self.logger.info("- simul_tps    [{}]".format(self.simul_tps ))
        self.logger.info("- start_all_prc_per_tspec [{}]".format(self.start_all_prc_per_tspec ))

        self.temp_internal_use_only_dir = self.pkg_dir + 'do_not_delete_internal_use'
        self.logger.debug("- internal_use_only_dir [{}]".
                format(self.temp_internal_use_only_dir))
        if(self.simul_dm_base_path):
            self.logger.info("- simul_dm_base_path [{}]".format(self.simul_dm_base_path ))

        self.temp_internal_use_only_dir_remote = self.temp_internal_use_only_dir + '/remote'
        self.logger.info("- test result dir        [{}]".format(self.test_result_dir ))

    #==================================================================    
    def set_log_level(self):
        #print ("log level is {}".format(self.__log_level))
        if(self.__log_level == 'DEBUG'):
            self.logger.setLevel(logging.DEBUG) 
        elif(self.__log_level == 'INFO'):
            self.logger.setLevel(logging.INFO) 
        elif(self.__log_level == 'WARNING'):
            self.logger.setLevel(logging.WARNING) 
        elif(self.__log_level == 'ERROR'):
            self.logger.setLevel(logging.ERROR) 
        elif(self.__log_level == 'CRITICAL'):
            self.logger.setLevel(logging.CRITICAL) 
        else:
            self.logger.setLevel(logging.INFO) 

    #==================================================================    
    #remove temp directory : self.temp_internal_use_only_dir 
    def clean_all(self):
        self.logger.debug("clean all temporary files")
        if(os.path.isdir(self.temp_internal_use_only_dir)):
            self.logger.debug("remove internal use only dir : {}".
                    format(self.temp_internal_use_only_dir))
            shutil.rmtree(self.temp_internal_use_only_dir) #XXX dangerous 

        return True

    #==================================================================    
    def get_groups(self):
        grp_dirs = os.listdir(self.pkg_dir)
        grp_dirs.sort()
        self.__group_dirs = []
        self.__group_dirs_full = []
        for grp_dir_name in grp_dirs :
            if(grp_dir_name.startswith(self.GROUP_DIR_PREFIX)) :
                # this is group directory
                if(self.__args.group is not None):
                    #TODO dup check 
                    for grp_arg in self.__args.group:
                        if(grp_dir_name == grp_arg):
                            self.logger.info("[run specific group] {}".format(grp_dir_name))
                            self.__group_dirs_full.append(self.pkg_dir+grp_dir_name) 
                            self.__group_dirs.append(grp_dir_name) 
                else:    
                    self.__group_dirs_full.append(self.pkg_dir+grp_dir_name) 
                    # pkg_dir ends with os.sep
                    self.__group_dirs.append(grp_dir_name) 

    #==================================================================    
    def run_groups(self):
        index =0
        for grp_dir_name in self.__group_dirs :
            self.logger.debug(" ")
            self.logger.debug("================================= group {}".
                    format(self.__group_dirs_full[index]))
            # TODO group 별 grp_setup.py , grp_teardown.py 실행
            #----------------------------
            self.get_test_per_group(self.__group_dirs_full[index],grp_dir_name)
            #----------------------------
            index += 1    

            if(self.__test_dirs_per_group_full):
                start_dtime = datetime.datetime.now()
                #-------------------------------------
                self.run_tests_per_group(grp_dir_name)
                #-------------------------------------
                end_dtime = datetime.datetime.now()
                elapsed = end_dtime - start_dtime
                self.logger.info(" ")
                if(len(self.__failed_tests)>0):
                    self.logger.error("[FAILED]   {} -> elapsed : {} secs".
                        format(grp_dir_name, elapsed.total_seconds()))
                else:    
                    self.logger.info("[PASSED]   {} -> elapsed : {} secs".
                        format(grp_dir_name, elapsed.total_seconds()))


    #==================================================================    
    def get_test_per_group(self, group_dir_full, grp_dir_name):
        self.logger.debug("grp_dir_name = {}".format(grp_dir_name))
        self.__test_dirs_per_group_full = []
        self.__test_dirs_per_group      = []
        test_dirs = os.listdir(group_dir_full)
        test_dirs.sort()
        for test_dir_name in test_dirs :
            if(not os.path.isdir(os.path.join(group_dir_full, test_dir_name))):
                self.logger.debug("not directory skip = {}".format(test_dir_name))
                continue

            self.logger.debug("test name = {}".format(test_dir_name))
            if(self.__args.test_id is not None):
                #run specific test : -t [group name].[test name]
                # ex) 'group_001.grp001_test001' 
                filter_name = grp_dir_name + "." + test_dir_name
                self.logger.debug("filter_name = {}".format(filter_name))
                for grp_and_test in self.__args.test_id:
                    if(filter_name == grp_and_test):
                        self.logger.debug("[run specific test] {}".format(grp_and_test))
                        self.__test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir_name)
                        self.__test_dirs_per_group.append(test_dir_name)
            elif(self.__args.spec is not None): #XXX specific tspec 
                for spec in self.__args.spec :
                    if grp_dir_name in spec :
                        if test_dir_name in spec :
                            test_dir = group_dir_full+os.sep+test_dir_name                     
                            if(test_dir not in self.__test_dirs_per_group_full):                     
                                self.__test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir_name)
                                self.__test_dirs_per_group.append(test_dir_name)
                                self.logger.debug("[run test] {}, {}".format(test_dir_name, spec))
            else:       
                self.logger.debug("[run whole test] {}".format(test_dir_name))
                self.__test_dirs_per_group_full.append(group_dir_full+os.sep+test_dir_name)
                self.__test_dirs_per_group.append(test_dir_name)

    #==================================================================    
    def run_tests_per_group(self, grp_dir_name):
        if(self.__args.spec is not None): #XXX specific tspec 
            is_found = False
            for spec in self.__args.spec :
                if (grp_dir_name in spec) :
                    self.logger.debug("GROUP={} : FOUND".format(grp_dir_name))
                    is_found = True
                    break
            if (is_found ==False):
                self.logger.debug("GROUP={} : SKIP".format(grp_dir_name))
                return True

        self.logger.info(" ")
        self.logger.info("////////////////////////////////////////////////////////////////////////////////")
        self.logger.info("[GROUP]    {}".format(grp_dir_name))
        #self.logger.debug(" --> TEST DIRS : {}".format(self.__test_dirs_per_group_full))
        index = 0
        for test_dir_full in self.__test_dirs_per_group_full :

            self.cur_ctx_test_path = os.path.abspath(test_dir_full) # absolute path
            start_dtime = datetime.datetime.now()
            self.__total_test_cnt += 1

            self.logger.debug("  --> test dir {}".format(test_dir_full))
            test_name = self.__test_dirs_per_group[index]
            self.logger.info(" ")
            self.logger.info(" ")
            self.logger.info("=== [TEST]    {}".format(test_name))
            self.logger.info(" ")
            tspecs_dir_full = test_dir_full +os.sep + self.TSPEC_DIR_NAME # tspec directory path
            # TODO test 별 test_setup.py , test_teardown.py 실행
            is_test_done = False
            #----------------------------
            if(os.path.isdir(tspecs_dir_full)):
                tspec_names = os.listdir(tspecs_dir_full) # all tspec path in tspec dir.
                tspec_names.sort()
                if(tspec_names):
                    #-----------------------------------------
                    is_all_tspec_ok = True
                    for tspec_name in tspec_names:
                        if(tspec_name.endswith(self.TSPEC_FILE_EXT)) :
                            #self.logger.debug("{}[tspec] {}".format(self.cur_indent,tspec_name))
                            if(self.__args.spec is not None): # specific tspec 
                                self.logger.debug("{}[filter tspec] {}".format(self.cur_indent, self.__args.spec))
                                #run specific tspec : -s [group name].[test name].[tspec name]
                                # ex) 'group_test.test001.spec001' 
                                filter_name = grp_dir_name + "." + test_name + "." + tspec_name 
                                self.logger.debug("{}filter_name = {}".format(self.cur_indent,filter_name))
                                for one_spec in self.__args.spec:
                                    if(filter_name==one_spec + self.TSPEC_FILE_EXT):
                                        self.logger.debug("{}==> tspec_name : {}".format(self.cur_indent, one_spec+ self.TSPEC_FILE_EXT))
                                        self.__total_tspec_cnt += 1
                                        is_test_done = True
                                        #--------------------
                                        tspec_name_no_ext = filter_name[:len(filter_name)-len(self.TSPEC_FILE_EXT)]
                                        if(self.run_one_tspec(tspecs_dir_full+os.sep+tspec_name, tspec_name) == False): 
                                            self.logger.error("{}tspec error : {}".format(self.cur_indent, filter_name))
                                            is_all_tspec_ok = False
                                            self.__failed_tspec_cnt += 1
                                            self.__failed_tests.append(tspec_name_no_ext)
                                        else:    
                                            self.__succeeded_tests.append(tspec_name_no_ext)
                                            self.__succeeded_tspec_cnt +=1
                            else:    
                                self.__total_tspec_cnt += 1
                                #self.logger.debug("{}==> tspec_name : {}".
                                #            format(self.cur_indent, grp_dir_name + "." + test_name + "." + tspec_name))
                                tspec_name_no_ext = tspec_name[:len(tspec_name)-len(self.TSPEC_FILE_EXT)]
                                is_test_done = True
                                if(self.run_one_tspec(tspecs_dir_full+os.sep+tspec_name, tspec_name) == False): 
                                    self.logger.error("{}tspec error : {}".format(self.cur_indent, 
                                                                    grp_dir_name + "." + test_name + "." + tspec_name))
                                    is_all_tspec_ok = False
                                    self.__failed_tspec_cnt += 1
                                    self.__failed_tests.append(grp_dir_name + "." + test_name +"."+ tspec_name_no_ext )
                                else:    
                                    self.__succeeded_tests.append(grp_dir_name + "." + test_name +"."+ tspec_name_no_ext)
                                    self.__succeeded_tspec_cnt +=1
                    #----------------------------------------- end of for 
                    self.logger.debug("{}all tspec end".format(self.cur_indent))
                    #all tspec end..                        
                    #check elapsed     
                    end_dtime = datetime.datetime.now()
                    elapsed = end_dtime - start_dtime
                    if is_test_done == False :
                        self.logger.error("{}no test done".format(self.cur_indent))
                        return True

                    if(is_all_tspec_ok == True):
                        self.__succeeded_test_cnt += 1
                        self.logger.debug("    [ALL TSPECS OK]  ")
                        self.logger.info(" ")
                        self.logger.info ("    [PASSED]  {} -> elapsed : {} sec".
                                format(self.__test_dirs_per_group[index],
                                    elapsed.total_seconds()))
                    else:
                        self.__failed_test_cnt += 1
                        self.logger.info(" ")
                        self.logger.error("    [SOME TSPEC FAILED] ")
                        self.logger.error("    [FAILED]  {} -> elapsed : {} sec".
                                format(self.__test_dirs_per_group[index],
                                    elapsed.total_seconds()))
            else:
                self.logger.error("tspec dir invalid : {}".format(tspecs_dir_full))
                return False

            index += 1    


    #==================================================================    
    # run a tspec file
    #==================================================================    
    def run_one_tspec(self, tspec_path_full, tspec_name):

        self.logger.info(" ")
        self.logger.info("======= [TSPEC] {}".format(tspec_name))
        self.logger.info(" ")
        try:
            self.is_xml_config_changed     = False
            self.ems_is_xml_config_changed = False
            self.change_xml_dbs            = {}
            self.pid_save                  = [] 
            self.info_repo                 = {} 
            self.cleanup_cli_cmds          = [] 
            self.dm_sim_cfg_backup_files   = []
            start_dtime = datetime.datetime.now()
            #XXX start all app first ...
            if(self.start_all_prc_per_tspec == 'Y'):
                lmt_process.run_cli_cmd_no_rollback(_g_runner_self,"STAR-PRC:${PACKAGE_NAME}:${SYSTEM_NAME}:${SERVICE_NAME}")

            #------------------------
            execfile(tspec_path_full)
            #------------------------

        except lmt_exception.LmtException as lmt_e:
            err_msg = '{}lmt exception : {} '.format(self.cur_indent,lmt_e)
            self.logger.error(err_msg)
            #traceback.print_exc()
            cl, exc, tb = sys.exc_info()
            if(tb):
                bt_len=len(traceback.extract_tb(tb))  
                if(bt_len>1):    
                    self.logger.error("{} - tspec   => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][0])) 
                    self.logger.error("{} - line no => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][1])) 
                    self.logger.error("{} - test    => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][3]))
                    #--------------
                    err_stack = traceback.extract_tb(tb)
                    for bt in err_stack:
                        self.logger.error("{}{}".format(self.cur_indent,bt))
                    #--------------
                del tb
            return False

        except Exception as e:
            err_msg = '{}error -> {} : {} :{}'. \
                format(self.cur_indent,tspec_name,e.__doc__, e.message)
            self.logger.error(err_msg)
            cl, exc, tb = sys.exc_info()
            if(tb):
                #traceback.print_exc()
                bt_len=len(traceback.extract_tb(tb))  
                if(bt_len>1):    
                    self.logger.error("{} - tspec   => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][0])) 
                    self.logger.error("{} - line no => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][1])) 
                    self.logger.error("{} - test    => {}". \
                            format(self.cur_indent,traceback.extract_tb(tb)[1][3]))
                    #--------------
                    err_stack = traceback.extract_tb(tb)
                    for bt in err_stack:
                        self.logger.error("{}{}".format(self.cur_indent,bt))
                    #--------------
                del tb
            return False

        finally:
            #XXX auto rollback       --> when tspec file ends..
            if(self.is_xml_config_changed == True):
                # set_xml_cfg 명령이 호출된 경우만 config 원복 
                self.logger.debug("{}auto rollback config".format(self.cur_indent)) 
                self.is_xml_config_changed = False
                self.rollback_config()

            if(self.ems_is_xml_config_changed == True):
                # set_xml_cfg 명령이 호출된 경우만 config 원복 
                self.logger.debug("{}auto rollback ems config".format(self.cur_indent)) 
                self.ems_is_xml_config_changed = False
                self.ems_rollback_config()

            if(len(self.change_xml_dbs) >0):
                # set_xml_db 명령이 호출된 경우만 xml db 원복 
                self.logger.debug("{}auto rollback xml_db".format(self.cur_indent)) 
                self.rollback_xml_db()
                self.change_xml_dbs = {}

            if(len(self.dm_sim_cfg_backup_files) > 0):
                # dm simul only
                #for backup in self.dm_sim_cfg_backup_files:
                #    self.logger.debug("{}backup : dm simul configs ={}".format(self.cur_indent,backup)) 

                self.logger.debug("{}auto rollback : dm simul configs".format(self.cur_indent)) 
                self.dm_simul_rollback_config()
                self.dm_sim_cfg_backup_files =[]

            #XXX invoke auto cleanup commands
            if(len(self.cleanup_cli_cmds)>0):
                self.logger.info("{}*** auto cleanup cli cmd".format(self.cur_indent)) 

            for cleanup_cmd in self.cleanup_cli_cmds: 
                self.logger.debug("{}auto cleanup cli cmd : {}".format(self.cur_indent,cleanup_cmd)) 
                #lmt_util.run_shell_cmd(self,cleanup_cmd) 
                os.system(cleanup_cmd)  # no error check.. XXX 
                lmt_time.wait_secs(self,5)

            self.cleanup_cli_cmds =[]    

        #check elapsed     
        end_dtime = datetime.datetime.now()
        elapsed = end_dtime - start_dtime
        self.logger.info("        [PASSED] {} , elapsed : {} sec".
                format(tspec_name,elapsed.total_seconds()))
        return True


    #==================================================================    
    def backup_config(self):
        src  = self.xml_cfg_path
        file_name = os.path.basename(self.xml_cfg_path)
        dest = os.path.join(self.temp_internal_use_only_dir, file_name )
        self.logger.debug("{}backup config : src  ={}".format(self.cur_indent, src))
        self.logger.debug("{}backup config : dest ={}".format(self.cur_indent, dest))
        #원본 파일은 move
        shutil.move(src, dest)
        #사용할 파일을 copy
        shutil.copyfile(dest, src)
        return True

    #==================================================================    
    def rollback_config(self):
        #self.logger.debug("rollback config")
        file_name = os.path.basename(self.xml_cfg_path)
        src  = os.path.join(self.temp_internal_use_only_dir, file_name )
        dest = self.xml_cfg_path
        self.logger.debug("{}rollback config : src  ={}".format(self.cur_indent, src))
        self.logger.debug("{}rollback config : dest ={}".format(self.cur_indent, dest))
        #원본 파일은 move
        shutil.move(src, dest)
        #shutil.copyfile(dest, src)
        return True

    #==================================================================    
    def ems_rollback_config(self):
        #self.logger.debug("rollback config")
        file_name = os.path.basename(self.ems_xml_cfg_path)
        src  = os.path.join(self.temp_internal_use_only_dir, file_name )
        dest = self.ems_xml_cfg_path
        self.logger.debug("{}rollback ems config : src  ={}".format(self.cur_indent, src))
        self.logger.debug("{}rollback ems config : dest ={}".format(self.cur_indent, dest))
        #원본 파일은 move
        #shutil.move(src, dest)
        #사용할 파일을 copy
        #shutil.copyfile(dest, src)
        lmt_remote.rollback_remote_file(self, self.ems_ip,self.ems_id, self.ems_passwd, self.ems_xml_cfg_path)
        return True
    #==================================================================    
    def backup_xml_db(self, table_path_full, table_name):
        self.change_xml_dbs[table_name] = True
        dest = os.path.join(self.temp_internal_use_only_dir, table_name)
        dest += ".xml"
        self.logger.debug("{}backup xml db : dest ={}".format(self.cur_indent, dest))
        #원본 파일은 move
        shutil.move(table_path_full, dest)
        #사용할 파일을 copy
        shutil.copyfile(dest, table_path_full)
        return True

    #==================================================================    
    def rollback_xml_db(self):
        self.logger.debug("{}ROLLBACK xml_db".format(self.cur_indent))
        self.logger.debug("{}self.change_xml_dbs : len= {}".format(self.cur_indent, len(self.change_xml_dbs)))
        for xml_db_file_name in self.change_xml_dbs:
            xml_db_file_name += ".xml"
            self.logger.debug("{}ROLLBACK : {}".format(self.cur_indent, xml_db_file_name))
            src  = os.path.join(self.temp_internal_use_only_dir, xml_db_file_name )
            dest = os.path.join(self.xml_db_path, xml_db_file_name)

            self.logger.debug("{}ROLLBACK xml_db : src  ={}".format(self.cur_indent, src))
            self.logger.debug("{}ROLLBACK xml_db : dest ={}".format(self.cur_indent, dest))
            #원본 파일은 move
            shutil.move(src, dest)
            #shutil.copyfile(dest, src)
        return True

    #==================================================================    
    # DIA_SIM 사용했던 설정파일 원복   
    def dm_simul_rollback_config(self):
        #XXX dm simul only  
        self.logger.debug("{}ROLLBACK dm simul config [{}]".format(self.cur_indent, self.simul_dm_base_path))
        # /CG/OFCS_SIM/IMS_SIM/config --> client.list
        # /CG/OFCS_SIM/IMS_SIM/raw    --> tas01.ini 
        #SIMUL_NAME = DIA_SIM
        #SUMUL_BASE_PATH=/CG/OFCS_SIM/IMS_SIM
        try:
            for dm_sim_cfg_file in self.dm_sim_cfg_backup_files:
                self.logger.info("{}dm_sim_cfg_file [{}] ".format(self.cur_indent, dm_sim_cfg_file))
                src  = os.path.join(self.temp_internal_use_only_dir, dm_sim_cfg_file )
                dest = ''
                if(dm_sim_cfg_file == 'client.list'):
                    dest = os.path.join(self.simul_dm_base_path,'config',dm_sim_cfg_file)
                elif('.ini' in dm_sim_cfg_file ):    
                    dest = os.path.join(self.simul_dm_base_path,'raw', dm_sim_cfg_file)

                self.logger.debug("{}ROLLBACK move client list : {} ==> {} ".format(self.cur_indent, src,dest))
                shutil.move(src, dest)
        except Exception as e:
            err_msg = '{}error -> {} :{}'. \
                format(self.cur_indent,e.__doc__, e.message)
            self.logger.error(err_msg)
            #--------------
            cl, exc, tb = sys.exc_info()
            err_stack = traceback.extract_tb(tb)
            for bt in err_stack:
                self.logger.error("{}{}".format(self.cur_indent,bt))
            #--------------
            del tb
            return False

        return True

#///////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
# tspec command 를 해당 모듈의 명령으로 전달 


#///////////////////////////////////////////////////////////////////////////////
# lmt_time.py
#///////////////////////////////////////////////////////////////////////////////
def wait_secs(secs):
    lmt_time.wait_secs(_g_runner_self, secs)

#///////////////////////////////////////////////////////////////////////////////
# lmt_shell.py
#///////////////////////////////////////////////////////////////////////////////
def run_shell_cmd(cmd):
    out = lmt_util.run_shell_cmd(_g_runner_self,cmd)
    return out

def run_shell_cmd_background(cmd):
    lmt_util.run_shell_cmd_background(_g_runner_self,cmd)

def do_interactive_cmd(run_cmd, dic_expect_val):
    lmt_shell.do_interactive_cmd(_g_runner_self,run_cmd,dic_expect_val)

#///////////////////////////////////////////////////////////////////////////////
# lmt_xml_config.py
#///////////////////////////////////////////////////////////////////////////////
def set_xml_cfg(xpath, val):
    lmt_xml_config.set_xml_cfg(_g_runner_self, xpath, val)
    return True

def get_xml_cfg(xpath):
    output = lmt_xml_config.get_xml_cfg(_g_runner_self, xpath)
    return output

def set_xml_cfg_ems(xpath, val):
    lmt_xml_config.set_xml_cfg_ems(_g_runner_self, xpath, val)
    return True

def get_xml_cfg_ems(xpath):
    output = lmt_xml_config.get_xml_cfg_ems(_g_runner_self, xpath)
    return output

#///////////////////////////////////////////////////////////////////////////////
# lmt_xml_db.py
#///////////////////////////////////////////////////////////////////////////////
def replace_xml_db_file (testing_file_path_full, table_name):
    lmt_xml_db.replace_xml_db_file(_g_runner_self, testing_file_path_full, table_name)
    return True

def assert_eq_xml_db_fields(table, dic_asserts, dic_conditons): 
    lmt_xml_db.assert_eq_xml_db_fields(_g_runner_self, table, dic_asserts, dic_conditons)
    return True

def set_xml_db(table, dic_field_vals, dic_conditons): 
    # table, field, val, kwargs
    lmt_xml_db.set_xml_db(_g_runner_self, table, dic_field_vals, dic_conditons)
    return True

""" not in use
def assert_eq_xml_db_field(*args, **kwargs): 
    # table, field, val, kwargs
    lmt_xml_db.assert_eq_xml_db_field(_g_runner_self, args, kwargs)
    return True
"""
#///////////////////////////////////////////////////////////////////////////////
# lmt_assert.py
#///////////////////////////////////////////////////////////////////////////////
def test_eq(a,b):
    lmt_assert.test_eq(_g_runner_self,a,b)

def assert_app_running(service_name, process_name, process_count):
    lmt_assert.assert_app_running(_g_runner_self,service_name, process_name, process_count)

def assert_prc_running(proc_name):
    lmt_assert.assert_prc_running(_g_runner_self,proc_name)

def assert_file_grep(to_find_str, file_name, max_wait_secs=0):
    lmt_assert.assert_file_grep( _g_runner_self,to_find_str, file_name, max_wait_secs)

def assert_file_grep_sequentially(to_find_str, file_name, max_wait_secs=0 ):
    lmt_assert.assert_file_grep_sequentially( _g_runner_self,to_find_str, file_name, max_wait_secs)

def assert_file_grep_sequentially_ems(to_find_str, file_name):
    lmt_assert.assert_file_grep_sequentially_ems( _g_runner_self,to_find_str, file_name, 0)

#not include 는 wait_secs를 수행하고 마지막에 호출하자
def assert_file_grep_sequentially_not_include(to_find_str, file_name):
    lmt_assert.assert_file_grep_sequentially_not_include( _g_runner_self,to_find_str, file_name, 0)

def assert_prc_same_pid(process_name):
    lmt_assert.assert_prc_same_pid(_g_runner_self,process_name)

def assert_alarm_exists(alarm_code):
    lmt_assert.assert_alarm_exists(_g_runner_self,alarm_code)

def assert_alarm_cleared(alarm_code):
    lmt_assert.assert_alarm_cleared(_g_runner_self,alarm_code)

def assert_mes_q_full(log_file_path):
    lmt_assert.assert_mes_q_full(_g_runner_self,log_file_path)

def assert_mes_q_not_full(log_file_path):
    lmt_assert.assert_mes_q_not_full(_g_runner_self,log_file_path)

def test_run_ok(cmd) :
    lmt_assert.test_run_ok(_g_runner_self, cmd)

def test_run_err(cmd) :
    lmt_assert.test_run_err(_g_runner_self,cmd) 

def assert_eq_cmd_output (cmd, expect_val):
    lmt_assert.assert_eq_cmd_output (_g_runner_self, cmd, expect_val)

def assert_cmd_output_include_string(cmd, expect_val):
    lmt_assert.assert_cmd_output_include_string(_g_runner_self, cmd, expect_val)

def assert_poll_cmd_output_include_string(cmd, expect_val, max_wait_secs=600):
    lmt_assert.assert_poll_cmd_output_include_string(_g_runner_self, cmd, expect_val, max_wait_secs)

#///////////////////////////////////////////////////////////////////////////////
# lmt_file.py
#///////////////////////////////////////////////////////////////////////////////
#def save_cur_file_line_cnt(file_name):
#    lmt_file.save_cur_file_line_cnt(_g_runner_self,file_name)

def remove_app_file_log(file_name):
    lmt_file.remove_app_file_log(_g_runner_self,file_name)

def remove_stat_file(file_name):
    lmt_file.remove_stat_file(_g_runner_self, file_name)

def remove_pfnm_file_log(file_name):
    lmt_file.remove_pfnm_file_log(_g_runner_self,file_name)

def remove_all_input_files() :
    """
    input 폴더내에 DATA, INFO 폴더가 있는데 이것들을 지우면 안됨. 자동 생성 안됨
    DATA, INFO 내의 파일만 지우게 처리한다.
    [DELL01:/POFCS/INPUT]cd /POFCS/INPUT/GTP_PGW
    [DELL01:/POFCS/INPUT/GTP_PGW]ll
    drwxrwxr-x 2 pofcs pofcs  4096  7월 22 13:50 DATA01
    drwxrwxr-x 2 pofcs pofcs     6  6월 24 20:18 DATA02
    drwxrwxr-x 2 pofcs pofcs 12288  7월 22 13:51 INFO01
    drwxrwxr-x 2 pofcs pofcs     6  6월 24 20:18 INFO02

    """
    del_input_dir = os.path.join( _g_runner_self.input_path , _g_runner_self.service_name )
    #get DATA, INFO directory list and remove files in it.
    del_dir_path = os.path.join(del_input_dir ,  "*" )
    dir_list=glob.glob(del_dir_path)
    for del_dir in dir_list:
        lmt_file.remove_all_files(_g_runner_self, del_dir ) 

    return True

def remove_all_work_files() :
    #XXX TODO DT 가 사용하는 *_LAST_INFO_MODIFIED 은 삭제하면 안됨. DT 재기동을 하면 무방
    del_work_dir = os.path.join( _g_runner_self.work_path , _g_runner_self.service_name )
    lmt_file.remove_all_files(_g_runner_self, del_work_dir ) 
    return True

# ex)  /POFCS/OUTPUT/GTP_PGW/IPMD/ 아래 모든 폴더내 파일 삭제
def remove_all_ipmd_output_files() :
    ipmd_dir_base = os.path.join( _g_runner_self.output_path , _g_runner_self.service_name ,"IPMD")
    lmt_file.remove_all_files(_g_runner_self, ipmd_dir_base) 
    return True

# ex)  /OUTPUT/IMS/ERR/ 아래 모든 폴더내 파일 삭제
def remove_all_err_output_files() :
    err_dir_base = os.path.join( _g_runner_self.output_path , _g_runner_self.service_name ,"ERR")
    lmt_file.remove_all_files(_g_runner_self, err_dir_base) 
    return True

# 해당 폴더안의 파일과 디렉토리 삭제. 인자로 넘긴 폴더는 삭제 안함
def remove_all_files(del_in_this_dir):
    lmt_file.remove_all_files(_g_runner_self, del_in_this_dir) 
    return True

def clear_file_db(proc_name='ALL') :
    lmt_file.clear_file_db(_g_runner_self,proc_name)

#///////////////////////////////////////////////////////////////////////////////
# lmt_oracle.py 
# lmt_mysql.py 
#///////////////////////////////////////////////////////////////////////////////
def assert_db_exists(table, where): 
    where = lmt_util.replace_all_symbols(_g_runner_self,where)
    if(_g_runner_self.db_type == 'ORACLE'):
        lmt_oracle.assert_oracle_exists(_g_runner_self,table, where) 
    elif(_g_runner_self.db_type == 'MYSQL'):
        lmt_mysql.assert_mysql_exists(_g_runner_self,table, where) 
    else:
        err_msg ="invalid DB type : {}".format(_g_runner_self.db_type)
        _g_runner_self.logger.error(err_msg)
        return False
    return True

def execute_sql(full_sql): 
    full_sql = lmt_util.replace_all_symbols(_g_runner_self,full_sql)
    if(_g_runner_self.db_type == 'ORACLE'):
        lmt_oracle.execute_sql(_g_runner_self,full_sql) 
    elif(_g_runner_self.db_type == 'MYSQL'):
        lmt_mysql.execute_sql(_g_runner_self,full_sql) 
    else:
        err_msg ="invalid DB type : {}".format(_g_runner_self.db_type)
        _g_runner_self.logger.error(err_msg)
        return False
    return True

#///////////////////////////////////////////////////////////////////////////////
# lmt_memory.py
#///////////////////////////////////////////////////////////////////////////////
def make_swap(): 
    lmt_memory.make_swap(_g_runner_self) 

def clear_mes_queue_restart_pfnm (): 
    #clear_all_shared_memory
    lmt_memory.clear_mes_queue_restart_pfnm(_g_runner_self) 

 
#///////////////////////////////////////////////////////////////////////////////
# lmt_process.py
#///////////////////////////////////////////////////////////////////////////////
def run_cli_cmd(cli_cmd):
    lmt_process.run_cli_cmd(_g_runner_self,cli_cmd)

def run_prc(run_cmd):
    lmt_process.run_prc(_g_runner_self,run_cmd)

def terminate_prc(proc_name):
    lmt_process.terminate_prc(_g_runner_self,proc_name)

def kill_prc(proc_name):
    lmt_process.kill_prc(_g_runner_self,proc_name)

def save_prc_pid(process_name):
    lmt_process.save_prc_pid(_g_runner_self,process_name)


#프로세스의 쓰레드 개수와 일치확인
def assert_process_thread_count_matching(name, expected_val):
    lmt_process.assert_process_thread_count_matching(_g_runner_self, name, expected_val)

#///////////////////////////////////////////////////////////////////////////////
# lmt_report.py
#///////////////////////////////////////////////////////////////////////////////
def write_report_msg (msg):
    lmt_report.write_report_msg (_g_runner_self,msg)


#///////////////////////////////////////////////////////////////////////////////
# lmt_simul.py
#///////////////////////////////////////////////////////////////////////////////
def send_simul_gtp (cdr_dir, config=None):
    config_path = config
    if config_path is None:
        lmt_simul.send_simul_gtp (_g_runner_self,cdr_dir,_g_runner_self.ini_config_path_full)
    else:    
        lmt_simul.send_simul_gtp (_g_runner_self,cdr_dir, config_path)

# XXX client.list 경로, tas01.ini 경로 인자로 넘긴다. 해당 파일을 copy 하여 사용후 , 원복 처리한다. 
# ex) send_simul_dm ("${TEST_DATA_DIR}/client_list/02.NotSpace", "${TEST_DATA_DIR}/raws/02.NotSpace") 
def send_simul_dm (client_list_path, raw_ini_path) :
    lmt_simul.send_simul_dm(_g_runner_self,client_list_path, raw_ini_path)

#///////////////////////////////////////////////////////////////////////////////
# lmt_network.py
#///////////////////////////////////////////////////////////////////////////////
def start_tcpdump(cmd_opt, dump_file_name):
    lmt_network.start_tcpdump(_g_runner_self,cmd_opt, dump_file_name)

def stop_tcpdump(cmd_opt):
    lmt_network.stop_tcpdump(_g_runner_self,cmd_opt)

#///////////////////////////////////////////////////////////////////////////////
# lmt_rms.py
#///////////////////////////////////////////////////////////////////////////////
def rms_mem_info_check():
    lmt_rms.rms_mem_info_check(_g_runner_self)

#///////////////////////////////////////////////////////////////////////////////
# lmt_remote.py
#///////////////////////////////////////////////////////////////////////////////
def assert_ems_zero_file_not_exist(path, file_name):
    lmt_remote.assert_ems_zero_file_not_exist(_g_runner_self, path, file_name)

def ems_run_shell_cmd(cmd):
    lmt_remote.ems_run_shell_cmd(_g_runner_self, cmd)

def ems_run_cli_cmd(cmd):
    lmt_remote.ems_run_cli_cmd(_g_runner_self, cmd)

def get_ems_file(file_name):
    lmt_remote.get_ems_file(_g_runner_self,file_name)

def put_ems_file(remote_path, file_name):
    lmt_remote.put_ems_file(_g_runner_self,remote_path, file_name)

def get_remote_file(host,user,password, file_name):
    lmt_remote.get_remote_file(_g_runner_self,host,user,password, file_name)

def put_remote_file(host,user,password,remote_path, local_path, file_name):
    lmt_remote.put_remote_file(_g_runner_self,host,user,password,remote_path, local_path, file_name, file_name)

def backup_ems_config(file_name_path):
    lmt_remote.backup_ems_config(_g_runner_self, file_name_path)

def rollback_ems_config(file_name_path):
    lmt_remote.rollback_ems_config(_g_runner_self, file_name_path)

def backup_remote_file(host,user,password, file_name_path):
    lmt_remote.backup_remote_file(_g_runner_self, host,user,password, file_name_path)

def psm_set_config_and_restart(after_min):
    lmt_remote.psm_set_config_and_restart(_g_runner_self, after_min)

def put_policy_files_to_ems():
    lmt_remote.put_policy_files_to_ems(_g_runner_self)

def test(name):
    lmt_process.test(_g_runner_self,name)
