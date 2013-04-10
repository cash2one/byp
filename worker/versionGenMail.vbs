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
	buildDir = "VersionBuild\"
	buildIdFile = ".\AutoBuild\versionBuildId.txt"
	If StrComp(buildType,"before") = 0 Then
		mailFile = ".\AutoBuild\BdmVersionBefore.txt"
	End If
	If StrComp(buildType,"after") = 0 Then
		mailFile = ".\AutoBuild\BdmVersionAfter.txt"
	End If
	errDir = "err\"
	buildId = get_file_info(buildIdFile)
	if StrComp(buildType,"before") = 0 Then
		buildId = buildId + 1
	End If
	
	buildVersion = "1.0.1." + CStr(buildId)
	buildProduct = "Baidu Manager"
	ClearFile mailFile
	GenBuildHeader mailFile,buildProduct,buildVersion

	If StrComp(buildType,"before") = 0 Then
		AppendFile mailFile,""
		AppendFile mailFile,"Weekly Build Started!"
		AppendFile mailFile,""
		AppendFile mailFile,"Warning: "
		AppendFile mailFile,"    Changes committed after this mail will NOT be merged into this version."
		AppendFile mailFile,""
		AppendFile mailFile,"You'll receive this email when weekly build starts.Do NOT want to be bothered? RTX liuheng."
		AppendFile mailFile,""
	End If
	If StrComp(buildType,"after") = 0 Then
		AppendFile mailFile,""
		AppendFile mailFile,"Weekly Build Finished!"
		AppendFile mailFile,""
		AppendFile mailFile,"Build Information"
		AppendFile mailFile,"--------------------------------------------------------"
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
		AppendFile mailFile,"You'll receive this email when weekly build finishes.Do NOT want to be bothered? RTX liuheng."
		AppendFile mailFile,""
	End If
	
End Function

Function GenBDKVMail(buildType)
	Dim mailFile,buildIdFile,confFile,buildDir,errDir,buildId,buildVersion,buildProduct
	mailFile = ".\AutoBuild\kvmail.txt"
	confFile = ".\AutoBuild\kvchecklog.conf"
	buildDir = "KVVersionBuild\"
	buildIdFile = ".\AutoBuild\kvversionBuildId.txt"
	If StrComp(buildType,"before") = 0 Then
		mailFile = ".\AutoBuild\BdkvVersionBefore.txt"
	End If
	If StrComp(buildType,"after") = 0 Then
		mailFile = ".\AutoBuild\BdkvVersionAfter.txt"
	End If
	errDir = "kverr\"
	buildId = get_file_info(buildIdFile)
	if StrComp(buildType,"before") = 0 Then
		buildId = buildId + 1
	End If
	
	buildVersion = "1.0.1." + CStr(buildId)
	buildProduct = "Baidu KV"
	ClearFile mailFile
	GenBuildHeader mailFile,buildProduct,buildVersion

	If StrComp(buildType,"before") = 0 Then
		AppendFile mailFile,""
		AppendFile mailFile,"Weekly Build Started!"
		AppendFile mailFile,""
		AppendFile mailFile,"Warning: "
		AppendFile mailFile,"    Changes committed after this mail will NOT be merged into this version."
		AppendFile mailFile,""
		AppendFile mailFile,"You'll receive this email when weekly build starts.Do NOT want to be bothered? RTX liuheng."
		AppendFile mailFile,""
	End If
	If StrComp(buildType,"after") = 0 Then
		AppendFile mailFile,""
		AppendFile mailFile,"Weekly Build Finished!"
		AppendFile mailFile,""
		AppendFile mailFile,"Build Information"
		AppendFile mailFile,"--------------------------------------------------------"
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
		AppendFile mailFile,"You'll receive this email when weekly build finishes.Do NOT want to be bothered? RTX liuheng."
		AppendFile mailFile,""
	End If
	
End Function

Dim arg
arg = GetCommandProduct()
If StrComp(arg,"bdm_before") = 0 Then
	GenBDMMail("before")
End If

If StrComp(arg,"bdm_after") = 0 Then
	GenBDMMail("after")
End If

If StrComp(arg,"bdkv_before") = 0 Then
	GenBDKVMail("before")
End If

If StrComp(arg,"bdkv_after") = 0 Then
	GenBDKVMail("after")
End If
