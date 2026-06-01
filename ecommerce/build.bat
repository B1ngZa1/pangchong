@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    PangChong E-Commerce - Build
echo ========================================
echo.

:: Change to project directory
cd /d "%~dp0"

echo [INFO] Building backend image...
docker build --network host -t pangchong-backend ./backend
if %errorlevel% neq 0 (
    echo [ERROR] Backend build failed.
    pause
    exit /b 1
)
echo [OK] Backend image built.
echo.

echo [INFO] Building frontend image...
docker build --network host -t pangchong-frontend ./frontend
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed.
    pause
    exit /b 1
)
echo [OK] Frontend image built.
echo.

echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Run start.bat to start the services.
echo.
pause
