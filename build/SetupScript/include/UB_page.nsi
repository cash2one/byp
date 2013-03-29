#  安装过程页面逻辑
!define MANUAL_UPDATE_SKIP_DIRECTORY 1

!macro MANUAL_UPDATE_SKIP_PAGE skinpage
  ${if} $varRunMode == ${RUM_MODE_LIVEUP}
    ${if} $varIsSilence == ${RUM_NOSILENCE}
      ${if} ${skinpage} == 1
        Abort
      ${endif}
    ${endif}
  ${endif}
!macroend



# 该函数位置不能改变，因为这里面改变了宏的定义，该改变仅针对directory页面
Function directory_page_pre
  !define MUI_DIRECTORYPAGE
  !insertmacro MUI_HEADER_TEXT $(MUI_TEXT_DIRECTORY_TITLE) $(MUI_TEXT_DIRECTORY_SUBTITLE)
  !insertmacro MANUAL_UPDATE_SKIP_PAGE ${MANUAL_UPDATE_SKIP_DIRECTORY}
FunctionEnd

var varDlgWnd
var varDirDialog
Function directory_page_show
    strcpy  $varDirDialog 0
    GetDlgItem $varDirDialog $HWNDPARENT 0
	
   !insertmacro Get_Ctrl_Handl 1006 1 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1023 1 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1024 1 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 1020 1 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   
   ;编辑框
   !insertmacro Get_Ctrl_Handl 1019 1 $MUI_HWND
   ;EnableWindow $MUI_HWND 0
   InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 28 95 400 24
   ;浏览按钮
   !insertmacro Get_Ctrl_Handl 1001 1 $MUI_HWND
   InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 434 93 77 28
   
   !insertmacro Get_Ctrl_Handl 1 0 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 2 0 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   !insertmacro Get_Ctrl_Handl 3 0 $MUI_HWND
   ShowWindow $MUI_HWND ${SW_HIDE}
   
   FindWindow $0 "#32770" "" $HWNDPARENT
   InstallHelper::CreateCustomPage /NOUNLOAD $0
FunctionEnd

#directory页面离开的回调函数
Function directory_page_leave
   !insertmacro Get_Ctrl_Handl 953 1 $MUI_HWND
   InstallHelper::GetCheck /NOUNLOAD $MUI_HWND
   Pop $R0
   ${if} $R0 == "0"
   strcpy  $isDesktopLink "2"
  ${endif}

  !insertmacro Get_Ctrl_Handl 955 1 $MUI_HWND
   InstallHelper::GetCheck /NOUNLOAD $MUI_HWND
   Pop $R0
   ${if} $R0 == "0"
   strcpy $isSetDefault "2"
   ${endif}

 !insertmacro Get_Ctrl_Handl 956 1 $MUI_HWND
   InstallHelper::GetCheck /NOUNLOAD $MUI_HWND
   Pop $R0
   ${if} $R0 == "0"
   strcpy  $isRunAfterInstall "2"
  ${endif}

 !insertmacro Get_Ctrl_Handl 959 1 $MUI_HWND
   InstallHelper::GetCheck /NOUNLOAD $MUI_HWND
   Pop $R0
   ${if} $R0 == "0"
    strcpy  $IsSendData "2"
  ${endif}

 !insertmacro Get_Ctrl_Handl 954 1 $MUI_HWND
   InstallHelper::GetCheck /NOUNLOAD $MUI_HWND
   Pop $R0
   ${if} $R0 == "0"
    strcpy  $isTaskbarLink "2"
  ${endif}
  
GetInstDirError $0
  ${Switch} $0
    ${Case} 0
      ${Break}
    ${Case} 1
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 3
      MessageBox MB_OK|MB_ICONQUESTION ${MACRO_INVALIDDIRECTORY}
      Abort
      ${Break}
    ${Case} 2
      !insertmacro POST_MSG_TO_HANDLWND $varWndHandle 0 1
      MessageBox MB_OK|MB_ICONSTOP ${MACRO_NOENOUGHFREESPACE}
      Abort
      ${Break}
  ${EndSwitch}
  StrCpy $varCheckSpace 1
FunctionEnd

var varDetailBtnWnd
var varBitmapWnd
var varListViewWnd
Function instfiles_page_pre
  !insertmacro Get_Ctrl_Handl 3 0 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
 !insertmacro Get_Ctrl_Handl 1039 0 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
!insertmacro Get_Ctrl_Handl 1034 0 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
!insertmacro Get_Ctrl_Handl 1036 0 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
FunctionEnd
Function instfiles_page_show
  ;隐藏详情按钮
  FindWindow $0 "#32770" "" $HWNDPARENT
  strcpy  $varDlgWnd $0
  strcpy  $varDetailBtnWnd 0
  GetDlgItem $varDetailBtnWnd $varDlgWnd 1027
  ${if} $varDetailBtnWnd != 0
    ShowWindow $varDetailBtnWnd SW_HIDE
  ${endif}
 !insertmacro Get_Ctrl_Handl 1006 1 $MUI_HWND
  InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 27 43 500 20
  ;增加宣传图片控件

