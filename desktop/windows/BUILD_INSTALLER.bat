@echo off
call "%~dp0tools\run_task.bat" installer
if errorlevel 1 pause
