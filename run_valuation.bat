@echo off
TITLE AlgoTech Valuation Dashboard
COLOR 0E

:: Ensure we are running in the directory where this file is located
cd /d "%~dp0"

echo ==================================================
echo           Starting Valuation Dashboard...
echo ==================================================
echo.
echo [1/2] Checking dependencies...
pip install -r valuation_tool/requirements.txt
echo.

echo [2/2] Launching Dashboard...
echo This will open your default web browser.
echo.
echo Press Ctrl+C in this window to stop the dashboard.
echo.

set PYTHONPATH=%CD%
streamlit run valuation_tool/app.py

echo.
echo ==================================================
echo           Dashboard Closed
echo ==================================================
pause
