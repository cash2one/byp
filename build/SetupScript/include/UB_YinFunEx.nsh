;----------------------------------------------------
;nsis常用辅助函数
;kenttong 2012-06-04
;----------------------------------------------------

;变量的定义

var varRunMode              #0正常安全,1liveup,2互助升级
var varIsSilence            #0静默 1非静默
var varWndHandle            #互助升级时使用，发送进度给窗口
var varRepair               #自动升级的时候使用

var vardefaultpath          #传入的默认安装路径

var varforceinstall	    #方便自动化测试使用
var SmDesktopDir            #桌面路径
var APP_DATA_PATH           #用户路径
var COVER_ERROR             #文件是否被占用
var NEED_INSTALL_IME        #是否需要执行ImmInstallIME，IME文件被占用不用执行ImmInstallIME
var SmProgramsDir           #记录开始菜单位置
var strInstallDir           #安装路径
var strOldInstDir           #老版本的安装路径，覆盖安装重启后删除
var strOldVersion           #老版本的版本号
var varBackupDir            #保存文件的临时目录

# 拷贝文件相关的数据
var strLastCopyFile         #最后一个被拷贝的文件
var strCopyToTemp           #是否拷贝到临时数据文件夹
var bOccupySetup            #是否是占用安装
var curCopyFileCount        #当前文件拷贝的进度(已经拷贝的文件数)

Var varWizardCheckBoxText   #最后设置向导的文字描述

Var varCheckSpace           #最后设置向导的文字描述

Var strFinishText           #完成页面的提示

;----------------------------------------------------宏定义----------------------------------------------------

!macro GET_CTRL_HANDL CONTROLID ISBELONGCHILDDIALOG HANDLE

  strcpy ${HANDLE} 0
  ;查找窗口
  ${if} ${ISBELONGCHILDDIALOG} == 1
    FindWindow $0 "#32770" "" $HWNDPARENT
    ${if} $0 != 0
      GetDlgItem ${HANDLE} $0 ${CONTROLID}
    ${endif}
  ${else}
    GetDlgItem ${HANDLE} $HWNDPARENT ${CONTROLID}
  ${endif}

!macroend

!macro POST_MSG_TO_HANDLWND hWnd dwProgress dwError
  ${if} ${hWnd} != 0
    ${if} ${hWnd} != ""
      InstallHelper::NotifyHostSetupStatus ${dwProgress} ${dwError} ${hWnd}
    ${endif}
  ${endif}
!macroend

#文件拷贝数目清零
Function ClearFileCopyCount
  StrCpy $curCopyFileCount 0
FunctionEnd

#递增文件拷贝进度
Function IncFileCopyCount
   IntOp $curCopyFileCount $curCopyFileCount + 1
FunctionEnd

#计算文件拷贝的进度，不设定为100是因为文件拷贝完成后还需要一些费时的操作
#安装全部结束的时候发送100
Function SendFileCopyProgress
  ${if} $varWndHandle != 0
    StrCpy $R0 $curCopyFileCount
    IntOp $R0 $R0 * 90
    IntOp $R0 $R0 / ${SETUP_FILE_MAX_COUNT}
    ;${if} $R0 > 90 #出错时的修正
    ;    StrCpy $R0 90
    ;${endif}
    !insertmacro POST_MSG_TO_HANDLWND $varWndHandle $R0 0
  ${endif}
FunctionEnd
