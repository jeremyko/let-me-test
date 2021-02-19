import time

#from tqdm import trange
from alive_progress import alive_bar, config_handler
from module_core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def wait_secs(runner_ctx,secs):
    runner_ctx.logger.debug("{}wait_secs start : args = {}".
            format(runner_ctx.cur_indent,secs))

    config_handler.set_global(length=20, theme='ascii', spinner='fish_bouncing')
    items = range(secs)
    with alive_bar(secs) as bar:
        for item in items:
            time.sleep(1)
            bar()

    return True

