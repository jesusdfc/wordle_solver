#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_URL="http://127.0.0.1:9000"
FRONTEND_URL="http://127.0.0.1:5173"

cleanup() {
  local pid
  for pid in "${BACKEND_PID:-}" "${FRONTEND_PID:-}"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

open_browser() {
  local url="$1"
  if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
    cmd.exe /c start "" "$url" >/dev/null 2>&1
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1
  elif [[ "${OSTYPE:-}" == darwin* ]]; then
    open "$url"
  else
    echo "Open $url in your browser"
  fi
}

wait_for_url() {
  local url="$1"
  local attempt=0
  while (( attempt < 60 )); do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then
      return 0
    fi
    sleep 0.5
    ((attempt += 1))
  done
  echo "Timed out waiting for $url" >&2
  return 1
}

echo "Installing backend dependencies..."
(cd "$ROOT/backend" && uv sync --quiet)

echo "Installing frontend dependencies..."
(cd "$ROOT/frontend" && npm install --silent)

echo "Starting backend on $BACKEND_URL ..."
(cd "$ROOT/backend" && uv run python -m uvicorn app.main:app --reload --port 9000) &
BACKEND_PID=$!

echo "Starting frontend on $FRONTEND_URL ..."
(cd "$ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "Waiting for frontend..."
wait_for_url "$FRONTEND_URL"

echo "Opening browser..."
open_browser "$FRONTEND_URL"

echo "Press Ctrl+C to stop both servers."
wait "$BACKEND_PID" "$FRONTEND_PID"
