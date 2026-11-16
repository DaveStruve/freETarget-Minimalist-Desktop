@echo off
setlocal
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC for %%I in (ISCC.exe) do if not "%%~$PATH:I"=="" set "ISCC=%%~$PATH:I"
if not defined ISCC (
 echo ERROR: Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php
 pause
 exit /b 1
)
if not exist "%~dp0release-x86\freETargetMinimalist\freETargetMinimalist.exe" (
 echo ERROR: Build the x86 app first using BUILD_WINDOWS_X86.bat
 pause
 exit /b 1
)
"%ISCC%" "%~dp0installer\freETargetDesktop-x86.iss"
if errorlevel 1 (echo Installer build failed. & pause & exit /b 1)
echo Installer saved to release-x86\installer
pause
