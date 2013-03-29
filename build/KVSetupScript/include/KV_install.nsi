#安装区段逻辑
!define PRODUCT_UNINST_KEY	"Software\Microsoft\Windows\CurrentVersion\Uninstall\${MACRO_PRODUCTNAME}"
!define INSTALL_LOG_FILE	"c:\bdkv_install.log"
!define UNINSTALL_LOG_FILE	"c:\bdkv_uninstall.log"
!define	IS_WRITE_SETUP_LOG	1

#文件拷贝
!macro File2 FileName SrcFilePath DesOutPath
	SetOutPath "$PLUGINSDIR\file"
	File ${SrcFilePath}
	ClearErrors
	CopyFiles /SILENT /FILESONLY "$PLUGINSDIR\file\${FileName}" "${DesOutPath}"
	IfErrors 0 +3
		!insertmacro WRITE_LOG_MSG "Failed Copy: ${SrcFilePath} $\n"
	Call IncFileCopyCount
	Call SendFileCopyProgress
	Delete "$PLUGINSDIR\file\${FileName}"
	SetOutPath ${DesOutPath}
!macroend

var lastdir
var installpackname
var AllUsersProfileDir
var AppDir
var debugpath
var SupplyID
var InstallMode
var InstallStartTime
var InstallEndTime
var TempDir
Section Install
	#记录开始时间
    KVInstallHelper::RecordStartTime /NOUNLOAD
	
	#----------------------------获取相关路径---------------------------------
	#获取桌面路径
	ReadRegStr $SmDesktopDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Desktop"
    ReadRegStr $SmProgramsDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Programs"

	!insertmacro WRITE_LOG_MSG "DesktopDir: $SmDesktopDir $\n"
	!insertmacro WRITE_LOG_MSG "ProgramsDir: $SmProgramsDir $\n"
	
	#获取AppData路径
	KVInstallHelper::GetAllUserAppDataDir /NOUNLOAD
	pop $R0
	StrCpy $AppDir $R0
	
	!insertmacro WRITE_LOG_MSG "AppDir: $AppDir $\n"

	#获取AllUserProfile路径
	KVInstallHelper::GetAllUserProfileDir /NOUNLOAD
	pop $R0
	StrCpy $AllUsersProfileDir $R0
	
	!insertmacro WRITE_LOG_MSG "AllUsersProfileDir: $AllUsersProfileDir $\n"
	
	#----------------------------临时-------------------------------------------	
	#设置 核心内存转储
	SetOverwrite try
	WriteRegDWORD HKLM "SYSTEM\CurrentControlSet\Control\CrashControl" "CrashDumpEnabled" 0x00000002
	
	#----------------------------删除老版本开始---------------------------------
    #读取老版本路径
    StrCpy $strOldInstDir ""
    StrCpy $strOldVersion ""
    ReadRegStr $strOldInstDir HKLM "${HKLM_REG_PATH}" "InstallDir"
    ReadRegStr $strOldVersion HKLM "${HKLM_REG_PATH}" "Version"
    StrCpy $lastdir "$strOldInstDir\$strOldVersion"

	!insertmacro WRITE_LOG_MSG "lastdir: $lastdir $\n"
	
	StrCpy $strInstallDir $INSTDIR
    StrCpy $INSTDIR "$strInstallDir\${BUILD_BASELINE}"

	!insertmacro WRITE_LOG_MSG "INSTDIR: $INSTDIR $\n"
	
	#停止服务
	ExecWait '"$lastdir\${SERVER_PROCESS_NAME}" -t'
	
	!insertmacro WRITE_LOG_MSG "stop server $\n"
	
	#然后杀掉所有可能的进程
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${MAINFRAME_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKV.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${TRAY_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVTray.exe $\n"
	KVInstallHelper::KillRunningProcess /NOUNLOAD "${SERVER_PROCESS_NAME}"
	!insertmacro WRITE_LOG_MSG "kill BDKVCoreSvr.exe $\n"
	
	#卸载服务	
	ExecWait '"$lastdir\${SERVER_PROCESS_NAME}" -u'
		
	!insertmacro WRITE_LOG_MSG "uninstall server $\n"
	
	#删除服务注册表
	DeleteRegKey HKLM "SYSTEM\CurrentControlSet\Services\BDKVRTP"
	
	!insertmacro WRITE_LOG_MSG "delete server reg $\n"
	
	#删除图标
	${if} $lastdir != $INSTDIR 
		#删除图标
		Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk"
		Delete "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" 
		RMDir /r  "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}"
		Delete "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" 
		
		!insertmacro WRITE_LOG_MSG "delete desktop icon $\n"
		
		${if} $lastdir != "\"
			#删除bd0001.dll
			KVInstallHelper::RenameAndDeleteFile /NOUNLOAD "$lastdir\bd0001.dll"
			!insertmacro WRITE_LOG_MSG "rename and delete bd0001.dll $\n"
			
			#大包存在则拷贝到新路径
			IfFileExists "$lastdir\kav\bases\klava\log0" 0 +3
				SetOutPath $INSTDIR\kav\bases
				CopyFiles /SILENT "$lastdir\kav\bases\*.*" "$INSTDIR\kav\bases"
			
			#删除上次安装文件
			RMDir /r $lastdir
		${endif}
		
		!insertmacro WRITE_LOG_MSG "delete lastdir $lastdir $\n"
	${else}
		#删除bd0001.dll
		KVInstallHelper::RenameAndDeleteFile /NOUNLOAD "$lastdir\bd0001.dll"
		!insertmacro WRITE_LOG_MSG "rename and delete bd0001.dll $\n"
	${endif}

	#----------------------------删除老版本结束---------------------------------

	#----------------------------卡巴驱动安装开始---------------------------------	   
	!insertmacro WRITE_LOG_MSG "install dir: $INSTDIR $\n"
	
	#拷贝卡巴相关文件
	SetOutPath "$INSTDIR\kav"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\kav\*.*" "$INSTDIR\kav"
	SetOutPath "$INSTDIR\kav\loc\common"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\kav\loc\common\*.*" "$INSTDIR\kav\loc\common"
	SetOutPath "$INSTDIR\kav\x64"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\kav\x64\*.*" "$INSTDIR\kav\x64"
	
	#大包不存在则拷贝，存在不拷贝
	IfFileExists "$INSTDIR\kav\bases\klava\log0" +3 0
		SetOutPath "$INSTDIR\kav\bases"
		File /r  "..\..\KVOutput\BinRelease\kav\bases\*.*"
	
	!insertmacro WRITE_LOG_MSG "copy kav $\n"
	
	#删除卡巴数据，避免license过期，ALLUSER路径需动态取
	RMDir /r  "$AllUsersProfileDir\Kaspersky SDK\*.dat"
	
	!insertmacro WRITE_LOG_MSG "delete kav data $\n"
	
	#拷贝卡巴sw2文件
	KVInstallHelper::GetSysTempDir /NOUNLOAD
	Pop $R0
	StrCpy $TempDir $R0
	StrCpy $TempDir "$TempDir\SDK8"
	SetOutPath $TempDir
	!insertmacro File2 "sw2.xms" "..\..\KVOutput\BinRelease\kav\bases\sw2.xms" "$TempDir"

	!insertmacro WRITE_LOG_MSG "TempDir: $TempDir $\n"
	!insertmacro WRITE_LOG_MSG "copy kav sw2.xms $\n"
	
	#拷贝卡巴斯基驱动安装文件
	SetOutPath "$INSTDIR\kavdrivers"
	File /r "..\..\KVOutput\BinRelease\kavdrivers\*.*"
	
	!insertmacro WRITE_LOG_MSG "copy kavdrivers $\n"
    
	#win7安装弹出不兼容的问题
	WriteRegDWORD HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted"  "$INSTDIR\kavdrivers\udinstaller32.exe" 0x1 
	
	#安装卡巴斯基驱动，后面改为调用DriverManager
	KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"   "--install "  "klif"
	#KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"   "--install "  "klim"
    #KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"   "--install "  "kl1"
    #KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"   "--install "  "kneps"
    #KVInstallHelper::InstallKaperskyDriver /NOUNLOAD "$INSTDIR\kavdrivers\"   "--install "  "kltdi"
	
	!insertmacro WRITE_LOG_MSG "isntall kav drivers $\n"
	
	#----------------------------驱动安装结束---------------------------------
	
	#----------------------------拷贝文件开始---------------------------------
	
	!insertmacro WRITE_LOG_MSG "start file copy... $\n"
	
	#拷贝插件
	SetOutPath "$INSTDIR\plugins"
	!insertmacro File2 "*.xml" "..\..\KVOutput\BinRelease\plugins\*.xml" "$INSTDIR\plugins"

	SetOutPath "$INSTDIR\plugins\bdkv"
	!insertmacro File2 "*.dll" "..\..\KVOutput\BinRelease\plugins\bdkv\*.dll" "$INSTDIR\plugins\bdkv"
	!insertmacro File2 "*.xml" "..\..\KVOutput\BinRelease\plugins\bdkv\*.xml" "$INSTDIR\plugins\bdkv"

	SetOutPath "$INSTDIR\plugins\bdkvtrayplugins"
	!insertmacro File2 "*.dll" "..\..\KVOutput\BinRelease\plugins\bdkvtrayplugins\*.dll" "$INSTDIR\plugins\bdkvtrayplugins"
	!insertmacro File2 "*.xml" "..\..\KVOutput\BinRelease\plugins\bdkvtrayplugins\*.xml" "$INSTDIR\plugins\bdkvtrayplugins"
  
	SetOutPath "$INSTDIR\plugins\bdkvrtpplugins"
	!insertmacro File2 "*.xml" "..\..\KVOutput\BinRelease\plugins\bdkvrtpplugins\*.xml" "$INSTDIR\plugins\bdkvrtpplugins"
	!insertmacro File2 "*.dll" "..\..\KVOutput\BinRelease\plugins\bdkvrtpplugins\*.dll" "$INSTDIR\plugins\bdkvrtpplugins"
  
	#拷贝杀毒模块 
	SetOutPath "$INSTDIR\bdmantivirus"
	#!insertmacro File2 "*.dat" "..\..\KVOutput\BinRelease\bdmantivirus\*.dat" "$INSTDIR\bdmantivirus"
	#!insertmacro File2 "*.esm" "..\..\KVOutput\BinRelease\bdmantivirus\*.esm" "$INSTDIR\bdmantivirus"
	#!insertmacro File2 "*.key" "..\..\KVOutput\BinRelease\bdmantivirus\*.key" "$INSTDIR\bdmantivirus"
	#!insertmacro File2 "*.kli" "..\..\KVOutput\BinRelease\bdmantivirus\*.kli" "$INSTDIR\bdmantivirus"
	#!insertmacro File2 "*.pbv" "..\..\KVOutput\BinRelease\bdmantivirus\*.pbv" "$INSTDIR\bdmantivirus"
	!insertmacro File2 "*.xml" "..\..\KVOutput\BinRelease\bdmantivirus\*.xml" "$INSTDIR\bdmantivirus"
	!insertmacro File2 "*.dll" "..\..\KVOutput\BinRelease\bdmantivirus\*.dll" "$INSTDIR\bdmantivirus"
	
	SetOutPath "$INSTDIR\bdmantivirus\kavupdate"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\bdmantivirus\kavupdate\*.*" "$INSTDIR\bdmantivirus\kavupdate"  
	
	#拷贝修复模块
	#SetOutPath "$INSTDIR\bdmsysrepair"
	#!insertmacro File2 "*.dll" "..\..\KVOutput\BinRelease\bdmsysrepair\*.dll" "$INSTDIR\bdmsysrepair"

	#拷贝皮肤
	SetOutPath "$INSTDIR\Skins\Default"
	File /r "..\..\KVOutput\BinRelease\Skins\Default\*.rdb"
   
	#atl库
	SetOutPath "$INSTDIR\Microsoft.VC80.ATL"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.ATL\*.*"
	SetOutPath "$INSTDIR\plugins\bdkv\Microsoft.VC80.ATL"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.ATL\*.*"
	SetOutPath "$INSTDIR\plugins\bdkvtrayplugins\Microsoft.VC80.ATL"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.ATL\*.*"
	SetOutPath "$INSTDIR\plugins\bdkvrtpplugins\Microsoft.VC80.ATL"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.ATL\*.*"
	SetOutPath "$INSTDIR\bdmantivirus\Microsoft.VC80.ATL"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.ATL\*.*"

	#crt库
	SetOutPath "$INSTDIR\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.CRT\*.*"
	SetOutPath "$INSTDIR\plugins\bdkv\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.CRT\*.*"
	SetOutPath "$INSTDIR\plugins\bdkvtrayplugins\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.CRT\*.*"
	SetOutPath "$INSTDIR\plugins\bdkvrtpplugins\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.CRT\*.*"
	SetOutPath "$INSTDIR\bdmantivirus\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\Microsoft.VC80.CRT\*.*"
	SetOutPath "$INSTDIR\bdmantivirus\kavupdate\Microsoft.VC80.CRT"
	File /r "..\..\KVOutput\BinRelease\bdmantivirus\kavupdate\Microsoft.VC80.CRT\*.*"

	SetOutPath "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\*.xml" "$INSTDIR"
	#!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\*.dat" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\*.ini" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\*.ico" "$INSTDIR"
	
	#单独拷贝EXE
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\${MAINFRAME_PROCESS_NAME}" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\${SERVER_PROCESS_NAME}" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\${TRAY_PROCESS_NAME}" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\${UPDATE_PROCESS_NAME}" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\${BUGREPORT_PROCESS_NAME}" "$INSTDIR"
	
	#单独拷贝DLL，有可能被占用
	#!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\AVCommon.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\bd0001.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDKVLogs.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDKVMainFrame.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDLogicUtils.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMAVE.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMDownload.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMEvents.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMNet.dll" "$INSTDIR"
	#!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMNetPlugin.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMPatchAgent.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMReport.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMSkin.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDMUpdate.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\DriverManager.dll" "$INSTDIR"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\rfp_api.dll" "$INSTDIR"
	#!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\BDShellExt.dll" "$INSTDIR"
	#最好放专门目录
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\*.sys" "$INSTDIR"
  	
	#创建卸载文件
	WriteUninstaller "$INSTDIR\uninst.exe"

	#拷贝配置到alluser的appdata目录
	SetOutPath "$AppDir\${ALL_USER_DATA_PATH}\Config"
	!insertmacro File2 "*.*" "..\..\KVOutput\BinRelease\Config\*.dat" "$AppDir\${ALL_USER_DATA_PATH}\Config"
   
	!insertmacro WRITE_LOG_MSG "end file copy... $\n"
	
   	#----------------------------拷贝文件结束---------------------------------

	#----------------------------安装自己驱动开始---------------------------------

	#拷贝安装自己的驱动  **注意务必要放到DriverManager.dll安装完后**
	SetOutPath "$INSTDIR\drivers"
	!insertmacro File2 "*.sys" "..\..\KVOutput\BinRelease\drivers\*.sys" "$INSTDIR\drivers"
	KVInstallHelper::InstallDrivers /NOUNLOAD "$INSTDIR\drivermanager.dll" "$INSTDIR\drivers" "$INSTDIR\drivers"
	Pop $R0
	${if} $R0 == "0"
		KVInstallHelper::ReportInstallData /NOUNLOAD "$INSTDIR\BDLogicUtils.dll" "$InstallMode" "$strOldVersion" "$varIsSilence" 1 "$SupplyID"
	${endif}
	
	
	!insertmacro WRITE_LOG_MSG "install own driver $\n"
	
	#安装服务
	ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -i'
	
	!insertmacro WRITE_LOG_MSG "install server $\n"

	#启动服务
	ExecWait '"$INSTDIR\${SERVER_PROCESS_NAME}" -s'

	!insertmacro WRITE_LOG_MSG "start server $\n"
	
	#安装下载组件
	#ExecWait '"$INSTDIR\BDDownloader.exe"'
	#Delete "$INSTDIR\BDDownloader.exe"
	
	#注册shell右键菜单
	#ExecWait '"RegSvr32.exe" /s "$INSTDIR\BDShellExt.dll"'

	
	#----------------------------安装自己驱动结束---------------------------------

	#----------------------------创建图标开始---------------------------------
	#创建快捷方式要在文件都copy完后再建立，防止桌面出现失效的图标
	
	#创建开始菜单图标
	CreateDirectory "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}"
	CreateShortCut "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" "$INSTDIR\${MAINFRAME_PROCESS_NAME}" "" "" 2 SW_SHOWNORMAL "" "${MACRO_SHORTCUT_DESCRIPTION}"
	CreateShortCut "$SmProgramsDir\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk" "$INSTDIR\uninst.exe"
    
	#添加桌面图标
	${if} $isDesktopLink != 2 
        CreateShortCut "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" "$INSTDIR\${MAINFRAME_PROCESS_NAME}" "" "" 2 SW_SHOWNORMAL "" "${MACRO_SHORTCUT_DESCRIPTION}"
	${endif}
	
	!insertmacro WRITE_LOG_MSG "create icon $\n"
	
	#----------------------------创建图标结束---------------------------------

	#----------------------------写新的注册表开始---------------------------------
	
	#将安装日期写入注册表
	SetOverwrite try  #不覆盖
	System::Alloc 16
	System::Call "kernel32::GetLocalTime(isR0)"
	System::Call "*$R0(&i2.R1,&i2.R2,&i2,&i2.R4)"
	System::Free $R0
	WriteRegStr HKLM "${HKLM_REG_PATH}" "InstallDate" "$R1-$R2-$R4"

	#病毒库时间
	ReadRegStr $R0 HKLM "${HKLM_REG_PATH}" "VirusTime"
	StrCmp $R0 "" 0 +2
		WriteRegStr HKLM "${HKLM_REG_PATH}" "VirusTime" "${MACRO_ANTIVIRUS_UPDATETIME}"

	##写注册表
	#卸载信息
	WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${MACRO_PRODUCTNAME}${BUILD_VERSION}"
	WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
	WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\app.ico"
	WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${BUILD_BASELINE}"
	WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${MACRO_COMPANYNAME}"
	#安装路径,版本信息
    WriteRegStr HKLM "${HKLM_REG_PATH}" "Version" "${BUILD_BASELINE}"
    WriteRegStr HKLM "${HKLM_REG_PATH}" "InstallDir" "$strInstallDir" #这里写入不带版本号
    WriteRegStr HKLM "${HKLM_REG_PATH}" "INSTLANG" "${LANG_SIMPCHINESE}"
    WriteRegStr HKLM "${HKLM_REG_PATH}" "SupplyID" "$SupplyID"
	
	!insertmacro WRITE_LOG_MSG "write reg $\n"
	!insertmacro WRITE_LOG_MSG "Version ${BUILD_BASELINE} $\n"
	!insertmacro WRITE_LOG_MSG "InstallDir $INSTDIR $\n"
	!insertmacro WRITE_LOG_MSG "SupplyID $SupplyID $\n"
	
	#----------------------------写新的注册表结束---------------------------------

	#----------------------------数据上报开始---------------------------------
	
	#记录完成时间
    KVInstallHelper::RecordEndTime /NOUNLOAD

	#$InstallMode安装模式
	#$strOldVersion老版本号，需解析
	#$varIsSilence静默安装
	#0这里均表示成功
	#$SupplyID渠道ID
	KVInstallHelper::ReportInstallData /NOUNLOAD "$INSTDIR\BDLogicUtils.dll" "$InstallMode" "$strOldVersion" "$varIsSilence" 0 "$SupplyID"

	!insertmacro WRITE_LOG_MSG "data report $\n"
	#----------------------------数据上报结束---------------------------------

	#安装进度完成
	!insertmacro POST_MSG_TO_HANDLWND $varWndHandle 100 0

SectionEnd


;安装前执行
${StrTok}
${Replace}
!insertmacro GetOptions
!insertmacro GetParameters
Function .onInit
	#判断是否静默安装
	Strcpy $varIsSilence "1"
	IfSilent +2
	Strcpy $varIsSilence "0"
	
	InitPluginsDir

	#解析参数
	${GetParameters} $R0
	${GetOptions} $R0 "/handle=" $varWndHandle
	${GetOptions} $R0 "/supplyid="  $SupplyID
	${GetOptions} $R0 "/installmode=" $InstallMode
	
	!insertmacro INIT_LOG_MSG "${INSTALL_LOG_FILE}"
	!insertmacro WRITE_LOG_MSG "start install section $\n"
		
	#判断安装版本
  	${StrTok} $0 "${BUILD_BASELINE}" "." "3" "1" 
	Pop $R0
	ReadRegStr $R0 HKLM "${HKLM_REG_PATH}" "Version"
	StrCpy $1 $R0
	${StrTok} $2 $1 "." "3" "1" 
	IntCmpU $0 $2 PROMPT_SAME_VERSION PROMPT_OLD_VERSION PROMPT_NEWER_VERSION
	
	#已经安装了更高的版本
	PROMPT_OLD_VERSION:
	${if} $varIsSilence == "0"
		Goto PROMPT_NEWER_VERSION
	${else}
		MessageBox MB_ICONQUESTION|MB_TOPMOST|MB_OKCANCEL|MB_DEFBUTTON2  "${MACRO_MESSAGEOLDVERSIONNOQUERY}"  IDOK PROMPT_NEWER_VERSION IDCANCEL 0
		Quit
	${endif}
 
	#已经安装了相同的版本
	PROMPT_SAME_VERSION:
 
	#已经安装的是旧版本,现在安装的版本高
	PROMPT_NEWER_VERSION:
	
	Call Init_Copy
FunctionEnd

Function .onInstSuccess
 Exec  '"$INSTDIR\${MAINFRAME_PROCESS_NAME}"'
FunctionEnd


