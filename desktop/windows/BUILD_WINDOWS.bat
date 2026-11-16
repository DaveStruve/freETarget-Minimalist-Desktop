@echo off
call "%~dp0tools\run_task.bat" build
if errorlevel 1 pause
