@echo off
setlocal
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC for %%I in (ISCC.exe) do if not "%%~$PATH:I"=="" set "ISCC=%%~$PATH:I"
if not defined ISCC (echo Inno Setup 6 not found. & pause & exit /b 1)
if not exist "%~dp0release\freETargetMinimalist\freETargetMinimalist.exe" (echo Build x64 app first. & pause & exit /b 1)
"%ISCC%" "%~dp0installer\freETargetDesktop.iss"
if errorlevel 1 (echo Installer build failed. & pause & exit /b 1)
echo Installer saved to release\installer
