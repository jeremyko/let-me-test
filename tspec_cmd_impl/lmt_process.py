import os
from core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def run_cli_cmd(runner_ctx,cli_cmd):
    cli_cmd = cli_cmd.replace("${PACKAGE_NAME}", runner_ctx.package_name)
    cli_cmd = cli_cmd.replace("${SYSTEM_NAME}" , runner_ctx.system_name)
    runner_ctx.logger.debug("cli cmd : {}".format(cli_cmd))

    cmd = "pfmCLI -u {} -p {} -c {} ".format(runner_ctx.pfnm_userid,
            runner_ctx.pfnm_passwd, cli_cmd)
    runner_ctx.logger.debug("cli cmd : {}".format(cmd))
    stream = os.popen(cmd)
    output = stream.read()
    if(output):
        runner_ctx.logger.debug("result : {}".format(output))
        #TODO error check !!! 

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
    return True
