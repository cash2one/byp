
#install filesÒ³ÃæÂß¼­

Function instfiles_page_pre
FunctionEnd


Function instfiles_page_show

	FindWindow $0 "#32770" "" $HWNDPARENT
	KVInstallHelper::GetWndHandle /NOUNLOAD $0
FunctionEnd



Function instfiles_page_leave
	Exec  '"$INSTDIR\${MAINFRAME_PROCESS_NAME}"'
	Quit
FunctionEnd



