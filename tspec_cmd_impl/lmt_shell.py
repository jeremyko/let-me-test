import pexpect

from module_core import lmt_exception
from module_core import lmt_util


#///////////////////////////////////////////////////////////////////////////////
def do_interactive_cmd(runner_ctx, run_cmd, dic_expect_val):
    # TODO
    """
    timeout_sec = 30
    #-------------------------------------
    child = pexpect.spawn('/bin/bash -c "cd /CG/OFCS_SIM/IMS_SIM/SRC; ./DIA_SIM"')
    child.logfile = sys.stdout
    #-------------------------------------
    child.setwinsize(100, 100)
    child.expect('CLOSE_NOT_READY', timeout=timeout_sec)
    runner_ctx.logger.info("CLOSE_NOT_READY")
    #-------------------------------------
    child.sendline('init 1\n')
    child.expect('OPEN_NOT_READY', timeout=timeout_sec)
    runner_ctx.logger.info("OPEN_NOT_READY")
    #-------------------------------------
    child.sendline('load 1\n')
    child.expect('OPEN_READY', timeout=timeout_sec)
    runner_ctx.logger.info("OPEN_READY")
    #-------------------------------------
    child.sendline('start 1\n')
    child.expect('ALL_SENT', timeout=120)
    runner_ctx.logger.info("ALL_SENT")
    #-------------------------------------
    child.sendline('quit')
    child.expect('GOOD BYE!', timeout=timeout_sec)
    runner_ctx.logger.info("GOOD BYE!")
    #-------------------------------------
    #child.terminate()
    child.close()
    """
    return True
