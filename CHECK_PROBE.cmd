@echo off
setlocal
>"%~dp0Aqua_Arm_Probe_Check.txt" echo Aqua Arm Probe started %date% %time%
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Probe.ps1" %* >"%~dp0Probe_Check_Console.txt" 2>&1
if errorlevel 1 (
    >>"%~dp0Aqua_Arm_Probe_Check.txt" echo PowerShell check failed to finish. Console output follows:
    type "%~dp0Probe_Check_Console.txt" >>"%~dp0Aqua_Arm_Probe_Check.txt"
)
type "%~dp0Probe_Check_Console.txt"
echo.
echo Report: "%~dp0Aqua_Arm_Probe_Check.txt"
echo Return that report with whether the save and first ground attack work.
pause
