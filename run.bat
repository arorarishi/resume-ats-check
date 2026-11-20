@echo off
title Resume ATS Check
cd /d "%~dp0"

echo [1/3] Checking Python environment...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment in .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing required packages...
    python -m pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo [2/3] Checking tray dependencies...
python -c "import pystray, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing tray icon dependencies...
    python -m pip install pystray pillow
)

echo [3/3] Launching ATS Resume Suite in the system tray...
echo A tray icon will appear ^(green = running, red = stopped^) with Start/Stop/Exit options.
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0tray_app.py"
