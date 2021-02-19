#!/bin/sh

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -g group_15.11.0 -f PKG_V15.11.0

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -g group_16.10.0 -f PKG_V16.10.0

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_17.03.0.ULI -f PKG_V17.03.0

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -g group_17.06.0 -f PKG_V17.06.0

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_17.08.1.STD_Error_STAT_Dup -f PKG_V17.08.1.STAT_DUP
                                                                                                
/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_17.08.1.STD_STOP_STAT_OMISSION -f PKG_V17.08.1.STAT_OMISSION

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_17.08.1.RATTYPE_Change -f PKG_V17.08.1.RATTYPE

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_17.10.0.DUP -f PKG_V17.10.0.DUP

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_18.09.0.001.GTP -f PKG_V17.10.0.001.GTP

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_18.09.0.002.DEC -f PKG_V17.10.0.002.DEC

/POFCS/CG/TEST_TOOL/pkg_test /POFCS/CG/TEST_TOOL/packages/POFCS -t group_18.09.0.003.STD -f PKG_V17.10.0.003.STD
