@echo off
title Resume ATS Check - Start Server
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server-start.ps1"
if errorlevel 1 (
    echo.
    echo Failed to start the server.
)
pause
