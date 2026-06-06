"""Hybrid strategies: entropy on turn 1, then threshold or hard Bellman."""

from __future__ import annotations

from collections.abc import Sequence

from solver.model.base import BaseModel
from solver.model.entropy import EntropyModel
from solver.model.hard_bellman import HardBellmanModel
from solver.model.threshold_bellman import DEFAULT_BELIEF_THRESHOLD, ThresholdBellmanModel


class OpenerHardBellmanModel(BaseModel):
    """Entropy opening guess, then hard-mode threshold Bellman."""

    def __init__(
        self,
        all_words: Sequence[str],
        *,
        bellman: HardBellmanModel | None = None,
        pattern_table=None,
        length: int = 5,
        dictionary_path=None,
        data_dir=None,
        persist: bool = True,
        show_progress: bool = True,
        threshold: int = DEFAULT_BELIEF_THRESHOLD,
    ) -> None:
        super().__init__(pattern_table=pattern_table)
        self.all_words = tuple(all_words)
        self._entropy = EntropyModel(pattern_table=pattern_table, all_words=all_words)
        self._bellman = bellman or HardBellmanModel(
            all_words,
            pattern_table=pattern_table,
            length=length,
            dictionary_path=dictionary_path,
            data_dir=data_dir,
            persist=persist,
            show_progress=show_progress,
            threshold=threshold,
        )

    @property
    def bellman(self) -> HardBellmanModel:
        return self._bellman

    def flush_cache(self) -> None:
        self._bellman.flush_cache()

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        pool = guesses if guesses is not None else self.all_words
        if not history:
            return self._entropy.best_guess(candidates, pool, history=history)
        return self._bellman.best_guess(candidates, pool, history=history)


class OpenerThresholdBellmanModel(BaseModel):
    """Entropy opening guess, then threshold Bellman."""

    def __init__(
        self,
        all_words: Sequence[str],
        *,
        bellman: ThresholdBellmanModel | None = None,
        pattern_table=None,
        length: int = 5,
        dictionary_path=None,
        data_dir=None,
        persist: bool = True,
        show_progress: bool = True,
        threshold: int = DEFAULT_BELIEF_THRESHOLD,
    ) -> None:
        super().__init__(pattern_table=pattern_table)
        self.all_words = tuple(all_words)
        self._entropy = EntropyModel(pattern_table=pattern_table, all_words=all_words)
        self._bellman = bellman or ThresholdBellmanModel(
            all_words,
            pattern_table=pattern_table,
            length=length,
            dictionary_path=dictionary_path,
            data_dir=data_dir,
            persist=persist,
            show_progress=show_progress,
            threshold=threshold,
        )

    @property
    def bellman(self) -> ThresholdBellmanModel:
        return self._bellman

    def flush_cache(self) -> None:
        self._bellman.flush_cache()

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        pool = guesses if guesses is not None else self.all_words
        if not history:
            return self._entropy.best_guess(candidates, pool, history=history)
        return self._bellman.best_guess(candidates, pool, history=history)
