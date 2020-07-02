#-*- coding: utf-8 -*-

import subprocess

from core import lmt_exception
from core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
def test_eq(runner_ctx,a,b):
    if(a != b):
        err_msg ="assert failed : {} != {} ".format(a,b)
        raise lmt_exception.LmtException(err_msg)
    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_app_running(runner_ctx, service_name, process_name):
    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_prc_running(runner_ctx,proc_name):
    return True

#///////////////////////////////////////////////////////////////////////////////
# ex) assert_file_grep("redis_pipeline_threshold_ [30]", "/GTP_SMF/FMS01_1.${CUR_YYYYMMDD}"):
def assert_file_grep(runner_ctx,to_find_str, file_path):

    #runner_ctx.log_base_path ends with os.sep
    file_path = lmt_util.replace_all_symbols(runner_ctx,file_path)
    tmp_file_path = runner_ctx.log_base_path + file_path
    saved_line_cnt = runner_ctx.info_repo['line_cnt'] 

    #get 증가한_라인수
    now_line_cnt = int(subprocess.check_output(['wc', '-l', tmp_file_path]).split()[0])
    diff_cnt = now_line_cnt - saved_line_cnt
    runner_ctx.logger.debug("file_path [{}], saved_line_cnt ={}, now cnt ={}, diff ={}".
            format(tmp_file_path, saved_line_cnt, now_line_cnt, diff_cnt))

    # tail -증가한_라인수 file | grep …
    # ex) tail -72  /LOG/GTP_SMF/FMS01_1.20200701 | fgrep "redis_pipeline_threshold_ [30]"
    cmd = 'tail -{} {} | fgrep "{}"'.format(diff_cnt, tmp_file_path, to_find_str)
    lmt_util.run_shell_cmd(runner_ctx,cmd)

    # TODO : file 내용을 result 폴더, test 단위 폴더에 별도로 저장한다.

    return True

#///////////////////////////////////////////////////////////////////////////////
def assert_prc_same_pid(runner_ctx,service_name, process_name):
    runner_ctx.logger.info(runner_ctx.info_repo)
    runner_ctx.logger.info("assert_prc_same_pid : {}".format('pid-'+service_name+process_name))
    runner_ctx.logger.info("pid = {}".format(runner_ctx.info_repo ['pid-'+service_name+process_name]))  # TEST
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


