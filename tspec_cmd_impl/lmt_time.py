import time

from core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def wait_secs(runner_ctx,secs):
    runner_ctx.logger.info("{}wait_secs start : args = {}".
            format(runner_ctx.cur_indent,secs))
    time.sleep(secs)
    return True

