"""Run benchmark strategies and write results.json."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from tqdm import tqdm

from solver.agent import WordleAgent
from solver.cli.benchmark.cache import load_cached_strategy_reports, write_results
from solver.cli.benchmark.config import BENCHMARK_STRATEGIES, BenchmarkConfig, BenchmarkStrategy
from solver.cli.benchmark.labels import (
    benchmark_report_key,
    benchmark_strategy_params,
    report_belief_threshold,
)
from solver.cli.benchmark.types import GameResult, StrategyReport
from solver.cli.benchmark.words import load_or_create_benchmark_words
from solver.data import PatternTable
from solver.strategies import WordleStrategies


def play_game(
    agent: WordleAgent,
    secret: str,
    *,
    pattern_table: PatternTable,
    max_guesses: int,
) -> GameResult:
    """Play one Wordle episode, reusing *agent* and resetting belief between games."""
    agent.reset()
    guesses = 0
    solved = False

    for _ in range(max_guesses):
        if agent.belief.is_solved():
            guess = agent.candidates[0]
        elif agent.belief.is_empty():
            break
        else:
            guess = agent.suggest()

        pattern = pattern_table.pattern(secret, guess)
        guesses += 1
        agent.update(guess, pattern)

        if guess == secret:
            solved = True
            break
        if agent.belief.is_empty():
            break

    return GameResult(secret=secret, guesses=guesses, solved=solved)


def run_strategy(
    entry: BenchmarkStrategy,
    secrets: tuple[str, ...],
    all_words: tuple[str, ...],
    *,
    pattern_table: PatternTable,
    dictionary: Path,
    max_guesses: int,
    persist: bool,
    fixed_opener: str,
) -> StrategyReport:
    opening_word = entry.opening_word
    if entry.strategy_id == "fixed-entropy":
        opening_word = fixed_opener

    agent = WordleAgent(
        all_words,
        strategy=entry.strategy_id,
        pattern_table=pattern_table,
        dictionary_path=dictionary,
        persist=persist and "bellman" in entry.strategy_id,
        show_progress=False,
        opening_word=opening_word,
        belief_threshold=entry.belief_threshold,
    )
    first_word = agent.suggest()
    agent.reset()

    started = time.perf_counter()
    results: list[GameResult] = []
    desc = benchmark_report_key(entry.strategy_id, entry.belief_threshold)
    bar = tqdm(
        secrets,
        desc=f"benchmark {desc}",
        unit=" words",
    )
    for secret in bar:
        result = play_game(
            agent,
            secret,
            pattern_table=pattern_table,
            max_guesses=max_guesses,
        )
        results.append(result)
        solved = sum(1 for item in results if item.solved)
        bar.set_postfix(
            mean=f"{sum(item.guesses for item in results) / len(results):.2f}",
            solved=solved,
            refresh=False,
        )

    if persist and "bellman" in entry.strategy_id:
        WordleStrategies.flush(agent.model)

    return StrategyReport(
        strategy_id=entry.strategy_id,
        label=entry.label,
        games=results,
        first_word=first_word,
        elapsed_seconds=time.perf_counter() - started,
        belief_threshold=entry.belief_threshold,
    )


def summarize_report(report: StrategyReport) -> dict[str, Any]:
    threshold = report_belief_threshold(report)
    params = benchmark_strategy_params(report.strategy_id, belief_threshold=threshold)
    base = {
        "strategy": report.strategy_id,
        "report_key": benchmark_report_key(report.strategy_id, report.belief_threshold),
        "label": report.label,
        "first_word": report.first_word,
        **params,
    }
    if report.belief_threshold is not None:
        base["belief_threshold"] = report.belief_threshold
    if not report.games:
        return {
            **base,
            "count": 0,
            "solve_rate": 0.0,
            "mean_guesses": 0.0,
        }

    solved = [game for game in report.games if game.solved]
    return {
        **base,
        "count": len(report.games),
        "solve_rate": len(solved) / len(report.games),
        "mean_guesses": sum(game.guesses for game in report.games) / len(report.games),
        "mean_guesses_solved": (
            sum(game.guesses for game in solved) / len(solved) if solved else 0.0
        ),
        "elapsed_seconds": round(report.elapsed_seconds, 3),
        "games": [
            {
                "secret": game.secret,
                "guesses": game.guesses,
                "solved": game.solved,
            }
            for game in report.games
        ],
    }


def build_summary(
    reports: list[StrategyReport],
    secrets: tuple[str, ...],
    config: BenchmarkConfig,
    *,
    dictionary_size: int,
    elapsed_seconds: float,
) -> dict[str, Any]:
    return {
        "dictionary_size": dictionary_size,
        "num_secrets": config.num_secrets,
        "secrets_played": len(secrets),
        "benchmark_words_path": str(config.benchmark_words_path),
        "benchmark_words": list(secrets),
        "max_guesses": config.max_guesses,
        "persist": config.persist,
        "fixed_opener": config.fixed_opener,
        "strategies": [summarize_report(report) for report in reports],
        "elapsed_seconds": round(elapsed_seconds, 2),
    }


def run_study(
    config: BenchmarkConfig,
    *,
    table: PatternTable,
    progress: bool = True,
) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    all_words = table.words
    secrets = load_or_create_benchmark_words(
        config.benchmark_words_path,
        all_words,
        num_secrets=config.num_secrets,
        seed=config.seed,
        resample=config.resample_words,
    )
    if config.max_secrets > 0:
        secrets = secrets[: config.max_secrets]

    if progress:
        print(f"Dictionary: {len(all_words)} words")
        print(f"Benchmark words: {config.benchmark_words_path.resolve()}")
        print(f"Secrets played: {len(secrets)}")
        print(f"Bellman persist: {config.persist}")
        print(f"Fixed opener: {config.fixed_opener}")
        print(f"Output: {output_dir.resolve()}")
        if config.force_rerun:
            print("Force rerun: yes (ignoring cached strategy results)")

    cached_reports = (
        {}
        if config.force_rerun
        else load_cached_strategy_reports(
            output_dir,
            secrets,
            config,
            dictionary_size=len(all_words),
        )
    )

    reports: list[StrategyReport] = []
    for entry in BENCHMARK_STRATEGIES:
        cache_key = benchmark_report_key(entry.strategy_id, entry.belief_threshold)
        cached = cached_reports.get(cache_key)
        if cached is not None:
            if progress:
                print(f"\n{entry.label} ({cache_key})... skipped (cached)")
            reports.append(cached)
        else:
            if progress:
                print(f"\n{entry.label} ({cache_key})...")
            reports.append(
                run_strategy(
                    entry,
                    secrets,
                    all_words,
                    pattern_table=table,
                    dictionary=config.dictionary,
                    max_guesses=config.max_guesses,
                    persist=config.persist,
                    fixed_opener=config.fixed_opener,
                )
            )

        write_results(
            output_dir,
            build_summary(
                reports,
                secrets,
                config,
                dictionary_size=len(all_words),
                elapsed_seconds=time.perf_counter() - started,
            ),
        )

    summary = build_summary(
        reports,
        secrets,
        config,
        dictionary_size=len(all_words),
        elapsed_seconds=time.perf_counter() - started,
    )
    write_results(output_dir, summary)

    if progress:
        for stats in summary["strategies"]:
            print(
                f"  {stats['label']} [{stats['first_word']}]: mean={stats['mean_guesses']:.3f} "
                f"solve_rate={stats['solve_rate']:.1%} "
                f"time={stats.get('elapsed_seconds', 0):.2f}s"
            )
        print(f"Done in {summary['elapsed_seconds']}s")

    return {"summary": summary, "reports": reports}
