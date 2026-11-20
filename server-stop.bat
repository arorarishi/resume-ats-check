@echo off
title ATS Resume Tracker - Stop Server
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server-stop.ps1"
pause
