


Function un.instfiles_page_pre
	#提示结束进程
	KVInstallHelper::IsProcessRunning /NOUNLOAD "${TRAY_PROCESS_NAME}"
	pop $R0
	${if} $R0 == "1"
		!insertmacro WRITE_LOG_MSG "promote process running $\n"
		MessageBox MB_ICONQUESTION|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEUNINSTALL_WARNING}" IDOK +2
		Quit
	${endif}
	
	#----------------------------强杀进程---------------------------------	
	#强杀
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${SERVER_PROCESS_NAME}"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${TRAY_PROCESS_NAME}"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${MAINFRAME_PROCESS_NAME}"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${UPDATE_PROCESS_NAME}"

FunctionEnd


Function un.instfiles_page_show
	FindWindow $0 "#32770" "" $HWNDPARENT
	KVInstallHelper::GetWndHandle /NOUNLOAD $0
FunctionEnd



Function un.instfiles_page_leave

FunctionEnd


