@echo off
TITLE AlgoTech Trading Engine
COLOR 0B

echo ==================================================
echo           Starting AlgoTech Trading Engine...
echo ==================================================
echo.
echo Do not close this black window (Terminal).
echo It runs the background logic for the Trading App.
echo.

python src/main.py

echo.
echo ==================================================
echo           Application Closed or Crashed
echo ==================================================
pause
