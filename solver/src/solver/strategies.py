"""Central registry of solver strategies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from solver.model.base import BaseModel
from solver.model.entropy import EntropyModel
from solver.model.hard_bellman import HardBellmanModel
from solver.model.hybrid import OpenerHardBellmanModel, OpenerThresholdBellmanModel
from solver.model.threshold_bellman import DEFAULT_BELIEF_THRESHOLD, ThresholdBellmanModel

THRESHOLD_BELLMAN_WARNING = (
    "Can be very slow when |B| is below the threshold — expect long waits between suggestions."
)


@dataclass(frozen=True, slots=True)
class StrategySpec:
    """Metadata for one selectable solver strategy."""

    id: str
    base_id: str
    label: str
    description: str
    requires_opening_word: bool = False
    belief_threshold: int | None = None
    warning: str | None = None
    highlight: str | None = None


def parse_strategy_id(strategy_id: str) -> tuple[str, int | None]:
    """Split a registry id into base strategy and optional belief threshold."""
    key = strategy_id.strip().lower()
    if "@" in key:
        base_id, suffix = key.rsplit("@", 1)
        return base_id, int(suffix)
    return key, None


def strategy_report_key(base_id: str, belief_threshold: int | None) -> str:
    if belief_threshold is not None and "bellman" in base_id:
        return f"{base_id}@{belief_threshold}"
    return base_id


class WordleStrategies:
    """Registry and factory for all solver strategies."""

    DEFAULT_ID = "entropy-threshold-bellman"
    DEFAULT_OPENING_WORD = "cario"
    DEFAULT_BELIEF_THRESHOLD = DEFAULT_BELIEF_THRESHOLD

    _BASE_SPECS: dict[str, StrategySpec] = {
        "full-entropy": StrategySpec(
            id="full-entropy",
            base_id="full-entropy",
            label="Full entropy",
            description="Greedy entropy every turn.",
        ),
        "fixed-entropy": StrategySpec(
            id="fixed-entropy",
            base_id="fixed-entropy",
            label="Fixed + entropy",
            description="Fixed opener, then entropy.",
            requires_opening_word=True,
        ),
        "entropy-threshold-bellman": StrategySpec(
            id="entropy-threshold-bellman",
            base_id="entropy-threshold-bellman",
            label="Entropy + threshold Bellman",
            description="Entropy, then exact Bellman DP.",
            belief_threshold=DEFAULT_BELIEF_THRESHOLD,
            warning=THRESHOLD_BELLMAN_WARNING,
            highlight="best",
        ),
        "entropy-hard-bellman": StrategySpec(
            id="entropy-hard-bellman",
            base_id="entropy-hard-bellman",
            label="Entropy + hard Bellman",
            description="Entropy, then hard-mode Bellman.",
            belief_threshold=DEFAULT_BELIEF_THRESHOLD,
        ),
    }

    _HARD_BELLMAN_THRESHOLDS: tuple[int, ...] = (20, 50, 100)

    @classmethod
    def _catalog(cls) -> tuple[StrategySpec, ...]:
        items: list[StrategySpec] = [
            cls._BASE_SPECS["full-entropy"],
            cls._BASE_SPECS["fixed-entropy"],
            cls._BASE_SPECS["entropy-threshold-bellman"],
        ]
        base = cls._BASE_SPECS["entropy-hard-bellman"]
        for threshold in cls._HARD_BELLMAN_THRESHOLDS:
            items.append(
                StrategySpec(
                    id=strategy_report_key("entropy-hard-bellman", threshold),
                    base_id=base.base_id,
                    label=f"{base.label} ({threshold})",
                    description=base.description,
                    belief_threshold=threshold,
                    highlight="fast" if threshold == 50 else None,
                )
            )
        return tuple(items)

    @classmethod
    def ids(cls) -> tuple[str, ...]:
        return tuple(spec.id for spec in cls._catalog())

    @classmethod
    def get(cls, strategy_id: str) -> StrategySpec:
        key = strategy_id.strip().lower()
        for spec in cls._catalog():
            if spec.id == key:
                return spec

        base_id, threshold = parse_strategy_id(key)
        if threshold is None and base_id in cls._BASE_SPECS:
            return cls._BASE_SPECS[base_id]

        raise ValueError(f"unknown strategy: {strategy_id!r}")

    @classmethod
    def resolve_threshold(cls, strategy_id: str) -> int:
        spec = cls.get(strategy_id)
        if spec.belief_threshold is not None:
            return spec.belief_threshold
        _, threshold = parse_strategy_id(strategy_id)
        if threshold is not None:
            return threshold
        return cls.DEFAULT_BELIEF_THRESHOLD

    @classmethod
    def list(cls) -> list[dict[str, Any]]:
        """JSON-serializable catalog for APIs and frontends."""
        return [
            {
                "id": spec.id,
                "label": spec.label,
                "description": spec.description,
                "requires_opening_word": spec.requires_opening_word,
                "default_opening_word": (
                    cls.DEFAULT_OPENING_WORD if spec.requires_opening_word else None
                ),
                "belief_threshold": spec.belief_threshold,
                "warning": spec.warning,
                "highlight": spec.highlight,
            }
            for spec in cls._catalog()
        ]

    @classmethod
    def create_model(
        cls,
        strategy_id: str = DEFAULT_ID,
        *,
        pattern_table=None,
        all_words: Sequence[str] | None = None,
        dictionary_path: Path | str | None = None,
        length: int = 5,
        persist: bool = True,
        show_progress: bool = True,
        opening_word: str | None = None,
        belief_threshold: int | None = None,
    ) -> BaseModel:
        spec = cls.get(strategy_id)
        base_id = spec.base_id
        threshold = (
            belief_threshold
            if belief_threshold is not None
            else cls.resolve_threshold(strategy_id)
        )

        if base_id == "full-entropy":
            return EntropyModel(pattern_table=pattern_table, all_words=all_words)

        if all_words is None:
            raise ValueError(f"{base_id} requires all_words")

        if base_id == "fixed-entropy":
            word = (opening_word or cls.DEFAULT_OPENING_WORD).lower()
            return EntropyModel(
                pattern_table=pattern_table,
                first_word=word,
                all_words=all_words,
            )

        if base_id == "entropy-hard-bellman":
            return OpenerHardBellmanModel(
                all_words,
                pattern_table=pattern_table,
                length=length,
                dictionary_path=dictionary_path,
                persist=persist,
                show_progress=show_progress,
                threshold=threshold,
            )

        if base_id == "entropy-threshold-bellman":
            return OpenerThresholdBellmanModel(
                all_words,
                pattern_table=pattern_table,
                length=length,
                dictionary_path=dictionary_path,
                persist=persist,
                show_progress=show_progress,
                threshold=threshold,
            )

        raise ValueError(f"unknown strategy: {strategy_id!r}")

    @classmethod
    def flush(cls, model: BaseModel) -> None:
        """Persist Bellman memoization when the model uses it."""
        if isinstance(model, ThresholdBellmanModel):
            model.flush_cache()
        elif isinstance(model, HardBellmanModel):
            model.flush_cache()
        elif isinstance(model, OpenerThresholdBellmanModel):
            model.flush_cache()
        elif isinstance(model, OpenerHardBellmanModel):
            model.flush_cache()
