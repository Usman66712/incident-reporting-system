@echo off
title Incident Reporting System - Web App
cd /d "%~dp0"
echo ============================================================
echo   Starting the web app...
echo   Open your browser at:  http://127.0.0.1:5000
echo   (Make sure MySQL window is already running.)
echo ============================================================
echo.
python app.py
pause
