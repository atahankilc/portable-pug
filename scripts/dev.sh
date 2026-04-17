#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Starting Django backend + Expo web dev server..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8081"
echo ""

trap 'kill 0' SIGINT SIGTERM

(
  cd "$ROOT_DIR/backend"
  source venv/bin/activate
  DJANGO_SETTINGS_MODULE=core_api.settings.local python manage.py runserver
) &

(
  cd "$ROOT_DIR/frontend"
  npx expo start --web
) &

wait
