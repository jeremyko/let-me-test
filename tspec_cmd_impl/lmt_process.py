#-*- coding: utf-8 -*-

import subprocess
import psutil
#202007 kojh create
from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_time

#///////////////////////////////////////////////////////////////////////////////
# cleanup_cli_cmds 에 저장안하는 기능임. lmt_runner.py 에서만 사용한다
def run_cli_cmd_no_rollback(runner_ctx,cli_cmd):
    cli_cmd = lmt_util.replace_all_symbols(runner_ctx,cli_cmd)

    full_cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.cli_name, runner_ctx.pfnm_userid,
            runner_ctx.pfnm_passwd, cli_cmd)
    runner_ctx.logger.info("{}full_cmd : {}".format(runner_ctx.cur_indent,full_cmd))

    if ("STAR-PRC" in full_cmd) :
        runner_ctx.logger.debug("{}START-PRC --> wait 5 secs : {}".format(runner_ctx.cur_indent,full_cmd))
        # STOP 이 아직 완료 안된 경우 바로 START 하면 성공 못함
        lmt_time.wait_secs(runner_ctx,5)

    lmt_util.run_shell_cmd(runner_ctx,full_cmd) 
    #------------------------------------------------
    lmt_time.wait_secs(runner_ctx,5)
    # cli 문제점 
    # 명령이 완료할때까지 대기하는게 아니고.. 바로 빠져나옴.
    # 때문에, STAR-PRC 호출하고, 아직 프로세스 기동하기 전인데, xml db 등을 조작하면
    # 프로세스가 xml db 를 못잊는 경우가 발생함.. 그래서 일단 5초 정도 명령이
    # 완료될 시간을 준다. TODO 만약 5초 이상 걸리는 명령은 ??? 
    #------------------------------------------------

    return True

#///////////////////////////////////////////////////////////////////////////////
# ex) run_cli_cmd("INIT-PRC:${PACKAGE_NAME}:${SYSTEM_NAME}:${SERVICE_NAME}:ST") 
# ex) run_cli_cmd("INIT-PFM:${PACKAGE_NAME}:${SYSTEM_NAME}:MES") 
# ex) run_cli_cmd("STAR-PRC:${PACKAGE_NAME}:${SYSTEM_NAME}:${SERVICE_NAME}:ST") 
def run_cli_cmd(runner_ctx,cli_cmd):
    cli_cmd = lmt_util.replace_all_symbols(runner_ctx,cli_cmd)

    full_cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.cli_name, runner_ctx.pfnm_userid,
            runner_ctx.pfnm_passwd, cli_cmd)
    runner_ctx.logger.info("{}full_cmd : {}".format(runner_ctx.cur_indent,full_cmd))

    # XXX 다음과 같은 INIT, START 명령을 수행한 경우엔, xml db, xml config 원복 이후  
    # 다시 재 초기화를 해줘야 한다. (프로세스를 이전 상태로 재 초기화) 
    # INIT-PRC:OFCS:POFCS3:GTP_PGW:ST 
    # INIT-PFM:OFCS:POFCS3:MES 
    # STAR-PRC:OFCS:POFCS3:GTP_PGW:ST 
    if ("STAR-PRC" in full_cmd) :
        runner_ctx.logger.debug("{}START-PRC --> wait 5 secs : {}".format(runner_ctx.cur_indent,full_cmd))
        # STOP 이 아직 완료 안된 경우 바로 START 하면 성공 못함
        lmt_time.wait_secs(runner_ctx,5)

    is_cleanup_need = False
    if ("INIT-PRC" in full_cmd) or ("INIT-PFM" in full_cmd) or ("STAR-PRC" in full_cmd):
        runner_ctx.logger.debug("{}is_cleanup_need True".format(runner_ctx.cur_indent))
        is_cleanup_need = True

    if is_cleanup_need and (full_cmd in runner_ctx.cleanup_cli_cmds) == False:
        #XXX 만약 START-PRC 명령이면, STOP_PRC 명령이 먼저 수행되도록 처리한다
        if ("STAR-PRC" in full_cmd):
            tmp_stop_prc_cmd = full_cmd.replace("STAR-PRC","STOP-PRC")
            runner_ctx.logger.debug("{}cleanup cli full_cmd append : {}".format(runner_ctx.cur_indent,tmp_stop_prc_cmd))
            runner_ctx.cleanup_cli_cmds.append(tmp_stop_prc_cmd)
        runner_ctx.logger.debug("{}cleanup cli full_cmd append : {}".format(runner_ctx.cur_indent,full_cmd))
        runner_ctx.cleanup_cli_cmds.append(full_cmd)

    lmt_util.run_shell_cmd(runner_ctx,full_cmd) 
    #------------------------------------------------
    lmt_time.wait_secs(runner_ctx,5)
    # cli 문제점 
    # 명령이 완료할때까지 대기하는게 아니고.. 바로 빠져나옴.
    # 때문에, STAR-PRC 호출하고, 아직 프로세스 기동하기 전인데, xml db 등을 조작하면
    # 프로세스가 xml db 를 못잊는 경우가 발생함.. 그래서 일단 5초 정도 명령이
    # 완료될 시간을 준다. TODO 만약 5초 이상 걸리는 명령은 ??? 
    #------------------------------------------------

    return True


def test(runner_ctx, name):
    assert_process_thread_count_matching(runner_ctx, name, 1)

def assert_process_thread_count_matching(runner_ctx, name, expected_val):
    for psinfo in psutil.process_iter(['name','pid', 'username']):
        if psinfo.info['name'] == name:
            p = psutil.Process(psinfo.info['pid'])
            runner_ctx.logger.info("{}process_name {} pid {} thread count {}".format(runner_ctx.cur_indent,psinfo.info['name'], psinfo.info['pid'], p.num_threads()))
            if p.num_threads() != expected_val:
                err_msg = "assert failed : {} thread count({}) != expected({})".format(psinfo.info['name'], p.num_threads(),expected_val)
                runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
                raise lmt_exception.LmtException(err_msg)
    return True

def get_thread_count_process(runner_ctx, name):
    "프로세스 명의 쓰레드 카운트를 돌려 준다."
    ls = []
    return ls

#///////////////////////////////////////////////////////////////////////////////
def run_prc(runner_ctx,run_cmd):

    return True

#///////////////////////////////////////////////////////////////////////////////
def terminate_prc(runner_ctx,proc_name):

    return True

#///////////////////////////////////////////////////////////////////////////////
def kill_prc(runner_ctx,proc_name):

    return True

#///////////////////////////////////////////////////////////////////////////////
def save_prc_pid(runner_ctx, process_name):
    process_name = lmt_util.replace_all_symbols(runner_ctx,process_name)
    cmd = "/usr/sbin/pidof " + process_name
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = proc.communicate()
    #del runner_ctx.info_repo[:]

    if(err):
        runner_ctx.logger.error("{}error : {}".format(runner_ctx.cur_indent,cmd))
        err_msg ="{}{} ".format(runner_ctx.cur_indent,err)
        raise lmt_exception.LmtException(err_msg)
    elif(proc.returncode == 0): #i found grep data
        runner_ctx.logger.info("info : {} => {}".format(cmd, output))
        runner_ctx.pid_save = output.split()

    runner_ctx.logger.info("save_prc_pid[{}] : {}".format(process_name, runner_ctx.pid_save))
    return True


