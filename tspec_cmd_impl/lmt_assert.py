#-*- coding: utf-8 -*-

#202007 kojh create

import subprocess
import os
import sys
import time
import datetime
import glob
import re

from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_time

#///////////////////////////////////////////////////////////////////////////////
def test_eq(runner_ctx,a,b):
    if(a != b):
        err_msg ="assert failed : {} != {} ".format(a,b)
        raise lmt_exception.LmtException(err_msg)
    return True


def assert_all_app_running(runner_ctx):
    return True

#///////////////////////////////////////////////////////////////////////////////
#프로세스 명의 개수를 입력 받아 실행 개수를 확인
def assert_app_running(runner_ctx, service_name, process_name, process_count):
    process_name = lmt_util.replace_all_symbols(runner_ctx,process_name)
    service_name = lmt_util.replace_all_symbols(runner_ctx,service_name)
    runner_ctx.logger.info("assert_app_running : service_name={}, process_name={}".format(service_name, process_name))
    cmd='ps -ef|grep -v grep |grep -v vi|grep -v vim|grep -v LOG|grep ' + service_name + '|grep ' + process_name + '|wc -l'
    # cmd='DISP-PRC:${PACKAGE_NAME}:${SYSTEM_NAME}:' + service_name + ':' + process_name 
    # cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    ps_count = lmt_util.run_shell_cmd(runner_ctx, cmd)
    # runner_ctx.logger.info("assert_app_running : {}".format('process_count : ' + ps_count.rstrip('\n') + '/' + str(process_count)))
    # if 'Inactive' in ps_count:
        # err_msg ="assert failed :  {} ".format(ps_count)
        # raise lmt_exception.LmtException(err_msg)
        
    # return True
    if(int(ps_count) == process_count):
        return True
    else:
        test_eq(runner_ctx, process_count, ps_count)
        return False

#프로세스명으로 pid 개수로 확인
#///////////////////////////////////////////////////////////////////////////////
def assert_prc_running(runner_ctx,proc_name):
    proc_name = lmt_util.replace_all_symbols(runner_ctx,proc_name)
    cmd='/usr/sbin/pidof ' + proc_name 
    runner_ctx.logger.info("assert_prc_running : process_name={}".format(proc_name))
    ps_id = lmt_util.run_shell_cmd(runner_ctx, cmd)
    if(len(ps_id.split()) != 0):
        runner_ctx.logger.info("assert_prc_running : process_name={}, count={}, pid={}".format(proc_name, len(ps_id.split()), ps_id))
        return True
    else:
        err_msg ="assert failed : {} not found ".format(proc_name)
        raise lmt_exception.LmtException(err_msg)

#///////////////////////////////////////////////////////////////////////////////
def assert_file_grep_sequentially_not_include(runner_ctx,to_find_str, file_name, max_wait_secs):
    assert_file_grep_sequentially_path(runner_ctx, to_find_str, os.path.dirname(file_name), os.path.basename(file_name), False, max_wait_secs)

def assert_file_grep_sequentially(runner_ctx,to_find_str, file_name, max_wait_secs):
    assert_file_grep_sequentially_path(runner_ctx, to_find_str, os.path.dirname(file_name), os.path.basename(file_name), True, max_wait_secs)

def assert_file_grep_sequentially_ems(runner_ctx,to_find_str, file_name, max_wait_secs):
    assert_file_grep_sequentially_path(runner_ctx, to_find_str, runner_ctx.temp_internal_use_only_dir_remote, file_name, True, max_wait_secs)

