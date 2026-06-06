"""Precomputed pattern lookup table for Wordle feedback."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from solver.env import WordleEnv


@dataclass(frozen=True)
class PatternTable:
    """O(1) lookup for feedback patterns over a fixed word list."""

    words: tuple[str, ...]
    _patterns: bytes
    _index: dict[str, int] = field(init=False, repr=False)
    _matrix: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        expected = len(self.words) ** 2
        if len(self._patterns) != expected:
            raise ValueError(f"pattern buffer length {len(self._patterns)} != {len(self.words)}²")
        object.__setattr__(
            self,
            "_index",
            {word: index for index, word in enumerate(self.words)},
        )

    def as_matrix(self):
        """Return the secret × guess pattern matrix as a NumPy uint8 array."""
        matrix = object.__getattribute__(self, "_matrix")
        if matrix is not None:
            return matrix

        import numpy as np

        count = len(self.words)
        matrix = np.frombuffer(self._patterns, dtype=np.uint8).reshape(count, count)
        object.__setattr__(self, "_matrix", matrix)
        return matrix

    @property
    def _pattern_count(self) -> int:
        return 3 ** len(self.words[0])

    def _candidate_indices(self, candidates: Sequence[str]):
        import numpy as np

        return np.fromiter(
            (self._index[word] for word in candidates),
            dtype=np.intp,
            count=len(candidates),
        )

    def _pool_indices(self, pool: Sequence[str]):
        import numpy as np

        return np.fromiter(
            (self._index[word] for word in pool),
            dtype=np.intp,
            count=len(pool),
        )

    def bucket_sizes(self, candidates: Sequence[str], guess: str):
        """Return non-zero bucket sizes for *guess* over *candidates*."""
        import numpy as np

        guess_index = self._index[guess]
        patterns = self.as_matrix()[self._candidate_indices(candidates), guess_index]
        counts = np.bincount(patterns, minlength=self._pattern_count)
        return counts[counts > 0]

    def entropy_scores(self, candidates: Sequence[str], pool: Sequence[str]):
        """Expected Shannon entropy (bits) for every guess in *pool*."""
        import numpy as np

        if not candidates or not pool:
            return np.array([], dtype=np.float64)

        matrix = self.as_matrix()
        candidate_indices = self._candidate_indices(candidates)
        pool_indices = self._pool_indices(pool)
        patterns = matrix[candidate_indices][:, pool_indices]
        total = len(candidates)
        minlength = self._pattern_count

        scores = np.empty(len(pool_indices), dtype=np.float64)
        for index, column in enumerate(patterns.T):
            counts = np.bincount(column, minlength=minlength)
            counts = counts[counts > 0]
            probabilities = counts / total
            scores[index] = -np.sum(probabilities * np.log2(probabilities))
        return scores

    def partition_groups(
        self,
        candidates: Sequence[str],
        guess: str,
    ) -> list[tuple[str, ...]]:
        """Group candidates by feedback pattern; each group is a sorted word tuple."""
        if not candidates:
            return []

        try:
            import numpy as np

            guess_index = self._index[guess]
            candidate_indices = self._candidate_indices(candidates)
            patterns = self.as_matrix()[candidate_indices, guess_index]
            order = np.argsort(patterns, kind="stable")
            patterns_sorted = patterns[order]
            indices_sorted = candidate_indices[order]
            words = self.words

            groups: list[tuple[str, ...]] = []
            start = 0
            for end in range(1, len(patterns_sorted) + 1):
                if end == len(patterns_sorted) or patterns_sorted[end] != patterns_sorted[start]:
                    bucket = tuple(sorted(words[index] for index in indices_sorted[start:end]))
                    groups.append(bucket)
                    start = end
            return groups
        except KeyError:
            from collections import defaultdict

            buckets: dict[int, list[str]] = defaultdict(list)
            for candidate in candidates:
                buckets[self.pattern(candidate, guess)].append(candidate)
            return [tuple(sorted(bucket)) for bucket in buckets.values()]

    @classmethod
    def build(
        cls,
        words: tuple[str, ...],
        *,
        length: int = 5,
        show_progress: bool = False,
    ) -> PatternTable:
        """Compute the full secret × guess pattern matrix."""
        count = len(words)
        patterns = bytearray(count * count)
        rows = enumerate(words)
        if show_progress:
            from tqdm import tqdm

            rows = tqdm(
                list(enumerate(words)),
                total=count,
                desc=f"entropy_{length}_lookup_table",
                unit=" rows",
            )
        for secret_index, secret in rows:
            row_offset = secret_index * count
            for guess_index, guess in enumerate(words):
                patterns[row_offset + guess_index] = WordleEnv.pattern(secret, guess)
        return cls(words=words, _patterns=bytes(patterns))

    def pattern(self, secret: str, guess: str) -> int:
        """Return feedback for `guess` when the answer is `secret`."""
        try:
            secret_index = self._index[secret]
            guess_index = self._index[guess]
        except KeyError:
            return WordleEnv.pattern(secret, guess)
        return self._patterns[secret_index * len(self.words) + guess_index]
