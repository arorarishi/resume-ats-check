@echo off
title Resume ATS Check - Stop Server
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server-stop.ps1"
pause
