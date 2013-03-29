
#主安装程序

;--------------------------------
# Script writen by yihongzhang (@Baidu) 
# date: 2012.2.22
;--------------------------------

!addincludedir "include"
!include "buildline.nsi"
#预定义一些常量
!define MACRO_VERSIONFIX  ""
!define RELEASE_VERSION  "182"
!define SC_CLOSE 0xF060

!define BUILD_VERSION "1.0"
!define BUILD_TIME  "2013-03-29 02:01:20"
!define BUILD_BASELINE "${BUILD_VERSION}.${BUILD_LINE}.${RELEASE_VERSION}" 

#拷贝文件数量
!define SETUP_FILE_MAX_COUNT        43

#产品信息
!define PRODUCT_VERSION "${BUILD_VERSION}";产品版本
!define PRODUCT_NAME "baidusd";产品名称
!define PRODUCT_PUBLISHER "BAIDU Inc.";产品发布者
!define PRODUCT_FILE_DESCRIPTION "baidusd Setup"
!define PRODUCT_LEGAL_COPYRIGHT "Copyright(C) 2012 - 2012 Baidu Inc. All Rights Reserved.";产品所有权

#进程信息
!define MAINFRAME_PROCESS_NAME "baidusd.exe"
!define TRAY_PROCESS_NAME "baidusdTray.exe"
!define SERVER_PROCESS_NAME "baidusdSvc.exe"
!define UPDATE_PROCESS_NAME "baidusdUpdate.exe"
!define BUGREPORT_PROCESS_NAME "baidusdBugRpt.exe"

!define HKLM_REG_PATH "Software\Baidu\baidusd"
!define ALL_USER_DATA_PATH "baidu\baidusd"

!define MUI_ICON "res\setup.ico";安装界面图标
!define MUI_UNICON "res\uninstall.ico";卸载界面图标

;提升权限
RequestExecutionLevel  admin
;--------------------------------

#包含文件
!addincludedir "include";向包含目录列表中添加另一个包含目录
!include "MUI.nsh";引入新式用户界面函数库
!include "KV_YinFunEx.nsh"
!include "Filefunc.nsh"

!define MUI_ABORTWARNING; #安装未完成，而用户要退出时显示提示。

#定义函数(初始化插件目录)
Function Init_Copy
  InitPluginsDir
                SetOutPath "$PLUGINSDIR\res"       
				File /oname=$PLUGINSDIR\res\InstallWnd.zip    	"res\InstallWnd.zip"
				SetOutPath "$PLUGINSDIR"
				File /oname=$PLUGINSDIR\BDMSkin.dll    			"res\BDMSkin.dll"
FunctionEnd

#定义函数(初始化皮肤资源)
!define MUI_CUSTOMFUNCTION_GUIINIT gui_init
Function gui_init
	ShowWindow $HWNDPARENT ${SW_HIDE}
   KVInstallHelper::GetXmlPath /NOUNLOAD "$PLUGINSDIR\res" "\InstallWnd.zip"  "${PRODUCT_NAME}" "${BUILD_VERSION}"    1  ;1表示安装
FunctionEnd

/*
!define MUI_CUSTOMFUNCTION_UnGUIINIT Un.gui_init
Function Un.gui_init
  KVInstallHelper::InitSkin /NOUNLOAD "$PLUGINSDIR\res" "\KV_InstallSkin.gt"  "${PRODUCT_NAME}" "${BUILD_VERSION}"  "\KV_PlayImage.gt"  0		;0表示卸载
FunctionEnd
*/

#声明directory页面
PageEx directory
Caption " "
DirVerify leave
  PageCallbacks directory_page_pre directory_page_show directory_page_leave
PageExEnd

#声明instfiles页面
!define MUI_PAGE_CUSTOMFUNCTION_PRE  instfiles_page_pre
!define MUI_PAGE_CUSTOMFUNCTION_SHOW  instfiles_page_show
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE instfiles_page_leave
!insertmacro MUI_PAGE_INSTFILES

#声明finish页面(自定义页面只支持两个回调函数)
Page custom finish_page_show finish_page_leave

/*
#声明卸载confirm页面(自定义页面只支持两个回调函数)
UninstPage custom  un.finish_page_show un.finish_page_leave
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
*/

#声明卸载第一个页面
UninstPage directory  un.directory_page_pre un.directory_page_show un.directory_page_leave

#声明卸载第二个页面
UninstPage instfiles un.instfiles_page_pre un.instfiles_page_show un.instfiles_page_leave

#声明卸载第三个页面
UninstPage custom  un.finish_page_show un.finish_page_leave 

#声明所有页面里面使用的全局变量
var isDesktopLink
var isSetDefault
var isRunAfterInstall
var isSendData
var isTaskbarLink

#包含文件
!include "nsDialogs.nsh"
!include "KV_Language.nsh"
!include "StrFuncEx.nsh"
!include  "UseFulLib.nsh"

#包含页面文件
!include "KV_install.nsi"
!include "KV_un_install.nsi"

!include "KV_directory_page.nsi"
!include "KV_instfiles_page.nsi"
!include "KV_finish_page.nsi"

!include "KV_un_directory_page.nsi"
!include "KV_un_instfiles_page.nsi"
!include "KV_un_finish_page.nsi"


VIProductVersion "1.0.0.182"
VIAddVersionKey /LANG=2052 "ProductName" "百度杀毒"
VIAddVersionKey /LANG=2052 "CompanyName" "百度在线网络技术（北京）有限公司"
VIAddVersionKey /LANG=2052 "LegalTrademarks" "Baidu"
VIAddVersionKey /LANG=2052 "LegalCopyright" "Copyright (C) 2013 Baidu Inc."
VIAddVersionKey /LANG=2052 "FileDescription" "百度杀毒安装程序"
VIAddVersionKey /LANG=2052 "FileVersion" "1.0.0.182"
VIAddVersionKey /LANG=2052 "ProductVersion" "1.0.0.182"


#常规设置
InstallDir "$PROGRAMFILES\Baidu\baidusd" ;默认安装目录
InstallDirRegKey HKLM "${HKLM_REG_PATH}" "InstallDir" ;Get installation folder from registry if available

;Name and file
Name "${MACRO_PRODUCTNAME}${PRODUCT_VERSION}${MACRO_VERSIONFIX}"
OutFile "..\kvsetup\Baidusd_Setup_${BUILD_BASELINE}.exe"








  




