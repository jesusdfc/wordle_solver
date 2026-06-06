"""Shared pytest configuration and fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from solver import default_dictionary_path

LEMARIO = default_dictionary_path()


@pytest.fixture
def lemario_path() -> Path:
    return LEMARIO
