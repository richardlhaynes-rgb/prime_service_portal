@echo off
TITLE PRIME Service Portal - Dev Shell
color 0A
mode con: cols=140 lines=40
cls

echo ==========================================
echo   Environment Activated. Ready to Code.
echo ==========================================

:: 1. Navigate to project
cd /d C:\Projects\prime_service_portal

:: 2. Activate venv
call venv\Scripts\activate.bat

:: 3. Stay open for commands
cmd /k