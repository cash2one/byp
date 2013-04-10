'some common utility functions

Function  get_file_info( filepath )
    get_file_info = 0
    If IsFileExists( filepath ) Then
      Set fso = CreateObject("SCripting.FileSystemObject")
      Set f = fso.GetFile(filepath)
      Set ts = f.OpenAsTextStream(1, -2)
       
      If Not ts.AtEndOfStream Then
       Do
           Str = ts.readLine()
		   get_file_info = Str
       Loop While Not ts.AtEndOfStream
      End If
      ts.Close()
      
      Set fso = Nothing
   End If
End  function

Function IsFileExists( sfile )
    Dim fso,f
    Set fso = CreateObject("Scripting.FileSystemObject")
    If ( fso.FileExists(sfile) ) Then
        IsFileExists = 1
    Else
        IsFileExists = 0
    End if
    Set fso = Nothing   
End Function

Function GetFileSize( txtfile )
   GetFileSize = 0
   IF IsFileExists( txtfile ) Then
    Set fso = CreateObject("SCripting.FileSystemObject")
    Set f = fso.GetFile(txtfile)
    GetFileSize = f.size
   End If
End Function

Function ClearFile( file )
   Dim fso, f
   Set fso = CreateObject("SCripting.FileSystemObject")
   Set f = fso.OpenTextFile(file,2,True)
   f.Close()
End Function

Function AppendFile( file, msg )
   Dim fso, f
   Set fso = CreateObject("SCripting.FileSystemObject")
   Set f = fso.OpenTextFile(file,8,False)
   f.WriteLine( msg )
   f.Close()
End Function

Function GetCommandProduct()
	Dim arg,args
	Set args = WScript.Arguments
	For Each s In args
		arg = arg + LCase(s)
	Next
	Set args = Nothing
	GetCommandProduct = arg
End Function

Function ShellRun( execmdline )
    Set objShell = CreateObject("Wscript.Shell")
    objShell.Run execmdline,1,true
    Set objShell = Nothing
End Function

Function CopyFile(sSrc,sDest)
    Dim fso,f
    Set fso = CreateObject("Scripting.FileSystemObject")
    If ( fso.FileExists(sSrc) ) Then
        fso.CopyFile sSrc,sDest
    End if
    Set fso = Nothing
End Function

Function CreateFolder(strPath)
    On Error Resume Next
    Dim astrPath, ulngPath, i, strTmpPath
    Dim objFSO
    strPath = Mappath(strPath)
    strPath=Replace(strPath, "\", "/") 
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    If objFSO.FolderExists(strPath) Then
            AutoCreateFolder = True
            Exit Function
    End If
    astrPath = Split(strPath, "/")
    ulngPath = UBound(astrPath)
    strTmpPath = ""
    For i = 0 To ulngPath
      strTmpPath = strTmpPath & astrPath(i) & "/"
      If Not objFSO.FolderExists(strTmpPath) Then
        objFSO.CreateFolder(strTmpPath)
      End If
    Next
    Set objFSO = Nothing
End Function

Function Pack(sFolderName, sOutFolderName)
	Dim fso, fd, sfd, ssfd
	Set fso = CreateObject("Scripting.FileSystemObject")
	Set fd = fso.GetFolder(sFolderName)
	For Each sfd In fd.SubFolders
        If fso.fileExists(sfd.Path & ".zip") Then
            fso.deletefile sfd.Path & ".zip"
        End If
		ShellRun(".\AutoBuild\7z.exe" & " a " & sfd.Path & ".zip " & sfd.Path & "\*")
		CopyFile sfd.Path & ".zip", sOutFolderName & sfd.Name & ".rdb"
		For Each ssfd In sfd.SubFolders
			ShellRun(".\AutoBuild\7z.exe" & " a " & ssfd.Path & ".zip " & ssfd.Path & "\*")
			CreateFolder(sOutFolderName & sfd.Name)
			CopyFile ssfd.Path & ".zip", sOutFolderName & sfd.Name & "\" & ssfd.Name & ".rdb"			
		Next
	Next
End Function
