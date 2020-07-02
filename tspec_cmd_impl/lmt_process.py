#-*- coding: utf-8 -*-

from core import lmt_exception
from core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
def run_cli_cmd(runner_ctx,cli_cmd):
    cli_cmd = lmt_util.replace_all_symbols(runner_ctx,cli_cmd)
    runner_ctx.logger.debug("cli cmd : {}".format(cli_cmd))

    cmd = "{} -u {} -p {} -c {} ".format( runner_ctx.cli_name, runner_ctx.pfnm_userid,
            runner_ctx.pfnm_passwd, cli_cmd)
    runner_ctx.logger.debug("{}cli cmd : {}".format(runner_ctx.cur_indent,cmd))

    lmt_util.run_shell_cmd(runner_ctx,cmd)

    return True

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
def save_prc_pid(runner_ctx,service_name, process_name):
    #TODO
    runner_ctx.logger.info("save_prc_pid : {}".format('pid-'+service_name+process_name))
    runner_ctx.info_repo ['pid-'+service_name+process_name] = 1000 # TEST
    return True

#///////////////////////////////////////////////////////////////////////////////
def make_hangup(runner_ctx,service_name, process_name,  hangup_time_sec):
    #TODO
    # proc.stdin.write('quit\n')
    # proc.stdin.write('y\n')
    return True

