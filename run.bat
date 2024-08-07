@echo off
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Python is installed.
    pip install flask flask_socketIO mss waitress pillow 
    python startup.py
) else (
    echo Python is not installed, installing now...
    python-3.12.4-amd64.exe
    /p Press enter to continue...
    pip install flask flask_socketIO mss waitress pillow
)

