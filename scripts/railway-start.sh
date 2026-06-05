#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export WORDLE_CACHE_DIR="${WORDLE_CACHE_DIR:-$ROOT/data/cache}"
mkdir -p "$WORDLE_CACHE_DIR"

echo "Warming pattern cache in $WORDLE_CACHE_DIR ..."
(cd "$ROOT/backend" && uv run python -c "from app.services.game import get_pattern_table; get_pattern_table()")

echo "Starting server..."
cd "$ROOT/backend"
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-9000}"
