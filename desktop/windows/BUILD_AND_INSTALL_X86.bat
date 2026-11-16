@echo off
call "%~dp0BUILD_WINDOWS_X86.bat"
if errorlevel 1 (echo x86 application build failed. & pause & exit /b 1)
call "%~dp0CREATE_INSTALLER_X86.bat"
