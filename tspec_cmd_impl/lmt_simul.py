#-*- coding: utf-8 -*-

import pexpect
import os
import sys
import shutil
import time

from module_core import lmt_exception
from module_core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
def send_simul_gtp (runner_ctx,cdr_dir,config):
    # 5G_SIM -d <cdr_path> -c <config_path>
    runner_ctx.logger.info("{}simul_gsn_binding_ip   : {}".format(runner_ctx.cur_indent,runner_ctx.simul_gsn_binding_ip))
    runner_ctx.logger.info("{}simul_gsn_binding_port : {}".format(runner_ctx.cur_indent,runner_ctx.simul_gsn_binding_port))
    runner_ctx.logger.info("{}simul_gtp_ip           : {}".format(runner_ctx.cur_indent,runner_ctx.simul_gtp_ip))
    runner_ctx.logger.info("{}simul_gtp_port         : {}".format(runner_ctx.cur_indent,runner_ctx.simul_gtp_port))

    cdr_dir = lmt_util.replace_all_symbols(runner_ctx,cdr_dir)
    runner_ctx.logger.info("{}cdr dir : {}".format(runner_ctx.cur_indent,cdr_dir))

    # 5G_SIM -d <cdr_path> -c <config_path>
    simul_cmd = "{} -d {} -c {}".format( runner_ctx.simul_name, cdr_dir, config) 
    #runner_ctx.ini_config_path_full 
    #runner_ctx.logger.info("{}simul cmd : {}".format(runner_ctx.cur_indent,simul_cmd))

    lmt_util.run_shell_cmd(runner_ctx,simul_cmd) 

    # directory 끝에 '/' 여부 무관.
    # 5G_SIM  -c /root/SKT_PKGTEST/sample/OFCS/per_pkg.ini -d /root/POFCS_SIM/DUP_CDRS/
    # 5G_SIM  -c /root/SKT_PKGTEST/sample/OFCS/per_pkg.ini -d /root/POFCS_SIM/DUP_CDRS

    return True


#///////////////////////////////////////////////////////////////////////////////
#XXX user input 이 필요한 시뮬 처리 => DIA_SIM, mVoIP_SIM 
# DIA_SIM 은 상대 경로로 raw 디렉토리를 찾고 있다.
# DIA_SIM 은 상대 경로로 config 디렉토리를 찾고 있다.
# client.list 찾고, 그내용으로 tas01.ini 을 찾고 있다 
# 실행시 다음처럼 해줘야 함 : bash -c "cd /CG/OFCS_SIM/IMS_SIM/SRC; DIA_SIM"

# ex) send_simul_dm ("${TEST_DATA_DIR}/client_list/02.NotSpace/client.list", "${TEST_DATA_DIR}/raws/02.NotSpace/tas01.ini") 
#///////////////////////////////////////////////////////////////////////////////

