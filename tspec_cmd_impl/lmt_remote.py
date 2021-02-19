#-*- coding: utf-8 -*-

import sys
import os
import datetime
import glob

import paramiko
import pexpect

from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_time
import lmt_xml_config
from tspec_cmd_impl import lmt_oracle

#///////////////////////////////////////////////////////////////////////////////
#PSM 동기화 프로세스 설정 및 프로세스 재기동
def psm_set_config_and_restart(runner_ctx, after_min):
    #현재 시간 + 5min
    run_time = datetime.datetime.now() + datetime.timedelta(minutes=after_min)
    run_time_str = run_time.strftime('%H:%M:00')     # 2015:04:19
    xpath = "MANAGEMENT/COMMON/STRD_TIME_1"
    runner_ctx.logger.info("{}set ems xml config {}={}".format(runner_ctx.cur_indent, xpath, run_time_str))
    lmt_xml_config.set_xml_cfg_ems(runner_ctx, xpath, run_time_str)

    cmd = "STOP-PRC:${EMS_PACKAGE_NAME}:${EMS_SYSTEM_NAME}:${EMS_SERVICE_NAME}:PM"
    cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.ems_cli_name, runner_ctx.pfnm_userid, runner_ctx.pfnm_passwd, cmd)
    remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)

    lmt_time.wait_secs(runner_ctx, 5)

    cmd = "STAR-PRC:${EMS_PACKAGE_NAME}:${EMS_SYSTEM_NAME}:${EMS_SERVICE_NAME}:PM"
    cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.ems_cli_name, runner_ctx.pfnm_userid, runner_ctx.pfnm_passwd, cmd)
    remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)
    


#///////////////////////////////////////////////////////////////////////////////
def backup_ems_config(runner_ctx, file_name_path):
    backup_remote_file(runner_ctx, runner_ctx.ems_ip,runner_ctx.ems_id, runner_ctx.ems_passwd, file_name_path)


#///////////////////////////////////////////////////////////////////////////////
def rollback_ems_config(runner_ctx, file_name_path):
    rollback_remote_file(runner_ctx, runner_ctx.ems_ip,runner_ctx.ems_id, runner_ctx.ems_passwd, file_name_path)


#///////////////////////////////////////////////////////////////////////////////
def ems_run_cli_cmd(runner_ctx, cmd):
    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.ems_cli_name, runner_ctx.pfnm_userid, runner_ctx.pfnm_passwd, cmd)
    if ("STAR-PRC" in cmd) :
        runner_ctx.logger.debug("{}START-PRC --> wait 5 secs : {}".format(runner_ctx.cur_indent,cmd))
        # ssh 접속에 약간 지연 있음. 그리고 STOP 이 아직 완료 안된 경우 바로 START 하면 성공 못함
        lmt_time.wait_secs(runner_ctx, 10)

    ems_run_shell_cmd(runner_ctx, cmd)


#///////////////////////////////////////////////////////////////////////////////
def ems_run_shell_cmd(runner_ctx, cmd):
    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    return remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)


#///////////////////////////////////////////////////////////////////////////////
#file_name의 패턴으로 zero file이 있으면 에러
def assert_ems_zero_file_not_exist(runner_ctx, path, file_name):
    path = lmt_util.replace_all_symbols(runner_ctx,path)
    cmd = "find {} -empty -name '{}'|wc -l".format(path, file_name)

    result =  remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent, result))
    runner_ctx.logger.info("{}[{}]".format(runner_ctx.cur_indent, result.split('\r\n')[1]))
    if int(result.split('\r\n')[1]) != 0:
        err_msg ="assert failed : {} != {} ".format(result,0)
        raise lmt_exception.LmtException(err_msg)


#///////////////////////////////////////////////////////////////////////////////
def remote_shell_cmd(runner_ctx, host, user, password, cmd):
    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    try:
        s = pexpect.pxssh.pxssh()
        s.login(host,user,password, port=22, sync_multiplier=5)
        runner_ctx.logger.info("{}remote_shell_cmd {}".format(runner_ctx.cur_indent, cmd))
        s.sendline(cmd)
        s.prompt()
        runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent, s.before))
        return s.before
    except Exception as e:
        err_msg ="assert failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)


