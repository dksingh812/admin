@echo off
TITLE AlgoTech Trading Engine
COLOR 0B

:: Ensure we are running in the directory where this file is located
cd /d "%~dp0"

echo ==================================================
echo           Starting AlgoTech Trading Engine...
echo ==================================================
echo.
echo Do not close this black window (Terminal).
echo It runs the background logic for the Trading App.
echo.

if exist src\main.py (
    python src\main.py
) else (
    echo.
    echo ERROR: src\main.py not found!
    echo Please make sure the 'src' folder is in this directory.
    pause
    exit /b
)

echo.
echo ==================================================
echo           Application Closed or Crashed
echo ==================================================
pause
