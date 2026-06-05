#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Building frontend..."
(cd "$ROOT/frontend" && npm ci && npm run build)

echo "Copying frontend dist to backend/static..."
rm -rf "$ROOT/backend/static"
mkdir -p "$ROOT/backend/static"
cp -r "$ROOT/frontend/dist/." "$ROOT/backend/static/"

echo "Installing Python dependencies..."
pip install uv
(cd "$ROOT/backend" && uv sync)

echo "Railway build complete."
