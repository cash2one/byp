#卸载区段逻辑
UninstallCaption "${MACRO_LNKUNINSTALL}${BUILD_VERSION}"

;提升权限
RequestExecutionLevel  admin

# 这里同时要删除drivers下的文件
!macro DeleteDriver driver
	DeleteRegKey HKLM "SYSTEM\CurrentControlSet\services\${driver}"
!macroend

#UI初始化
Function un.onGUIInit
	InitPluginsDir
	SetOutPath "$PLUGINSDIR\res"       
	File /oname=$PLUGINSDIR\res\InstallWnd.zip    	"res\InstallWnd.zip"
	SetOutPath "$PLUGINSDIR"
	File /oname=$PLUGINSDIR\BDMSkin.dll    			"res\BDMSkin.dll"			
	KVInstallHelper::GetXmlPath /NOUNLOAD "$PLUGINSDIR\res" "\InstallWnd.zip"  "${PRODUCT_NAME}" "${BUILD_VERSION}"    0 ;0表示卸载
FunctionEnd

#卸载前执行
Function un.onInit
	!insertmacro WRITE_LOG_MSG "Uninstall Section $\n"

	#判断是否静默安装
	Strcpy $varIsSilence "1"
	IfSilent +2
	Strcpy $varIsSilence "0"

FunctionEnd

var nUninstallReason
var strUninstallReason
var strSupplyID
var AllUserProfileDir

Section "Uninstall" 	
	#----------------------------获取相关路径---------------------------------
	#获取appdata路径
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
	
	#获得SupplyID
	ReadRegStr $strSupplyID HKLM "${HKLM_REG_PATH}" "SupplyID"
	!insertmacro WRITE_LOG_MSG "SupplyID: $strSupplyID $\n"
	
	!insertmacro WRITE_LOG_MSG "INSTDIR: $INSTDIR $\n"

	#获取卸载原因
	KVInstallHelper::GetUnInstallReason /NOUNLOAD
	pop $strUninstallReason
	pop $nUninstallReason

	!insertmacro WRITE_LOG_MSG "UninstallReason $nUninstallReason $\n"
	!insertmacro WRITE_LOG_MSG "UninstallReason $strUninstallReason $\n"
	
	#卸载数据上报
	KVInstallHelper::ReportUninstallData /NOUNLOAD "$INSTDIR\BDLogicUtils.dll" 0 "$nUninstallReason" "$strUninstallReason" "" "$strSupplyID"
	
	!insertmacro WRITE_LOG_MSG "Data Report $\n"
	
	#----------------------------临时---------------------------------
	#win7安装弹出不兼容的问题
	WriteRegDWORD HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted"  "$INSTDIR\uninst.exe" 0x1 

	#----------------------------卸载驱动开始---------------------------------
	
    #卸载卡巴斯基驱动
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "klim"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kl1"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kneps"
	#InstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "kltdi"
    KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"  "--uninstall "  "klif"
	!insertmacro WRITE_LOG_MSG "uninstall kav driver $\n"
	
	# 删除相关驱动文件和注册表,注意不是卸载驱动
	!insertmacro DeleteDriver bd0001
	!insertmacro DeleteDriver bd0002
	!insertmacro DeleteDriver bd0003
	!insertmacro WRITE_LOG_MSG "delete driver reg $\n"
	
	#反注册右键菜单DLL
    #ExecWait '"RegSvr32.exe" /s /u "$INSTDIR\BDShellExt.dll"'
    
	#----------------------------卸载驱动结束---------------------------------
	
	#----------------------------停止服务开始---------------------------------
    #结束CoreSvr服务
    ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -t'
	!insertmacro WRITE_LOG_MSG "stop server $\n"
	
	#然后杀掉所有可能的进程
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${MAINFRAME_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKV.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${TRAY_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVTray.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${SERVER_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVCoreSvr.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${UPDATE_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVUpdate.exe $\n"
	
	#卸载服务
    ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -u'
	!insertmacro WRITE_LOG_MSG "uninstall server $\n"
	
	#删除服务配置
	DeleteRegKey  HKLM "SYSTEM\CurrentControlSet\Services\BDKVRTP"

	#----------------------------停止服务结束---------------------------------
	
	#----------------------------删除文件开始---------------------------------
	#删除bd0001.dll
	KVInstallHelper::RenameAndDeleteFile /NOUNLOAD "$INSTDIR\bd0001.dll"
	!insertmacro WRITE_LOG_MSG "rename and delete bd0001.dll $\n"
	
	#删除appdata文件
    RMDir /r  "$AppDir\${ALL_USER_DATA_PATH}"
	
	#删除安装包下文件
    RMDir /r $INSTDIR
	
	#删除卡巴斯基数据，避免license过期，ALLUSER路径需动态取
	RMDir /r  "$AllUserProfileDir\Kaspersky SDK\*.dat"
	
	#----------------------------删除文件结束---------------------------------
	
	#删除快捷方式
    Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk"
    Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" 
    RMDir /r "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}"
    Delete "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" 
	
	#删除注册表项
    DeleteRegKey  HKLM "${HKLM_REG_PATH}" 
    DeleteRegKey  HKLM "${PRODUCT_UNINST_KEY}"
	
SectionEnd
