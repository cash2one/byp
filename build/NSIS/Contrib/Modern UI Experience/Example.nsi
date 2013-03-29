Name                 "Example"
OutFile              "Example.exe"
SetCompressor        lzma
ShowInstDetails      show

Var                  HWND

!include             MUIXP.nsh
!include             LogicLib.nsh

	;Ҫʹ�ò�ͬ���Ľ��棬ȡ�������ע�� 
	;!define MUI_SKIN "InstallShield"
	;!define MUI_SKIN "Windows XP"
	;!define MUI_SKIN "Modern-blue"
	;!define MUI_SKIN "Orange"
	;!define MUI_SKIN "Delphi 8"
	;!define MUI_SKIN "InstallWizard"
	;!define MUI_SKIN "InstallWizard Modern"
	;!define MUI_SKIN "InstallSpider"
	
	;ȡ������Ķ���ǰ��ע�Ϳ���ʹ�ò�����������Ľ���
	;!define MUI_COMPONENTSPAGE_NODESC
	
	;����ҳ�� 
	!insertmacro MUI_PAGE_WELCOME
	!insertmacro MUI_PAGE_COMPONENTS
	Page custom SetCustomA
	
	!insertmacro MUI_PAGE_INSTFILES
	!insertmacro MUI_PAGE_FINISH
	
	!insertmacro MUI_UNPAGE_CONFIRM
	!insertmacro MUI_UNPAGE_INSTFILES
	
	;�������� 
	!insertmacro MUI_LANGUAGE English
	!insertmacro MUI_LANGUAGE SimpChinese
	!insertmacro MUI_LANGUAGE TradChinese

!macro InsertSection SECTION
	Section "���� ${SECTION}" sec${SECTION}
	    DetailPrint "Modern UI Experience example, do nothing."
	    Sleep 100
	SectionEnd
!macroend

;SectionGroup Test
!insertmacro InsertSection 1
!insertmacro InsertSection 2
!insertmacro InsertSection 3
!insertmacro InsertSection 4
!insertmacro InsertSection 5
!insertmacro InsertSection 6
!insertmacro InsertSection 7
!insertmacro InsertSection 8
!insertmacro InsertSection 9
;SectionGroupEnd

Section "����ж�س���"
	WriteUninstaller $EXEDIR\Uninstaller.exe
SectionEnd

Function .onInit
	InitPluginsDir
	File "/oname=$PLUGINSDIR\ioA.ini" ".\ioA.ini"
FunctionEnd

;��ʾ�Զ���ҳ��������������
Function SetCustomA
	InstallOptions::initDialog /NOUNLOAD "$PLUGINSDIR\ioA.ini"
	Pop $HWND
!ifdef MUI_TEXT_COLOR & MUI_TEXT_BGCOLOR
	SetCtlColors $HWND ${MUI_TEXT_COLOR} ${MUI_TEXT_BGCOLOR}
	${For} $1 0 5 ;�����пؼ��ı�������Ϊ ${MUI_TEXT_COLOR} ${MUI_TEXT_BGCOLOR}
		GetDlgItem $0 $HWND "120$1"
		SetCtlColors $0 ${MUI_TEXT_COLOR} ${MUI_TEXT_BGCOLOR}
	${Next}
!endif
	!insertmacro MUI_HEADER_TEXT "����" "�ӱ���"
	InstallOptions::show
FunctionEnd

Function .onMouseOverSection
	!insertmacro MUI_DESCRIPTION_BEGIN
	
	!insertmacro MUI_DESCRIPTION_TEXT ${sec1} "�������� 1"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec2} "�������� 2"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec3} "�������� 3"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec4} "�������� 4"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec5} "�������� 5"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec6} "�������� 6"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec7} "�������� 7"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec8} "�������� 8"
	!insertmacro MUI_DESCRIPTION_TEXT ${sec9} "�������� 9"

	!insertmacro MUI_DESCRIPTION_END
FunctionEnd


Section Uninstall
	Delete $INSTDIR\Uninstaller.exe
SectionEnd

