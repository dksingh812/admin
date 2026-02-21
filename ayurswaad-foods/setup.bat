@echo off
echo ===================================================
echo     Ayurswaad Foods - One-Click Setup (Windows)
echo ===================================================

cd /d "%~dp0"

echo.
echo [1/4] Cleaning Previous Installation...
if exist node_modules (
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)

echo.
echo [2/4] Installing Dependencies...
call npm install

echo.
echo [3/4] Generating Database Client...
call npx prisma generate

echo.
echo [4/4] Updating Database Schema & Seeding...
call npx prisma db push
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