def send_simul_dm (runner_ctx,client_list_path, raw_ini_path) :
    client_list_path = lmt_util.replace_all_symbols(runner_ctx,client_list_path)
    raw_ini_path = lmt_util.replace_all_symbols(runner_ctx,raw_ini_path)
    runner_ctx.logger.debug("{}client_list_path dir : {}".format(runner_ctx.cur_indent,client_list_path))
    runner_ctx.logger.debug("{}raw_ini_path dir     : {}".format(runner_ctx.cur_indent,raw_ini_path))
    # 먼저 client.list , tas01.ini 파일을 backup . 
    # XXX : diameter simul use relative path !!!! 
    # /CG/OFCS_SIM/IMS_SIM/config --> client.list
    # /CG/OFCS_SIM/IMS_SIM/raw    --> tas01.ini 
    #SIMUL_NAME = DIA_SIM
    #SUMUL_BASE_PATH=/CG/OFCS_SIM/IMS_SIM
    #------------------------------------------- backup
    # 원본 파일 backup
    list_name = os.path.basename(client_list_path) #client.list
    ini_name = os.path.basename(raw_ini_path)
    runner_ctx.dm_sim_cfg_backup_files.append(list_name)
    runner_ctx.dm_sim_cfg_backup_files.append(ini_name)
    runner_ctx.logger.debug("{}list_name      = {}".format(runner_ctx.cur_indent,list_name))
    runner_ctx.logger.debug("{}ini name       = {}".format(runner_ctx.cur_indent,ini_name))
    ori_client_list_path = os.path.join(runner_ctx.simul_dm_base_path,'config','client.list')
    ori_ini_path = os.path.join(runner_ctx.simul_dm_base_path,'raw',ini_name) 
    runner_ctx.logger.debug("{}BACKUP client.list, ini file".format(runner_ctx.cur_indent))
    runner_ctx.logger.debug("{}ori client.list = {}".format(runner_ctx.cur_indent,ori_client_list_path))
    runner_ctx.logger.debug("{}ori ini         = {}".format(runner_ctx.cur_indent,ori_ini_path))
    bkup_client_list = os.path.join(runner_ctx.temp_internal_use_only_dir, list_name)
    bkup_ini_file = os.path.join(runner_ctx.temp_internal_use_only_dir, ini_name)
    runner_ctx.logger.debug("{}backup list_name : dest ={}".format(runner_ctx.cur_indent,bkup_client_list))
    runner_ctx.logger.debug("{}backup ini       : dest ={}".format(runner_ctx.cur_indent,bkup_ini_file))
    #원본 파일 move --> backup
    shutil.move(ori_client_list_path, bkup_client_list)
    shutil.move(ori_ini_path, bkup_ini_file)

    #------------------------------------------- copy
    # client.list , tas01.ini 파일을 copy 하여 사용후, 원복 처리한다. 
    # *** 테스트할 client.list 파일 copy 
    shutil.copy(client_list_path, ori_client_list_path)

    # *** 테스트할 ini 파일 생성. copy 아니고 직접 파일 생성한다 
    # ini 파일 내용중 ACR_FILE_PATH=${TEST_DATA_DIR}/sample_cdr/02.NotSpace 이걸 실제 경로로 치환한다.
    # read sample ini file and replace string 
    f_ini_sample = open(raw_ini_path, "rt")
    ini_contents = f_ini_sample.read()
    ini_contents = lmt_util.replace_all_symbols(runner_ctx, ini_contents)
    f_ini_sample.close()
    runner_ctx.logger.info("{}sample ini file contents : {}".format(runner_ctx.cur_indent,ini_contents))

    # over write to existing ini file.
    f_ini_real = open(ori_ini_path, "wt")
    f_ini_real.write(ini_contents)
    f_ini_real.close()
    runner_ctx.logger.debug("{}real config over write done".format(runner_ctx.cur_indent))
    #debug
    runner_ctx.logger.info("{}new ini : {}".format(runner_ctx.cur_indent,raw_ini_path))
    runner_ctx.logger.info("{}contents".format(runner_ctx.cur_indent))
    os.system("cat {}".format(ori_ini_path)) #XXX debug

    #------------------------------------------- send simul
    timeout_sec = 120
    #-------------------------------------
    # ('/bin/bash -c "cd /CG/OFCS_SIM/IMS_SIM/SRC; ./DIA_SIM"')
    simul_cmd = '/bin/bash -c "cd {}/SRC; ./{}"'.format(runner_ctx.simul_dm_base_path, runner_ctx.simul_name)
    runner_ctx.logger.info("{}simul run ={}".format(runner_ctx.cur_indent,simul_cmd))
    child = pexpect.spawn(simul_cmd)
    child.logfile = sys.stdout
    #-------------------------------------
    child.setwinsize(200, 1000)
    for waited_cnt in range(0, timeout_sec):
        time.sleep(1)
        child.sendline('\n') # XXX 
        index = child.expect(['CLOSE_NOT_READY',pexpect.TIMEOUT], timeout=timeout_sec)
        if index == 0:
            runner_ctx.logger.info("{}CLOSE_NOT_READY".format(runner_ctx.cur_indent))
            break
        elif index ==1:
            runner_ctx.logger.info("{}timeout --> keep waiting {}".format(runner_ctx.cur_indent,waited_cnt))
            if(waited_cnt == timeout_sec-1):
                runner_ctx.logger.error("{}timeout --> giveup".format(runner_ctx.cur_indent))
                return False
            continue

    #-------------------------------------
    child.sendline('init 1\n')
    for waited_cnt in range(0, timeout_sec):
        time.sleep(1)
        child.sendline('\n') # XXX 
        index = child.expect(['OPEN_NOT_READY',pexpect.TIMEOUT], timeout=timeout_sec)
        if index == 0:
            runner_ctx.logger.info("{}OPEN_NOT_READY".format(runner_ctx.cur_indent))
            break
        elif index ==1:
            runner_ctx.logger.info("{}timeout --> keep waiting {}".format(runner_ctx.cur_indent,waited_cnt))
            if(waited_cnt == timeout_sec-1):
                runner_ctx.logger.error("{}timeout --> giveup".format(runner_ctx.cur_indent))
                return False
            continue
    #-------------------------------------
    child.sendline('load 1\n')
    for waited_cnt in range(0, timeout_sec):
        time.sleep(1)
        child.sendline('\n') # XXX 
        index = child.expect(['OPEN_READY',pexpect.TIMEOUT], timeout=timeout_sec)
        if index == 0:
            runner_ctx.logger.info("{}OPEN_READY".format(runner_ctx.cur_indent))
            break
        elif index ==1:
            runner_ctx.logger.info("{}timeout --> keep waiting {}".format(runner_ctx.cur_indent,waited_cnt))
            if(waited_cnt == timeout_sec-1):
                runner_ctx.logger.error("{}timeout --> giveup".format(runner_ctx.cur_indent))
                return False
            continue
    #-------------------------------------
    child.sendline('start 1\n')
    #child.expect('PROCESSING', timeout=timeout_sec)
    #runner_ctx.logger.info("PROCESSING")
    # XXX simul 에서 화면 갱신이 안됨. 원하는 값이 나올때까지 엔터 넣는다
    for waited_cnt in range(0, timeout_sec):
        time.sleep(1)
        child.sendline('\n') # XXX 
        index = child.expect(['ALL_SENT',pexpect.TIMEOUT], timeout=1)
        if index == 0:
            runner_ctx.logger.info("{}ALL_SENT".format(runner_ctx.cur_indent))
            break
        elif index ==1:
            runner_ctx.logger.info("{}timeout --> keep waiting {}".format(runner_ctx.cur_indent,waited_cnt))
            if(waited_cnt == timeout_sec-1):
                runner_ctx.logger.error("{}timeout --> giveup".format(runner_ctx.cur_indent))
                return False
            continue

    #-------------------------------------
    child.sendline('quit')
    for waited_cnt in range(0, timeout_sec):
        time.sleep(1)
        child.sendline('\n') # XXX 
        index = child.expect(['GOOD BYE!',pexpect.TIMEOUT], timeout=1)
        if index == 0:
            runner_ctx.logger.info("{}GOOD BYE!".format(runner_ctx.cur_indent))
            break
        elif index ==1:
            runner_ctx.logger.info("{}timeout --> keep waiting {}".format(runner_ctx.cur_indent,waited_cnt))
            if(waited_cnt == timeout_sec-1):
                runner_ctx.logger.error("{}timeout --> giveup".format(runner_ctx.cur_indent))
                return False
            continue
    #-------------------------------------
    #child.terminate()
    child.close()
    runner_ctx.logger.info("{}simul send OK".format(runner_ctx.cur_indent))

    return True

    
#///////////////////////////////////////////////////////////////////////////////
# aaa_sim, radius_sim, aims_sim 
"""
./radius_sim ./CFG/DROP_PGW_UDR.CFG &

[OFCS2:/CG/OFCS_SIM/RADIUS/AAA_SIM]cat aaa_sim.sh
	DATE=`date "+%Y%m%d"`
	LOG_FILE=`echo ./LOG/aaa_sim.$DATE`
	nohup ./aaa_sim  192.168.1.225 5050 &

[OFCS2:/CG/OFCS_SIM/RADIUS/AIMS_SIM]cat EXAM_AIMS.sh
./aims_sim 60.50.35.143 1999 &

"""

