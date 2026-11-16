@echo off
setlocal
py -3.12-32 "%~dp0tools\windows_tasks.py" build-x86
exit /b %errorlevel%
