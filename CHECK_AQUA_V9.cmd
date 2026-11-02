@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Animations_v9.ps1" %*
pause
