"""Benchmark plots generated from results.json."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.table import Table

from solver.cli.benchmark.cache import load_results, results_path
from solver.cli.benchmark.config import PLOT_FILENAME, STRATEGY_COLORS
from solver.cli.benchmark.labels import stats_plot_label

_GRID_COLOR = "#d8dee9"
_AXIS_COLOR = "#4c566a"
_HEADER_BG = "#2e3440"
_HEADER_FG = "#eceff4"
_ROW_EVEN = "#f8f9fb"
_ROW_ODD = "#ffffff"
_TABLE_EDGE = "#cbd5e1"
_MIN_LOG_TIME = 0.01


def _opening_word_table(strategies: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [stats_plot_label(stats), stats.get("first_word", "")]
        for stats in strategies
    ]


def _style_bar_axes(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=_GRID_COLOR, linestyle="-", linewidth=0.8, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_AXIS_COLOR)
    ax.spines["bottom"].set_color(_AXIS_COLOR)
    ax.tick_params(axis="both", colors=_AXIS_COLOR, labelsize=9)
    ax.tick_params(axis="x", labelrotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")


def _log_time_floor(times: list[float]) -> float:
    positive = [time for time in times if time > 0]
    if not positive:
        return _MIN_LOG_TIME
    return max(min(positive) / 10, _MIN_LOG_TIME)


def _style_table(table: Table, *, colors: tuple[str, ...]) -> None:
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.55)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(_TABLE_EDGE)
        cell.set_linewidth(0.9)
        cell.set_height(0.12)

        if row == 0:
            cell.set_facecolor(_HEADER_BG)
            cell.set_text_props(color=_HEADER_FG, weight="bold", fontsize=8)
            continue

        cell.set_facecolor(_ROW_EVEN if row % 2 == 0 else _ROW_ODD)
        if col == 0:
            color = colors[(row - 1) % len(colors)]
            cell.set_text_props(color=color, weight="bold", fontsize=7.5)
        elif col == 1:
            cell.set_text_props(family="monospace", fontsize=8, weight="medium")


def _strategy_entries(strategies: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any], str]]:
    """Return (original_index, stats, color) for each strategy."""
    return [
        (index, stats, STRATEGY_COLORS[index % len(STRATEGY_COLORS)])
        for index, stats in enumerate(strategies)
    ]


def _sorted_for_means(entries: list[tuple[int, dict[str, Any], str]]) -> list[tuple[int, dict[str, Any], str]]:
    return sorted(entries, key=lambda item: item[1]["mean_guesses"])


def _sorted_for_times(entries: list[tuple[int, dict[str, Any], str]]) -> list[tuple[int, dict[str, Any], str]]:
    return sorted(entries, key=lambda item: item[1].get("elapsed_seconds", 0.0))


def _plot_mean_guesses(ax: plt.Axes, entries: list[tuple[int, dict[str, Any], str]]) -> None:
    labels = [stats_plot_label(stats) for _, stats, _ in entries]
    means = [stats["mean_guesses"] for _, stats, _ in entries]
    colors = [color for _, _, color in entries]
    x_positions = range(len(labels))

    ax.bar(
        x_positions,
        means,
        color=colors,
        edgecolor="white",
        linewidth=1.2,
        width=0.72,
        zorder=3,
    )
    ax.set_xticks(list(x_positions), labels)
    ax.set_ylabel("Mean guesses (max 6)", fontsize=10, color=_AXIS_COLOR)
    ax.set_title("Average guesses", fontsize=11, fontweight="bold", color=_HEADER_BG, pad=12)
    ax.set_ylim(0, max(6.0, max(means) * 1.12 if means else 6.0))
    _style_bar_axes(ax)
    for index, mean in enumerate(means):
        ax.text(
            index,
            mean + 0.06,
            f"{mean:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=_HEADER_BG,
        )


def _plot_wall_clock(ax: plt.Axes, entries: list[tuple[int, dict[str, Any], str]]) -> None:
    labels = [stats_plot_label(stats) for _, stats, _ in entries]
    times = [stats.get("elapsed_seconds", 0.0) for _, stats, _ in entries]
    colors = [color for _, _, color in entries]
    x_positions = range(len(labels))

    time_floor = _log_time_floor(times)
    plot_times = [max(time, time_floor) for time in times]
    bars = ax.bar(
        x_positions,
        plot_times,
        color=colors,
        edgecolor="white",
        linewidth=1.2,
        width=0.72,
        zorder=3,
    )
    ax.set_xticks(list(x_positions), labels)
    ax.set_yscale("log", base=10)
    ax.set_ylabel("Elapsed time (seconds, log₁₀)", fontsize=10, color=_AXIS_COLOR)
    ax.set_title("Wall-clock time", fontsize=11, fontweight="bold", color=_HEADER_BG, pad=12)
    ymax = max(plot_times) if plot_times else time_floor
    ax.set_ylim(
        time_floor * 0.8,
        ymax * (10 ** math.ceil(math.log10(max(ymax / time_floor, 1.5)))),
    )
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _: f"{value:g}"))
    _style_bar_axes(ax)
    for bar, elapsed, plotted in zip(bars, times, plot_times, strict=True):
        label = f"{elapsed:.2f}s" if elapsed >= 0.01 else "<0.01s"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            plotted * 1.15,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=_HEADER_BG,
        )


def plot_benchmark(
    summary: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Write benchmark.png from a results.json summary dict."""
    output_dir.mkdir(parents=True, exist_ok=True)
    strategies = summary["strategies"]
    secrets_played = summary["secrets_played"]
    entries = _strategy_entries(strategies)

    fig, (ax_means, ax_times, ax_table) = plt.subplots(
        1,
        3,
        figsize=(max(15, len(strategies) * 4.2), 5.2),
    )
    fig.patch.set_facecolor("#ffffff")

    _plot_mean_guesses(ax_means, _sorted_for_means(entries))
    _plot_wall_clock(ax_times, _sorted_for_times(entries))

    table_colors = [color for _, _, color in entries]
    ax_table.axis("off")
    table = ax_table.table(
        cellText=_opening_word_table(strategies),
        colLabels=["Strategy", "Opening word"],
        loc="center",
        cellLoc="center",
        bbox=[0.02, 0.08, 0.96, 0.84],
    )
    _style_table(table, colors=tuple(table_colors))
    ax_table.set_title(
        "Opening words",
        fontsize=11,
        fontweight="bold",
        color=_HEADER_BG,
        pad=12,
    )

    fig.suptitle(
        f"Strategy benchmark ({secrets_played} secrets played)",
        fontsize=13,
        fontweight="bold",
        color=_HEADER_BG,
        y=1.01,
    )
    fig.tight_layout()

    plot_path = output_dir / PLOT_FILENAME
    fig.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return plot_path


def plot_benchmark_file(
    results_file: Path,
    output_dir: Path | None = None,
) -> Path:
    """Load *results.json* and write benchmark.png next to it (or in *output_dir*)."""
    summary = load_results(results_file)
    target_dir = output_dir if output_dir is not None else results_file.parent
    return plot_benchmark(summary, target_dir)


def plot_benchmark_dir(output_dir: Path) -> Path:
    """Load output_dir/results.json and write output_dir/benchmark.png."""
    return plot_benchmark_file(results_path(output_dir), output_dir)
