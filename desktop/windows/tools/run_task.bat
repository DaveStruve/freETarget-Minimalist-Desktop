@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 goto trypython
py -3.12 -c "import sys" >nul 2>nul
if errorlevel 1 goto pydefault
py -3.12 tools\windows_tasks.py %1
exit /b %errorlevel%
:pydefault
py -3 tools\windows_tasks.py %1
exit /b %errorlevel%
:trypython
where python >nul 2>nul
if errorlevel 1 goto missing
python tools\windows_tasks.py %1
exit /b %errorlevel%
:missing
echo Python was not found. The source launcher/build step needs Python 3.12 x64.
echo Download Python from https://www.python.org/downloads/windows/
echo A compiled release will not need a separate Python installation.
exit /b 1
