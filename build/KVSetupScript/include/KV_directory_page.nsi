
#directoryҳ���߼�


# �ú���λ�ò��ܸı䣬��Ϊ������ı��˺�Ķ��壬�øı�����directoryҳ��
Function directory_page_pre
	#������ʾ,ֻ����ʾ
	
	#��ʾ��������
	KVInstallHelper::IsProcessRunning /NOUNLOAD "${TRAY_PROCESS_NAME}"
	pop $R0
	${if} $varIsSilence == "0"
	    ${if} $R0 == "1"
			!insertmacro WRITE_LOG_MSG "promote process running $\n"
			MessageBox MB_ICONQUESTION|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEINSTALL_WARNING}" IDOK +2 IDCANCEL 0
			Quit
		${endif}
	${endif}
	
	#�жϲ���ϵͳ�Ƿ����(��Ĭ��װ��Ҫ��Ҫ��ʾ��? Ŀǰ�Ǿ�Ĭ��װ��Ȼ��ʾ)
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

#directoryҳ���뿪�Ļص�����
Function directory_page_leave

#�жϰ�װ·���Ϸ���

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
