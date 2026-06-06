"""Benchmark suite configuration and constants."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from solver import default_dictionary_path
from solver.strategies import WordleStrategies

STRATEGY_COLORS = ("#538d4e", "#b59f3b", "#5a7fb5", "#c45c5c", "#8e6bad", "#c97d4a", "#6b8e9f")

FIXED_ENTROPY_OPENER = "acero"
DEFAULT_BENCHMARK_WORDS_PATH = default_dictionary_path().parent / "benchmark_words.json"
DEFAULT_BELIEF_THRESHOLD = WordleStrategies.DEFAULT_BELIEF_THRESHOLD
RESULTS_FILENAME = "results.json"
PLOT_FILENAME = "benchmark.png"


@dataclass(frozen=True, slots=True)
class BenchmarkStrategy:
    """One strategy row in the benchmark suite."""

    strategy_id: str
    label: str
    opening_word: str | None = None
    belief_threshold: int | None = None


BENCHMARK_STRATEGIES: tuple[BenchmarkStrategy, ...] = (
    BenchmarkStrategy("full-entropy", "Full entropy"),
    BenchmarkStrategy(
        "fixed-entropy",
        "Fixed + entropy",
        opening_word=FIXED_ENTROPY_OPENER,
    ),
    BenchmarkStrategy(
        "entropy-threshold-bellman",
        "Entropy + threshold Bellman",
        belief_threshold=20,
    ),
    BenchmarkStrategy(
        "entropy-hard-bellman",
        "Entropy + hard Bellman",
        belief_threshold=20,
    ),
    BenchmarkStrategy(
        "entropy-hard-bellman",
        "Entropy + hard Bellman",
        belief_threshold=50,
    ),
    BenchmarkStrategy(
        "entropy-hard-bellman",
        "Entropy + hard Bellman",
        belief_threshold=100,
    ),
)


@dataclass
class BenchmarkConfig:
    dictionary: Path
    num_secrets: int = 100
    max_secrets: int = 0
    max_guesses: int = 6
    output_dir: Path = Path("outputs")
    seed: int = 42
    persist: bool = True
    fixed_opener: str = FIXED_ENTROPY_OPENER
    benchmark_words_path: Path = DEFAULT_BENCHMARK_WORDS_PATH
    resample_words: bool = False
    force_rerun: bool = False
