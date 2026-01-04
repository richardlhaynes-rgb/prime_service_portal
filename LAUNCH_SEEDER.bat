@echo off
setlocal EnableExtensions DisableDelayedExpansion
title PRIME AE // ASSET SEEDER // COMMAND MODE
color 0C

:: --- 1. CREDENTIALS ---
echo [INIT] Loading Credentials...
set "PG_CONF=%APPDATA%\postgresql\pgpass.conf"

if exist "%PG_CONF%" (
    for /f "usebackq tokens=5 delims=:" %%A in ("%PG_CONF%") do (
        set "DB_PASSWORD=%%A"
        set "PGPASSWORD=%%A"
    )
    echo [OK] Credentials Loaded.
) else (
    color 4F
    echo [ERROR] pgpass.conf not found!
    pause
    exit /b
)

:: --- 2. PYTHON ---
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

:: --- 3. UI ---
cls
echo.
echo  ======================================================
echo   PRIME AE // ASSET DATABASE RESET
echo  ======================================================
echo.
echo   [!] WARNING: This will WIPE the database.
echo.

:PROMPT
set /p "CONFIRM=Type 'DESTROY' to confirm >> "
if /I not "%CONFIRM%"=="DESTROY" exit /b

:: --- 4. EXECUTE ---
cls
color 0A
echo.
echo [SYSTEM] Running Management Command...
echo.

:: This matches the filename of the script in step 2 (without .py)
python manage.py seed_assets --force

if %ERRORLEVEL% NEQ 0 (
    color 4F
    echo.
    echo [FAILURE] Command Failed.
    echo Check if 'inventory/management/commands/seed_assets.py' exists.
    pause
) else (
    echo.
    echo [SUCCESS] Done.
    pause
)