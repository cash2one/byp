Function un.directory_page_pre

FunctionEnd

Function un.directory_page_show
	FindWindow $0 "#32770" "" $HWNDPARENT
	KVInstallHelper::CreateUnInstallWnd /NOUNLOAD $0
FunctionEnd

Function un.directory_page_leave
	
FunctionEnd