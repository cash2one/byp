;--------------------------------
# Script writen by yihongzhang (@Baidu) 
# date: 2012.2.22
;--------------------------------

!addincludedir "include"
!include "buildline.nsi"
#预定义一些常量
!define MACRO_VERSIONFIX  ""
!define RELEASE_VERSION  "185"
!define SC_CLOSE 0xF060

!define BUILD_VERSION "1.0"
!define BUILD_TIME  "2013-03-29 12:36:36"
!define BUILD_BASELINE "${BUILD_VERSION}.${BUILD_LINE}.${RELEASE_VERSION}" 

#产品信息
!define PRODUCT_VERSION "${BUILD_VERSION}";产品版本
!define PRODUCT_NAME "BDM";产品名称
!define PRODUCT_PUBLISHER "BAIDU Inc.";产品发布者
!define PRODUCT_FILE_DESCRIPTION "BDM Setup"
!define PRODUCT_LEGAL_COPYRIGHT "Copyright(C) 2012 - 2012 Baidu Inc. All Rights Reserved.";产品所有权

!define MUI_ICON "res\setup.ico";安装界面图标
!define MUI_UNICON "res\uninstall.ico";卸载界面图标
;提升权限
RequestExecutionLevel  admin
;--------------------------------

#包含文件
!include "MUI.nsh";引入新式用户界面函数库
!include "UB_YinFunEx.nsh"
!include "Filefunc.nsh"

#声明变量
var debugpath
var DefaultDir
var SupplyID

#定义函数(初始化插件目录)
Function Init_Copy
  InitPluginsDir
                SetOutPath "$PLUGINSDIR\res"
                File /oname=$PLUGINSDIR\res\nsis_skin.gt    "res\nsis_skin.gt"  
                SetOutPath "$INSTDIR\${BUILD_BASELINE}" 
                StrCpy $DefaultDir "$INSTDIR\${BUILD_BASELINE}"    	
FunctionEnd
;--------------------------------
;Pages

!define MUI_ABORTWARNING; #安装未完成，而用户要退出时显示提示。
#welcome
#!insertmacro MUI_PAGE_WELCOME
!define MUI_CUSTOMFUNCTION_GUIINIT gui_init
Function gui_init
  InstallHelper::InitSkin /NOUNLOAD "$PLUGINSDIR\res" "\nsis_skin.gt" "${PRODUCT_NAME}" "${BUILD_VERSION}"
FunctionEnd
#license
var TestWnd
Function  license_page_pre
FunctionEnd
Function  license_page_show

   strcpy  $TestWnd 0
   !insertmacro Get_Ctrl_Handl 1040 1 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1006 1 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1256 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1028 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1034 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1035 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1037 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1038 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1046 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1000 1 $TestWnd
    InstallHelper::MoveWindowRect /NOUNLOAD $TestWnd 27 64 494 263
   !insertmacro Get_Ctrl_Handl 1000 1 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 2 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 3 0 $TestWnd
   ShowWindow $TestWnd ${SW_HIDE}

   FindWindow $0 "#32770" "" $HWNDPARENT
   InstallHelper::CreateWelcomePage /NOUNLOAD $0
   
   ;重设一遍安装路径，否则在点击自定义返回后，会有错误
   StrCpy $INSTDIR "$PROGRAMFILES\Baidu\BDM"
   
FunctionEnd

Function  license_page_leave
FunctionEnd
!define MUI_PAGE_CUSTOMFUNCTION_PRE   license_page_pre
!define MUI_PAGE_CUSTOMFUNCTION_SHOW  license_page_show
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE license_page_leave
!insertmacro MUI_PAGE_LICENSE "include\license.txt"
#directory 
;!insertmacro MUI_PAGE_DIRECTORY
PageEx directory
Caption " "
DirVerify leave
  PageCallbacks directory_page_pre directory_page_show directory_page_leave
PageExEnd


#install
LangString Install_Section ${LANG_ENGLISH} "UB Install"
;Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Install} $(Install_Section)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
!define MUI_PAGE_CUSTOMFUNCTION_PRE  instfiles_page_pre
!define MUI_PAGE_CUSTOMFUNCTION_SHOW  instfiles_page_show
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE instfiles_page_leave
!insertmacro MUI_PAGE_INSTFILES


# Finish page
#!define MUI_FINISHPAGE_TITLE ${MACRO_MSGFINISHPAGETITLE}

#!define MUI_FINISHPAGE_BUTTON ${MACRO_TEXTFINISH}

#!define MUI_FINISHPAGE_RUN
#!define MUI_FINISHPAGE_RUN_FUNCTION SetDeafult

