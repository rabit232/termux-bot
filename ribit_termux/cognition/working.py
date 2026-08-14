"""Bounded working memory and diagnostic thought trace for one Termux runtime.

Adapted from the supplied ``working_memory.py`` and ``thought_stream.py``.
Entries are local metadata, not hidden reasoning or executable task state.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class WorkingMemoryItem:
    key: str
    value: Any
    category: str
    importance: float
    created_at: str


@dataclass(slots=True)
class TraceEvent:
    stage: str
    summary: str
    created_at: str


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class WorkingMemory:
    """Small local LRU-like memory with bounded importance-aware eviction."""

    def __init__(self, *, capacity: int = 64) -> None:
        self.capacity = max(1, capacity)
        self.items: dict[str, WorkingMemoryItem] = {}

    def put(self, key: str, value: Any, *, category: str, importance: float = 0.5) -> None:
        self.items[key[:160]] = WorkingMemoryItem(
            key=key[:160],
            value=value,
            category=category[:80],
            importance=max(0.0, min(float(importance), 1.0)),
            created_at=_now(),
        )
        self._evict()

    def find(self, category: str) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.items.values() if item.category == category]

    def stats(self) -> dict[str, int]:
        return {"items": len(self.items), "capacity": self.capacity}

    def _evict(self) -> None:
        excess = len(self.items) - self.capacity
        if excess <= 0:
            return
        low_value = sorted(self.items.values(), key=lambda item: (item.importance, item.created_at))[:excess]
        for item in low_value:
            self.items.pop(item.key, None)


class ThoughtTrace:
    """A bounded, user-safe event summary log, not a chain-of-thought store."""

    def __init__(self, *, capacity: int = 128) -> None:
        self.events: deque[TraceEvent] = deque(maxlen=max(1, capacity))

    def add(self, stage: str, summary: str) -> None:
        self.events.append(TraceEvent(stage=stage[:80], summary=" ".join(summary.split())[:300], created_at=_now()))

    def latest(self, *, limit: int = 8) -> list[dict[str, str]]:
        return [asdict(event) for event in list(self.events)[-max(1, limit):]]

    def stats(self) -> dict[str, int]:
        return {"events": len(self.events), "capacity": self.events.maxlen or 0}
