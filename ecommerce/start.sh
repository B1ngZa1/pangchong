#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

echo "========================================"
echo "  Pangchong ecommerce - one-click start"
echo "========================================"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker was not found. Please install Docker first:"
  echo "https://docs.docker.com/get-docker/"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[ERROR] Docker Compose was not found."
  exit 1
fi

echo "[INFO] Docker is ready."
echo "[INFO] Using: ${COMPOSE_CMD[*]}"
echo

if [ ! -f ".env" ]; then
  echo "[INFO] No .env file found. Docker Compose will use the defaults in docker-compose.yml."
  echo "[INFO] Copy .env.example to .env only if you need to override passwords, JWT secret, CORS, or third-party keys."
  echo
fi

echo "[INFO] Building and starting services..."
echo "[INFO] The first run may take a while while images are downloaded."
echo

if ! "${COMPOSE_CMD[@]}" up -d --build; then
  echo
  echo "[ERROR] Startup failed. Please check the log above."
  echo
  echo "Common checks:"
  echo "  1. Port conflicts: 5432, 6379, 8000, 3000"
  echo "  2. Docker memory is too low"
  echo "  3. Image download/network issues"
  exit 1
fi

echo "[INFO] Waiting for backend and frontend health checks..."
ready=false
for ((attempt = 1; attempt <= 90; attempt += 1)); do
  backend_health="$(docker inspect --format '{{.State.Health.Status}}' pangchong-backend 2>/dev/null || true)"
  frontend_health="$(docker inspect --format '{{.State.Health.Status}}' pangchong-frontend 2>/dev/null || true)"
  if [[ "${backend_health}" == "healthy" && "${frontend_health}" == "healthy" ]]; then
    ready=true
    break
  fi
  sleep 2
done

if [[ "${ready}" != "true" ]]; then
  echo
  echo "[ERROR] Services did not become healthy within 180 seconds."
  "${COMPOSE_CMD[@]}" ps
  "${COMPOSE_CMD[@]}" logs --tail 80 backend frontend
  exit 1
fi

echo
echo "========================================"
echo "  Started successfully"
echo "========================================"
echo
echo "Frontend:   http://localhost:3000"
echo "Backend:    http://localhost:8000"
echo "API docs:   http://localhost:8000/docs"
echo "PostgreSQL: localhost:5432"
echo "Redis:      localhost:6379"
echo
echo "Test accounts:"
echo "  testuser / test123456"
echo "  admin    / test123456"
echo
echo "========================================"
echo

open_browser=""
if [[ -t 0 ]]; then
  read -r -p "Open browser? (y/n): " open_browser || true
fi
if [[ "${open_browser}" =~ ^[Yy]$ ]]; then
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000 >/dev/null 2>&1 || true
    sleep 2
    xdg-open http://localhost:8000/docs >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open http://localhost:3000
    sleep 2
    open http://localhost:8000/docs
  fi
fi

echo
echo "Useful commands:"
echo "  View logs:   ${COMPOSE_CMD[*]} logs -f"
echo "  Stop stack:  ${COMPOSE_CMD[*]} down"
echo "  Restart:     ${COMPOSE_CMD[*]} restart"
echo "  Status:      ${COMPOSE_CMD[*]} ps"
echo "  Remove data: ${COMPOSE_CMD[*]} down -v"
echo
