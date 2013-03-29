

!addincludedir "include"
!include "buildline.nsi"

; ��װ�����ʼ���峣��
!define PRODUCT_NAME "�ٶ�ɱ��-���߰�װ"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "�ٶ�, Inc."
!define PRODUCT_WEB_SITE "http://www.baidu.com"

!define BUILD_VERSION "1.0"
!define BUILD_TIME  "2013-03-19 03:13:55"
!define RELEASE_VERSION "1.0"
!define BUILD_BASELINE "${BUILD_VERSION}.${BUILD_LINE}.${RELEASE_VERSION}" 

SetCompressor lzma

; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
;!define MUI_ABORTWARNING
;�û������ʼ������
!define MUI_CUSTOMFUNCTION_GUIINIT gui_init
!define MUI_ICON "res\setup.ico"
; ��װ�����������������
;!insertmacro MUI_LANGUAGE "SimpChinese"


;����Ȩ��
RequestExecutionLevel  admin

;==============================================ֻ�а�װ  û��ж��===================================


Page directory directory_page_pre directory_page_show directory_page_leave
Page instfiles  instfiles_page_pre instfiles_page_show instfiles_page_leave

;==================================================================================================
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\KVNetSetUp\KVNetSetup.exe"
InstallDir "$PROGRAMFILES\Baidu\BDKV" ;Ĭ�ϰ�װĿ¼
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
  #�жϰ�װ·���Ϸ���
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
  
  #�ж�·��ֻ��
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

