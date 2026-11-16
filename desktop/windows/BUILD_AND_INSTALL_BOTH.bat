@echo off
call "%~dp0BUILD_AND_INSTALL_X64.bat"
if errorlevel 1 exit /b 1
call "%~dp0BUILD_AND_INSTALL_X86.bat"
