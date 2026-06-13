@echo off
title Incident Reporting System - One Click Launcher
cd /d "%~dp0"
echo ============================================================
echo     INCIDENT REPORTING SYSTEM  -  one click launcher
echo ============================================================
echo.

call :isup 3306
if "%UP%"=="1" (echo [1/3] MySQL is already running. & goto mysql_ready)
echo [1/3] Starting MySQL database...
start "MySQL Server - keep this window open" cmd /k mysql\bin\mysqld --no-defaults --basedir="%~dp0mysql" --datadir="%~dp0mysql_data" --port=3306 --console
echo       waiting for the database to be ready...
call :waitport 3306
timeout /t 2 /nobreak >nul
:mysql_ready

call :isup 5000
if "%UP%"=="1" (echo [2/3] Web app is already running. & goto app_ready)
echo [2/3] Starting the web app...
start "Web App - keep this window open" cmd /k python app.py
echo       waiting for the web app...
call :waitport 5000
:app_ready

echo [3/3] Opening http://127.0.0.1:5000 in your browser...
start "" http://127.0.0.1:5000
echo.
echo ============================================================
echo  Done!  The system is running.
echo  Keep the two server windows open during your demo.
echo  Close those windows to stop the system.
echo ============================================================
timeout /t 6 >nul
exit /b

:waitport
call :isup %1
if "%UP%"=="1" goto :eof
timeout /t 1 /nobreak >nul
goto waitport

:isup
set UP=0
for /f %%a in ('netstat -an ^| findstr "LISTENING" ^| findstr /R ":%1[^0-9]"') do set UP=1
goto :eof