#!define MUI_FINISHPAGE_SHOWREADME
#!define MUI_FINISHPAGE_SHOWREADME_FUNCTION  RunBrowser

#!define MUI_PAGE_CUSTOMFUNCTION_PRE   finish_page_pre
#!define MUI_PAGE_CUSTOMFUNCTION_SHOW  finish_page_show
#!define MUI_PAGE_CUSTOMFUNCTION_LEAVE finish_page_leave

#!define MUI_FINISHPAGE_TEXT_REBOOT ${MACRO_TEXTQUERYREBOOT}
#!define MUI_FINISHPAGE_TEXT_REBOOTNOW ${MACRO_TEXTREBOOTNOW}
#!define MUI_FINISHPAGE_TEXT_REBOOTLATER ${MACRO_TEXTREBOOTLATER}
#!insertmacro MUI_PAGE_FINISH
Page custom finish_page_show



;!insertmacro MUI_UNPAGE_WELCOME

;!define MUI_PAGE_CUSTOMFUNCTION_SHOW  un.confirm_page_show
;!define MUI_PAGE_CUSTOMFUNCTION_LEAVE  un.confirm_page_leave
;!insertmacro MUI_UNPAGE_CONFIRM
UninstPage custom  un.confirm_page_show un.confirm_page_leave 
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

var isDesktopLink
var isSetDefault
var isRunAfterInstall
var isSendData
var isTaskbarLink

!include "UB_Language.nsh"
!include "UB_install.nsi"
!include "UB_page.nsi"
!include "StrFuncEx.nsh"
!include  "UseFulLib.nsh"
;--------------------------------
;General

;Default installation folder
InstallDir "$PROGRAMFILES\Baidu\BDM"

;Get installation folder from registry if available
InstallDirRegKey HKCU "Software\Baidu\BDM" ""

;Name and file
Name "${MACRO_PRODUCTNAME}${PRODUCT_VERSION}${MACRO_VERSIONFIX}"
OutFile "..\setup\BDM_Setup_${BUILD_BASELINE}.exe"

;--------------------------------
;init 判断版本 或者一些其他工作


${StrTok}
;${StrStrAdv}
${Replace}
!insertmacro GetOptions
!insertmacro GetParameters

Function .onInit
 Strcpy $varIsSilence  ${RUM_SILENCE}
 IfSilent +2
   Strcpy $varIsSilence  ${RUM_SILENCE}+1
InitPluginsDir
strcpy $debugpath ""
${GetParameters} $R0

${GetOptions} $R0 "/handle=" $varWndHandle
${GetOptions} $R0 "/debugpath=" $debugpath
${GetOptions} $R0 "/supplyid="  $SupplyID


  ${StrTok} $0 "${BUILD_BASELINE}" "." "3" "1" 
  Pop $R0
  ReadRegStr $R0 HKLM "Software\Baidu\BDM" "Version"
  StrCpy $1 $R0
  ${StrTok} $2 $1 "." "3" "1" 
  IntCmpU $0 $2 PROMPT_SAME_VERSION 0 PROMPT_NEWER_VERSION
  
  #安装的版本比现在的版本老
 
  ${if} $varIsSilence == ${RUM_SILENCE}
    Goto PROMPT_NEWER_VERSION
    ${if} $varRunMode == ${RUM_MODE_UNIFORM}
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 7
      MessageBox MB_OK|MB_TOPMOST "${MACRO_MESSAGEOLDVERSIONNOQUERY}"
      Quit
    ${else}
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 7
      Quit
    ${endif}
  ${else}
    MessageBox MB_ICONINFORMATION|MB_TOPMOST|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEOLDVERSION}"  IDOK PROMPT_NEWER_VERSION
  ${endif}
  Quit
 PROMPT_SAME_VERSION:
  ${if} $varIsSilence == ${RUM_SILENCE}
     Goto PROMPT_NEWER_VERSION
    ${if} $varRunMode == ${RUM_MODE_UNIFORM}
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 7
      MessageBox MB_OK|MB_TOPMOST "${MACRO_MESSAGEOLDVERSIONNOQUERY_SAME}"
      Quit
    ${else}
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 7
      Quit
    ${endif}
  ${else}
    MessageBox MB_ICONINFORMATION|MB_TOPMOST|MB_OKCANCEL|MB_DEFBUTTON2 "${MACRO_MESSAGEOLDVERSION_SAME}"  IDOK PROMPT_NEWER_VERSION
  ${endif}
  Quit
 PROMPT_NEWER_VERSION:
Call Init_Copy
FunctionEnd




  




