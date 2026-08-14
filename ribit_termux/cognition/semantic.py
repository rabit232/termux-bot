"""Bounded deterministic semantic retrieval for a local Termux runtime.

This module harmonizes the archive's ``tensor_memory.py``, ``embedding_engine``
and ``mock_model`` patterns. It purposely uses a stable SHA-256 hash projection
rather than an optional heavyweight embedding model, so retrieval behaves the
same across Termux restarts and requires no network or model download.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

_TOKEN_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text) if len(token) > 1]


def embed(text: str, *, dimension: int = 96) -> tuple[float, ...]:
    """Create a stable normalized signed-hash vector from text tokens."""

    values = [0.0] * dimension
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = -1.0 if digest[4] & 1 else 1.0
        values[index] += sign * (1.0 + min(len(token), 12) / 20.0)
    norm = math.sqrt(sum(value * value for value in values)) or 1.0
    return tuple(value / norm for value in values)


def cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right))


@dataclass(slots=True)
class SemanticRecord:
    """One bounded, local semantic-memory entry."""

    key: str
    text: str
    tags: tuple[str, ...] = ()
    importance: float = 1.0
    access_count: int = 0
    attention: float = 0.0
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    vector: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        self.text = " ".join(self.text.split())[:2000]
        self.tags = tuple(sorted({tag.casefold().strip() for tag in self.tags if tag.strip()}))
        self.importance = max(0.0, min(float(self.importance), 3.0))
        if not self.vector:
            self.vector = embed(self.text)


class SemanticMemory:
    """A capped in-process semantic index with transparent ranking metadata."""

    def __init__(self, *, max_records: int = 800, dimension: int = 96) -> None:
        self.max_records = max(50, max_records)
        self.dimension = dimension
        self.records: dict[str, SemanticRecord] = {}

    def add(
        self,
        key: str,
        text: str,
        *,
        tags: tuple[str, ...] = (),
        importance: float = 1.0,
    ) -> None:
        if not key.strip() or not text.strip():
            return
        record = SemanticRecord(key=key[:200], text=text, tags=tags, importance=importance)
        previous = self.records.get(record.key)
        if previous is not None:
            record.access_count = previous.access_count
            record.attention = previous.attention
            record.created_at = previous.created_at
        self.records[record.key] = record
        self._enforce_limit()

    def search(self, query: str, *, limit: int = 5) -> list[dict[str, object]]:
        if not query.strip():
            return []
        query_vector = embed(query, dimension=self.dimension)
        ranked: list[tuple[float, SemanticRecord]] = []
        for record in self.records.values():
            score = cosine(query_vector, record.vector) * 0.75 + record.importance * 0.15 + record.attention * 0.10
            ranked.append((score, record))
        ranked.sort(key=lambda item: item[0], reverse=True)
        result: list[dict[str, object]] = []
        for score, record in ranked[: max(1, limit)]:
            record.access_count += 1
            record.attention = min(1.0, record.attention + 0.05)
            record.updated_at = _now()
            result.append(
                {
                    "key": record.key,
                    "text": record.text,
                    "score": round(score, 4),
                    "tags": list(record.tags),
                    "importance": record.importance,
                    "attention": round(record.attention, 3),
                }
            )
        return result

    def decay_attention(self, *, factor: float = 0.98) -> None:
        factor = max(0.0, min(factor, 1.0))
        for record in self.records.values():
            record.attention *= factor

    def stats(self) -> dict[str, int | str]:
        return {"records": len(self.records), "dimension": self.dimension, "backend": "stable-hash"}

    def _enforce_limit(self) -> None:
        overflow = len(self.records) - self.max_records
        if overflow <= 0:
            return
        candidates = sorted(
            self.records.values(),
            key=lambda record: (record.importance + record.attention, record.updated_at),
        )
        for record in candidates[:overflow]:
            self.records.pop(record.key, None)
