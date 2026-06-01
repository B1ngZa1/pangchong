@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    PangChong E-Commerce - Start
echo ========================================
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Install Docker Desktop first.
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose not found.
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo [OK] Docker environment ready.
echo.

:: Change to project directory
cd /d "%~dp0"

:: .env is optional for Docker. Compose uses local defaults when it is absent.
if not exist ".env" (
    echo [INFO] .env not found; using local Docker defaults from docker-compose.yml.
    echo [INFO] To customize secrets or service settings, copy .env.example to .env first.
    echo.
)

echo [INFO] Building and starting services...
echo [INFO] First run may take a few minutes to download images.
echo.

:: Build and start all services
%COMPOSE_CMD% up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Startup failed. Check the error messages above.
    echo.
    echo Troubleshooting:
    echo   1. Port in use - Check ports 5432/6379/8000/3000
    echo   2. Not enough memory - Increase Docker Desktop memory
    echo   3. Network issue - Check internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Startup Successful!
echo ========================================
echo.
echo  Frontend:     http://localhost:3000
echo  Backend API:  http://localhost:8000
echo  API Docs:     http://localhost:8000/docs
echo  Database:     localhost:5432
echo  Redis:        localhost:6379
echo.
echo  Test Accounts:
echo  User:    testuser / test123456
echo  Admin:   admin / test123456
echo.
echo ========================================
echo.

:: Ask to open browser
set /p openBrowser="Open browser? (Y/N): "
if /i "%openBrowser%"=="Y" (
    start http://localhost:3000
    timeout /t 2 >nul
    start http://localhost:8000/docs
)

echo.
echo Common Commands:
echo   View logs:    %COMPOSE_CMD% logs -f
echo   Stop:         %COMPOSE_CMD% down
echo   Restart:      %COMPOSE_CMD% restart
echo   Status:       %COMPOSE_CMD% ps
echo.
pause
