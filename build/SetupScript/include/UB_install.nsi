#  主要的安装逻辑



!include "Filefunc.nsh"

!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${MACRO_PRODUCTNAME}"

!macro File2 FileName SrcFilePath DesOutPath
   SetOutPath "$PLUGINSDIR"
   File ${SrcFilePath}
   CopyFiles /SILENT /FILESONLY "$PLUGINSDIR\${FileName}" "${DesOutPath}"
   Call IncFileCopyCount
   Call SendFileCopyProgress
   Delete "$PLUGINSDIR\${FileName}"
   SetOutPath ${DesOutPath}
!macroend

var tmpdir
var lastdir
var installpackname
var AppDir
!insertmacro GetExeName

Section Install
    #读取老版本路径
    StrCpy $strOldInstDir ""
    StrCpy $strOldVersion ""
    ReadRegStr $strOldInstDir HKLM "Software\Baidu\BDM" "InstallDir"
    ReadRegStr $strOldVersion HKLM "Software\Baidu\BDM" "Version"
    StrCpy $lastdir "$strOldInstDir\$strOldVersion"

    #写注册表安装路径之类的
    WriteRegStr HKLM "Software\Baidu\BDM" "Version" "${BUILD_BASELINE}"
    WriteRegStr HKLM "Software\Baidu\BDM" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\Baidu\BDM" "INSTLANG" "${LANG_SIMPCHINESE}"
    WriteRegDword HKCU "Software\Baidu\BDM\Launch" "Learned" 0x1
    WriteRegStr HKLM "Software\Baidu\BDM" "SupplyID" "$SupplyID"

    #IE精灵注册表项
    WriteRegStr HKCU "Software\Baidu\BDManager\AppBooster" "iexplorer.exe" "$INSTDIR\iexplore.exe.xml"

    #进行文件copy
    Strcpy $tmpdir $INSTDIR
    ;Store installation folder
    WriteRegStr HKCU "Software\Baidu\BDM" "" "$INSTDIR"

    StrCpy $strInstallDir $INSTDIR
    StrCpy $INSTDIR "$strInstallDir\${BUILD_BASELINE}"
   
    Call ClearFileCopyCount
    InstallHelper::GetUBAppData /NOUNLOAD "$PLUGINSDIR"
    Pop $R0
    StrCpy $AppDir $R0
    ${GetExeName} $R0
    WriteRegDWORD HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted"  "$R0" 0x1 



    RMDir /r    "$AppDir\Skin"


    ReadRegStr $SmDesktopDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Desktop"
    ReadRegStr $SmProgramsDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Programs"
  
  
    ${if} $lastdir != $INSTDIR 
        ;InstallDR::RemoveFirewall "$lastdir"
        Delete "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk"
        Delete "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" 
        RMDir /r  "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}"
        Delete "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" 
        SetOutPath $INSTDIR
        RMDir /r  $lastdir
    ${endif}
  
    ${if} $debugpath != ""
        StrCpy  $INSTDIR  $debugpath 
    ${endif}
	
    StrCpy $R1 0

    CreateDirectory "$SmProgramsDir\${MACRO_PRODUCTGROUP}"
    CreateDirectory "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}"
    CreateShortCut "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" "$INSTDIR\BDMgr.exe"
    CreateShortCut "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk" "$INSTDIR\uninst.exe"
  
    ${if} $isTaskbarLink != 2 
        Exec  '"$PLUGINSDIR\res\TaskbarHelper.exe" A $SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk'
    ${endif} 
      
  Call ClearFileCopyCount
  SetOutPath "$INSTDIR"
  SetOverwrite try
  
  ;不覆盖的拷贝数据库
   SetOverwrite try

   #插件
   SetOutPath "$INSTDIR\plugins"
   File /r "..\..\Output\BinRelease\plugins\*.*"
   
   #皮肤
   SetOutPath "$INSTDIR\Skins\Default"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\Skins\Default\*.*" "$INSTDIR\Skins\Default"
   
   #系统优化
   SetOutPath "$INSTDIR\FTSOManager"
   File /r "..\..\Output\BinRelease\FTSOManager\*.*"

   #软件管理模块
   SetOutPath "$INSTDIR\FTSWManager"
   File /r "..\..\Output\BinRelease\FTSWManager\*.*"

   #atl库
   SetOutPath "$INSTDIR\Microsoft.VC80.ATL"
   File /r "..\..\Output\BinRelease\Microsoft.VC80.ATL\*.*"
   
   #crt库
   SetOutPath "$INSTDIR\Microsoft.VC80.CRT"
   File /r "..\..\Output\BinRelease\Microsoft.VC80.CRT\*.*"

   SetOutPath "$INSTDIR"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.exe" "$INSTDIR"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.dll" "$INSTDIR"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.xml" "$INSTDIR"
   
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.dat" "$INSTDIR"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.rad" "$INSTDIR"
   !insertmacro File2 "*.*" "..\..\Output\BinRelease\*.ini" "$INSTDIR"

   #IE精灵插件注册
   #Exec '"RegSvr32.exe" /s "$INSTDIR\bho.dll"'
   #WSInstallPlugin::WsInstallAll /NOUNLOAD "$INSTDIR\iexplore.exe.xml" "1" "$INSTDIR\AdBlockerWeb.dll" "ChinaList" "$INSTDIR\adblock_easy.rad" "$INSTDIR\adblock_easy.pad" "" "1" "1"

   	#安装下载组件
	ExecWait '"$INSTDIR\BDDownloader.exe"'
	Delete "$INSTDIR\BDDownloader.exe"

  ;SetOverwrite try
  
  
  
  

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"

  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${MACRO_PRODUCTNAME}${BUILD_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\app.ico"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${BUILD_BASELINE}"
  WriteRegStr HKLM  "${PRODUCT_UNINST_KEY}" "Publisher" "baidu Company"

  #增加桌面图标
  ${if} $isDesktopLink != 2 
    CreateShortCut "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" "$INSTDIR\BDMgr.exe"   
  ${endif}
  

  !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 100 0

SectionEnd


;--------------------------------
;Uninstaller Section

!include "nsDialogs.nsh"

var Dialog
var CheckBoxClearData
var CheckStateClearData

UninstallCaption "${MACRO_LNKUNINSTALL}${BUILD_VERSION}"

Section "Uninstall"

  
 RMDir /r  $AppDir
 RMDir /r  $INSTDIR
 WriteRegDWORD HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted"  "$INSTDIR\uninst.exe" 0x1 
 ReadRegStr $SmDesktopDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Desktop"
 ReadRegStr $SmProgramsDir HKLM "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" "Common Programs"
 DeleteRegKey  HKCU "SOFTWARE\Baidu\BDM"
 Delete "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUNINSTALL}.lnk"
 Delete "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}\${MACRO_LNKUBORWSER}.lnk" 
 RMDir /r  "$SmProgramsDir\${MACRO_PRODUCTGROUP}\${MACRO_PRODUCT_FOLDER_NAME}"
 Delete "$SmDesktopDir\${MACRO_LNKUBORWSER}.lnk" 
 DeleteRegKey  HKLM "SOFTWARE\Baidu\BDM" 
 DeleteRegKey  HKLM "${PRODUCT_UNINST_KEY}"
 RMDir /r  $INSTDIR
SectionEnd

#增加卸载前判断（是否卸载及当前程序实例是否在运行）
Function un.onInit
	MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "${MACRO_MESSAGEUNINSTALL}" IDYES +2
	Quit
    StrCpy $0 0
	FindWindow $0 "BDMTrayClass"
	IntCmp $0 0  no_run no_run is_run
	is_run:
     MessageBox MB_ICONQUESTION|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEUNINSTALL_WARNING}" IDOK +2
     Quit
	 FindWindow $1 "BDMMainFrame"
	 SendMessage $0 ${WM_CLOSE} 0 0
	 SendMessage $1 ${WM_CLOSE} 0 0
	no_run: 
   FunctionEnd
   

