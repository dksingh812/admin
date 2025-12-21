@echo off
TITLE AlgoTech Valuation Dashboard Setup
COLOR 0A

:: Ensure we are running in the directory where this file is located
cd /d "%~dp0"

echo ==================================================
echo      Valuation Dashboard - One-Time Setup
echo ==================================================
echo.
echo This script will install the necessary libraries for
echo the Valuation Dashboard (Streamlit, YFinance, Plotly).
echo.
pause

echo.
echo [1/1] Installing dependencies...
if exist valuation_tool\requirements.txt (
    pip install -r valuation_tool\requirements.txt
) else (
    echo.
    echo ERROR: valuation_tool\requirements.txt not found!
    echo Please make sure the 'valuation_tool' folder is present.
    pause
    exit /b
)

echo.
echo ==================================================
echo                Setup Complete!
echo ==================================================
echo You can now run the dashboard using 'run_valuation.bat'
echo.
pause
