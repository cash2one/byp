at 06:01 /every:M,T,W,Th,F,S,Su taskkill /F /IM python.exe
SCHTASKS /RU WORK /RP 9ol.)P:? /Create /TN "RESTART_SCRIPT_21" /SC DAILY /ST 06:02:00 /TR "python E:\XBUILD\byp\cron\restart_cron.py -r 10.52.156.21"