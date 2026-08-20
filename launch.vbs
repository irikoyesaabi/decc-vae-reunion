Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root

python = root & "\python\python.exe"
If Not fso.FileExists(python) Then python = root & "\python\install\python.exe"
If Not fso.FileExists(python) Then
  MsgBox "Python Standalone introuvable. Executez install.bat.", 16, "DECC/VAE"
  WScript.Quit 1
End If

manage = root & "\decc_vae\manage.py"
cmd = """" & python & """ """ & manage & """ runserver 127.0.0.1:8000 --noreload"
sh.Run cmd, 0, False
WScript.Sleep 2000
sh.Run "http://127.0.0.1:8000", 1, False
