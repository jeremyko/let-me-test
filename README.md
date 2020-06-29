# Let Me Test 

Test Automation Framework

"#" 로 시작하는 라인은 주석으로 처리됨. 
| test spec command | arguments |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| set_cfg                 |(설정파일명, xpath, 변경할값)|
| run_cli_cmd                                   |(cli명령)|
| run_shell_cmd                                     |(명령)|
| run_prc                            |(실행파일명  인자)|
| terminate_prc                               |(실행파일명)|
| kill_prc                                 |(실행파일명)|
| assert_app_running            |(service_name, process_name)|
| assert_prc_running                            |(실행파일명)|
| send_simul                               |(보낼cdr폴더)|
| wait_secs                                         |(초)|
| save_cur_file_line_cnt                            |(파일경로)|
| assert_file_grep                   |(찾을문자열, 파일경로)|
| save_prc_pid               |(service_name, process_name)|
| assert_prc_same_pid            |(service_name, process_name)|
| assert_alarm_exists                            |(alarm_code)|
| assert_alarm_cleared                           |(alarm_code)|
| make_hangup            |(service_name, process_name,  hangup 할 시간초)|
| assert_cdr_fld_len                        |(필드명, 자리수)|
| save_cdr_fld_value              |(cdr형식, 필드명, cdr경로)|
| assert_cdr_fld_eq                                 |(필드명)|
| assert_mes_q_full                           |(로그파일경로)|
| assert_mes_q_not_full                         |(로그파일경로)|
| test_run_ok                          |(명령 or 실행파일)|
| test_run_err                         |(명령 or 실행파일)|
| test_eq                       |(비교할 값,  비교할 값)|
| test_eq_prc_output           |(명령 or 실행파일, 비교할 값)|
| make_swap                                           |없음|
| write_report_msg               |(report파일에 저장될 내용)|

