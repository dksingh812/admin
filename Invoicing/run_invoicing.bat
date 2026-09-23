@echo off
echo Checking for pip...
python -m ensurepip --default-pip >nul 2>&1
if %errorlevel% neq 0 (
    echo "ensurepip" failed, attempting to download get-pip.py...
    curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

echo Installing required dependencies...
python -m pip install reportlab pywhatsapp pyautogui num2words

echo.
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
