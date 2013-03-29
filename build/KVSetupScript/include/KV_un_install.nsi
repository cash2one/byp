#ж�������߼�
UninstallCaption "${MACRO_LNKUNINSTALL}${BUILD_VERSION}"

;����Ȩ��
RequestExecutionLevel  admin

# ����ͬʱҪɾ��drivers�µ��ļ�
!macro DeleteDriver driver
	DeleteRegKey HKLM "SYSTEM\CurrentControlSet\services\${driver}"
!macroend

#UI��ʼ��
Function un.onGUIInit
	InitPluginsDir
	SetOutPath "$PLUGINSDIR\res"       
	File /oname=$PLUGINSDIR\res\InstallWnd.zip    	"res\InstallWnd.zip"
	SetOutPath "$PLUGINSDIR"
	File /oname=$PLUGINSDIR\BDMSkin.dll    			"res\BDMSkin.dll"			
	KVInstallHelper::GetXmlPath /NOUNLOAD "$PLUGINSDIR\res" "\InstallWnd.zip"  "${PRODUCT_NAME}" "${BUILD_VERSION}"    0 ;0��ʾж��
FunctionEnd

#ж��ǰִ��
Function un.onInit
	!insertmacro WRITE_LOG_MSG "Uninstall Section $\n"

	#�ж��Ƿ�Ĭ��װ
	Strcpy $varIsSilence "1"
	IfSilent +2
	Strcpy $varIsSilence "0"

FunctionEnd

var nUninstallReason
var strUninstallReason
var strSupplyID
var AllUserProfileDir

Section "Uninstall" 	
	#----------------------------��ȡ���·��---------------------------------
	#��ȡappdata·��
	KVInstallHelper::GetAllUserAppDataDir /NOUNLOAD
	pop $R0 
	StrCpy $AppDir $R0
	
	!insertmacro WRITE_LOG_MSG "AppDir: $AppDir $\n"
	
	KVInstallHelper::GetAllUserProfileDir /NOUNLOAD
	pop $R0 
	StrCpy $AllUserProfileDir $R0
	
	!insertmacro WRITE_LOG_MSG "AllUserProfileDir: $AllUserProfileDir $\n"
	
	ReadRegStr $SmDesktopDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Desktop"
    ReadRegStr $SmProgramsDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Programs"

	!insertmacro WRITE_LOG_MSG "DesktopDir: $SmDesktopDir $\n"
	!insertmacro WRITE_LOG_MSG "ProgramsDir: $SmProgramsDir $\n"
	
	#���SupplyID
	ReadRegStr $strSupplyID HKLM "${HKLM_REG_PATH}" "SupplyID"
	!insertmacro WRITE_LOG_MSG "SupplyID: $strSupplyID $\n"
	
	!insertmacro WRITE_LOG_MSG "INSTDIR: $INSTDIR $\n"

	#��ȡж��ԭ��
	KVInstallHelper::GetUnInstallReason /NOUNLOAD
	pop $strUninstallReason
	pop $nUninstallReason

	!insertmacro WRITE_LOG_MSG "UninstallReason $nUninstallReason $\n"
	!insertmacro WRITE_LOG_MSG "UninstallReason $strUninstallReason $\n"
	
	#ж�������ϱ�
	KVInstallHelper::ReportUninstallData /NOUNLOAD "$INSTDIR\BDLogicUtils.dll" 0 "$nUninstallReason" "$strUninstallReason" "" "$strSupplyID"
	
	!insertmacro WRITE_LOG_MSG "Data Report $\n"
	
	#----------------------------��ʱ---------------------------------
	#win7��װ���������ݵ�����
	WriteRegDWORD HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted"  "$INSTDIR\uninst.exe" 0x1 

	#----------------------------ж��������ʼ---------------------------------
	
    #ж�ؿ���˹������
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "klim"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kl1"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kneps"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kltdi"
    KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "klif"
	!insertmacro WRITE_LOG_MSG "uninstall kav driver $\n"
	
	# ɾ����������ļ���ע���,ע�ⲻ��ж������
	!insertmacro DeleteDriver bd0001
	!insertmacro DeleteDriver bd0002
	!insertmacro DeleteDriver bd0003
	!insertmacro WRITE_LOG_MSG "delete driver reg $\n"
	
	#��ע���Ҽ��˵�DLL
    #ExecWait '"RegSvr32.exe" /s /u "$INSTDIR\BDShellExt.dll"'
    
	#----------------------------ж����������---------------------------------
	
	#----------------------------ֹͣ����ʼ---------------------------------
    #����CoreSvr����
    ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -t'
	!insertmacro WRITE_LOG_MSG "stop server $\n"
	
	#Ȼ��ɱ�����п��ܵĽ���
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${MAINFRAME_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKV.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${TRAY_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVTray.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${SERVER_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVCoreSvr.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${UPDATE_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVUpdate.exe $\n"
	
	#ж�ط���
    ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -u'
	!insertmacro WRITE_LOG_MSG "uninstall server $\n"
	
	#ɾ����������
	DeleteRegKey  HKLM "SYSTEM\CurrentControlSet\Services\BDKVRTP"

	#----------------------------ֹͣ�������---------------------------------
	
	#----------------------------ɾ���ļ���ʼ---------------------------------
	#ɾ��bd0001.dll
	KVInstallHelper::RenameAndDeleteFile /NOUNLOAD "$INSTDIR\bd0001.dll"
	!insertmacro WRITE_LOG_MSG "rename and delete bd0001.dll $\n"
	
	#ɾ��appdata�ļ�
    RMDir /r  "$AppDir\${ALL_USER_DATA_PATH}"
	
	#ɾ����װ�����ļ�
    RMDir /r $INSTDIR
	
	#ɾ������˹�����ݣ�����license���ڣ�ALLUSER·���趯̬ȡ
	RMDir /r  "$AllUserProfileDir\Kaspersky SDK\*.dat"
	
	#----------------------------ɾ���ļ�����---------------------------------
	
	#ɾ����ݷ�ʽ
    Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk"
    Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" 
    RMDir /r "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}"
    Delete "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" 
	
	#ɾ��ע�����
    DeleteRegKey  HKLM "${HKLM_REG_PATH}" 
    DeleteRegKey  HKLM "${PRODUCT_UNINST_KEY}"
	
SectionEnd
