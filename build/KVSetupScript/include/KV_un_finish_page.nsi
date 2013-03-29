
#卸载confirm页面逻辑
Function  un.finish_page_show

	FindWindow $0 "#32770" "" $HWNDPARENT
	KVInstallHelper::GetWndHandle /NOUNLOAD $0
	
    Quit

FunctionEnd


Function  un.finish_page_leave
FunctionEnd
