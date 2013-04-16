include "util.vbs"
Dim arg
arg = GetCommandProduct()
If StrComp(arg,"bdm") = 0 Then
	Call Pack("..\..\basic\Output\SkinResources", "..\..\basic\Output\BinRelease\Skins\Default\")
End If
If StrComp(arg,"bdkv") = 0 Then
	Call Pack("..\..\basic\KVOutput\SkinResources", "..\..\basic\KVOutput\BinRelease\Skins\Default\")
End If

Sub include(file)
    Dim fso, f, str
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set f = fso.OpenTextFile(file, 1)
    ExecuteGlobal f.ReadAll
	f.Close
	Set fso = Nothing
End Sub
