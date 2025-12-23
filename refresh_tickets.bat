@echo off
cd /d "%~dp0"

REM --- SET WARNING COLORS (Red Background) ---
color 4F

echo.
echo ######################################################################
echo #                                                                    #
echo #               WARNING: DEMO DATA RESET INITIATED                   #
echo #                                                                    #
echo #   1. THIS WILL DELETE 100%% OF EXISTING TICKETS.                    #
echo #   2. ALL HISTORICAL ANALYTICS WILL BE LOST (FLATLINED).            #
echo #   3. THIS CANNOT BE UNDONE.                                        #
echo #                                                                    #
echo #   USE ONLY FOR:                                                    #
echo #   - Preparing for a fresh demo presentation.                       #
echo #   - Resetting dates so "30 mins ago" is accurate relative to NOW.  #
echo #                                                                    #
echo ######################################################################
echo.
echo Are you sure you want to wipe the database and reset time?
echo Press CTRL+C to Cancel, or
pause

REM --- RESET COLORS (Normal) ---
color 07

echo.
echo ==========================================
echo      PRIME SERVICE PORTAL - DATA RESET
echo ==========================================

REM --- 1. Activate Virtual Environment ---
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo Error: Virtual environment 'venv' not found.
    pause
    exit /b
)

echo.
echo [1/2] Wiping all existing tickets...
python manage.py shell -c "from service_desk.models import Ticket; count = Ticket.objects.all().delete()[0]; print(f'Successfully deleted {count} tickets.')"

echo.
echo [2/2] Generating fresh demo data (Target: 75 Tickets)...
python manage.py generate_demo_tickets

echo.
echo ==========================================
echo      REFRESH COMPLETE - TIME RESET
echo ==========================================
echo.
pause