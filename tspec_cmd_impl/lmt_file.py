import subprocess

from core import lmt_exception
from core import lmt_util

#///////////////////////////////////////////////////////////////////////////////
def save_cur_file_line_cnt(runner_ctx,file_path):
    file_path = runner_ctx.log_base_path + lmt_util.replace_all_symbols(runner_ctx,file_path)
    runner_ctx.logger.debug("file_path : {}".format(file_path))

    line_cnt = int(subprocess.check_output(['wc', '-l', file_path]).split()[0])
    runner_ctx.logger.debug("file [{}] -> line cnt : {}".format(file_path,line_cnt))
    runner_ctx.info_repo['line_cnt'] = line_cnt
    return True