def assert_file_grep_sequentially_path(runner_ctx,to_find_str, path, file_name, include, max_wait_secs):
    file_name = lmt_util.replace_all_symbols(runner_ctx,file_name)
    path = lmt_util.replace_all_symbols(runner_ctx,path)
    #file_name = runner_ctx.service_name + os.sep + file_name
    tmp_file_path = path + '/' + file_name
    runner_ctx.logger.info("{}file_path [{}]".format(runner_ctx.cur_indent,tmp_file_path))
    runner_ctx.logger.info("{}max wait secs : {}".format(runner_ctx.cur_indent, max_wait_secs))


    start_dtime = datetime.datetime.now()
    while True:
        #뺑뺑이 돌면서 각각 검사한다. 한개라도 있으면 OK
        file_list=glob.glob(tmp_file_path)

        match_count = 0
        find_all_pattern = False

        file_list.sort()
        for f in file_list:
            runner_ctx.logger.info("{}find pattern {} {}".format(runner_ctx.cur_indent,f, to_find_str))
            ff = open(f, 'rb')
            line = ff.readline()

            pattern_idx = 0
            match_count = 0
            while line:
                #runner_ctx.logger.debug("{}  {} : {}   =>   {}".format(runner_ctx.cur_indent,f,to_find_str[pattern_idx], line))
                rex = re.compile(to_find_str[pattern_idx])
                if rex.search(line) :
                    runner_ctx.logger.info("{}  {} : {}   =>   {}".format(runner_ctx.cur_indent,f,to_find_str[pattern_idx], line))
                    pattern_idx += 1
                    match_count += 1

                if pattern_idx >= len(to_find_str):
                    break
                line = ff.readline()
            ff.close()

            if(match_count == len(to_find_str)):
                find_all_pattern = True

        #include :true : 패턴 모두 포함하고 all match 가 아니면.. 에러
        if include == True and find_all_pattern == True:
            runner_ctx.logger.info("{}all find include pattern {}".format(runner_ctx.cur_indent,to_find_str))
            break

        # if include == True and find_all_pattern == False:
            # err_msg ="{}pattern not found {}".format(runner_ctx.cur_indent,to_find_str)
            # runner_ctx.logger.error("{}grep pattern not found {} : timeout error".format(runner_ctx.cur_indent,to_find_str))
            # break
            # #raise lmt_exception.LmtException(err_msg)

        #include :false : 패턴 일부가 없어야 성공
        # if include == False and match_count == 0:
            # runner_ctx.logger.info("{}find exclude pattern {}".format(runner_ctx.cur_indent,to_find_str))
            # break
        if include == False: #find_all_pattern == True:
            if match_count != 0:
                err_msg ="{}pattern found {}".format(runner_ctx.cur_indent,to_find_str)
                runner_ctx.logger.error("{}pattern found {}".format(runner_ctx.cur_indent,to_find_str))
                raise lmt_exception.LmtException(err_msg)
            else:
                runner_ctx.logger.info("{}pattern not found {}".format(runner_ctx.cur_indent,to_find_str))
                break;


        if include == True:
            time.sleep(2)
            end_dtime = datetime.datetime.now()
            elapsed = end_dtime - start_dtime
            if(elapsed.total_seconds() >= max_wait_secs):
                runner_ctx.logger.error("{}find pattern {} : timeout error".format(runner_ctx.cur_indent,to_find_str))
                err_msg ="{}max_wait_secs {} timeout error".format(runner_ctx.cur_indent,max_wait_secs)
                raise lmt_exception.LmtException(err_msg)

            continue
        else:
            break

    return True


