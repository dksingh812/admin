@echo off
TITLE AlgoTech Debug Mode
COLOR 0C

:: Ensure correct directory
cd /d "%~dp0"

echo ==================================================
echo           AlgoTech Debug Mode
echo ==================================================
echo.
echo Running the application in Verbose Mode...
echo Output is being saved to 'debug_output.txt'
echo.

python -m src.main > debug_output.txt 2>&1

echo.
echo ==================================================
echo           Execution Finished
echo ==================================================
echo.
echo Please check the file 'debug_output.txt' in this folder.
echo It contains the error details.
echo.
pause
