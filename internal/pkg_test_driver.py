#-*- coding: utf-8 -*-

import sys
import os

from tspec_cmd_impl import test_lib

_g_info_repo = {}
_g_logger  = None

#///////////////////////////////////////////////////////////////////////////////
"""
.
└── test_pkg
    ├── group_001
    │   ├── grp001_test001
    │   │   ├── data
    │   │   │   └── mydata_01
    │   │   │       └── test.txt
    │   │   └── tspecs
    │   │       ├── grp001_test001_spec001.tspec
    │   │       └── grp001_test001_spec002.tspec
    │   └── grp001_test002
    │       ├── data
    │       │   └── mydata_01
    │       │       └── test.txt
    │       └── tspecs
    │           ├── grp001_test002_spec001.tspec
    │           └── grp001_test002_spec002.tspec
    └── group_002
        ├── grp002_test001
        │   ├── data
        │   │   └── mydata_01
        │   │       └── test.txt
        │   └── tspecs
        │       ├── grp002_test001_spec001.tspec
        │       └── grp002_test001_spec002.tspec
        └── grp002_test002
            ├── data
            │   └── mydata_01
            │       └── test.txt
            └── tspecs
                ├── grp002_test002_spec001.tspec
                └── grp002_test002_spec002.tspec
"""   

#///////////////////////////////////////////////////////////////////////////////
class PkgTestDriver:

    #config = None
    _group_dirs = []
    _test_dir_per_group = []
    _args = None
    _tspec_ext ='.tspec'
    _group_prefix ='group_'

    #==================================================================    
    def __init__(self,logger,args):
        self.logger = logger;
        self._args = args
        global _g_logger
        _g_logger = logger

    #==================================================================    
    def run_auto_test(self):
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
            else:            
                err_msg ="invalid pkg dir {}".format(_args.pkg_dir)
                self.logger.error(err_msg)
                return False

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
                self._group_dirs.append(pkg_dir+os.sep+dir_name)

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
            self.logger.debug("--- group {}".format(grp_dir))
            self.get_all_test_cases_per_group(grp_dir)
            if(self._test_dirs_per_group):
                self.run_all_tests_per_group(self._test_dirs_per_group)

    #==================================================================    
    def run_all_tests_per_group(self, test_dirs):
        for test_dir in test_dirs:
            self.logger.debug("  --> test dir {}".format(test_dir))
            tspecs_dir = test_dir +"/tspecs"
            self.logger.debug("  --> test spec dir {}".format(tspecs_dir))
            if(os.path.exists(tspecs_dir)):
                test_specs_per_test = os.listdir(tspecs_dir)
                if(test_specs_per_test):
                    test_specs_per_test.sort()
                    self.run_all_tspecs_per_test(tspecs_dir,test_specs_per_test)
            else:    
                self.logger.warning("spec dir not exists {}".format(test_specs_per_test))

    #==================================================================    
    def run_all_tspecs_per_test(self,tspecs_dir,test_specs_per_test):
        for tspec in test_specs_per_test:
            if(tspec.endswith(self._tspec_ext)) :
                # group_dir , test_dir, specs_dir, test_specs_per_test
                if (self.run_one_tspec(tspecs_dir+os.sep+tspec) != True):
                    self.logger.critical("test failed : {}".format(tspec))
                    return False
        return True

    #==================================================================    
    # run tspec file
    #==================================================================    
    def run_one_tspec(self, tspec):
        self.logger.info("    --> tspec file : {}".format(tspec))
        try:
            execfile(tspec)
            #my_locals = {"self": self}
            #execfile(tspec, globals(),my_locals)
        except Exception as e:
            err_msg = 'error : {} :{}'.format(e.__doc__, e.message)
            self.logger.error(err_msg)
            return False
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
    _g_logger.info("_g_logger test 1") 
    #print(_g_info_repo)
    return True

def test_cmd_remember():
    global _g_info_repo 
    print("do you remember : ")
    print(_g_info_repo ) 
    print("clear repo  : ")
    _g_info_repo = {} 
    print(_g_info_repo ) 
    global _g_logger
    _g_logger.info("_g_logger test 2 ") 
    return True


