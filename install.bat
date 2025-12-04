@echo off
TITLE AlgoTech Setup
COLOR 0A

:: Ensure we are running in the directory where this file is located
cd /d "%~dp0"

echo ==================================================
echo        AlgoTech Trading Engine - One-Time Setup
echo ==================================================
echo.
echo This script will install the necessary 'ingredients' (libraries)
echo for the software to run.
echo.
echo Working Directory: %CD%
echo.
echo Please ensure you have Python installed and added to PATH.
echo.
pause

echo.
echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/2] Installing dependencies from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo.
    echo ERROR: requirements.txt not found in this folder!
    echo Please make sure you extracted all files.
    pause
    exit /b
)

echo.
echo ==================================================
echo                Setup Complete!
echo ==================================================
echo You can now run the software using 'run.bat'
echo.
pause
