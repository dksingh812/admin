@echo off
echo Installing required dependencies...
python -m pip install reportlab pywhatsapp pyautogui
echo Starting Parigantavya Invoicing Application...
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo ----------------------------------------------------
    echo AN ERROR OCCURRED WHILE STARTING THE APPLICATION!
    echo Please take a screenshot of this window and send it.
    echo ----------------------------------------------------
)
pause
