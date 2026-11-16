@echo off
setlocal
cd /d "%~dp0"
py -3.12-64 "tools\windows_tasks.py" build
if errorlevel 1 (echo x64 build failed. & pause & exit /b 1)
