@echo off
TITLE PRIME Service Portal - Demo Data Refresh
color 0B
mode con: cols=120 lines=40
cls

echo ========================================================
echo   PRIME SERVICE PORTAL - DEMO DATA REFRESH v9.0
echo ========================================================
echo.
echo   [STEP 1] ACTIVATING ENVIRONMENT...
call venv\Scripts\activate.bat

echo.
echo   [STEP 2] RUNNING GENERATOR (Wipe + Seed + Survey)...
echo   - This process cleans the DB and builds 325 tickets.
echo   - It also generates user surveys and history.
echo.

python manage.py seed_tickets

echo.
echo ========================================================
echo   PROCESS COMPLETE
echo ========================================================
echo   You now have 325 fresh tickets with rich analytics.
echo   Dashboard graphs should now look populated and realistic.
echo.
pause