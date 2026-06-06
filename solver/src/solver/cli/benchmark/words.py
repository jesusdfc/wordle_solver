"""Benchmark secret-word list loading and sampling."""

from __future__ import annotations

import json
import random
from pathlib import Path


def subsample_secrets(words: tuple[str, ...], size: int, *, seed: int) -> tuple[str, ...]:
    """Return *size* random secrets drawn from *words* (0 = all words)."""
    if size <= 0 or size >= len(words):
        return words
    rng = random.Random(seed)
    return tuple(sorted(rng.sample(list(words), size)))


def _validate_secrets(secrets: tuple[str, ...], all_words: tuple[str, ...]) -> None:
    word_set = set(all_words)
    missing = [word for word in secrets if word not in word_set]
    if missing:
        raise ValueError(
            f"benchmark word list contains {len(missing)} words not in the dictionary "
            f"(e.g. {missing[0]!r}); delete the file or pass --resample-words"
        )


def load_or_create_benchmark_words(
    path: Path,
    all_words: tuple[str, ...],
    *,
    num_secrets: int,
    seed: int,
    resample: bool = False,
) -> tuple[str, ...]:
    """Load a fixed secret-word list from *path*, or sample and save it once."""
    if path.is_file() and not resample:
        payload = json.loads(path.read_text(encoding="utf-8"))
        secrets = tuple(payload["words"])
        _validate_secrets(secrets, all_words)
        return secrets

    secrets = subsample_secrets(all_words, num_secrets, seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "seed": seed,
                "num_secrets": num_secrets,
                "dictionary_size": len(all_words),
                "words": list(secrets),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return secrets
