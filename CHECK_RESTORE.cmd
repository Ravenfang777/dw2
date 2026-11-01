@echo off
setlocal
>"%~dp0Sora_Restore_Check.txt" echo Sora Restore Check started %date% %time%
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Sora_Restore.ps1" %* >"%~dp0Restore_Check_Console.txt" 2>&1
if errorlevel 1 (
    >>"%~dp0Sora_Restore_Check.txt" echo PowerShell check failed to finish. Console output follows:
    type "%~dp0Restore_Check_Console.txt" >>"%~dp0Sora_Restore_Check.txt"
)
type "%~dp0Restore_Check_Console.txt"
echo.
echo Report: "%~dp0Sora_Restore_Check.txt"
echo Return that report with whether each save loads.
pause
