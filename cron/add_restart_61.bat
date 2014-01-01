at 06:00 /every:M,T,W,Th,F,S,Su taskkill /F /IM python.exe
SCHTASKS /RU ADMINISTRATOR /RP 1qaz2wsx /Create /TN "RESTART_SCRIPT_61" /SC DAILY /ST 06:01:00 /TR "python F:\BDMTrunk\byp\cron\restart_cron.py -r 10.52.156.21"
