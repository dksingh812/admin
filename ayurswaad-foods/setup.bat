@echo off
echo ===================================================
echo     Ayurswaad Foods - One-Click Setup (Windows)
echo ===================================================

cd /d "%~dp0"

echo.
echo [1/4] Checking Environment Configuration...
if not exist .env (
    echo DATABASE_URL="file:./dev.db" > .env
    echo .env file created.
) else (
    echo .env file already exists.
)

echo.
echo [2/4] Installing Dependencies...
call npm install

echo.
echo [3/4] Setting up Database...
call npx prisma db push

echo.
echo [4/4] Seeding Initial Data...
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
