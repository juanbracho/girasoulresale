@echo off
title Girasoul Business Dashboard Server
echo.
echo =========================================
echo   🌻 GIRASOUL BUSINESS DASHBOARD 🌻
echo =========================================
echo.
echo Starting server...
echo.

REM Change to the script's directory (where app.py is located)
cd /d "%~dp0"

REM Start the Flask server in background and open browser
start /b py app.py

REM Wait for server to start (3 seconds)
timeout /t 3 /nobreak >nul

REM Open Google Chrome to the dashboard
start chrome "http://127.0.0.1:5000/"

echo.
echo ✅ Server started successfully!
echo ✅ Dashboard opened in Chrome
echo.
echo 📋 Server is running at: http://127.0.0.1:5000/
echo.
echo ⚠️  KEEP THIS WINDOW OPEN while using the dashboard
echo ❌ Close this window to stop the server
echo.
echo =========================================

REM Keep the window open and wait for user to close it
pause >nul