#///////////////////////////////////////////////////////////////////////////////
def assert_file_grep(runner_ctx, to_find_str, file_name, max_wait_secs): 

    file_name = lmt_util.replace_all_symbols(runner_ctx,file_name)
    runner_ctx.logger.debug("{}file_path [{}]".format(runner_ctx.cur_indent,file_name))
    #XXX fgrep XXX
    cmd = 'fgrep "{}" {}'.format(to_find_str, file_name)
    runner_ctx.logger.info("{}cmd => {}".format(runner_ctx.cur_indent,cmd))
    runner_ctx.logger.info("{}max wait secs : {}".format(runner_ctx.cur_indent, max_wait_secs))
    #-----------------------------------------------
    start_dtime = datetime.datetime.now()
    CHK_INTERVAL=3
    while True:
        try:
            process = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE)
        except:
            runner_ctx.logger.error("{}grep cmd {} : error  => {}".
                    format(runner_ctx.cur_indent,cmd, sys.exc_info()[1]))
            return False

        while True:
            line = process.stdout.readline()
            if not line:
                #runner_ctx.logger.debug("{} not line".format(runner_ctx.cur_indent))
                # "그런 파일이나 디렉터리가 없습니다" 에러 경우도 여기에서 처리됨
                time.sleep(CHK_INTERVAL)
                #------------------------------------ 
                end_dtime = datetime.datetime.now()
                elapsed = end_dtime - start_dtime
                if(elapsed.total_seconds() >= max_wait_secs):
                    runner_ctx.logger.error("{}grep cmd {} : timeout error".format(runner_ctx.cur_indent,cmd))
                    err_msg ="{}max_wait_secs {} timeout error".format(runner_ctx.cur_indent,max_wait_secs)
                    raise lmt_exception.LmtException(err_msg)
                #------------------------------------ 
                break
            line = line.rstrip()
            line = line.replace("\r","")
            line = line.replace("\n","")
            runner_ctx.logger.debug("{}line ={}".format(runner_ctx.cur_indent, line))
            if(to_find_str in line):
                runner_ctx.logger.info("{}found expected : {}".format(runner_ctx.cur_indent,line))
                return True
            else:
                #runner_ctx.logger.info("{}debug 2".format(runner_ctx.cur_indent))
                time.sleep(CHK_INTERVAL)
                #lmt_time.wait_secs(runner_ctx,CHK_INTERVAL)
                end_dtime = datetime.datetime.now()
                elapsed = end_dtime - start_dtime
                if(elapsed.total_seconds() >= max_wait_secs):
                    runner_ctx.logger.error("{}grep cmd {} : timeout error".format(runner_ctx.cur_indent,cmd))
                    err_msg ="{}max_wait_secs {} timeout error".format(runner_ctx.cur_indent,max_wait_secs)
                    raise lmt_exception.LmtException(err_msg)

                continue


#///////////////////////////////////////////////////////////////////////////////
def assert_prc_same_pid(runner_ctx, process_name):
    runner_ctx.logger.info(runner_ctx.pid_save)
    runner_ctx.logger.info("assert_prc_same_pid : {}".format('pid-'+process_name))

    cmd = "/usr/sbin/pidof " + process_name
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = proc.communicate()

    if(err):
        runner_ctx.logger.error("{}error : {}".format(runner_ctx.cur_indent,cmd))
        err_msg ="{}{} ".format(runner_ctx.cur_indent,err)
        raise lmt_exception.LmtException(err_msg)
    elif(proc.returncode == 0): #i found grep data
        runner_ctx.logger.info("info : {} => {}".format(cmd, output))

    for pid in runner_ctx.pid_save :
        if pid in output.split():
            runner_ctx.logger.info("process pid found : {} => {}".format(process_name, pid))
        else:
            runner_ctx.logger.info("process pid not found : {} => {}".format(process_name, pid))
            err_msg ="{}{} ".format(runner_ctx.cur_indent,err)
            raise lmt_exception.LmtException(err_msg)

    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_alarm_exists(runner_ctx,alarm_code):
    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_alarm_cleared(runner_ctx,alarm_code):
    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_mes_q_full(runner_ctx,log_file_path):
    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_mes_q_not_full(runner_ctx,log_file_path):
    return True

#///////////////////////////////////////////////////////////////////////////////
def test_run_ok(runner_ctx,cmd) :
    return True

#///////////////////////////////////////////////////////////////////////////////
def test_run_err(runner_ctx,cmd) :
    return True

#///////////////////////////////////////////////////////////////////////////////
def test_eq_prc_output(runner_ctx,cmd, val):
    return True

#///////////////////////////////////////////////////////////////////////////////
#command 실행 후 결과가 있는지 확인. XXX cmd 는 한번만 수행된다.
# ex) assert_eq_cmd_output (
#       "ov -f PGW_META ${OUTPUT_IPMD}/FME*/* | fgrep '[UserLocationInfo] : 20202020202020202020202020'  | wc -l", 2)
def assert_eq_cmd_output (runner_ctx, cmd, expect_val ): 
    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    runner_ctx.logger.info("{}cmd   : {}".format(runner_ctx.cur_indent,cmd))
    runner_ctx.logger.info("{}expected : {}".format(runner_ctx.cur_indent,expect_val))

    output = subprocess.check_output(cmd, shell=True)

    if(output):
        output = output.replace("\r","")
        output = output.replace("\n","")
        runner_ctx.logger.info("{}cmd returns : {}".format(runner_ctx.cur_indent,output))
        if(expect_val != output):
            err_msg = "assert failed : actual({}) != expected({})".format(output,expect_val)
            runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
    else:
        err_msg = "assert failed : actual({}) != expected({})".format(output,expect_val)
        runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    return True

