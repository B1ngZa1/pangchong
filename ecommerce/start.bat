@echo off
setlocal EnableExtensions

chcp 65001 >nul
pushd "%~dp0"

echo ========================================
echo   Pangchong ecommerce - one-click start
echo ========================================
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker was not found. Please install Docker Desktop first:
    echo https://www.docker.com/products/docker-desktop/
    pause
    popd
    exit /b 1
)

set "COMPOSE_CMD="
docker compose version >nul 2>&1
if not errorlevel 1 set "COMPOSE_CMD=docker compose"

if not defined COMPOSE_CMD (
    docker-compose --version >nul 2>&1
    if not errorlevel 1 set "COMPOSE_CMD=docker-compose"
)

if not defined COMPOSE_CMD (
    echo [ERROR] Docker Compose was not found.
    echo Please install Compose v2 or make sure docker-compose is available.
    pause
    popd
    exit /b 1
)

echo [INFO] Docker is ready.
echo [INFO] Using: %COMPOSE_CMD%
echo.

if not exist ".env" (
    echo [INFO] No .env file found. Docker Compose will use the defaults in docker-compose.yml.
    echo [INFO] Copy .env.example to .env only if you need to override passwords, JWT secret, CORS, or third-party keys.
    echo.
)

echo [INFO] Building and starting services...
echo [INFO] The first run may take a while while images are downloaded.
echo.

call %COMPOSE_CMD% up -d --build
if errorlevel 1 (
    echo.
    echo [ERROR] Startup failed. Please check the log above.
    echo.
    echo Common checks:
    echo   1. Port conflicts: 5432, 6379, 8000, 3000
    echo   2. Docker memory is too low
    echo   3. Image download/network issues
    echo.
    pause
    popd
    exit /b 1
)

echo.
echo ========================================
echo   Started successfully
echo ========================================
echo.
echo Frontend:   http://localhost:3000
echo Backend:    http://localhost:8000
echo API docs:   http://localhost:8000/docs
echo PostgreSQL: localhost:5432
echo Redis:      localhost:6379
echo.
echo Test accounts:
echo   testuser / test123456
echo   admin    / test123456
echo.
echo ========================================
echo.

set /p openBrowser="Open browser? (Y/N): "
if /i "%openBrowser%"=="Y" (
    start "" http://localhost:3000
    timeout /t 2 /nobreak >nul
    start "" http://localhost:8000/docs
)

echo.
echo Useful commands:
echo   View logs:   %COMPOSE_CMD% logs -f
echo   Stop stack:  %COMPOSE_CMD% down
echo   Restart:     %COMPOSE_CMD% restart
echo   Status:      %COMPOSE_CMD% ps
echo   Remove data: %COMPOSE_CMD% down -v
echo.
pause
popd
