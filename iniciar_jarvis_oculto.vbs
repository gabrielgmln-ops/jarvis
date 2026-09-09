Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

WScript.Sleep 5000

pastaAtual = FSO.GetParentFolderName(WScript.ScriptFullName)
arquivoBat = pastaAtual & "\iniciar_jarvis.bat"

WshShell.Run chr(34) & arquivoBat & chr(34), 0, False

Set WshShell = Nothing
Set FSO = Nothing