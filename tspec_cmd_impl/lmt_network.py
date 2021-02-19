#-*- coding: utf-8 -*-

import os
#import subprocess
import logging
#import time

from module_core import lmt_exception
from module_core import lmt_util

# XXX sudo tcpdump 명령 수행시 비번  없이 가능하게 설정되어야 함 XXX
# pofcs   ALL=NOPASSWD: ALL

#ex) start_tcpdump("port 2015 -s 0", "GTPPtoRADIUS_ODA.${CUR_YYYYMMDDHH}.pcap")
#ex) start_tcpdump("-i lo udp port 3381 -s 0", "GTPPtoRADIUS_ODA.${CUR_YYYYMMDDHH}.pcap")
#ex) stop_tcpdump("port 2015 -s 0")
#ex) stop_tcpdump("-i lo udp port 3381 -s 0")

#///////////////////////////////////////////////////////////////////////////////
def start_tcpdump(runner_ctx, cmd_opt, dump_file_name):
    #--------------------------------------
    #pkg_test_result 에 tcpdump 결과 저장할 directory 생성 
    dump_file_name = lmt_util.replace_all_symbols(runner_ctx, dump_file_name)
    #log_paths = [handler.baseFilename for handler in runner_ctx.logger.handlers if isinstance(handler, logging.FileHandler)]
    #log_path = next(iter(log_paths))
    #runner_ctx.logger.info("{}log path =[{}]".format(runner_ctx.cur_indent,log_path))
    #file_name = os.path.basename(log_path)
    #dir_name  = os.path.splitext(file_name)[0]
    #runner_ctx.logger.info("{}dir_name =[{}]".format(runner_ctx.cur_indent, dir_name))
    #test_result_dir = os.path.join(os.path.dirname(os.path.abspath(log_path)), dir_name)    
    runner_ctx.logger.info("{}test_result_dir  =[{}]".format(runner_ctx.cur_indent, runner_ctx.test_result_dir ))

    if(os.path.isdir(runner_ctx.test_result_dir)==False):
        runner_ctx.logger.info("{}create dir : {}".format(runner_ctx.cur_indent,runner_ctx.test_result_dir))
        os.mkdir(runner_ctx.test_result_dir)
    #-------------------------------------- run tcpdump in background
    dump_full_path = os.path.join(runner_ctx.test_result_dir, dump_file_name)
    full_cmd = "sudo tcpdump {} -w {} & ".format(cmd_opt, dump_full_path)
    runner_ctx.logger.info("{}full_cmd : {}".format(runner_ctx.cur_indent,full_cmd))

    #background 로 기동하고 바로 다음 진행
    lmt_util.run_shell_cmd_background(runner_ctx, full_cmd) 
    runner_ctx.logger.info("{}tcp dump started".format(runner_ctx.cur_indent))


#///////////////////////////////////////////////////////////////////////////////
def stop_tcpdump(runner_ctx, cmd_opt):
    #해당 명령의 pid 를 알아서 TERM signal 을 보낸다 
    """
    full_cmd = 'ps -ef | grep tcpdump | grep -v grep'
    runner_ctx.logger.info("{}full_cmd : {}".format(runner_ctx.cur_indent,full_cmd))
    lmt_util.run_shell_cmd(runner_ctx,full_cmd) 
    """

    full_cmd = 'pgrep -f "tcpdump {}" | xargs sudo kill -TERM'.format(cmd_opt, cmd_opt)
    runner_ctx.logger.info("{}full_cmd : {}".format(runner_ctx.cur_indent,full_cmd))
    #lmt_util.run_shell_cmd(runner_ctx,full_cmd)  #XXX return code = -15 --> error 
    os.system(full_cmd) 



