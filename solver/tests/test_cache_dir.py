from pathlib import Path

from solver.data.cache.base import get_cache_dir


def test_get_cache_dir_defaults_to_cache_subdir(tmp_path: Path) -> None:
    cache_dir = get_cache_dir(tmp_path)
    assert cache_dir == tmp_path / "cache"
    assert cache_dir.is_dir()


def test_get_cache_dir_honors_env_override(tmp_path: Path, monkeypatch) -> None:
    override = tmp_path / "custom"
    monkeypatch.setenv("WORDLE_CACHE_DIR", str(override))
    assert get_cache_dir(tmp_path / "data") == override
    assert override.is_dir()