#  strcpy  $varBitmapWnd 0
#  strcpy  $varListViewWnd 0
#  ;添加一个子控件
#  ${if} $varDlgWnd != 0
#    InstallHelper::CreateBitmapCtrl /NOUNLOAD $HWNDPARENT 1028 $varDlgWnd 1004
#	StrCpy $varBitmapWnd $R0
#    ${if} $varBitmapWnd != 0
#	  GetDlgItem $varListViewWnd $HWNDPARENT 1016
#      call SetInstallpackPoster
#    ${endif}
#  ${endif}
  
  ;进度提示
  ;!insertmacro Get_Ctrl_Handl 1006 1 $MUI_HWND
  ;InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 27 43 447 20
  !insertmacro Get_Ctrl_Handl 1006 1 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
  ;进度条
  !insertmacro Get_Ctrl_Handl 1004 1 $MUI_HWND
  ;InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 133 155 283 66
  ShowWindow $MUI_HWND ${SW_HIDE}
  ;广告图
  !insertmacro Get_Ctrl_Handl 0 1 $MUI_HWND
   InstallHelper::MoveWindowRect /NOUNLOAD $MUI_HWND 34 100 494 266

  FindWindow $0 "#32770" "" $HWNDPARENT
  InstallHelper::CreateInstallPage /NOUNLOAD $0
  ;InstallHelper::IsBrowserRunning  /NOUNLOAD $MUI_HWND
 ; Pop $R0
 ;  ${if} $R0 == "1"
 ;     MessageBox MB_YESNO|MB_TOPMOST "${MACRO_MESSAGE_CLOSE_BROWSER_TIPS}"  IDYES PROMPT_KILL_BROWSER
 ;     Quit
 ;  ${endif}
 ;PROMPT_KILL_BROWSER:
 ;;InstallHelper::KillRunningBrowser  /NOUNLOAD $MUI_HWND
FunctionEnd


Function instfiles_page_leave

  FindWindow $0 "#32770" "" $HWNDPARENT
  InstallHelper::CreateFinishPage /NOUNLOAD $0
;  ${GetSystemMenu} $0 $HWNDPARENT
 ; System::Call "user32::EnableMenuItem(i, i, i) i ($0, ${SC_CLOSE}, ${MF_BYCOMMAND}|${MF_ENABLE})"


  !insertmacro Get_Ctrl_Handl 1006 1 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
  ;进度条
  !insertmacro Get_Ctrl_Handl 1004 1 $MUI_HWND
  ShowWindow $MUI_HWND ${SW_HIDE}
  ;广告图
 ; !insertmacro Get_Ctrl_Handl 0 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
  
 ; !insertmacro Get_Ctrl_Handl 3 0 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1035 0 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1036 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1256 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1028 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1034 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1036 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1037 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}
 ; !insertmacro Get_Ctrl_Handl 1046 1 $MUI_HWND
 ; ShowWindow $MUI_HWND ${SW_HIDE}

    ${if} $isSetDefault != "2"
        Call SetDeafult
    ${endif}

    ${if} $isSendData != "2"
        WriteRegDword HKCU "Software\Tencent\UBrowser\Launch" "EnableUEData" 0x1
    ${else}
        WriteRegDword HKCU "Software\Tencent\UBrowser\Launch" "EnableUEData" 0
    ${endif}

    ${if} $isRunAfterInstall != "2"#立即运行程序之后应该结束安装程序
	     Exec  '"$INSTDIR\BDMCoreSvr.exe"'
	     Exec  '"$INSTDIR\BDMgr.exe"'
         Quit
    ${endif}

FunctionEnd



#Function finish_page_show
#   GetDlgItem $R9 $MUI_HWND "1203"
#    SendMessage $R9 ${BM_SETCHECK} 1 0 
#    SendMessage $R9 ${WM_SETTEXT} 0 "STR:${MACRO_CHECKDEAFULTBROWSER}"
#   GetDlgItem $R9 $MUI_HWND "1204"
#    SendMessage $R9 ${BM_SETCHECK} 1 0
#    SendMessage $R9 ${WM_SETTEXT} 0 "STR:${MACRO_CHECKRUNNOW}"

#   FindWindow $0 "#32770" "" $HWNDPARENT
#   InstallHelper::CreateFinishPage /NOUNLOAD $0
#FunctionEnd

Function finish_page_pre
FunctionEnd
Function finish_page_show
  GetDlgItem $R9 $MUI_HWND "1200"
  ShowWindow $R9 ${SW_HIDE}
 GetDlgItem $R9 $MUI_HWND "1201"
  ShowWindow $R9 ${SW_HIDE}
 GetDlgItem $R9 $MUI_HWND "1202"
  ShowWindow $R9 ${SW_HIDE}
  FindWindow $0 "#32770" "" $HWNDPARENT
  InstallHelper::CreateFinishPage /NOUNLOAD $0
  
  
  ;${GetSystemMenu} $0 $HWNDPARENT
  ;System::Call "user32::EnableMenuItem(i, i, i) i ($0, ${SC_CLOSE}, ${MF_BYCOMMAND}|${MF_ENABLE})"
FunctionEnd

Function  finish_page_leave
FunctionEnd

Function SetDeafult
Exec  '"$INSTDIR\UBrowser.exe" -module=UBrowserAssistant.dll -setdefaultbrowser'
;;InstallDR::SetDefBrow "$INSTDIR\UBrowser.exe"
FunctionEnd

Function RunBrowser
Exec '"$INSTDIR\UBrowser.exe"'
FunctionEnd