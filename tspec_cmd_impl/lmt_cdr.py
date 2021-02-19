#-*- coding: utf-8 -*-

#import os
#import subprocess
#import glob
from module_core import lmt_exception
from module_core import lmt_util

#TODO
# assert_cdr_fld_len              |(필드명, 자리수)|
# assert_cdr_fld_eq               |(필드명)|
# save_cdr_fld_value              |(cdr형식, 필드명, cdr경로)|



"""
first = []
for file in glob.glob(monthDir +"/"+day+"*.txt"):
    if fileContains(file, 'Algeria|Bahrain') and fileContains(file, 'Protest|protesters'):
        file.append(first)
"""

"""
#///////////////////////////////////////////////////////////////////////////////
# CDR 특정 항목 값들을 로깅한다. (근거 자료 준비 등에 사용)
#///////////////////////////////////////////////////////////////////////////////
def grep_ov_result (runner_ctx, ov_cmd, to_find_str, head_n):
    ov_cmd = lmt_util.replace_all_symbols(runner_ctx,ov_cmd)
    runner_ctx.logger.debug("{}ov cmd : {}".format(runner_ctx.cur_indent,ov_cmd))

    #================================================ using check_output
    ov_cmd_full = "{} | grep '{}' | head -n {} ".format( ov_cmd, to_find_str, head_n) 
    runner_ctx.logger.info("{}ov cmd full : {}".format(runner_ctx.cur_indent,ov_cmd_full))
    output = subprocess.check_output(ov_cmd_full, shell=True)
    if(output):
        out_list = output.split("\n")
        if(out_list):
            for outval in out_list:
                if(len(outval)>0):
                    runner_ctx.logger.info("{}grep ov : {}".format(runner_ctx.cur_indent,outval))
    #================================================ using Popen

    return True

#///////////////////////////////////////////////////////////////////////////////
def ov_grep_assert_eq (runner_ctx, ov_cmd, expect_num):
    ov_cmd = lmt_util.replace_all_symbols(runner_ctx,ov_cmd)
    runner_ctx.logger.info("{}ov cmd   : {}".format(runner_ctx.cur_indent,ov_cmd))
    runner_ctx.logger.info("{}expected : {}".format(runner_ctx.cur_indent,expect_num))

    output = subprocess.check_output(ov_cmd, shell=True)
    if(output):
        found_cnt = int(output)
        runner_ctx.logger.debug("{}ov cmd returns : {}".format(runner_ctx.cur_indent,found_cnt))
        if(expect_num != found_cnt):
            err_msg = "ov grep assert failed : actual({}) != expected({})".format(found_cnt,expect_num)
            runner_ctx.logger.error("{}".format(runner_ctx.cur_indent,err_msg))
            raise lmt_exception.LmtException(err_msg)
    else:
        return False

    return True
"""

"""
#cmd_list = ov_cmd.split(" ")
#p1 = subprocess.Popen(cmd_list,stdout=subprocess.PIPE) # 파일 명시하면 ok ,* 사용시 에러 
p1 = subprocess.Popen(ov_cmd, shell=True, stdout=subprocess.PIPE) # shell=True -> for "*" 
p2 = subprocess.Popen(["grep", to_find_str], stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(["head", "-n", str(head_n)], stdin=p2.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
p2.stdout.close()
output = p3.communicate()[0]
#output = p3.stdout.read()
if(output):
    out_list = output.split("\n")
    if(out_list):
        for outval in out_list:
            if(len(outval)>0):
                runner_ctx.logger.info("{}grep ov : {}".format(runner_ctx.cur_indent,outval))
"""                
#================================================
