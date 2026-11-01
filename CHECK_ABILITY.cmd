@echo off
setlocal
>"%~dp0Aqua_Ability_Check.txt" echo Aqua Ability Test started %date% %time%
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check_Aqua_Ability.ps1" %* >"%~dp0Aqua_Ability_Console.txt" 2>&1
if errorlevel 1 (
    >>"%~dp0Aqua_Ability_Check.txt" echo PowerShell check failed to finish. Console output follows:
    type "%~dp0Aqua_Ability_Console.txt" >>"%~dp0Aqua_Ability_Check.txt"
)
type "%~dp0Aqua_Ability_Console.txt"
echo.
echo Report: "%~dp0Aqua_Ability_Check.txt"
echo Return that report with whether the save and first ground attack work.
pause
