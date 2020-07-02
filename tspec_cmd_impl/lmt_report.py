from core import lmt_exception

#///////////////////////////////////////////////////////////////////////////////
def write_report_msg (runner_ctx,msg):
    runner_ctx.logger.info("{}- user msg : \n  {}{}".
            format(runner_ctx.cur_indent, runner_ctx.cur_indent, msg))
    return True
