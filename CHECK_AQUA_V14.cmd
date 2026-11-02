@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v14.ps1" %*
pause
