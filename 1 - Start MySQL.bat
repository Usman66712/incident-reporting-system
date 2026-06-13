@echo off
title MySQL Server - Incident Reporting System
cd /d "%~dp0"
echo ============================================================
echo   Starting the MySQL database server...
echo   KEEP THIS WINDOW OPEN during your demo / viva.
echo   (Close it to stop the database.)
echo ============================================================
echo.
mysql\bin\mysqld --no-defaults --basedir="%~dp0mysql" --datadir="%~dp0mysql_data" --port=3306 --console
pause
