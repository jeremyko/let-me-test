from module_core import lmt_exception

#202007 kojh create
#///////////////////////////////////////////////////////////////////////////////
def write_report_msg (runner_ctx,msg):
    #runner_ctx.logger.info(" ")
    runner_ctx.logger.info("{}{}".format(runner_ctx.cur_indent,  msg))
    runner_ctx.logger.info("{}--------------------------------------------------------------------".
            format(runner_ctx.cur_indent))
    return True
