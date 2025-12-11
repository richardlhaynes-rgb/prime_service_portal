@echo off
TITLE PRIME Service Portal - Server
color 0A
mode con: cols=140 lines=40
cls

echo ==========================================
echo   Starting PRIME Service Portal...
echo ==========================================
echo.
echo   [INFO] Environment: Development
echo   [INFO] Port: 8000
echo   [INFO] Access: http://127.0.0.1:8000/
echo.

:: 1. Navigate to the project folder
cd /d C:\Projects\prime_service_portal

:: 2. Activate the Virtual Environment
call venv\Scripts\activate.bat

:: 3. Run the Django Server
python manage.py runserver

:: 4. Keep window open if server crashes
pause

@echo off
title PRIME Service Portal - SERVER

:: Activate Virtual Environment (Adjust path if needed)
call venv\Scripts\activate

:: Run Server
python manage.py runserver