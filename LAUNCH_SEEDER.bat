@echo off
setlocal EnableExtensions DisableDelayedExpansion
title PRIME AE // MASTER DATA CONTROLLER
color 0B

:: --- CREDENTIALS CHECK ---
if not exist "%APPDATA%\postgresql\pgpass.conf" (
    color 4F
    echo [CRITICAL] pgpass.conf not found.
    pause
    exit /b
)
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

:MAIN_MENU
cls
echo.
echo  =============================================================
echo   PRIME AE // DATA ORCHESTRATION SYSTEM
echo  =============================================================
echo   Select a Module to Manage:
echo.
echo   [1]  INVENTORY (Assets)
echo   [2]  SERVICE DESK (Tickets, Users, Team)
echo   [3]  KNOWLEDGE BASE (Articles)
echo.
echo   -------------------------------------------------------------
echo   [4]  WIPE EVERYTHING (EXCEPT MAX HEADROOM)
echo   [5]  WIPE ^& REPOPULATE EVERYTHING (Full Demo)
echo   -------------------------------------------------------------
echo   [0]  EXIT
echo.
set /p "CHOICE=Select Option >> "

if "%CHOICE%"=="1" goto MENU_INVENTORY
if "%CHOICE%"=="2" goto MENU_TICKETS
if "%CHOICE%"=="3" goto MENU_KB
if "%CHOICE%"=="4" goto ACTION_WIPE_ALL
if "%CHOICE%"=="5" goto ACTION_REPOPULATE_ALL
if "%CHOICE%"=="0" exit /b

goto MAIN_MENU

:: ==========================================
:: 1. INVENTORY MENU
:: ==========================================
:MENU_INVENTORY
cls
echo.
echo   [INVENTORY MODULE]
echo   1. Seed Assets (325 items)
echo   2. Clear Assets Only
echo   9. Back
echo.
set /p "SUB=Option >> "
if "%SUB%"=="1" python manage.py seed_assets
if "%SUB%"=="2" python manage.py seed_assets --clear
if "%SUB%"=="9" goto MAIN_MENU
pause
goto MENU_INVENTORY

:: ==========================================
:: 2. SERVICE DESK MENU
:: ==========================================
:MENU_TICKETS
cls
echo.
echo   [SERVICE DESK MODULE]
echo   1. Seed Tickets & Users (325 Smart Tickets)
echo   2. Clear Tickets Only
echo   9. Back
echo.
set /p "SUB=Option >> "
if "%SUB%"=="1" python manage.py seed_tickets
if "%SUB%"=="2" python manage.py seed_tickets --clear
if "%SUB%"=="9" goto MAIN_MENU
pause
goto MENU_TICKETS

:: ==========================================
:: 3. KNOWLEDGE BASE MENU
:: ==========================================
:MENU_KB
cls
echo.
echo   [KNOWLEDGE BASE MODULE]
echo   1. Seed Articles (45 items)
echo   2. Clear Articles Only
echo   9. Back
echo.
set /p "SUB=Option >> "
if "%SUB%"=="1" python manage.py seed_kb
if "%SUB%"=="2" python manage.py seed_kb --clear
if "%SUB%"=="9" goto MAIN_MENU
pause
goto MENU_KB

:: ==========================================
:: 4. WIPE ALL
:: ==========================================
:ACTION_WIPE_ALL
cls
color 4F
echo.
echo  [WARNING] This will DELETE ALL DATA (Tickets, Assets, KB).
echo  Only the Superuser (Max) will remain.
echo.
set /p "CONFIRM=Type 'NUKE' to confirm >> "
if /I not "%CONFIRM%"=="NUKE" goto MAIN_MENU

cls
color 0C
echo [SYSTEM] Initiating Factory Reset...
python manage.py setup_god_mode
call :SHOW_CREDS
pause
color 0B
goto MAIN_MENU

:: ==========================================
:: 5. WIPE & REPOPULATE ALL
:: ==========================================
:ACTION_REPOPULATE_ALL
cls
color 1F
echo.
echo  This will reset the system and generate the Full Demo Experience.
echo.
set /p "CONFIRM=Type 'DESTROY' to confirm >> "
if /I not "%CONFIRM%"=="DESTROY" goto MAIN_MENU

cls
color 0A
echo [0/5] Updating Database Schema...
python manage.py makemigrations
python manage.py migrate

echo [1/5] Factory Reset (Preserving Max)...
python manage.py setup_god_mode

echo [2/5] Seeding Service Desk (Users ^& Tickets)...
python manage.py seed_tickets

echo [3/5] Seeding Inventory...
python manage.py seed_assets

echo [4/5] Seeding Knowledge Base...
python manage.py seed_kb

call :SHOW_CREDS
pause
color 0B
goto MAIN_MENU

:: ==========================================
:: CREDENTIAL DISPLAY SUBROUTINE
:: ==========================================
:SHOW_CREDS
echo.
echo  =============================================================
echo   SYSTEM CREDENTIALS
echo  =============================================================
echo.
echo   [SYSTEM ADMIN]
echo   User:      max.headroom
echo   Password:  admin123
echo.
echo   [STANDARD USER]
echo   User:      marty.mcfly (or doc.brown, etc)
echo   Password:  GreatScott!
echo.
exit /b