#///////////////////////////////////////////////////////////////////////////////
#백업 수행. 해당 자이의 파일을 .backup으로 복사
def backup_remote_file(runner_ctx, host,user,password, file_name_path):
    file_name_path = lmt_util.replace_all_symbols(runner_ctx,file_name_path)
    try:
        s = pexpect.pxssh.pxssh()
        s.login(host,user,password, port=22, sync_multiplier=5)
        cmd = "cp -p {} {}.backup".format(file_name_path, file_name_path)
        runner_ctx.logger.info("{}cmd {}".format(runner_ctx.cur_indent, cmd))
        s.sendline(cmd)
        s.prompt()
        return s
    except Exception as e:
        err_msg ="assert failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)


#///////////////////////////////////////////////////////////////////////////////
def rollback_remote_file(runner_ctx, host,user,password, file_name_path):
    file_name_path = lmt_util.replace_all_symbols(runner_ctx,file_name_path)
    runner_ctx.logger.info("{}rollback_remote_file".format(runner_ctx.cur_indent))
    try:
        s = pexpect.pxssh.pxssh()
        s.login(host,user,password, port=22, sync_multiplier=5)
        cmd = "cp -p {}.backup {}".format(file_name_path, file_name_path)
        runner_ctx.logger.info("{}cmd {}".format(runner_ctx.cur_indent, cmd))
        s.sendline(cmd)
        s.prompt()

        cmd = "STOP-PRC:${EMS_PACKAGE_NAME}:${EMS_SYSTEM_NAME}:${EMS_SERVICE_NAME}:PM"
        cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.ems_cli_name, runner_ctx.pfnm_userid, runner_ctx.pfnm_passwd, cmd)
        remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)

        lmt_time.wait_secs(runner_ctx, 10)

        cmd = "STAR-PRC:${EMS_PACKAGE_NAME}:${EMS_SYSTEM_NAME}:${EMS_SERVICE_NAME}:PM"
        cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.ems_cli_name, runner_ctx.pfnm_userid, runner_ctx.pfnm_passwd, cmd)
        remote_shell_cmd(runner_ctx, runner_ctx.ems_ip, runner_ctx.ems_id, runner_ctx.ems_passwd, cmd)
        return s
    except Exception as e:
        err_msg ="assert failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)

#///////////////////////////////////////////////////////////////////////////////
def get_ems_file(runner_ctx,file_name):
    get_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd,file_name)


#///////////////////////////////////////////////////////////////////////////////
def put_ems_file(runner_ctx,remote_path, file_name):
    put_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd, remote_path, runner_ctx.temp_internal_use_only_dir_remote, file_name, file_name)


