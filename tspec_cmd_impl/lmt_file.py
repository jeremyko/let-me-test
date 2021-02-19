#-*- coding: utf-8 -*-

import subprocess
import os
import glob
#import shutil

from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_xml_config

#///////////////////////////////////////////////////////////////////////////////
"""
def save_cur_file_line_cnt(runner_ctx,file_name):
    file_path = os.path.join(runner_ctx.log_base_path , runner_ctx.service_name ,   \
                        lmt_util.replace_all_symbols(runner_ctx,file_name))
    runner_ctx.logger.debug("{}file_path : {}".format(runner_ctx.cur_indent,file_path))

    line_cnt = int(subprocess.check_output(['wc', '-l', file_path]).split()[0])
    runner_ctx.logger.debug("{}file [{}] -> line cnt : {}".format(runner_ctx.cur_indent,file_path,line_cnt))
    runner_ctx.info_repo['line_cnt'] = line_cnt
    return True
"""

def remove_stat_file(runner_ctx,file_name):
    runner_ctx.logger.debug("{}remove_stat_file : {}".format(runner_ctx.cur_indent,file_name))
    file_path = runner_ctx.stat_path + runner_ctx.service_name + os.sep + \
                        lmt_util.replace_all_symbols(runner_ctx,file_name)
    runner_ctx.logger.debug("{}file_path : {}".format(runner_ctx.cur_indent,file_path))
    file_list=glob.glob(file_path)
    for del_file in file_list:
        #XXX safety check !!! 안전을 위해 bak 파일만 삭제되게 강제함
        if(del_file.find('bak')==-1):
            err_msg = 'not a .bak file, delete impossible : {}'.format(del_file)
            runner_ctx.logger.error("{}{}".
                    format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
        else:
            runner_ctx.logger.info("{} delete file : {}".format(runner_ctx.cur_indent,del_file))
            os.remove(del_file)
    return True
#///////////////////////////////////////////////////////////////////////////////
# ex) remove_app_file_log("VLD*.${CUR_YYYYMMDD}")
def remove_app_file_log(runner_ctx,file_name):
    runner_ctx.logger.debug("{}remove_app_file_log : {}".format(runner_ctx.cur_indent,file_name))
    file_path = os.path.join(runner_ctx.log_base_path , runner_ctx.service_name , \
                        lmt_util.replace_all_symbols(runner_ctx,file_name))
    runner_ctx.logger.debug("{}file_path : {}".format(runner_ctx.cur_indent,file_path))
    file_list=glob.glob(file_path)
    for del_file in file_list:
        #XXX safety check !!! 안전을 위해 LOG 파일만 삭제되게 강제함
        if(del_file.find('LOG')==-1):
            err_msg = 'not a LOG file, delete impossible : {}'.format(del_file)
            runner_ctx.logger.error("{}{}".
                    format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
        else:
            runner_ctx.logger.info("{} delete file : {}".format(runner_ctx.cur_indent,del_file))
            os.remove(del_file)
    return True

#///////////////////////////////////////////////////////////////////////////////
# ex) remove_pfnm_file_log("MES*.${CUR_YYYYMMDD}")
def remove_pfnm_file_log(runner_ctx,file_name):
    runner_ctx.logger.debug("{}remove_pfnm_file_log : {}".format(runner_ctx.cur_indent,file_name))

    #[DELL01:/POFCS/LOG/PFNM]ls /POFCS/LOG/PFNM/*/MES*20200720
    #/POFCS/LOG/PFNM/SVC/MES.01.LOG.20200720

    file_path = os.path.join(runner_ctx.log_base_path , "PFNM" , "*" , \
                        lmt_util.replace_all_symbols(runner_ctx,file_name))
    runner_ctx.logger.info("{}file_path : {}".format(runner_ctx.cur_indent,file_path))
    file_list=glob.glob(file_path)
    for del_file in file_list:
        #XXX safety check !!! 안전을 위해 LOG 파일만 삭제되게 강제함
        if(del_file.find('LOG')==-1):
            err_msg = 'not a LOG file, delete impossible : {}'.format(del_file)
            runner_ctx.logger.error("{}{}".
                    format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
        else:
            runner_ctx.logger.info("{} delete file : {}".format(runner_ctx.cur_indent,del_file))
            os.remove(del_file)
    return True

#///////////////////////////////////////////////////////////////////////////////
# 해당 폴더안의 파일 삭제. 폴더안의 폴더는 삭제 안됨. 인자로 넘긴 폴더는 삭제 안함
#ex) /POFCS/OUTPUT/GTP_PGW/IPMD 내 폴더 삭제 등에 사용
# XXX TODO DT 가 사용하는 *_LAST_INFO_MODIFIED 은 삭제하면 안됨. DT 재기동을 하면 무방

def remove_all_files(runner_ctx, del_dir_base) :
    if(os.sep == del_dir_base or '/CG' == del_dir_base):
        runner_ctx.logger.error("{}can not remove root dir !!")
        return False
 
    runner_ctx.logger.info("{}remove files in dir : {}".format(runner_ctx.cur_indent,del_dir_base))

    for root, dirs, files in os.walk(del_dir_base):
        for name in files:
            if "LAST_INFO_MODIFIED" not in name: #DT 정보 파일 제외
                runner_ctx.logger.info("{}remove file [{}]".format(runner_ctx.cur_indent, os.path.join(root, name))) 
                os.remove(os.path.join(root, name))

        #for name in dirs:
        #    runner_ctx.logger.info("{}remove dir  [{}]".format(runner_ctx.cur_indent, os.path.join(root, name)))
        #    shutil.rmtree(os.path.join(root, name))
    """
    dirs = os.listdir(del_dir_base)
    #TODO
    for one_dir in dirs :
        full_dir_path = os.path.join(del_dir_base, one_dir, "*")
        runner_ctx.logger.info("{}dir : {}".format(runner_ctx.cur_indent,full_dir_path))
        file_list=glob.glob(full_dir_path)
        for del_file in file_list:
            runner_ctx.logger.info("{} delete file : {}".format(runner_ctx.cur_indent,del_file))
            os.remove(del_file)
    #shutil.rmtree(del_dir_base)
    """
    return True


#///////////////////////////////////////////////////////////////////////////////
"""
[root@localhost FILE_DB]# ll
합계 20640
-rw-r--r--. 1 root root 2112100 11월 29  2019 5G_SA_AGG01.M.RFDB
-rw-r--r--. 1 root root 2112100 11월 29  2019 5G_SA_CRL01.I.RFDB
-rw-r--r--. 1 root root 2112100 11월 29  2019 5G_SA_CRL01.M.RFDB
-rw-r--r--. 1 root root 2112100 11월 20  2019 GTP_PGW_AGG02.M.RFDB
-rw-r--r--. 1 root root 2112100 11월 20  2019 GTP_PGW_CRL02.I.RFDB
-rw-r--r--. 1 root root 2112100 11월 20  2019 GTP_PGW_CRL02.M.RFDB
-rw-r--r--. 1 root root 2112100  2월 13 16:21 GTP_SMF_AGG01.I.RFDB
-rw-r--r--. 1 root root 2112100  7월 21 14:14 GTP_SMF_AGG01.M.RFDB
-rw-r--r--. 1 root root 2112100  7월 21 14:14 GTP_SMF_CRL01.I.RFDB
-rw-r--r--. 1 root root 2112100  7월 21 14:14 GTP_SMF_CRL01.M.RFDB
"""
#///////////////////////////////////////////////////////////////////////////////
def clear_file_db(runner_ctx, proc_name='ALL') :
    runner_ctx.logger.info("{}---proc_name= [{}]".format(runner_ctx.cur_indent,proc_name ))
    #get file db dir path from NMD_Config.xml
    #ex) APPLICATION/COMMON/RFDB_IMS
    file_db_xpath = 'APPLICATION/COMMON/RFDB_' + runner_ctx.service_name
    runner_ctx.logger.info("{}file db xpath= [{}]".format(runner_ctx.cur_indent,file_db_xpath))

    file_db_dir = lmt_xml_config.get_xml_cfg(runner_ctx, file_db_xpath)
    runner_ctx.logger.info("{}file_db_dir = [{}]".format(runner_ctx.cur_indent,file_db_dir))
    #ex) /OPER/FILE_DB    

    #get list of file db files
    file_db_files = os.path.join(file_db_dir, "*")
    runner_ctx.logger.debug("{}dir : {}".format(runner_ctx.cur_indent,file_db_files))
    file_list=glob.glob(file_db_files)
    for file_db in file_list:
        if(runner_ctx.service_name in file_db):
            fdb_cmd = "fdbClear -d {}".format(file_db)
            if(proc_name != 'ALL'):
                if(proc_name in file_db):
                    #run fdbClear 
                    runner_ctx.logger.info("{} file db clear [{}]".format(runner_ctx.cur_indent,fdb_cmd))
                    lmt_util.run_shell_cmd(runner_ctx, fdb_cmd ) 
            else:        
                #run fdbClear 
                #ex) fdbClear -d /CG/FILE_DB/5G_SA_AGG01.M.RFDB
                runner_ctx.logger.info("{} file db clear [{}]".format(runner_ctx.cur_indent,fdb_cmd))
                lmt_util.run_shell_cmd(runner_ctx, fdb_cmd ) 



