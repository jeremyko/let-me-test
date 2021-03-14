# Test Automation Framework

linux shell-based test automation framework (made of python)

### install dependencies

    cd dependencies

    pip install --ignore-installed  -r requirements.txt


### usage 

    설명 출력 
        pkg_test -h

    전체 package 모두 수행
        pkg_test  [package_directory_path]
        
        ex) pkg_test ./packages/POFCS

    특정 그룹 수행
        -g [group name]
                        
            ex) pkg_test ./packages/POFCS -g group_19.12.0
            ex) pkg_test ./packages/POFCS -g group_18.10.1 -g group_19.12.0

    특정 test 수행
        -t [group name].[test name] 
                       
            ex) pkg_test ./packages/POFCS -t group_19.12.0.MES_Alarm
            ex) pkg_test ./packages/POFCS -t group_19.12.0.MES_Alarm  -t group_19.12.0.VLD_Validation

    특정 spec 수행
        -s [group name].[test name].[tspec name]
                        
            ex) pkg_test ./packages/POFCS -s group_19.12.0.MES_Alarm.mes_alarm_valid_time
            ex) pkg_test ./packages/POFCS -s group_19.12.0.MES_Alarm.mes_alarm_valid_time  -s group_19.12.0.MES_Alarm.mes_alarm_no_check