#///////////////////////////////////////////////////////////////////////////////
#ems의 file을 가져온다.
def get_remote_file(runner_ctx,host,user,password,file_name):
    file_name = lmt_util.replace_all_symbols(runner_ctx,file_name)
    try:
        transport = paramiko.Transport(host, 22)
        transport.connect(username = user, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sourcefilepath =file_name 
        #파일이 local과 중복 될 수 있으니 디렉토리 만들어서 별도 보관하자
        localpath = "{}/{}".format(runner_ctx.temp_internal_use_only_dir_remote, os.path.basename(file_name))
        if os.path.isdir(runner_ctx.temp_internal_use_only_dir_remote) == False:
            os.mkdir(runner_ctx.temp_internal_use_only_dir_remote)

        runner_ctx.logger.info("{} {} {} {} {}".format(runner_ctx.cur_indent, host,user,password,file_name))
        sftp.get(sourcefilepath, localpath)
        sftp.close()
        transport.close()
    except Exception as e:
        err_msg ="get_remote_file failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)

#///////////////////////////////////////////////////////////////////////////////
def put_policy_files_to_ems(runner_ctx):
    local_path = "{}/policy_files".format(runner_ctx.cur_ctx_test_path)
    file_list=glob.glob(local_path + '/*.csv')
    runner_ctx.logger.info("{}put policy file to ems {}".format(runner_ctx.cur_indent, file_list))
    #remote_path = '/EMS/PEMS/POLICY_DATA'
    remote_path = runner_ctx.ems_policy_path

    for file_name in file_list:
        cur_date = lmt_util.replace_all_symbols(runner_ctx,"${CUR_YYYYMMDD}")
        remote_file_name = "{}_{}".format(cur_date,os.path.basename(file_name))
        runner_ctx.logger.info("{}put policy file to ems {}".format(runner_ctx.cur_indent, file_name))
        put_remote_file(runner_ctx,runner_ctx.ems_ip,runner_ctx.ems_id,runner_ctx.ems_passwd, remote_path, local_path,  remote_file_name, file_name)


#///////////////////////////////////////////////////////////////////////////////
def put_remote_file(runner_ctx,host,user,password,remote_path, local_path, remote_file_name, local_file_name):
    local_file_name = lmt_util.replace_all_symbols(runner_ctx,local_file_name)
    remote_file_name = lmt_util.replace_all_symbols(runner_ctx,remote_file_name)
    remote_path = lmt_util.replace_all_symbols(runner_ctx,remote_path)
    try:
        transport = paramiko.Transport(host, 22)
        transport.connect(username = user, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        destfilepath ="{}/{}".format(remote_path,remote_file_name) 
        localpath = "{}/{}".format(local_path, os.path.basename(local_file_name))

        runner_ctx.logger.info("{} {} {} {} local:{} remote:{} {}".format(runner_ctx.cur_indent, host,user,password,localpath, remote_path, local_file_name))

        sftp.put(localpath, destfilepath)
        sftp.close()
        transport.close()
    except Exception as e:
        err_msg ="put_remote_file failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)


#///////////////////////////////////////////////////////////////////////////////
##################################### Not use
def get_remote_file_1(runner_ctx,host,user,password,file_name):
    file_name = lmt_util.replace_all_symbols(runner_ctx,file_name)
    try:
        cmd = "sftp {}@{}:{} {}".format(user, host, file_name, runner_ctx.temp_internal_use_only_dir)
        runner_ctx.logger.info("{}cmd {}".format(runner_ctx.cur_indent, cmd))
        child = pexpect.spawn(cmd)
        #child.logfile = sys.stdout
        index = child.expect(['please try again','password:'])

        #child.expect(pexpect.EOF)
        #print(child.before)
        child.sendline(password)
        #print('send')
        index = child.expect(['please try again','password:',pexpect.EOF])
        print("index {}".format(index))
        child.terminate()
        child.interact()
        child.close()
        print('close')
        if index == 0:
            err_msg ="assert failed : {}".format('error')
            raise lmt_exception.LmtException(err_msg)

        return
    except Exception as e:
        err_msg ="assert failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)

    index = child.expect(['again'])#,pexpect.TIMEOUT])
    if index == 0:
        runner_ctx.logger.error("{}invalid password {}".format(runner_ctx.cur_indent, password))
        child.terminate(True)
        err_msg ="assert failed : {}".format(child.before)
        raise lmt_exception.LmtException(err_msg)


#///////////////////////////////////////////////////////////////////////////////
#remote file put
def put_remote_file2(runner_ctx,host,user,password,remote_path, file_name):
    file_name = lmt_util.replace_all_symbols(runner_ctx,file_name)
    remote_path = lmt_util.replace_all_symbols(runner_ctx,remote_path)
    try:
        cmd="sftp  {}@{}:{} <<< $\'put {}/{}\'".format(user, host, remote_path, runner_ctx.temp_internal_use_only_dir, file_name)
        runner_ctx.logger.info("{}cmd {}".format(runner_ctx.cur_indent, cmd))
        child = pexpect.spawn("bash",['-c',cmd])
        child.expect('password:')
        child.sendline(password)
        print('aa')
        child.interact()
        child.close()
        return
    except Exception as e:
        err_msg ="assert failed : {}".format(e)
        raise lmt_exception.LmtException(err_msg)
    print('aa')
    index = child.expect(['again'])#,pexpect.TIMEOUT])
    if index == 0:
        runner_ctx.logger.error("{}invalid password {}".format(runner_ctx.cur_indent, password))
        child.terminate(True)
        err_msg ="assert failed : {}".format(child.before)
        raise lmt_exception.LmtException(err_msg)

