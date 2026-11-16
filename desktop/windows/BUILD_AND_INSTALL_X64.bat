@echo off
call "%~dp0BUILD_WINDOWS_X64.bat"
if errorlevel 1 exit /b 1
call "%~dp0CREATE_INSTALLER_X64.bat"