Function  un.confirm_page_show
	Strcpy $LANGUAGE 2052
	nsDialogs::Create /NOUNLOAD 1018
	Pop $Dialog
	!insertmacro MUI_HEADER_TEXT "${MACRO_LNKUNINSTALL}" "${MACRO_LNKUNINSTALL}${BUILD_VERSION}"
	${NSD_CreateLabel} 0u 10u 100% 20u "${MACRO_LNKUNINSTALL_TIPS}"
	Pop $0
	${NSD_CreateLabel} 0u 54u 15% 15u "${MACRO_UNINSTALL_DIRTXT}"
		Pop $0
		nsDialogs::CreateControl /NOUNLOAD "EDIT" ${__NSD_Text_STYLE}|${WS_DISABLED} ${__NSD_Text_EXSTYLE} 15% 50u 75% 15u $INSTDIR
		Pop $0
	${NSD_CreateCheckbox} 0u 88u 100% 20u "${MACRO_UNINSTALL_APP_CHECK}"
	Pop $CheckBoxClearData
	
	nsDialogs::Show	
FunctionEnd

Function  un.confirm_page_leave
	;${NSD_GetState} $CheckBoxClearData $CheckStateClearData
              ; ExecWait  '"$TMPDIR\UBrowser.exe" -module=UBrowserAssistant.dll -uninstall -result=1'
FunctionEnd
