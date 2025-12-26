@echo off
echo Launching PRIME Control Panel...
:: This launches the script minimized
if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF

:minimized
call venv\Scripts\activate
python control_center.py