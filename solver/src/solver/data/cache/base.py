"""Cache directory helpers."""

from __future__ import annotations

import os
from pathlib import Path


def get_cache_dir(data_dir: Path) -> Path:
    """Return the directory for pickle caches (override with WORDLE_CACHE_DIR)."""
    override = os.environ.get("WORDLE_CACHE_DIR")
    if override:
        path = Path(override)
        path.mkdir(parents=True, exist_ok=True)
        return path
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
