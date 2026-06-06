"""Wordle scoring models: entropy, Bellman variants, and hybrid openers."""

from __future__ import annotations

from solver.model.base import BaseModel
from solver.model.entropy import EntropyModel
from solver.model.hard_bellman import HardBellmanModel
from solver.model.hybrid import OpenerHardBellmanModel, OpenerThresholdBellmanModel
from solver.model.threshold_bellman import DEFAULT_BELIEF_THRESHOLD, ThresholdBellmanModel
from solver.strategies import WordleStrategies

# Backward-compatible default (entropy).
WordleModel = EntropyModel

__all__ = [
    "BaseModel",
    "DEFAULT_BELIEF_THRESHOLD",
    "EntropyModel",
    "HardBellmanModel",
    "OpenerHardBellmanModel",
    "OpenerThresholdBellmanModel",
    "ThresholdBellmanModel",
    "WordleModel",
    "WordleStrategies",
]
