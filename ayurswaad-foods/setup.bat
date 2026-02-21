@echo off
echo ===================================================
echo     Ayurswaad Foods - One-Click Setup (Windows)
echo ===================================================

cd /d "%~dp0"

echo.
echo [1/3] Installing Dependencies...
call npm install

echo.
echo [2/3] Setting up Database (SQLite)...
call npx prisma db push

echo.
echo [3/3] Seeding Initial Data...
call node prisma/seed.js

echo.
echo ===================================================
echo           SETUP COMPLETE!
echo ===================================================
echo.
echo To start the website, run: npm run dev
echo Then open http://localhost:3000 in your browser.
echo.
pause
