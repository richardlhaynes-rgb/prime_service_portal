@echo off
cd /d "C:\Projects\prime_service_portal"
echo Activating Virtual Environment...
call venv\Scripts\activate
echo Starting Production Server...
python run_production.py
pause