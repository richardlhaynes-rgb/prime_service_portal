@echo off
TITLE PRIME Service Portal - Server
echo ==========================================
echo   Starting PRIME Service Portal...
echo ==========================================

:: 1. Navigate to the project folder
cd /d C:\Projects\prime_service_portal

:: 2. Activate the Virtual Environment
call venv\Scripts\activate.bat

:: 3. Run the Django Server
python manage.py runserver

:: 4. Keep window open if server crashes
pause