#///////////////////////////////////////////////////////////////////////////////
#command 실행 후 결과가 있는지 확인. XXX cmd 는 한번만 수행된다.
def assert_cmd_output_include_string (runner_ctx, cmd, expect_val ): 
    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    runner_ctx.logger.info("{}cmd : {}".format(runner_ctx.cur_indent,cmd))
    runner_ctx.logger.info("{}expect val : {}".format(runner_ctx.cur_indent,expect_val))
    if expect_val is not None :
        runner_ctx.logger.info("{}expected : {}".format(runner_ctx.cur_indent,expect_val))

    output = subprocess.check_output(cmd, shell=True)

    if(output):
        runner_ctx.logger.info("{}cmd returns : {}".format(runner_ctx.cur_indent,output))
        if(expect_val is not None and expect_val not in output):
            err_msg = "assert failed : actual({}) not in expected({})".format(output,expect_val)
            runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
    else:
        err_msg = "assert failed : string not found"
        runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    return True

#///////////////////////////////////////////////////////////////////////////////
#ov command 실행 후 결과가 있는지 확인 --> XXX cmd 는 loop 를 돌면서 여러번 수행된다  
def assert_poll_cmd_output_include_string (runner_ctx, cmd, expect_val, max_wait_secs ): 

    cmd = lmt_util.replace_all_symbols(runner_ctx,cmd)
    runner_ctx.logger.info("{}cmd : {}".format(runner_ctx.cur_indent,cmd))
    runner_ctx.logger.info("{}max wait secs : {}".format(runner_ctx.cur_indent, max_wait_secs))
    if expect_val is None :
        err_msg = "invalid usage! : expect_val is mandaroty"
        runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
        raise lmt_exception.LmtException(err_msg)

    #-----------------------------------------------
    CHK_INTERVAL=3
    start_dtime = datetime.datetime.now()
    while True:
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        except:
            runner_ctx.logger.error("{}grep cmd {} : error  => {}".
                    format(runner_ctx.cur_indent,cmd, sys.exc_info()[1]))
            return False

        while True:
            line = process.stdout.readline()
            if not line:
                time.sleep(CHK_INTERVAL)
                #lmt_time.wait_secs(runner_ctx,CHK_INTERVAL)
                break

            line = line.rstrip()
            line = line.replace("\r","")
            line = line.replace("\n","")
            runner_ctx.logger.debug("{}line ={}".format(runner_ctx.cur_indent, line))
            if(expect_val in line):
                runner_ctx.logger.info("{}found expected : {}".format(runner_ctx.cur_indent,line))
                return True
            else:    
                #retry
                runner_ctx.logger.debug("{}retry : {}".format(runner_ctx.cur_indent,cmd))
                end_dtime = datetime.datetime.now()
                elapsed = end_dtime - start_dtime
                if(elapsed.total_seconds() >= max_wait_secs):
                    runner_ctx.logger.error("{}grep cmd {} : timeout error".format(runner_ctx.cur_indent,cmd))
                    err_msg ="{}max_wait_secs {} timeout error".format(runner_ctx.cur_indent,max_wait_secs)
                    raise lmt_exception.LmtException(err_msg)
                else:
                    #time.sleep(CHK_INTERVAL)
                    continue

        runner_ctx.logger.debug("{}retry : {}".format(runner_ctx.cur_indent,cmd))
        time.sleep(CHK_INTERVAL)
        #lmt_time.wait_secs(runner_ctx,CHK_INTERVAL)
        end_dtime = datetime.datetime.now()
        elapsed = end_dtime - start_dtime
        if(elapsed.total_seconds() >= max_wait_secs):
            runner_ctx.logger.error("{}grep cmd {} : timeout error".format(runner_ctx.cur_indent,cmd))
            err_msg ="{}max_wait_secs {} timeout error".format(runner_ctx.cur_indent,max_wait_secs)
            raise lmt_exception.LmtException(err_msg)

        continue

    return True

