

!addincludedir "include"
!include "buildline.nsi"

; 安装程序初始定义常量
!define PRODUCT_NAME "百度杀毒-在线安装"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "百度, Inc."
!define PRODUCT_WEB_SITE "http://www.baidu.com"

!define BUILD_VERSION "1.0"
!define BUILD_TIME  "2013-03-19 03:13:55"
!define RELEASE_VERSION "1.0"
!define BUILD_BASELINE "${BUILD_VERSION}.${BUILD_LINE}.${RELEASE_VERSION}" 

SetCompressor lzma

; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
;!define MUI_ABORTWARNING
;用户界面初始化函数
!define MUI_CUSTOMFUNCTION_GUIINIT gui_init
!define MUI_ICON "res\setup.ico"
; 安装界面包含的语言设置
;!insertmacro MUI_LANGUAGE "SimpChinese"


;提升权限
RequestExecutionLevel  admin

;==============================================只有安装  没有卸载===================================


Page directory directory_page_pre directory_page_show directory_page_leave
Page instfiles  instfiles_page_pre instfiles_page_show instfiles_page_leave

;==================================================================================================
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\KVNetSetUp\KVNetSetup.exe"
InstallDir "$PROGRAMFILES\Baidu\BDKV" ;默认安装目录
InstallDirRegKey HKLM "Software\Baidu\BDKV" "InstallDir"
ShowInstDetails hide

Section "MainSection" SEC01
SectionEnd

Section -Post
SectionEnd

!include "KV_Language.nsh"
Function Init_Copy
  InitPluginsDir
			SetOutPath "$PLUGINSDIR\res"       
			File /oname=$PLUGINSDIR\res\onlineWnd.zip    	"res\onlineWnd.zip"
			SetOutPath "$PLUGINSDIR"
			File /oname=$PLUGINSDIR\BDMSkin.dll    			"res\BDMSkin.dll"	
			File /oname=$PLUGINSDIR\config.ini    			"res\config.ini"				
FunctionEnd

Function .onInit
  Call Init_Copy
FunctionEnd


Function gui_init
   KVNetInstallHelpler::GetXmlPath /NOUNLOAD "$PLUGINSDIR\res" "\onlineWnd.zip"  "${PRODUCT_NAME}" "${BUILD_VERSION}" 1 "config.ini"
FunctionEnd


Function directory_page_pre
  
FunctionEnd

Function directory_page_show
	FindWindow $0 "#32770" "" $HWNDPARENT
	KVNetInstallHelpler::CreateOnLineWnd /NOUNLOAD $0 
FunctionEnd

Function directory_page_leave
  #判断安装路径合法性
GetInstDirError $0
  ${Switch} $0
    ${Case} 0
      ${Break}
    ${Case} 1
      ;!insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 3
      ;MessageBox MB_OK|MB_ICONQUESTION ${MACRO_INVALIDDIRECTORY}
	  KVNetInstallHelpler::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
      Abort
      ${Break}
    ${Case} 2
      ;!insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 1
      ;MessageBox MB_OK|MB_ICONSTOP ${MACRO_NOENOUGHFREESPACE}
	  KVNetInstallHelpler::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
      Abort
      ${Break}
  ${EndSwitch}
  
  #判定路径只读
  KVNetInstallHelpler::ValidateInstDir /NOUNLOAD
pop $R0
${if} $R0 == "0"
     KVNetInstallHelpler::KVMessageBox /NOUNLOAD 0 0 ${MACRO_MESSAGEBOX_BTN_OK}  ${MACRO_DIRECTORY_ERROR}
     Abort
${endif}
FunctionEnd

Function instfiles_page_pre
  
FunctionEnd

Function instfiles_page_show
  FindWindow $0 "#32770" "" $HWNDPARENT
  ;KVNetInstallHelpler::GetWndHandle /NOUNLOAD $0
  KVNetInstallHelpler::GoNext /NOUNLOAD $0
    Abort
FunctionEnd

Function instfiles_page_leave
   Abort
FunctionEnd

