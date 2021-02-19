#-*- coding: utf-8 -*-
import os
from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_time


#///////////////////////////////////////////////////////////////////////////////
# pfnm 중단 후 공유메모리 모두 지우고(mes queue 삭제) pfnm 재기동 한다.
# XXX pfmStp.sh, pfmRun.sh 에서 비번을 물어보는 경우 작동 안됨.
# XXX 비번을 안물어보게 수정하여 pfmStp.sh.test, pfmRun.sh.test 로 rename 해서 사용 

def clear_mes_queue_restart_pfnm (runner_ctx): 

    runner_ctx.logger.info("{}pfnm 중단 시작".format(runner_ctx.cur_indent))
    #lmt_util.run_shell_cmd(runner_ctx, "pfmStp.sh all ")
    lmt_util.run_shell_cmd(runner_ctx, "pfmStp.sh.test all ")
    runner_ctx.logger.info("{}pfnm 중단 완료".format(runner_ctx.cur_indent))
    lmt_time.wait_secs(runner_ctx,10)

    lmt_util.clear_all_shared_memory(runner_ctx) 

    runner_ctx.logger.info("{}pfnm start 시작".format(runner_ctx.cur_indent))
    #lmt_util.run_shell_cmd(runner_ctx, "pfmRun.sh all ${PACKAGE_ID} ") --> error. hang. 
    #cmd = lmt_util.replace_all_symbols(runner_ctx,"pfmRun.sh all ${PACKAGE_ID} ")
    cmd = lmt_util.replace_all_symbols(runner_ctx,"pfmRun.sh.test all ${PACKAGE_ID} ")
    runner_ctx.logger.info("{}cmd = {}".format(runner_ctx.cur_indent, cmd))
    os.system(cmd) # XXX 
    # wait pfnm process all started...
    lmt_time.wait_secs(runner_ctx,60)
    runner_ctx.logger.info("{}pfnm start 완료".format(runner_ctx.cur_indent))

#///////////////////////////////////////////////////////////////////////////////
def make_swap(runner_ctx): 
    #TODO
    return True
