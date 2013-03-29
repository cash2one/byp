
#directory页面逻辑


# 该函数位置不能改变，因为这里面改变了宏的定义，该改变仅针对directory页面
Function directory_page_pre
	#运行提示,只是提示
	
	#提示结束进程
	KVInstallHelper::IsProcessRunning /NOUNLOAD "${TRAY_PROCESS_NAME}"
	pop $R0
	${if} $varIsSilence == "0"
	    ${if} $R0 == "1"
			!insertmacro WRITE_LOG_MSG "promote process running $\n"
			MessageBox MB_ICONQUESTION|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEINSTALL_WARNING}" IDOK +2 IDCANCEL 0
			Quit
		${endif}
	${endif}
	
	#判断操作系统是否兼容(静默安装下要不要提示呢? 目前是静默安装仍然提示)
	KVInstallHelper::IsSystemCompatible /NOUNLOAD
	pop $R0
	${if} $varIsSilence == "0"
		${if} $R0 == "0"
			MessageBox MB_ICONQUESTION|MB_TOPMOST|MB_OKCANCEL|MB_DEFBUTTON2  "${MACO_MESSAGE_SYSTEMCOMPATIBLE}"  IDOK +2 IDCANCEL 0
			Quit
		${endif}
	${endif}
	
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${SERVER_PROCESS_NAME}"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${TRAY_PROCESS_NAME}"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${MAINFRAME_PROCESS_NAME}"

FunctionEnd

Function directory_page_show
	FindWindow $0 "#32770" "" $HWNDPARENT
	KVInstallHelper::CreateInstallWnd /NOUNLOAD $0 
	
FunctionEnd

#directory页面离开的回调函数
Function directory_page_leave

#判断安装路径合法性

GetInstDirError $0
  ${Switch} $0
    ${Case} 0
      ${Break}
    ${Case} 1
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 3
      ;MessageBox MB_OK|MB_ICONQUESTION ${MACRO_INVALIDDIRECTORY}
	  KVInstallHelper::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
      Abort
      ${Break}
    ${Case} 2
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 1
      ;MessageBox MB_OK|MB_ICONSTOP ${MACRO_NOENOUGHFREESPACE}
	  KVInstallHelper::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
      Abort
      ${Break}
  ${EndSwitch}

KVInstallHelper::ValidateInstDir /NOUNLOAD
pop $R0
${if} $R0 == "0"
     KVInstallHelper::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
     Abort
${endif}

FunctionEnd
