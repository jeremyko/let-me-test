 #-*- coding: utf-8 -*-

import os
import platform

from module_core import lmt_exception
from module_core import lmt_util
from tspec_cmd_impl import lmt_file
from tspec_cmd_impl import lmt_assert


#///////////////////////////////////////////////////////////////////////////////
def get_mem_info():
    ''' Return the information in /proc/meminfo
    as a dictionary '''
    meminfo={}

    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()

    return meminfo

#///////////////////////////////////////////////////////////////////////////////
def rms_mem_info_check(runner_ctx):

    # print RMS memory total log...
    # 먼저 RMS 로그를 삭제하고, memory total 로그가 나올때까지 기다린다
    lmt_file.remove_pfnm_file_log(runner_ctx, "RMS*.${CUR_YYYYMMDD}")
    grep_cmd = lmt_util.replace_all_symbols(runner_ctx, "grep 'MEM total' ${LOG_BASE_PATH}/PFNM/SYS/RMS*.${CUR_YYYYMMDD} ")

    lmt_assert.assert_poll_cmd_output_include_string (runner_ctx, grep_cmd, "MEM total", 600)
    
    #RMS 에서 memory total 로그가 기록되면 즉시, 실제 메모리 정보 동일하게 계산
    meminfo = get_mem_info()
    #runner_ctx.logger.debug("{}{}".format(runner_ctx.cur_indent, meminfo))

    total       = int(meminfo['MemTotal'].replace("kB",""))
    free        = int(meminfo['MemFree'].replace("kB",""))
    buffers     = int(meminfo['Buffers'].replace("kB",""))
    cached      = int(meminfo['Cached'].replace("kB",""))
    shared      = int(meminfo['Shmem'].replace("kB",""))
    slab        = int(meminfo['Slab'].replace("kB",""))
    active_file = int(meminfo['Active(file)'].replace("kB",""))
    swap_total  = int(meminfo['SwapTotal'].replace("kB",""))
    swap_free   = int(meminfo['SwapFree'].replace("kB",""))
    used = 0

    #runner_ctx.logger.debug("{}uname = {}".format(runner_ctx.cur_indent, platform.uname()))
    release = platform.release()
    #runner_ctx.logger.info("{}release = {}".format(runner_ctx.cur_indent, release))
    os_ver = ""
    if("el6" in release):
        os_ver ="6"
        # (MemTotal – MemFree – Buffers – Cached + Shared + Active(file)) 
        used = total - ( free + buffers + cached ) + shared+ active_file ;
    elif("el7" in release):
        os_ver ="7"
        # (MemTotal – MemFree – Buffers – Cached - Slab + Shared + Active(file)) 
        used = total - ( free + buffers + cached + slab ) + shared + active_file ;
    else:
        os_ver ="other"
        # MemTotal – MemFree – Buffers – Cached) 
        used = total - ( free + buffers + cached ) ;

    #runner_ctx.logger.debug("{}used {} KB".format(runner_ctx.cur_indent, used))    
    swap_used   = swap_total - swap_free 
    total_mem   = total             
    free_mem    = total - used   

    mem_total_mb      = total_mem / 1024;
    mem_free_mb       = free_mem  / 1024;
    mem_used_mb       = (total_mem - free_mem) / 1024;

    mem_swap_total_mb = swap_total / 1024;
    mem_swap_free_mb  = (swap_total - swap_used) / 1024;
    mem_swap_used_mb  = swap_used / 1024;
    mem_usage         = (float(mem_used_mb) / float(mem_total_mb)) * 100
    mem_swap_usage    = (float(mem_swap_used_mb) / float(mem_swap_total_mb)) * 100
    runner_ctx.logger.info("{}version={}, MEM total {} kb, free {} kb, used {} kb usage {}".
            format(runner_ctx.cur_indent, os_ver, total_mem, free_mem, total_mem - free_mem, mem_usage) ) ;


