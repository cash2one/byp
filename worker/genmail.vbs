include "AutoBuild/util.vbs"

Sub include(file)
    Dim fso, f, str
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set f = fso.OpenTextFile(file, 1)
    ExecuteGlobal f.ReadAll
	f.Close
	Set fso = Nothing
End Sub

Sub GenLogMsg(mailFile,confFile,errDir,logFile)
	Dim Fsys,fso,txt,indent,proj,user
	Set Fsys=CreateObject("Scripting.FileSystemObject")
	Set fso=Fsys.opentextfile(confFile,1)
	Do While fso.atendofstream<>true
		txt = fso.Readline
		indent = InStr(txt," ")
		If indent = 0 Then
			Exit Do
		End If
		proj = Mid(txt,1,indent-1)
		user = Mid(txt,indent+1)
		If GetFileSize(".\AutoBuild\"+errDir+proj+logFile) > 0 Then
			AppendFile mailFile,proj+" Error ("+user+")"
		Else
			AppendFile mailFile,proj+" Ok"
		End If
	Loop
	fso.close()
	Set fso = Nothing
	Set Fsys = Nothing
End Sub
	
Sub GenDirMsg(mailFile,buildDir,buildVersion)
	AppendFile mailFile,""
	AppendFile mailFile,"Log:"
	AppendFile mailFile,"\\192.168.10.242\public\"+buildDir+buildVersion+"\Log"
	AppendFile mailFile,"Setup:"
	AppendFile mailFile,"\\192.168.10.242\public\"+buildDir+buildVersion+"\"
	AppendFile mailFile,"Debug:"
	AppendFile mailFile,"\\192.168.10.242\public\"+buildDir+buildVersion+"\Debug"
	AppendFile mailFile,"Release:"
	AppendFile mailFile,"\\192.168.10.242\public\"+buildDir+buildVersion+"\Release"
End Sub

Sub GenBuildHeader(mailFile,buildProduct,buildVersion)
	AppendFile mailFile,"Build Product:"
	AppendFile mailFile,buildProduct
	AppendFile mailFile,""
	AppendFile mailFile,"Build Version:"
	AppendFile mailFile,buildVersion
End Sub

Function GenBDMMail(buildType)
	Dim mailFile,buildIdFile,confFile,buildDir,errDir,buildId,buildVersion,buildProduct
	mailFile = ".\AutoBuild\mail.txt"
	confFile = ".\AutoBuild\checklog.conf"
	If StrComp(buildType,"daily") = 0 Then
		buildIdFile = ".\AutoBuild\buildId.txt"
		buildDir = "DailyBuild\"
	End If
	If StrComp(buildType,"version") = 0 Then
		buildIdFile = ".\AutoBuild\versionBuildId.txt"
		buildDir = "VersionBuild\"
	End If
	If StrComp(buildType,"partial") = 0 Then
		buildIdFile = ".\AutoBuild\buildId.txt"
		buildDir = "DailyBuild\"
	End If
	errDir = "err\"
	buildId = get_file_info(buildIdFile)
	If StrComp(buildType,"daily") = 0 Then
		buildVersion = "1.0.0." + buildId
	End If
	If StrComp(buildType,"version") = 0 Then
		buildVersion = "1.0.1." + buildId
	End If
	If StrComp(buildType,"partial") = 0 Then
		buildVersion = "1.0.0." + buildId
	End If
	buildProduct = "Baidu Manager"

	ClearFile mailFile
	
	GenBuildHeader mailFile,buildProduct,buildVersion

	AppendFile mailFile,""
	AppendFile mailFile,"Debug|Win32 Build Results:"
	AppendFile mailFile,""

	logFile = "Debug.log"
	GenLogMsg mailFile,confFile,errDir,logFile
	
	AppendFile mailFile,""
	AppendFile mailFile,"Release|Win32 Build Results:"
	AppendFile mailFile,""

	logFile = "Release.log"
	GenLogMsg mailFile,confFile,errDir,logFile

	GenDirMsg mailFile,buildDir,buildVersion
	AppendFile mailFile,""
	AppendFile mailFile,"You'll receive this email when daily/nighty build finishes.Do NOT want to be bothered? RTX liuheng."
	AppendFile mailFile,""
End Function

Function GenBDKVMail(buildType)
	Dim mailFile,buildIdFile,confFile,buildDir,errDir,buildId,buildVersion,buildProduct
	mailFile = ".\AutoBuild\kvmail.txt"
	confFile = ".\AutoBuild\kvchecklog.conf"
	If StrComp(buildType,"daily") = 0 Then
		buildIdFile = ".\AutoBuild\kvbuildId.txt"
		buildDir = "KVDailyBuild\"
	End If
	If StrComp(buildType,"version") = 0 Then
		buildIdFile = ".\AutoBuild\kvVersionBuildId.txt"
		buildDir = "KVVersionBuild\"
	End If
	If StrComp(buildType,"partial") = 0 Then
		buildIdFile = ".\AutoBuild\kvBuildId.txt"
		buildDir = "KVDailyBuild\"
	End If
	errDir = "kverr\"
	buildId = get_file_info(buildIdFile)
	If StrComp(buildType,"daily") = 0 Then
		buildVersion = "1.0.0." + buildId
	End If
	If StrComp(buildType,"version") = 0 Then
		buildVersion = "1.0.1." + buildId
	End If
	If StrComp(buildType,"partial") = 0 Then
		buildVersion = "1.0.0." + buildId
	End If
	buildProduct = "Baidu KV"
	
	ClearFile mailFile
	
	GenBuildHeader mailFile,buildProduct,buildVersion

	AppendFile mailFile,""
	AppendFile mailFile,"KVDebug|Win32 Build Results:"
	AppendFile mailFile,""

	logFile = "Debug.log"
	GenLogMsg mailFile,confFile,errDir,logFile
	
	AppendFile mailFile,""
	AppendFile mailFile,"KVRelease|Win32 Build Results:"
	AppendFile mailFile,""

	logFile = "Release.log"
	GenLogMsg mailFile,confFile,errDir,logFile

	GenDirMsg mailFile,buildDir,buildVersion
	AppendFile mailFile,""
	AppendFile mailFile,"You'll receive this email when daily/nighty build finishes.Do NOT want to be bothered? RTX liuheng."
	AppendFile mailFile,""
End Function

Dim arg
arg = GetCommandProduct()
If StrComp(arg,"bdm_daily") = 0 Then
	GenBDMMail("daily")
End If

If StrComp(arg,"bdm_version") = 0 Then
	GenBDMMail("version")
End If

If StrComp(arg,"bdm_partial") = 0 Then
	GenBDMMail("partial")
End If

If StrComp(arg,"bdkv_daily") = 0 Then
	GenBDKVMail("daily")
End If

If StrComp(arg,"bdkv_version") = 0 Then
	GenBDKVMail("version")
End If

If StrComp(arg,"bdkv_partial") = 0 Then
	GenBDKVMail("partial")
End If
